##### to fix pytorch auto-download problem with SSL certificate ###
import ssl
import os


#### NIMA: to fix proxy issue - from Simran ####
os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['ftp_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'
os.environ['no_proxy'] = '127.0.0.*,*.huawei.com,localhost'
os.environ['cntlm_proxy'] = '127.0.0.1:3128'
os.environ['SSL_CERT_DIR'] = '/etc/ssl/certs'
ssl._create_default_https_context = ssl._create_unverified_context
#####

from torchvision.io import read_image
from torchvision.models import resnet50, ResNet50_Weights

main_dir = './imagenet_sub/0/'
# Step 1: Initialize model with the best available weights
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

# Step 2: Initialize the inference transforms
preprocess = weights.transforms()
preprocess.resize_size = [256]
# classname = "class1_"
counter_cl0 = 0.
counter_cl1 = 0.
counter_total = 0
for root, dirs, files in os.walk(main_dir):
    for file in files:
        if "class0" in file:
            counter_total +=1
            #filename = file.split('.')[0]
            file_dir = os.path.join(root, file)
            img = read_image(file_dir)

            # Step 3: Apply inference preprocessing transforms
            batch = preprocess(img).unsqueeze(0)

            # Step 4: Use the model and print the predicted category
            prediction = model(batch).squeeze(0).softmax(0)
            class_id = prediction.argmax().item()
            score = prediction[class_id].item()
            category_name = weights.meta["categories"][class_id]
            print(f"{file}_{class_id}_{category_name}: {100 * score:.1f}%")
            if class_id == 0:
                counter_cl0 +=1.
        elif "class1" in file:
            counter_total += 1
            #filename = file.split('.')[0]
            file_dir = os.path.join(root, file)
            img = read_image(file_dir)

            # Step 3: Apply inference preprocessing transforms
            batch = preprocess(img).unsqueeze(0)

            # Step 4: Use the model and print the predicted category
            prediction = model(batch).squeeze(0).softmax(0)
            class_id = prediction.argmax().item()
            score = prediction[class_id].item()
            category_name = weights.meta["categories"][class_id]
            print(f"{file}_{class_id}_{category_name}: {100 * score:.1f}%")
            if class_id == 999:
                counter_cl1 +=1.

print(f'Accuracy is {(counter_cl0+ counter_cl1)/counter_total}')