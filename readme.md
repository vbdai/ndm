# NFT-Based Data Marketplace with Digital Watermarking
This is the notebook for the [NFT-Based Data Marketplace with Digital Watermarking accepted](https://dl.acm.org/doi/abs/10.1145/3580305.3599876) for publication in 29TH ACM SIGKDD CONFERENCE ON KNOWLEDGE DISCOVERY AND DATA MINING. The notebook has three parts: The first part is for the watermarking experiments, the second part is related to the blockchain experiments, and the third part is related to the codes for demo. 

Link to Huawei's AI Gallery Notebook: https://developer.huaweicloud.com/develop/aigallery/notebook/detail?id=d46d68ac-2e75-42c3-9c11-295a13f5c2c1

Get the code and unzip it using the following code

```python
!wget https://vbdai-notebooks.obs.cn-north-4.myhuaweicloud.com/ndm/code.zip 
!unzip -qo code.zip
```

## Watermarking codes
This part of the code is to reproduce the results in Section 4.2.3: Watermarking Robustness. 

### prepare data
In the paper data from two classes (tench/n01440764 and toilet paper/n15075141) of imagenet validation dataset (can be downloaded from https://image-net.org/download.php) are used. You can use your own data as well by setting --data_dir. Add "class0_" to the image names in n01440764 and "class1_" to image names in n15075141 (e.g., class0_ILSVRC2012_val_00000293.jpg) when copying the imagenet subset images into imagenet_sub directory.  

### prepare env


```python
#create a conda env with  (in our case nft_kdd)
#conda create -n nft_kdd python=3.8.13
#!conda activate nft_kdd
#!conda list
!pip install -r ./wm_codes/requirements.txt
```


```bash
%%bash
# Download pretrained models 
if ! [ -f ./wm_codes/normlayers/out2048_coco_orig.pth ]; then
    echo "Did not detect out2048_yfcc_orig.pth. Downloading fresh copy to wn_codes/normlayers..."
    mkdir -p ./wm_codes/normlayers
    wget --no-check-certificate https://dl.fbaipublicfiles.com/ssl_watermarking/out2048_coco_orig.pth -P ./wm_codes/normlayers
fi

if ! [ -f ./wm_codes/models/dino_r50_plus.pth ]; then
    echo "Did not detect dino_r50_plus.pth. Downloading fresh copy to src/ssl_watermarking/models..."
    mkdir -p ./wm_codes/models
    wget --no-check-certificate https://dl.fbaipublicfiles.com/ssl_watermarking/dino_r50_plus.pth -P ./wm_codes/models
fi

if ! [ -f ~/.cache/torch/hub/checkpoints/resnet50-0676ba61.pth ]; then
    echo "Did not detect resnet50.pth. Downloading fresh copy to ...~/.cache/torch/hub/checkpoints"
    wget --no-check-certificate https://download.pytorch.org/models/resnet50-0676ba61.pth -P ~/.cache/torch/hub/checkpoints/
fi
```

### run experiments
set data directory (--data_dir) accordingly


```python
## results with L=6 with ECC, L=15 with ECC and L=25 (W/O ECC)
!python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 6 --num_bits 12 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --save_images false

!python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 15 --num_bits 30 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --save_images false

!python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 25 --num_bits 50 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --save_images false
```


```python
## results with L=6 with ECC, L=15 with ECC and L=25 with ECC 
!python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 6 --num_bits 20 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --ecc true --save_images false

!python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 15 --num_bits 40 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --ecc true --save_images false

python ./wm_codes/main_multibit.py --data_dir ./wm_codes/input/ --model_path ./wm_codes/models/dino_r50_plus.pth --normlayer_path ./wm_codes/normlayers/out2048_coco_orig.pth --user_path ./wm_codes/users --output_dir ./wm_codes/output/ --target_psnr_list 20 25 30 35 40 45 --num_bits_ID 25 --num_bits 60 --batch_size 1 --carrier_dir ./wm_codes/carriers/ --ecc true --save_images false
```

### visualize 
After the execution all the final results are saved as csv files in the ./wm_codes/output dir. We included our execution results in ./wm_codes/output/csvs/*. To visualize the results in Figure 5, use the python code in  ./wm_codes/plots_paper


```python
!python ./wm_codes/plots_paper/Plot_ECC.py 
```

The image EEC.png is saved in ./wm_codes/plots_paper

## Blockchain codes
To reproduce the results related to Section 4.2.1 Gas Consumption and 4.2.2 Batch minting: 
The smart contracts and the codes are in codes/eth_codes

### Dependencies
Python: 3.8.15 or higher

web3.py: https://github.com/ethereum/web3.py

hardhat: https://hardhat.org/

matplotlib: https://matplotlib.org/stable/index.html#

numpy: https://numpy.org/

pycryptodome: https://github.com/Legrandin/pycryptodome

### Running the code
Each of the scripts in the `plots/` directory will produce the results related to the blockchain experiment found in the paper. 

All of these scripts require an Ethereum node. Easiest way to set this up is to
use a local node provided by Hardhat. You can also use your own Ethereum node or 
a Ethereum Test Network, however, you will need to change the hardcoded Ethereum 
endpoint in the scripts. After installing all the dependencies, you can boot one 
up using:

```
$ npx hardhat node
```
The `contracts/` directory contains all the smart contracts used by our market.
The scripts will automatically deploy these contracts when you run them, however
you still need to compile these smart contracts. Compile them using

```
$ npx hardhat compile
```

Hardhat should automatically detect where the contracts are located and produce an 
`artifacts/` directory. Do not modify the layout of this directory, the scripts
are expecting the default layout.

`python plots/gas_method.py` plots how much gas is needed to deploy each contract
and how much gas each smart contract method costs (Table 1. top )

`python plots/registration_trade_plot.py` plots how much gas is needed for each
stage of the market. (Table 1 bottom)

`python plots/batchmint_gas_plot.py` plots how much gas is needed to mint a certain
number of assets (Figure 3)

The `plots/contract_local.py` is a wrapper over the web3.py library and used
by every other script. 

## Demo 
This part of the repo has the code to run a POC demo for the proposed data marketplace. The readme file in the ./demo includes the instructions to run the code.    

## Video Demo


```python
%%HTML
<video width="1280" controls>
    <source src="https://vbdai-notebooks.obs.cn-north-4.myhuaweicloud.com/ndm/demo_final.mp4" type="video/mp4">
</video>
```


<video width="1280" controls>
    <source src="https://vbdai-notebooks.obs.cn-north-4.myhuaweicloud.com/ndm/demo_final.mp4" type="video/mp4">
</video>



## Citation: 
@inproceedings{nft_marketplace,
  title={NFT-Based Data Marketplace with Digital Watermarking},
  author={Ranjbar Alvar, Saeed and Akbari, Mohammad and Yue, David (Ming Xuan) and Zhang, Yong },
  booktitle={29TH ACM SIGKDD CONFERENCE ON KNOWLEDGE DISCOVERY AND DATA MINING},
  year={2023},
  organization={ACM},
}

## References: 
For the watermarking codes, we borrowed code from the following repo:
https://github.com/facebookresearch/ssl_watermarking


