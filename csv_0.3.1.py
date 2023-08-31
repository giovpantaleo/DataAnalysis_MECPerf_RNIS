''' 
V2 --> DIFFERENT VISUALIZATION WITH 2 UEs
The statistics and the data returned are:
- Bandwidth 
- HISTOGRAM, CDF and PDF of PRBs size in 0.1s 
- HISTOGRAM, CDF and PDF  of Bytes/frame size in 0.1s  
- HISTOGRAM, CDF and PDF  of PRBs number in 0.1s 
- HISTOGRAM, CDF and PDF  of PRBs used for retransmission 

While the function pdf_cdf(values, bins = 10), takes in input 2 values:
1) an array of values 
2) the number of bins. If this value is not specified, it will be 10 by default
The output of the function are:
1) pdf: probability distribution function. Considering y = pdf(x), y is the probabilty to have x in the referance interval
2) cdf: cumualtive distribution function. Considering y = pdf(x), y is the probabilty to have x1<=x
3) bins_count: they are the intervall used to the analysis

How the script works:
1) Read the file
2) For each line, starting from the string generate a JSON obj.
3) Verify if the obj has data inside or not. 
    If yes, it collects the value in specific fields, and perform statistics. 
    If not, it adds a value 'NaN'
How are values saved?
All the data are saved in a dictionary. The key is the rnti of each UE, the value is a dictionary. This dictionary sotred all the 
information required (it is possible to add o remove fields).
If a new rnti is discovered, a new association k:v is added to the first dictionary.
Then, for each value required is verified if the field is empty or not. If it is empty the line is skipped.

N.B. some lines are commented to make the execution of ths script faster
'''

import ast
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
 

###################
#### FUNCTIONS ####
###################
def pdf_cdf(values, bins = 10):
    # getting data of the histogram
    count, bins_count = np.histogram(values, bins)
    # finding the PDF of the histogram using count values
    pdf = count / sum(count)
    # using numpy np.cumsum to calculate the CDF
    cdf = np.cumsum(pdf)
    return pdf, cdf, bins_count


# Sometimes eNB can crash. If it crashes, you don't have all the possible values associated to a specific rnti
# The function verify_fields verifies if there specific values or not
def verify_fields(tp):
    flag = False
    if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])>=0:
        if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalPrbUl'])>=0:
            if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi'])>=0:
                if int(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Dl'])>=0:
                    flag = True
    return flag

###################
## READ THE FILE ##
###################

file1 = open("16-08/output2.csv", "r")
lines = file1.readlines()


###################
#DATA MANIPULATION#
###################

timestamp = []
nUE = []
dict_key = {}
for i, line in enumerate(lines):  
# if necessary you can select only few lines,lines[aa:bb]

    # creation of json obj
    tp = ast.literal_eval(line) 
    
    # check that eNB is up and not down
    if (tp['eNB_config']==[]):
        break

    # timestamp conversion
    timestamp_notsec = tp['date_time']
    dt_obj = datetime.strptime(timestamp_notsec, '%Y-%m-%dT%H:%M:%S.%f' )
    sec = dt_obj.timestamp() 
    timestamp.append(str(sec))

    # number of UEs attached
    nUE.append(len(tp['mac_stats'][0]['ue_mac_stats']))
    # UEs can attach and leave the network, using index is not correct, it is better if there is a match of rnti values.

    # Data
    if len(tp['mac_stats'])>0:
        keys_temp = [tp['mac_stats'][0]['ue_mac_stats'][j]['rnti'] for j in range(nUE[i])] # define rtni
    list_keys_in = list(dict_key.keys()) # see what are the rnti memorized
    #keys_temp are the rnti in a specific line, list_keys_in are the rnti in the dictionary. If in the line there is a new rnti, a new  
    #structure will be created in the dictionary
    #Sometimes the eNB has bugs, so it is better to verify the content of the query, if it exist or not
    for key in keys_temp:
        if key in list_keys_in:
            try:
                if verify_fields(tp):
                    dict_key[key]['timestamp'].append(sec)
                    dict_key[key]['totalBytesSdusUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])#totalBytesSdusDl
                    dict_key[key]['total_UL_PRBs'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalPrbUl'])#totalPrbDl
                    dict_key[key]['prbRetxUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['prbRetxUl'])
                    dict_key[key]['prbRetxDl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['prbRetxDl'])
                    dict_key[key]['CqiUE'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi'])
                    dict_key[key]['mcs1Dl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Dl'])
                    dict_key[key]['mcs2Dl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs2Dl'])
                    dict_key[key]['mcs1Ul'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Ul'])
                    dict_key[key]['mcs2Ul'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs2Ul'])

            except:
                print('except')
                
                dict_key[key]['timestamp'].append('NaN')
                dict_key[key]['totalBytesSdusUl'].append('NaN')
                dict_key[key]['total_UL_PRBs'].append('NaN')
                dict_key[key]['prbRetxUl'].append('NaN')
                dict_key[key]['prbRetxDl'].append('NaN')
                dict_key[key]['CqiUE'].append('NaN')
                dict_key[key]['mcs1Dl'].append('NaN')
                dict_key[key]['mcs2Dl'].append('NaN')
                dict_key[key]['mcs1Ul'].append('NaN')
                dict_key[key]['mcs2Ul'].append('NaN')
                
        else:
            dict_key[key] = {'timestamp':[], 'totalBytesSdusUl':[],'total_UL_PRBs':[],'prbRetxUl':[],'prbRetxDl':[],'CqiUE':[],'mcs1Dl':[],'mcs2Dl':[],'mcs1Ul':[],'mcs2Ul':[]}
            if (len(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats'])>0 ):
                if verify_fields(tp):
                    dict_key[key]['timestamp'].append(sec)
                    dict_key[key]['totalBytesSdusUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalBytesSdusUl'])#totalBytesSdusDl
                    dict_key[key]['total_UL_PRBs'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['totalPrbUl'])#totalPrbDl
                    dict_key[key]['prbRetxUl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['prbRetxUl'])
                    dict_key[key]['prbRetxDl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['prbRetxDl'])
                    dict_key[key]['CqiUE'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['dlCqiReport']['csiReport'][0]['p10csi']['wbCqi'])
                    dict_key[key]['mcs1Dl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Dl'])
                    dict_key[key]['mcs2Dl'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs2Dl'])
                    dict_key[key]['mcs1Ul'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs1Ul'])
                    dict_key[key]['mcs2Ul'].append(tp['mac_stats'][0]['ue_mac_stats'][keys_temp.index(key)]['mac_stats']['macStats']['mcs2Ul'])


final_keys = list(dict_key.keys())
#creation of dictonary and dataframe
print('In the csv file have been found ',len(final_keys),' UEs, with RNTI: ', final_keys)
for val in final_keys:
    lennn = len([*set(dict_key[val]['totalBytesSdusUl'])]) #remove duplicate and not useful ue
    if lennn < 10:
        del dict_key[val]
final_keys = list(dict_key.keys())
print('From the initial file, have been considered only ',len(final_keys),' UEs, with RNTI: ', final_keys)
for val in final_keys:
    for vall in dict_key[val].keys():
        lennn = len([*set(dict_key[val][vall])]) #remove duplicate and not useful ue
dataFrames = [pd.DataFrame(dict_key[key]) for key in final_keys]

# REMOVE DUPLICATE ROWS, FILTERING BY TOTAL NUMBER OF PRBs
dataFrames_diff = []
for dataframe in dataFrames:
    no_duplicate = dataframe.drop_duplicates(subset=['total_UL_PRBs'])
 
    totalBytesUL= list(no_duplicate['totalBytesSdusUl'])
    diff_totalBitesUL = [0]
    for i in range(len(totalBytesUL)-1):
        delta = (float(totalBytesUL[i+1])-float(totalBytesUL[i]))*0.008 #kBit
        diff_totalBitesUL.append(delta)
    no_duplicate.loc[:,'diff_totalBitsUL']=diff_totalBitesUL
    
    prb= list(no_duplicate['total_UL_PRBs'])
    PRBs = [0]
    for i in range(len(prb)-1):
        delta = float(prb[i+1])-float(prb[i])
        PRBs.append(delta)
    no_duplicate.loc[:,'diff_UL_PRBs']=PRBs   
    
    dataFrames_diff.append(no_duplicate)


bits_for_prb_total = []
for j,i in enumerate(dataFrames_diff):
    bits_for_prb = []
    # the base station allocates PRBs, these PRBs couldn't be used by the UE (no bytes trasnmitted)
    # the PRBs have a time duration, if you consider different slots, you can't cumulate PRBs
    # so, I don't care about PRBs, but I consider just the PRBs used when the number of bytes changes
    for jj, ii in i.iterrows():
        if float(ii.loc['diff_totalBitsUL'])!=0:
            ratio = float(ii.loc['diff_totalBitsUL'])/float(ii.loc['diff_UL_PRBs'])
            if ratio != 'nan':
                bits_for_prb.append(ratio)
    bits_for_prb_total.append(bits_for_prb)
    try:
        average_ratio = sum(bits_for_prb)/len(bits_for_prb)
        print('The average value of kBits for single PRB is: ',average_ratio, 'kBits/PRB')
    except:
        print('It is not possible to define an average value of kBits for single PRB')

###################
#### BANDWIDTH ####
###################
# from the previous dataFrame_diff, it is possible to remove rows with the same number of total Bytes
# and it is possible to perform the dt and bandwidth

bandwidths = []
for dataFrame_diff in dataFrames_diff:
    bandwidth=dataFrame_diff.drop_duplicates(subset=['totalBytesSdusUl'])
    #bandwidth=dataFrame_diff
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
    time_interval = 0 # [s]
    k = 0
    t =[0]
    for i,j in bandwidth.iterrows():   
        if j.loc['timestamp']>0:
            time_interval+=j.loc['timestamp']
            t.append(time_interval)
            bw_current = j.loc['diff_totalBitsUL']/j.loc['timestamp']
            if k ==0:
                bw_est = bw_current
            else:
                bw_est = bw[k-1]*alfa +(1-alfa)*bw_current
            bw.append(bw_est)
            BW_current.append(bw_current)
            k += 1
    bandwidth.loc[:, 'estimated']=bw
    bandwidth.loc[:, 'current']=BW_current
    bandwidth.loc[:, 'real_time']=t
    bandwidths.append(bandwidth)

###################
###### PLOTS ######
###################

plt.figure(1)
plt.plot(bandwidths[0]['real_time'],bandwidths[0]['current'], label ='Current value of bw in kBits/s Client 1',alpha=0.7)
#plt.plot(bandwidths[0]['real_time'],bandwidths[0]['estimated'], label ='Estimated value of bw in Bytes/s Client 1', linewidth=3)
plt.plot(bandwidths[1]['real_time'],bandwidths[1]['current'], label ='Current value of bw in kBits/s Client 2',alpha=0.7)
#plt.plot(bandwidths[1]['real_time'],bandwidths[1]['estimated'], label ='Estimated value of bw in Bytes/s Client 2', linewidth=3)
plt.xlabel('t [s]' , fontsize=16, weight='bold')
plt.ylabel('BW [kBits/s]' , fontsize=16, weight='bold')
plt.legend(fontsize=16)
plt.title(f"Bandwidth of UEs" , fontsize=20, weight='bold')
plt.grid('on')

plt.figure(2)
plt.plot(bandwidths[0]['real_time'], bandwidths[0]['mcs1Dl'], label ='mcs1Dl Client 1',alpha=0.7) 
plt.plot(bandwidths[0]['real_time'],  bandwidths[0]['mcs1Ul'], label ='mcs1Ul Client 1',alpha=0.7)
plt.plot(bandwidths[1]['real_time'], bandwidths[1]['mcs1Dl'], label ='mcs1Dl Client 2',alpha=0.7) 
plt.plot(bandwidths[1]['real_time'],  bandwidths[1]['mcs1Ul'], label ='mcs1Ul Client 2',alpha=0.7)
plt.legend(fontsize=16)
plt.grid('on')
plt.xlabel('t [s]' , fontsize=16, weight='bold')
plt.ylabel('MCS' , fontsize=16, weight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.title(f"Modulation and Coding Scheme before rate matching" , fontsize=20, weight='bold')

plt.figure(3)
plt.plot(bandwidths[0]['real_time'], bandwidths[0]['mcs2Dl'], label ='mcs2Dl Client 1',alpha=0.7) 
plt.plot(bandwidths[0]['real_time'],  bandwidths[0]['mcs2Ul'], label ='mcs2Ul Client 1',alpha=0.7)
plt.plot(bandwidths[1]['real_time'], bandwidths[1]['mcs2Dl'], label ='mcs2Dl Client 2',alpha=0.7) 
plt.plot(bandwidths[1]['real_time'],  bandwidths[1]['mcs2Ul'], label ='mcs2Ul Client 2',alpha=0.7)
plt.legend(fontsize=16)
plt.grid('on')
plt.xlabel('t [s]' , fontsize=16, weight='bold')
plt.ylabel('MCS' , fontsize=16, weight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.title(f"Modulation and Coding Scheme after rate matching" , fontsize=20, weight='bold')


#Bits_num = sum(bandwidths[0]['diff_totalBitsUL'])
#TIME = sum(bandwidths[0]['timestamp'])
#if TIME != 0:
#    BW = Bits_num/TIME
#    print('The average bandwidth in the interval time of osservation is: ',BW, '[kBits/s]')

# In CDF of Bytes/frame size in 0.1s
# -> N.B. a frame is 10 ms, in 0.1s there are 10 frames
kbits_for_frame1 = bandwidths[0]['diff_totalBitsUL'].multiply(0.01).divide(bandwidths[0]['timestamp'])#*0.008 from Bytes to kBits
kbits_for_frame2 = bandwidths[1]['diff_totalBitsUL'].multiply(0.01).divide(bandwidths[1]['timestamp'])#*0.008 from Bytes to kBits
# Histogram of PRBs size in 0.1s
plt.figure(4)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
plt.title(f'Histogram PRBs size in kBits', fontsize=28, weight='bold')
plt.hist(bits_for_prb_total[0], bins = 15, label= 'Client 1',alpha=0.7)#,range=[46, 62])
plt.hist(bits_for_prb_total[1], bins = 15, label= 'Client 2',alpha=0.7)#,range=[46, 62])
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=20)
#plt.xlim([0, 70])




# CDF of PRBs size in 0.1s
plt.figure(5)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
plt.title(f'CDF PRBs size in kBits', fontsize=28, weight='bold')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.hist(bits_for_prb_total[0], cumulative=True, label= 'Client 1',alpha=0.7)#, bins = 10,range=[46, 62])
plt.hist(bits_for_prb_total[1], cumulative=True, label= 'Client 2',alpha=0.7)#, bins = 10,range=[46, 62])
plt.legend(fontsize=20)

# CDF normalized and PDF of PRBs size in 0.1s
pdf_bytes_for_prb0, cdf_bytes_for_prb0, bins_bytes_for_prb0 = pdf_cdf(bits_for_prb_total[0], 20)
pdf_bytes_for_prb1, cdf_bytes_for_prb1, bins_bytes_for_prb1 = pdf_cdf(bits_for_prb_total[1], 20)
plt.figure(6)
plt.title('CDF normalized and PDF of PRBs size in 0.1s' , fontsize=28, weight='bold')
plt.ylabel('Normalized probability', fontsize=20, weight='bold')
plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
plt.plot(bins_bytes_for_prb0[1:], pdf_bytes_for_prb0, color="red", label="PDF Client 1",alpha=0.7)
plt.plot(bins_bytes_for_prb0[1:], cdf_bytes_for_prb0, label="CDF Client 1",alpha=0.7)
plt.plot(bins_bytes_for_prb1[1:], pdf_bytes_for_prb1, color="red", label="PDF Client 2",alpha=0.7)
plt.plot(bins_bytes_for_prb1[1:], cdf_bytes_for_prb1, label="CDF Client 2",alpha=0.7)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=20)
plt.grid('on')




plt.figure(7)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)    
plt.title(f'Histogram Frame size in kBits' , fontsize=28, weight='bold')
plt.hist(kbits_for_frame1, label= 'Client 1',alpha=0.7)#, bins = 300)
plt.hist(kbits_for_frame2, label= 'Client 2',alpha=0.7)#, bins = 300)
plt.legend(fontsize=20)

# CDF of Bytes/frame size in 0.1s
plt.figure(8)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
plt.title(f'CDF Frame size in kBits' , fontsize=28, weight='bold')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)    
plt.hist(kbits_for_frame1, cumulative=True, label='Client 1',alpha=0.7)#, bins = 300)
plt.hist(kbits_for_frame2, cumulative=True, label='Client 2',alpha=0.7)#, bins = 300)
plt.legend(fontsize=20)

# CDF normalized and PDFof Bytes/frame size in 0.1s 
pdf_kbits_for_frame1, cdf_kbits_for_frame1, bins_kbits_for_frame1 = pdf_cdf(kbits_for_frame1[1:], 20)
pdf_kbits_for_frame2, cdf_kbits_for_frame2, bins_kbits_for_frame2 = pdf_cdf(kbits_for_frame2[1:], 20)
plt.figure(9)
plt.title('CDF normalized and PDFof kBits/frame size in 0.1s' , fontsize=28, weight='bold')
plt.ylabel('Normalized probability', fontsize=20, weight='bold')
plt.xlabel('Frame size in [kBits]', fontsize=20, weight='bold')
plt.plot(bins_kbits_for_frame1[1:], pdf_kbits_for_frame1, color="red", label="PDF Client 1",alpha=0.7)
plt.plot(bins_kbits_for_frame1[1:], cdf_kbits_for_frame1, label="CDF Client 1",alpha=0.7)
plt.plot(bins_kbits_for_frame2[1:], pdf_kbits_for_frame2, color="red", label="PDF Client 2",alpha=0.7)
plt.plot(bins_kbits_for_frame2[1:], cdf_kbits_for_frame2, label="CDF Client 2",alpha=0.7)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)    
plt.legend(fontsize=20)
plt.grid('on')



# Histogram of PRBs number in 0.1s
plt.figure(10)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
plt.title(f'Histogram of PRBs number' , fontsize=28, weight='bold')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)   
plt.hist(bandwidths[0]['diff_UL_PRBs'], label='Client 1',alpha=0.7)#, bins = 300)
plt.hist(bandwidths[1]['diff_UL_PRBs'], label='Client 2',alpha=0.7)#, bins = 300)
plt.legend(fontsize=20) 

# CDF of PRBs number in 0.1s
plt.figure(11)
plt.grid('on')
plt.ylabel('Number of times', fontsize=20, weight='bold')
plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
plt.title(f'CDF of PRBs number' , fontsize=28, weight='bold')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.hist(list(bandwidths[0]['diff_UL_PRBs']), cumulative=True, label='Client 1',alpha=0.7)#, bins = 300)
plt.hist(list(bandwidths[1]['diff_UL_PRBs']), cumulative=True, label='Client 2',alpha=0.7)#, bins = 300)
plt.legend(fontsize=20)    
# CDF normalized and PDF of PRBs number in 0.1s 
pdf_diff_UL_PRBs1, cdf_diff_UL_PRBs1, bins_diff_UL_PRBs1 = pdf_cdf(list(bandwidths[0]['diff_UL_PRBs']), 20)
pdf_diff_UL_PRBs2, cdf_diff_UL_PRBs2, bins_diff_UL_PRBs2 = pdf_cdf(list(bandwidths[1]['diff_UL_PRBs']), 20)
plt.figure(12)
plt.title('CDF normalized and PDF of PRBs number in 0.1s' , fontsize=28, weight='bold')
plt.plot(bins_diff_UL_PRBs1[1:], pdf_diff_UL_PRBs1, color="red", label="PDF Client 1",alpha=0.7)
plt.plot(bins_diff_UL_PRBs1[1:], cdf_diff_UL_PRBs1, label="CDF Client 1",alpha=0.7)
plt.plot(bins_diff_UL_PRBs2[1:], pdf_diff_UL_PRBs2, color="red", label="PDF Client 2",alpha=0.7)
plt.plot(bins_diff_UL_PRBs2[1:], cdf_diff_UL_PRBs2, label="CDF Client 2",alpha=0.7)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=20)
plt.grid('on')


# Histogram of PRBs used for retransmission 
plt.figure(13)
plt.grid('on')
plt.ylabel('Number of times', fontsize=16, weight='bold')
plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
plt.title(f'Histogram PRBs used for retransmission' , fontsize=20, weight='bold')
#plt.hist(prbRetxUl, label='PRBs rtx Ul',density=True, histtype='step')#, bins = 300)
#plt.hist(prbRetxDl, label='PRBs rtx Dl',density=True, histtype='step')#, bins = 300)
val_max = max(max(bandwidths[0]['prbRetxUl'].max(), bandwidths[0]['prbRetxDl'].max()), max(bandwidths[1]['prbRetxUl'].max(), bandwidths[1]['prbRetxDl'].max()))
plt.hist(bandwidths[0]['prbRetxUl'], label='PRBs rtx Ul Client 1', bins=15, range=(0, val_max),alpha=0.7)
plt.hist(bandwidths[0]['prbRetxDl'], label='PRBs rtx Dl Client 1', bins=15, range=(0, val_max),alpha=0.7)
plt.hist(bandwidths[1]['prbRetxUl'], label='PRBs rtx Ul Client 2', bins=15, range=(0, val_max),alpha=0.7)
plt.hist(bandwidths[1]['prbRetxDl'], label='PRBs rtx Dl Client 2', bins=15, range=(0, val_max),alpha=0.7)
#plt.hist(bandwidths[0]['prbRetxUl'], label='PRBs rtx Ul Client 1', bins=15, range=(0, max(bandwidths[0]['prbRetxUl'].max(), bandwidths[0]['prbRetxDl'].max())),alpha=0.7)
#plt.hist(bandwidths[0]['prbRetxDl'], label='PRBs rtx Dl Client 1', bins=15, range=(0, max(bandwidths[0]['prbRetxUl'].max(), bandwidths[0]['prbRetxDl'].max())),alpha=0.7)
#plt.hist(bandwidths[1]['prbRetxUl'], label='PRBs rtx Ul Client 2', bins=15, range=(0, max(bandwidths[1]['prbRetxUl'].max(), bandwidths[1]['prbRetxDl'].max())),alpha=0.7)
#plt.hist(bandwidths[1]['prbRetxDl'], label='PRBs rtx Dl Client 2', bins=15, range=(0, max(bandwidths[1]['prbRetxUl'].max(), bandwidths[1]['prbRetxDl'].max())),alpha=0.7)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=16)

# CDF  of PRBs used for retransmission 
plt.figure(14)
plt.grid('on')
plt.ylabel('Number of times', fontsize=16, weight='bold')
plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
plt.title(f'CDF PRBs used for retransmission' , fontsize=20, weight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.hist(bandwidths[0]['prbRetxUl'],label='PRBs rtx Ul Client 1', cumulative=True,alpha=0.7)#,  bins=15, range=(0, int(m3)), density=True)#bw[['prbRetxUl', 'prbRetxDl']].max().max()))#, bins = 300)
plt.hist(bandwidths[0]['prbRetxDl'], label='PRBs rtx Dl Client 1', cumulative=True,alpha=0.7)#, range=(int(m3)), bins=15)#range=[max([bw['prbRetxUl'],bw['prbRetxDl']])])#, bins = 300)
plt.hist(bandwidths[1]['prbRetxUl'],label='PRBs rtx Ul Client 2', cumulative=True,alpha=0.7)#,  bins=15, range=(0, int(m3)), density=True)#bw[['prbRetxUl', 'prbRetxDl']].max().max()))#, bins = 300)
plt.hist(bandwidths[1]['prbRetxDl'], label='PRBs rtx Dl Client 2', cumulative=True,alpha=0.7)#, range=(int(m3)), bins=15)#range=[max([bw['prbRetxUl'],bw['prbRetxDl']])])#, bins = 300)
plt.legend(fontsize=16)
# CDF normalized and PDF of PRBs number in 0.1s 
pdf_prbRetxUl1, cdf_prbRetxUl1, bins_prbRetxUl1 = pdf_cdf(bandwidths[0]['prbRetxUl'], 20)
pdf_prbRetxDl1, cdf_prbRetxDl1, bins_prbRetxDl1 = pdf_cdf(bandwidths[0]['prbRetxDl'], 20)
pdf_prbRetxUl2, cdf_prbRetxUl2, bins_prbRetxUl2 = pdf_cdf(bandwidths[1]['prbRetxUl'], 20)
pdf_prbRetxDl2, cdf_prbRetxDl2, bins_prbRetxDl2 = pdf_cdf(bandwidths[1]['prbRetxDl'], 20)
plt.figure(15)
plt.plot(bins_prbRetxUl1[1:], pdf_prbRetxUl1, label="PDF Ul Client 1",alpha=0.7)
plt.plot(bins_prbRetxUl1[1:], cdf_prbRetxUl1, label="CDF Ul Client 1",alpha=0.7)
plt.plot(bins_prbRetxDl1[1:], pdf_prbRetxDl1, color="red", label="PDF Dl Client 1",alpha=0.7)
plt.plot(bins_prbRetxDl1[1:], cdf_prbRetxDl1, label="CDF Dl Client 1",alpha=0.7)
plt.plot(bins_prbRetxUl2[1:], pdf_prbRetxUl2, label="PDF Ul Client 2",alpha=0.7)
plt.plot(bins_prbRetxUl2[1:], cdf_prbRetxUl2, label="CDF Ul Client 2",alpha=0.7)
plt.plot(bins_prbRetxDl2[1:], pdf_prbRetxDl2, color="red", label="PDF Dl Client 2",alpha=0.7)
plt.plot(bins_prbRetxDl2[1:], cdf_prbRetxDl2, label="CDF Dl Client 2",alpha=0.7)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=16)
plt.grid('on')
plt.title('CDF normalized and PDF of PRBs used for retransmission' , fontsize=20, weight='bold')



plt.show()
