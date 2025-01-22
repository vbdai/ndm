import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

output_dir = './output/'
quality_list = [20,25,30,35,40,45]
acc_list = []
df_list = []
value_list = []
max_value = 75.0 #np.amax(value_attacks) #obtain by running the imagnet_class.py
for q in quality_list:
    df_filename =  f'df_agg_{q}.csv'
    df_name = os.path.join(output_dir,df_filename)
    df = pd.read_csv(df_name)
    df_list.append(df.values)
    acc_list.append((pd.to_numeric(df['ID_acc'][2:]).mean(axis=0))*100.0)
    value_attacks = pd.to_numeric(df['pred_acc'][2:])
    value_attacks = (value_attacks/ max_value)*100.0
    value_list.append(value_attacks.mean(axis=0))


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(quality_list, acc_list, 'b.-')
ax2.plot(quality_list, value_list, 'go-')
#plt.plot(quality_list, acc_list,".-")
#plt.xlabel('PSNR (original asset vs watermakred asset)')
#plt.ylabel('Average user ID recovery accuracy')
ax1.set_xlabel('PSNR (original asset vs watermakred asset)')
#plt.set_ylabel('Average user ID recovery accuracy')
ax1.set_ylabel('Average user ID recovery accuracy', color='b')
ax2.set_ylabel('Average aseet value', color='g')
plt.savefig('overall_attack.png')
plt.show()

#plot per attack
plt.figure()
n_sub_row = 10
n_sub_col = 6
fig, axs = plt.subplots(n_sub_row, n_sub_col,constrained_layout=True)
fig.set_size_inches(20,15)
for ax in fig.get_axes():
    ax.set_ybound(lower=0.0, upper=110.0)

counter = -1
for i in np.arange(2,df_list[0].shape[0]):
    counter +=1
    attack_name  = df_list[0][i][0]
    attack_param =  df_list[0][i][1]
    ID_recovery_acc = []
    value = []
    for j in np.arange(len(quality_list)):
        ID_recovery_acc.append(float(df_list[j][i][10])*100.0)
        value.append((float(df_list[j][i][14])*100./max_value) * 100.0)
    x_ax = counter// 6
    y_ax  = counter % 6
    ax_here = axs[x_ax,y_ax]
    ax_here_2nd = ax_here.twinx()
    ax_here.plot(quality_list, ID_recovery_acc,"b.-")
    ax_here_2nd.plot(quality_list, value,"g.-")
    #axs[x_ax,y_ax].set_xlabel('PSNR (original asset vs watermakred asset)')
    #axs[x_ax,y_ax].set_ylabel('User ID recovery accuracy')
    ax_here.set_ybound(lower=0.0, upper=1.1*100.0) #set_ylim([0,1])
    ax_here_2nd.set_ybound(lower=0.0, upper=1.1 * 100.0)
    ax_here.title.set_text(f'{attack_name}_{attack_param:.4}_{np.mean(np.array(value)):.4}')
    ax_here.set_ylabel('ID rec (%)', color='b')
    ax_here_2nd.set_ylabel('Value', color='g')
fig.supxlabel('PSNR (original asset vs watermakred asset)',)
#fig.supylabel('Average user ID recovery accuracy')
#for ax in fig.get_axes():
#    ax.label_outer()
fig.delaxes(axs[9,3])
fig.delaxes(axs[9,4])
fig.delaxes(axs[9,5])
plt.savefig('per_attack.png')
plt.show()
