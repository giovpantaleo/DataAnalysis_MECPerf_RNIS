
''' 
This script returns the statistics related to 5G RNIS blueprint.
'''

import ast
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np




# READ THE FILE


file1 = open("measure/07-07/test.log", "r")

lines = file1.readlines()


# TRANSFORMATION AND SELECTION OF THE FIELDS

dict_key = {'cqi':[], 'rsrp':[], 'mcs_ul': [], 'mcs_dl':[], 'phr':[], 'bler_ul':[], 'bler_dl':[], 'data_ul':[], 'data_dl':[], 'snr':[], 'timestamp':[]}
for i, line in enumerate(lines[4:]):#[900:1160]):     
    # creation of json obj
    tp = ast.literal_eval(line) 
    # creation of dictionary for the UE
    dict_key['cqi'].append(tp['Report']['cqi']['value'])
    dict_key['rsrp'].append(tp['Report']['rsrp']['value'])
    dict_key['mcs_ul'].append(tp['Report']['mcs_ul']['value'])
    dict_key['mcs_dl'].append(tp['Report']['mcs_dl']['value'])
    dict_key['phr'].append(tp['Report']['phr']['value'])
    dict_key['bler_ul'].append(tp['Report']['bler_ul']['value'])
    dict_key['bler_dl'].append(tp['Report']['bler_dl']['value'])
    dict_key['data_ul'].append(tp['Report']['data_ul']['value'])
    dict_key['data_dl'].append(tp['Report']['data_dl']['value'])
    dict_key['snr'].append(tp['Report']['snr']['value'])
    dict_key['timestamp'].append(tp['TimeStamp'])

delta_time = [0]
for i, j in enumerate(dict_key['timestamp']):
    if i > 0:
        delta = j-dict_key['timestamp'][i-1]
        delta_time.append(delta)
dict_key['timediff'] = delta_time
dataFrame = pd.DataFrame(dict_key)
dataFrame2 = dataFrame[dataFrame['timediff']>0]
[nRow, nCol] = dataFrame2.shape
idxs_old = list(dataFrame2.index)
dict_new_index = {idxs_old[i]: i for i in range(nRow) }
dataFrame2 = dataFrame2.rename(index = dict_new_index )#, inplace=True)


t = 0
#t_real = [0]
t_real = []
bw_ul = []
bw_dl = []
i = 0
for j in dataFrame2['timediff']:
    t = t+j
    t_real.append(t)
    #print(dataFrame2.data_ul[3])

    bw_ul.append(dataFrame2.loc[i, 'data_ul']/dataFrame2.loc[i, 'timediff']*0.008) #kBits/s
    bw_dl.append(dataFrame2.loc[i, 'data_dl']/dataFrame2.loc[i, 'timediff']*0.008)
    i = i + 1

dataFrame2['bw_ul'] = bw_ul
dataFrame2['bw_dl'] = bw_dl

#BANDWIDTH --- Estimation of the bandwidth
bw = []
alfa = 75/80#0.8
for i,j in enumerate(bw_ul):   #dataFrame2['bw_ul']
    if i ==0:
        bw_est = j
    else:
        bw_est = bw[i-1]*alfa +(1-alfa)*j
    bw.append(bw_est)
dataFrame2['est_bw_ul']=bw

bw = []
alfa = 75/80#0.8
for i,j in enumerate(bw_dl):   #dataFrame2['bw_ul']
    if i ==0:
        bw_est = j
    else:
        bw_est = bw[i-1]*alfa +(1-alfa)*j
    bw.append(bw_est)
dataFrame2['est_bw_dl']=bw







keys = dataFrame2.columns
print(dataFrame2)
#keys = ['cqi', 'rsrp', 'mcs_ul', 'mcs_dl', 'phr', 'bler_ul', 'bler_dl', 'data_ul', 'data_dl', 'snr', 'timestamp', 'timediff', 'bw_ul', 'bw_dl']
for i,j in enumerate(keys):
    if j == 'bler_dl':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'{j}') 
        plt.legend()
        plt.grid('on')
        plt.title(f" {j.upper()}")
        plt.legend(fontsize=20)
        plt.xlabel('t [s]' , fontsize=20, weight='bold')
        plt.ylabel('BLER DL' , fontsize=20, weight='bold')
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title(f"5G network -- BLER Downlink channel UE 1" , fontsize=28, weight='bold')
    if j == 'mcs_ul':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'{j}') 
        plt.grid('on')
        plt.title(f" {j.upper()}")
        plt.legend(fontsize=20)#16
        plt.xlabel('t [s]' , fontsize=20, weight='bold')#16
        plt.ylabel('MCS UL' , fontsize=20, weight='bold')#16
        plt.xticks(fontsize=20)#12
        plt.yticks(fontsize=20)#12
        plt.title(f"5G network -- MCS Uplink channel UE 1" , fontsize=28, weight='bold')#20
    if j == 'mcs_dl':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'{j}') 
        plt.legend()
        plt.grid('on')
        plt.legend(fontsize=16)
        plt.xlabel('t [s]' , fontsize=16, weight='bold')
        plt.ylabel('MCS DL' , fontsize=16, weight='bold')
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title(f"5G network -- MCS Downlink channel UE 1" , fontsize=20, weight='bold')
    if j == 'bler_ul':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'{j}') 
        plt.grid('on')
        plt.legend(fontsize=20)
        plt.xlabel('t [s]' , fontsize=20, weight='bold')
        plt.ylabel('BLER UL' , fontsize=20, weight='bold')
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title(f"5G network -- BLER Uplink channel UE 1" , fontsize=28, weight='bold')
    if j == 'snr':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'{j}') 
        plt.legend()
        plt.grid('on')
        plt.legend(fontsize=16)
        plt.xlabel('t [s]' , fontsize=16, weight='bold')
        plt.ylabel('SNR' , fontsize=16, weight='bold')
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title(f"5G network -- SNR channel UE 1" , fontsize=20, weight='bold')
    if j == 'bw_ul':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'Current uplink bandwidth') 
        plt.plot(t_real, dataFrame2['est_bw_ul'], label = f'Estimated uplink bandwidth') 
        plt.legend()
        plt.grid('on')
        plt.title(f" {j.upper()}")
        plt.legend(fontsize=16)
        plt.xlabel('t [s]' , fontsize=16, weight='bold')
        plt.ylabel('Bandwidth [kBits/s]' , fontsize=16, weight='bold')
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title(f"5G network -- Bandwidth Uplink channel UE 1" , fontsize=20, weight='bold')
    if j == 'bw_dl':
        plt.figure(i)
        plt.plot(t_real, dataFrame2[j], label = f'Current downlink bandwidth') 
        plt.plot(t_real, dataFrame2['est_bw_dl'], label = f'Estimated downlink bandwidth') 
        plt.legend()
        plt.grid('on')
        plt.title(f" {j.upper()}")
        plt.legend(fontsize=16)
        plt.xlabel('t [s]' , fontsize=16, weight='bold')
        plt.ylabel('Bandwidth [kBits/s]' , fontsize=16, weight='bold')
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title(f"5G network -- Bandwidth Downlink channel UE 1" , fontsize=20, weight='bold')
plt.show()