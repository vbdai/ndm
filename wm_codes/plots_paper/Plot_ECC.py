import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

quality_list = [20,25,30,35,40,45]
user_number = [6,15,25]
df_list = []
df_list_ecc=[]

color_list = ['tab:blue','tab:orange','tab:red']
marker_list = ['v',".",'*']
fig, ax1 = plt.subplots(figsize=(10, 7.5))
for i, wm_bit in enumerate(user_number):
    acc_list = []
    acc_ecc_lsit = []
    for q in quality_list:
        output_dir = f'./wm_codes/output/'  
        df_filename =  f'df_agg_{int(q)}_{int(wm_bit)}.csv'
        df_name = os.path.join(output_dir,df_filename)
        df = pd.read_csv(df_name)
        df = df.drop([9,21,23,41,49,50]) #Excluding the birghtness1,crop1,contracst1,NONE,resize1,rotate0 attack as they are not attacks
        df_list.append(df.values)
        acc_list.append((pd.to_numeric(df['ID_acc'][2:]).mean(axis=0))*100.0)

        output_dir_ecc = f'./wm_codes/output/'
        df_filename_ecc =  f'df_agg_{int(q)}_{int(wm_bit)}_ecc.csv'
        df_name_ecc = os.path.join(output_dir_ecc,df_filename_ecc)
        df_ecc = pd.read_csv(df_name_ecc)
        df_ecc = df_ecc.drop([9, 21, 23, 41, 49, 50])
        df_list_ecc.append(df_ecc.values)
        acc_ecc_lsit.append((pd.to_numeric(df_ecc['ID_acc'][2:]).mean(axis=0))*100.0)


    print(acc_ecc_lsit[2])
    print(acc_ecc_lsit[0]-acc_list[0])
    print(acc_ecc_lsit[1] - acc_list[1])
    print(acc_ecc_lsit[2] - acc_list[2])
    print(acc_ecc_lsit[3] - acc_list[3])
    print(acc_ecc_lsit[4] - acc_list[4])
    print(acc_ecc_lsit[5] - acc_list[5])
    ax1.plot(quality_list, acc_list,marker_list[i]+"-",
             color=color_list[i],label=f'$L={user_number[i]}$',markersize=12,linewidth=3.0)
    ax1.plot(quality_list, acc_ecc_lsit,marker_list[i]+"-.",
             color=color_list[i],label=f'$L={user_number[i]}$ with ECC ',markersize=12,linewidth=3.0)

    ax1.set_xlabel('PSNR (original vs watermarked) dB')
    ax1.set_ylabel('Average extracted ID accuracy') 
    ax1.set_ybound(lower=28.0, upper=1.05*100.0) 

for item in ([ax1.title, ax1.xaxis.label, ax1.yaxis.label] + ax1.get_xticklabels() + ax1.get_yticklabels()):
    item.set_fontsize(24)

plt.legend(loc="lower left",fontsize=22)
plt.savefig('./wm_codes/plots_paper/ECC.png')
plt.show()
