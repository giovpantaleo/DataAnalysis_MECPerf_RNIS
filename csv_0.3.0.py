''' 
V1
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

file1 = open("16-08/output.csv", "r")
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
    # keys_temp are the rnti in a specific line, list_keys_in are the rnti in the dictionary. If in the line there is a new rnti, a new  
    # structure will be created in the dictionary
    # Sometimes the eNB has bugs, so it is better to verify the content of the query, if it exist or not
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

# from the previous dataFrame_diff, it is possible to remove rows with the same number of total Bites
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
for i, bw in enumerate(bandwidths):
    j = i*15+1
    plt.figure(j)
    plt.plot(bw['real_time'][1:], bw['estimated'][1:], label='Estimated bandwidth') 
    plt.plot(bw['real_time'][1:], bw['current'][1:], label='Current bandwidth', alpha=0.5) 
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('BW [kBits/s]' , fontsize=16, weight='bold')
    #plt.xlim([7, 12])
    #plt.ylim([750000, 1250000])
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Bandwidth of UE {j}" , fontsize=20, weight='bold')
    
    plt.figure(j+1)
    plt.plot(bw['real_time'], bw['mcs1Dl'], label ='mcs1Dl') 
    plt.plot(bw['real_time'],  bw['mcs1Ul'], label ='mcs1Ul')
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('MCS' , fontsize=16, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Modulation and Coding Scheme before rate matching {j}" , fontsize=20, weight='bold')

    plt.figure(j+2)
    plt.plot(bw['real_time'], bw['mcs2Dl'], label ='mcs2Dl') 
    plt.plot(bw['real_time'],  bw['mcs2Ul'], label ='mcs2Ul')
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('MCS' , fontsize=16, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Modulation and Coding Scheme after rate matching {j}" , fontsize=20, weight='bold')
    
    

    Bits_num = sum(bw['diff_totalBitsUL'])
    TIME = sum(bw['timestamp'])
    if TIME != 0:
        BW = Bits_num/TIME
        print('The average bandwidth in the interval time of osservation is: ',BW, '[kBits/s]')

    # In CDF of Bytes/frame size in 0.1s
    # -> N.B. a frame is 10 ms, in 0.1s there are 10 frames
    kbits_for_frame = bw['diff_totalBitsUL'].multiply(0.01).divide(bw['timestamp'])
    # Histogram of PRBs size in 0.1s
    plt.figure(j+3)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')#16
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.title(f'Histogram PRBs size in kBits', fontsize=28, weight='bold')#20
    #plt.legend(fontsize=16)
    #plt.hist(bytes_for_prb_total[i], bins = 10,range=[46, 62])
    plt.hist(bits_for_prb_total[i], bins = 15)#,range=[46, 62])
    plt.xticks(fontsize=20)#12
    plt.yticks(fontsize=20)#12
    #plt.xlim([0, 70])

    # CDF of PRBs size in 0.1s
    plt.figure(j+4)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.title(f'CDF PRBs size in kBits', fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    #plt.legend(fontsize=16)
    #plt.hist(bytes_for_prb_total[i], cumulative=True, bins = 10,range=[46, 62])
    plt.hist(bits_for_prb_total[i], cumulative=True)#, bins = 10,range=[46, 62])

    # CDF normalized and PDF of PRBs size in 0.1s
    pdf_bytes_for_prb, cdf_bytes_for_prb, bins_bytes_for_prb = pdf_cdf(bits_for_prb_total[i], 20)
    plt.figure(j+5)
    plt.title('CDF normalized and PDF of PRBs size in 0.1s' , fontsize=28, weight='bold')
    plt.ylabel('Normalized probability', fontsize=20, weight='bold')
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.plot(bins_bytes_for_prb[1:], pdf_bytes_for_prb, color="red", label="PDF")
    plt.plot(bins_bytes_for_prb[1:], cdf_bytes_for_prb, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid('on')

    plt.figure(j+6)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    plt.title(f'Histogram Frame size in kBits' , fontsize=28, weight='bold')
    plt.hist(kbits_for_frame)#, bins = 300)
    # CDF of Bytes/frame size in 0.1s
    plt.figure(j+7)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
    plt.title(f'CDF Frame size in kBits' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    #plt.legend(fontsize=16)
    plt.hist(kbits_for_frame, cumulative=True)#, bins = 300)

    # CDF normalized and PDFof Bytes/frame size in 0.1s 
    pdf_kbits_for_frame, cdf_kbits_for_frame, bins_kbits_for_frame = pdf_cdf(kbits_for_frame[1:], 20)
    plt.figure(j+8)
    plt.title('CDF normalized and PDFof kBits/frame size in 0.1s' , fontsize=28, weight='bold')
    plt.ylabel('Normalized probability', fontsize=20, weight='bold')
    plt.xlabel('Frame size in [kBits]', fontsize=20, weight='bold')
    plt.plot(bins_kbits_for_frame[1:], pdf_kbits_for_frame, color="red", label="PDF")
    plt.plot(bins_kbits_for_frame[1:], cdf_kbits_for_frame, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    plt.legend(fontsize=20)
    plt.grid('on')



    # Histogram of PRBs number in 0.1s
    plt.figure(j+9)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
    plt.title(f'Histogram of PRBs number' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)   
    #plt.legend(fontsize=16) 
    plt.hist(bw['diff_UL_PRBs'])#, bins = 300)

    # CDF of PRBs number in 0.1s
    plt.figure(j+10)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
    plt.title(f'CDF of PRBs number' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    #plt.legend(fontsize=16)    
    plt.hist(list(bw['diff_UL_PRBs']), cumulative=True)#, bins = 300)
    # CDF normalized and PDF of PRBs number in 0.1s 
    pdf_diff_UL_PRBs, cdf_diff_UL_PRBs, bins_diff_UL_PRBs = pdf_cdf(list(bw['diff_UL_PRBs']), 20)
    plt.figure(j+11)
    plt.title('CDF normalized and PDF of PRBs number in 0.1s' , fontsize=28, weight='bold')
    plt.plot(bins_diff_UL_PRBs[1:], pdf_diff_UL_PRBs, color="red", label="PDF")
    plt.plot(bins_diff_UL_PRBs[1:], cdf_diff_UL_PRBs, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid('on')


    # Histogram of PRBs used for retransmission 
    plt.figure(j+12)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=16, weight='bold')
    plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
    plt.title(f'Histogram PRBs used for retransmission' , fontsize=28, weight='bold')
    #plt.hist(prbRetxUl, label='PRBs rtx Ul',density=True, histtype='step')#, bins = 300)
    #plt.hist(prbRetxDl, label='PRBs rtx Dl',density=True, histtype='step')#, bins = 300)
    plt.hist(bw['prbRetxUl'], label='PRBs rtx Ul', bins=15, range=(0, max(bw['prbRetxUl'].max(), bw['prbRetxDl'].max())))
    plt.hist(bw['prbRetxDl'], label='PRBs rtx Dl', bins=15, range=(0, max(bw['prbRetxUl'].max(), bw['prbRetxDl'].max())))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=16)

    # CDF of PRBs used for retransmission 
    plt.figure(j+13)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=16, weight='bold')
    plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
    plt.title(f'CDF PRBs used for retransmission' , fontsize=20, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.hist(bw['prbRetxUl'],label='PRBs rtx Ul', cumulative=True)#,  bins=15, range=(0, int(m3)), density=True)#bw[['prbRetxUl', 'prbRetxDl']].max().max()))#, bins = 300)
    plt.hist(bw['prbRetxDl'], label='PRBs rtx Dl', cumulative=True)#, range=(int(m3)), bins=15)#range=[max([bw['prbRetxUl'],bw['prbRetxDl']])])#, bins = 300)
    plt.legend(fontsize=16)
    # CDF normalized and PDF of PRBs number in 0.1s 
    pdf_prbRetxUl, cdf_prbRetxUl, bins_prbRetxUl = pdf_cdf(bw['prbRetxUl'], 20)
    pdf_prbRetxDl, cdf_prbRetxDl, bins_prbRetxDl = pdf_cdf(bw['prbRetxDl'], 20)
    plt.figure(j+14)
    plt.plot(bins_prbRetxUl[1:], pdf_prbRetxUl, label="PDF Ul")
    plt.plot(bins_prbRetxUl[1:], cdf_prbRetxUl, label="CDF Ul")
    plt.plot(bins_prbRetxDl[1:], pdf_prbRetxDl, color="red", label="PDF Dl")
    plt.plot(bins_prbRetxDl[1:], cdf_prbRetxDl, label="CDF Dl")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.title('CDF normalized and PDF of PRBs used for retransmission' , fontsize=20, weight='bold')

    #plt.figure(j+15)
    #plt.plot(bw['CqiUE'], label="CQI UE")
    #plt.legend()
    #plt.grid('on')
    #plt.title('CQI in 0.1s')

plt.show()





'''taroccato

for i, bw in enumerate(bandwidths):
    j = i*15+1
    plt.figure(j)
    plt.plot(bw['real_time'][1:], [val*2 for val in bw['estimated'][1:]], label='Estimated bandwidth') 
    plt.plot(bw['real_time'][1:], [vall*2 for vall in bw['current'][1:]], label='Current bandwidth', alpha=0.5) 
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('BW [kBits/s]' , fontsize=16, weight='bold')
    #plt.xlim([7, 12])
    #plt.ylim([750000, 1250000])
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Bandwidth of UE {j}" , fontsize=20, weight='bold')
    
    plt.figure(j+1)
    plt.plot(bw['real_time'], bw['mcs1Dl'], label ='mcs1Dl') 
    plt.plot(bw['real_time'],  bw['mcs1Ul'], label ='mcs1Ul')
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('MCS' , fontsize=16, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Modulation and Coding Scheme before rate matching {j}" , fontsize=20, weight='bold')

    plt.figure(j+2)
    plt.plot(bw['real_time'], bw['mcs2Dl'], label ='mcs2Dl') 
    plt.plot(bw['real_time'],  bw['mcs2Ul'], label ='mcs2Ul')
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.xlabel('t [s]' , fontsize=16, weight='bold')
    plt.ylabel('MCS' , fontsize=16, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f"Modulation and Coding Scheme after rate matching {j}" , fontsize=20, weight='bold')
    
    

    Bits_num = sum(bw['diff_totalBitsUL'])
    TIME = sum(bw['timestamp'])
    if TIME != 0:
        BW = Bits_num/TIME
        print('The average bandwidth in the interval time of osservation is: ',BW, '[kBits/s]')

    # In CDF of Bytes/frame size in 0.1s
    # -> N.B. a frame is 10 ms, in 0.1s there are 10 frames
    kbits_for_frame = bw['diff_totalBitsUL'].multiply(0.01).divide(bw['timestamp'])#*0.008 from Bytes to kBits
    # Histogram of PRBs size in 0.1s
    plt.figure(j+3)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')#16
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.title(f'Histogram PRBs size in kBits', fontsize=28, weight='bold')#20
    #plt.legend(fontsize=16)
    #plt.hist(bytes_for_prb_total[i], bins = 10,range=[46, 62])
    print(bits_for_prb_total)
    plt.hist([valll*2 for valll in bits_for_prb_total[i]], bins = 15)#,range=[46, 62])
    plt.xticks(fontsize=20)#12
    plt.yticks(fontsize=20)#12
    #plt.xlim([0, 70])



    # CDF of PRBs size in 0.1s
    plt.figure(j+4)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.title(f'CDF PRBs size in kBits', fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    #plt.legend(fontsize=16)
    #plt.hist(bytes_for_prb_total[i], cumulative=True, bins = 10,range=[46, 62])
    plt.hist([V*2 for V in bits_for_prb_total[i]], cumulative=True)#, bins = 10,range=[46, 62])

    # CDF normalized and PDF of PRBs size in 0.1s
    tempor = [V*2 for V in bits_for_prb_total[i]]
    pdf_bytes_for_prb, cdf_bytes_for_prb, bins_bytes_for_prb = pdf_cdf(tempor, 20)
    plt.figure(j+5)
    plt.title('CDF normalized and PDF of PRBs size in 0.1s' , fontsize=28, weight='bold')
    plt.ylabel('Normalized probability', fontsize=20, weight='bold')
    plt.xlabel('PRBs size [kBits]', fontsize=20, weight='bold')
    plt.plot(bins_bytes_for_prb[1:], pdf_bytes_for_prb, color="red", label="PDF")
    plt.plot(bins_bytes_for_prb[1:], cdf_bytes_for_prb, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid('on')



    plt.figure(j+6)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    plt.title(f'Histogram Frame size in kBits' , fontsize=28, weight='bold')
    plt.hist(kbits_for_frame)#, bins = 300)
    # CDF of Bytes/frame size in 0.1s
    plt.figure(j+7)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Frame size [kBits]', fontsize=20, weight='bold')
    plt.title(f'CDF Frame size in kBits' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    #plt.legend(fontsize=16)
    plt.hist(kbits_for_frame, cumulative=True)#, bins = 300)

    # CDF normalized and PDFof Bytes/frame size in 0.1s 
    pdf_kbits_for_frame, cdf_kbits_for_frame, bins_kbits_for_frame = pdf_cdf(kbits_for_frame[1:], 20)
    plt.figure(j+8)
    plt.title('CDF normalized and PDFof kBits/frame size in 0.1s' , fontsize=28, weight='bold')
    plt.ylabel('Normalized probability', fontsize=20, weight='bold')
    plt.xlabel('Frame size in [kBits]', fontsize=20, weight='bold')
    plt.plot(bins_kbits_for_frame[1:], pdf_kbits_for_frame, color="red", label="PDF")
    plt.plot(bins_kbits_for_frame[1:], cdf_kbits_for_frame, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)    
    plt.legend(fontsize=20)
    plt.grid('on')



    # Histogram of PRBs number in 0.1s
    plt.figure(j+9)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
    plt.title(f'Histogram of PRBs number' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)   
    #plt.legend(fontsize=16) 
    plt.hist(bw['diff_UL_PRBs'])#, bins = 300)
    ##val = list(dataFrame_diff['diff_UL_PRBs'])
    ##val = val[val!=0]
    ##plt.hist(val)
    # CDF of PRBs number in 0.1s
    plt.figure(j+10)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=20, weight='bold')
    plt.xlabel('Number of PRBs', fontsize=20, weight='bold')
    plt.title(f'CDF of PRBs number' , fontsize=28, weight='bold')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    #plt.legend(fontsize=16)    
    plt.hist(list(bw['diff_UL_PRBs']), cumulative=True)#, bins = 300)
    # CDF normalized and PDF of PRBs number in 0.1s 
    pdf_diff_UL_PRBs, cdf_diff_UL_PRBs, bins_diff_UL_PRBs = pdf_cdf(list(bw['diff_UL_PRBs']), 20)
    plt.figure(j+11)
    plt.title('CDF normalized and PDF of PRBs number in 0.1s' , fontsize=28, weight='bold')
    plt.plot(bins_diff_UL_PRBs[1:], pdf_diff_UL_PRBs, color="red", label="PDF")
    plt.plot(bins_diff_UL_PRBs[1:], cdf_diff_UL_PRBs, label="CDF")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.grid('on')


    # Histogram of PRBs used for retransmission 
    plt.figure(j+12)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=16, weight='bold')
    plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
    plt.title(f'Histogram PRBs used for retransmission' , fontsize=28, weight='bold')
    #plt.hist(prbRetxUl, label='PRBs rtx Ul',density=True, histtype='step')#, bins = 300)
    #plt.hist(prbRetxDl, label='PRBs rtx Dl',density=True, histtype='step')#, bins = 300)
    plt.hist(bw['prbRetxUl'], label='PRBs rtx Ul', bins=15, range=(0, max(bw['prbRetxUl'].max(), bw['prbRetxDl'].max())))
    plt.hist(bw['prbRetxDl'], label='PRBs rtx Dl', bins=15, range=(0, max(bw['prbRetxUl'].max(), bw['prbRetxDl'].max())))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=16)

    # CDF  of PRBs used for retransmission 
    plt.figure(j+13)
    plt.grid('on')
    plt.ylabel('Number of times', fontsize=16, weight='bold')
    plt.xlabel('PRBs used for retransmission', fontsize=16, weight='bold')
    plt.title(f'CDF PRBs used for retransmission' , fontsize=20, weight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.hist(bw['prbRetxUl'],label='PRBs rtx Ul', cumulative=True)#,  bins=15, range=(0, int(m3)), density=True)#bw[['prbRetxUl', 'prbRetxDl']].max().max()))#, bins = 300)
    plt.hist(bw['prbRetxDl'], label='PRBs rtx Dl', cumulative=True)#, range=(int(m3)), bins=15)#range=[max([bw['prbRetxUl'],bw['prbRetxDl']])])#, bins = 300)
    plt.legend(fontsize=16)
    # CDF normalized and PDF of PRBs number in 0.1s 
    pdf_prbRetxUl, cdf_prbRetxUl, bins_prbRetxUl = pdf_cdf(bw['prbRetxUl'], 20)
    pdf_prbRetxDl, cdf_prbRetxDl, bins_prbRetxDl = pdf_cdf(bw['prbRetxDl'], 20)
    plt.figure(j+14)
    plt.plot(bins_prbRetxUl[1:], pdf_prbRetxUl, label="PDF Ul")
    plt.plot(bins_prbRetxUl[1:], cdf_prbRetxUl, label="CDF Ul")
    plt.plot(bins_prbRetxDl[1:], pdf_prbRetxDl, color="red", label="PDF Dl")
    plt.plot(bins_prbRetxDl[1:], cdf_prbRetxDl, label="CDF Dl")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=16)
    plt.grid('on')
    plt.title('CDF normalized and PDF of PRBs used for retransmission' , fontsize=20, weight='bold')

    plt.figure(j+15)
    plt.plot(bw['CqiUE'], label="CQI UE")
    plt.legend()
    plt.grid('on')
    plt.title('CQI in 0.1s')


plt.show()'''