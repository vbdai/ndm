import os
# move files from Imagnet subfolder to SSL image folder
main_dir = './imagenet_sub/n01440764/'
target_dir = './imagenet_sub/0/'
classname = "class0_"
for root, dirs, files in os.walk(main_dir):
    for file in files:
        os.rename(os.path.join(root, file), os.path.join(target_dir,classname+file ))

#class 0 : tench class_id 0  n01440764
#class1 : toilet tissue 999 n15075141

# Rename JPEG to JPG fileformat
main_dir = './imagenet_sub/0/'
# classname = "class1_"
for root, dirs, files in os.walk(main_dir):
    for file in files:
        filename = file.split('.')[0]
        if '.JPEG' in file:
            os.rename(os.path.join(root, file), os.path.join(root,filename+".jpg" ))



##class0 : corn class_id 987 n13133613