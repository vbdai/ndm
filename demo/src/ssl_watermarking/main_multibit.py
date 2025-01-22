# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import os
from os import path, remove
from shutil import move
from tempfile import NamedTemporaryFile
import numpy as np
import torch
from torchvision.transforms import ToPILImage
from glob import glob
from os import remove
from os.path import join
from ssl_watermarking import data_augmentation
from ssl_watermarking import encode
from ssl_watermarking import evaluate
from ssl_watermarking import utils
from ssl_watermarking import utils_img
import hamming_codec
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    # random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


class Watermark:

    def __init__(self) -> None:

        self.data_dir = "src/ssl_watermarking/input"
        self.carrier_dir = "src/ssl_watermarking/carriers"
        self.output_dir = "src/ssl_watermarking/output"
        self.save_images = True
        self.decode_only = False
        self.verbose = 1

        self.msg_type = "bit"
        self.msg_path = None
        self.num_bits = 17
        self.target_psnr = 32.0
        self.target_fpr = 1e-6
        self.model_name = "resnet50"
        self.model_path = "src/ssl_watermarking/models/dino_r50_plus.pth"
        self.normlayer_path = "src/ssl_watermarking/normlayers/out2048_yfcc_orig.pth"

        self.epochs = 100
        self.data_augmentation = "all"
        self.optimizer = "Adam,lr=0.01"
        self.scheduler = None
        self.batch_size = 1
        self.lambda_w = 5e4
        self.lambda_i = 1.0

        # Set seeds for reproductibility
        set_seed(1)
        # torch.manual_seed(0)
        # np.random.seed(0)
        self.carrier = None
        self.model = None
        # If message file, set num_bits to the maximum number of message payload in the file
        if self.msg_path is not None:
            num_bits = utils.get_num_bits(
                self.msg_path, self.msg_type)
            if self.num_bits != num_bits:
                warning_msg = 'WARNING: Number of bits in the loaded message ({a}) does not match the number of bits indicated in the num_bit argument ({b}). \
                    Setting num_bits to {a} \
                    Try with "--num_bit {a}" to remove the warning'.format(a=num_bits, b=self.num_bits)
                print(warning_msg)
            self.num_bits = num_bits

        # Loads backbone and normalization layer
        if self.verbose > 0:
            print('>>> Building backbone and normalization layer...')
        backbone = utils.build_backbone(
            path=self.model_path, name=self.model_name)
        normlayer = utils.load_normalization_layer(
            path=self.normlayer_path)
        self.model = utils.NormLayerWrapper(backbone, normlayer)
        for p in self.model.parameters():
            p.requires_grad = False
        self.model.eval()

        # Load or generate carrier and angle
        if not os.path.exists(self.carrier_dir):
            os.makedirs(self.carrier_dir, exist_ok=True)
        D = self.model(torch.zeros((1, 3, 224, 224)).to(device)).size(-1)
        K = self.num_bits
        carrier_path = os.path.join(
            self.carrier_dir, 'carrier_%i_%i.pth' % (K, D))
        if os.path.exists(carrier_path):
            if self.verbose > 0:
                print('>>> Loading carrier from %s' % carrier_path)
            self.carrier = torch.load(carrier_path)
            assert D == self.carrier.shape[1]
        else:
            if self.verbose > 0:
                print(
                    '>>> Generating carrier into %s... (can take up to a minute)' % carrier_path)
            self.carrier = utils.generate_carriers(
                K, D, output_fpath=carrier_path)
        # direction vectors of the hyperspace
        self.carrier = self.carrier.to(device, non_blocking=True)

    def remove_dir_contents(self, dir: str):

        files = glob(join(dir, "*"))

        for f in files:
            remove(f)

    def decode_watermark(self):
        # Decode only
        if self.verbose > 0:
            print('>>> Decoding watermarks...')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        df = evaluate.decode_multibit_from_folder(
            self.data_dir, self.carrier, self.model, self.msg_type)
        return df['msg'].tolist()

    def watermark(self):
        # Load images
        if self.verbose > 0:
            print('>>> Loading images from %s...' % self.data_dir)
        dataloader = utils_img.get_dataloader(
            self.data_dir, batch_size=self.batch_size)

        # Generate messages
        if self.verbose > 0:
            print('>>> Loading messages...')
        if self.msg_path is None:
            msgs = utils.generate_messages(
                len(dataloader.dataset), self.num_bits)  # NxK
        # if a msg_path is given, save/load from it instead
        else:
            if not os.path.exists(self.msg_path):
                if self.verbose > 0:
                    print('Generating random messages into %s...' %
                          self.msg_path)
                os.makedirs(os.path.dirname(
                    self.msg_path), exist_ok=True)
                msgs = utils.generate_messages(
                    len(dataloader.dataset), self.num_bits)  # NxK
                utils.save_messages(msgs, self.msg_path)
            else:
                if self.verbose > 0:
                    print('Loading %s messages from %s...' %
                          (self.msg_type, self.msg_path))
                msgs = utils.load_messages(
                    self.msg_path, self.msg_type, len(dataloader.dataset))

        # Construct data augmentation
        if self.data_augmentation == 'all':
            data_aug = data_augmentation.All()
        elif self.data_augmentation == 'none':
            data_aug = data_augmentation.DifferentiableDataAugmentation()

        # Marking
        if self.verbose > 0:
            print('>>> Marking images...')
        pt_imgs_out = encode.watermark_multibit(
            dataloader, msgs, self.carrier, self.model, data_aug, self)
        imgs_out = [ToPILImage()(utils_img.unnormalize_img(pt_img).squeeze(0))
                    for pt_img in pt_imgs_out]

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        imgs_dir = os.path.join(self.output_dir, 'imgs')
        if self.verbose > 0:
            print('>>> Saving images into %s...' % imgs_dir)
        if not os.path.exists(imgs_dir):
            os.mkdir(imgs_dir)
        for ii, img_out in enumerate(imgs_out):
            img_out.save(os.path.join(imgs_dir, '%i_out.png' %
                         ii), format="PNG")

    def extract_watermark(self, img_filepath: str):
        self.remove_dir_contents(join(self.data_dir, "0"))
        base = path.basename(img_filepath)

        new_path = path.join(self.data_dir, base)

        move(img_filepath, new_path)

        wm = self.decode_watermark()

        move(new_path, img_filepath)
        print("decode before hamming: %s" % wm[0])
        wm = hamming_codec.decode(int(wm[0], 2), 17)

        oid = int(wm[:6], 2)
        bid = int(wm[6:], 2)

        return oid, bid

    def set_watermark(self, owner_id: int, buyer_id: int):

        t = NamedTemporaryFile("w", delete=False)

        owner_bin = bin(owner_id)[2:]
        buyer_bin = bin(buyer_id)[2:]

        owner_bin = owner_bin.zfill(8)
        buyer_bin = buyer_bin.zfill(8)

        watermark_bin = owner_bin[2:] + buyer_bin[2:]

        encoded_message = int(watermark_bin, 2)

        encoded_message = hamming_codec.encode(encoded_message, 12)

        print(len(encoded_message))

        print("encoded watermark: %s" % encoded_message)

        t.write(encoded_message)

        t.close()

        self.msg_path = t.name

    def watermark_image(self, img_filepath: str):

        base = path.basename(img_filepath)

        new_path = path.join(self.data_dir, "0", base)

        self.remove_dir_contents(path.join(self.data_dir, "0"))

        move(img_filepath, new_path)

        self.watermark()

        remove(new_path)

        move(path.join(self.output_dir, "imgs/0_out.png"), img_filepath)
