''' 
This script returns the plot of bandwidth in UL and DL for different UEs.
'''

import ast
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def verify_fields(tp):
    flag = False
    if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])>=0:
        if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalPrbUl'])>=0:
            if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi'])>=0:
                if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Dl'])>=0:
                    flag = True
    return flag

# READ THE FILE


file1 = open("16-08/output2.csv", "r")
lines = file1.readlines()


# TRANSFORMATION AND SELECTION OF THE FIELDS
timestamp = []
nUE = []
dict_key = {}
for i, line in enumerate(lines):     
    # creation of json obj
    tp = ast.literal_eval(line) 
    
    # check that eNB is up and not down
    #if (tp['eNB_config']==[]):
    #    break

    # timestamp conversion
    timestamp_notsec = tp['date_time']
    dt_obj = datetime.strptime(timestamp_notsec, '%Y-%m-%dT%H:%M:%S.%f' )
    sec = dt_obj.timestamp() 
    timestamp.append(str(sec))
    #dict_key['timestamp'].append(sec)

    # number of UEs attached
    nUE.append(len(tp['mac_stats'][0]['ue_mac_stats']))
    # UEs can attach and leave the network, using index is not correct, it is better if there is a match of rnti values.

    # data
    if len(tp['mac_stats'])>0:
        keys_temp = [tp['mac_stats'][0]['ue_mac_stats'][j]['rnti'] for j in range(nUE[i])] 
    list_keys_in = list(dict_key.keys()) # see what are the rnti memorized
    for key in keys_temp:
        if key in list_keys_in:
            try:
                if verify_fields(tp):
                    dict_key[key]['timestamp'].append(sec)
                    dict_key[key]['totalBytesSdusUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])
                    dict_key[key]['totalBytesSdusDl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusDl'])

            except:
                print('except')
                
                dict_key[key]['timestamp'].append('NaN')
                dict_key[key]['totalBytesSdusUl'].append('NaN')
                dict_key[key]['totalBytesSdusDl'].append('NaN')         
                
        else:
            dict_key[key] = {'timestamp':[], 'totalBytesSdusUl':[], 'totalBytesSdusDl':[]}
            if (len(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats'])>0 ):
                if verify_fields(tp):
                    dict_key[key]['timestamp'].append(sec)
                    dict_key[key]['totalBytesSdusUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])
                    dict_key[key]['totalBytesSdusDl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusDl'])




final_keys = list(dict_key.keys())
#creation of dictonary and dataframe
print('In the csv file have been found ',len(final_keys),' UEs, with RNTI: ', final_keys)
for val in final_keys:
    lennn = len([*set(dict_key[val]['totalBytesSdusUl'])]) #remove duplicate and not useful ue
    if lennn < 10:
        del dict_key[val]
final_keys = list(dict_key.keys())
print('B In the csv file have been found ',len(final_keys),' UEs, with RNTI: ', final_keys)
for val in final_keys:
    for vall in dict_key[val].keys():
        lennn = len([*set(dict_key[val][vall])]) #remove duplicate and not useful ue
        print(vall, lennn)
#print(dict_key)
dataFrames = [pd.DataFrame(dict_key[key]) for key in final_keys]

# REMOVE DUPLICATE ROWS, FILTERING BY TOTAL NUMBER OF PRBs
dataFrames_diff = []
for dataframe in dataFrames:
#    no_duplicate = dataframe.drop_duplicates(subset=['total_UL_PRBs'])
    no_duplicate = dataframe 
    totalBytesUL= list(no_duplicate['totalBytesSdusUl'])
    diff_totalBytesUL = [0]
    for i in range(len(totalBytesUL)-1):
        delta = float(totalBytesUL[i+1])-float(totalBytesUL[i])
        diff_totalBytesUL.append(delta)
    no_duplicate.loc[:,'diff_totalBytesUL']=diff_totalBytesUL
    

    totalBytesDL= list(no_duplicate['totalBytesSdusDl'])
    diff_totalBytesDL = [0]
    for i in range(len(totalBytesDL)-1):
        delta = float(totalBytesDL[i+1])-float(totalBytesDL[i])
        diff_totalBytesDL.append(delta)
    no_duplicate.loc[:,'diff_totalBytesDL']=diff_totalBytesDL

    dataFrames_diff.append(no_duplicate)


###########################################################
# Bandwidth
# from the previous dataFrame_diff, it is possible to remove rows with the same number of total Bytes
# and it is possible to perform the dt and bandwidth

bandwidths_UL = []
for dataFrame_diff in dataFrames_diff:
    bandwidth=dataFrame_diff.drop_duplicates(subset=['totalBytesSdusUl'])
    #bandwidth=dataFrame_diff
    #print(bandwidth)
    tt= list(bandwidth['timestamp'])
    dt = [0]
    for i in range(len(tt)-1):
        dT = float(tt[i+1])-float(tt[i])
        dt.append(dT)
    bandwidth.loc[:, 'timestamp']=dt


    # Estimation of the bandwidth
    bw = [0]
    BW_current =[0]
    alfa = 7/8#0.8
    total_bytes = 0
    time_interval = 0 # [s]
    k = 0
    t =[0]
    for i,j in bandwidth.iterrows():   
    #    if i>0:
        if j.loc['timestamp']>0:
            time_interval+=j.loc['timestamp']
            t.append(time_interval)
            total_bytes+=j.loc['diff_totalBytesUL']
            #bw_current = total_bytes/time_interval
            bw_current = j.loc['diff_totalBytesUL']/j.loc['timestamp']
            #(bw_current, 'bw')
            if k ==0:
                bw_est = bw_current
            else:
                bw_est = bw[k-1]*alfa +(1-alfa)*bw_current
            bw.append(bw_est)
            BW_current.append(bw_current)
            k += 1
    bandwidth.loc[:, 'estimated UL']=bw
    bandwidth.loc[:, 'current UL']=BW_current
    bandwidth.loc[:, 'real_time']=t
    bandwidths_UL.append(bandwidth)


bandwidths_DL = []
for dataFrame_diff in dataFrames_diff:
    bandwidth=dataFrame_diff.drop_duplicates(subset=['totalBytesSdusDl'])
    tt= list(bandwidth['timestamp'])
    dt = [0]
    for i in range(len(tt)-1):
        dT = float(tt[i+1])-float(tt[i])
        dt.append(dT)
    bandwidth.loc[:, 'timestamp']=dt


    # Estimation of the bandwidth
    bw = [0]
    BW_current =[0]
    alfa = 7/8#0.8
    total_bytes = 0
    time_interval = 0 # [s]
    k = 0
    t =[0]
    for i,j in bandwidth.iterrows():   
    #    if i>0:
        if j.loc['timestamp']>0:
            time_interval+=j.loc['timestamp']
            t.append(time_interval)
            total_bytes+=j.loc['diff_totalBytesDL']
            #bw_current = total_bytes/time_interval
            bw_current = j.loc['diff_totalBytesDL']/j.loc['timestamp']
            #(bw_current, 'bw')
            if k ==0:
                bw_est = bw_current
            else:
                bw_est = bw[k-1]*alfa +(1-alfa)*bw_current
            bw.append(bw_est)
            BW_current.append(bw_current)
            k += 1
    bandwidth.loc[:, 'estimated DL']=bw
    bandwidth.loc[:, 'current DL']=BW_current
    bandwidth.loc[:, 'real_time']=t
    bandwidths_DL.append(bandwidth)
print(bandwidths_DL, bandwidths_UL)
    

for i, bw in enumerate(bandwidths_UL):
    plt.figure(i)
    #plt.plot(bw['real_time'], bw['estimated UL'], label='Estimated UL') 
    plt.plot(bw['real_time'], bw['current UL']*8/(1000), label ='Current value bandwidth in Uplink',alpha=0.7)
    #plt.plot(bandwidths_DL[i]['real_time'], bandwidths_DL[i]['estimated DL'], label='Estimated DL') 
    plt.plot(bandwidths_DL[i]['real_time'], bandwidths_DL[i]['current DL']*8/(1000), label = 'Current value bandwidth in Downlink',alpha=0.7) 
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('BW [kBits/s]' , fontsize=16, weight='bold')
    plt.legend(fontsize=16)
    plt.title(f"Bandwidth used by the UE" , fontsize=20, weight='bold')
    plt.show()


   
