'''
This script processes the bandwidth log file of the Observer
How it works:
1. Specify the name and the path of the log file
2. Specify the path of the genereted file
3. Choose a client, among the choices
4. Specify an index
'''

# FUNCTIONS LEN 4 AND 12
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

#in tcp the system saves the actual time
#in udp the system saves the difference of times between the arrival of 2 pckts

def tcp_bandwidth(id, lines): 
    """
    estimates the bandwidth for a tcp connections.
    It requires two inputs: 
    - id of the test
    - lines to take data
    """
    # read the file 
    nanoTimes = []
    kBytes = 0
    dataTrace = []
    k = 0
    for line in lines:
        # clean each row from spaces and so on and divide the row in single values 
        row = line.rstrip().split(',')
        # take just the id necessary
        if row[0] == str(id):        
            # compute bandwidth
            nanoTime = float(row[2])
            kByte = float(row[3])
            nanoTimes.append(nanoTime)
            kBytes += kByte
            if k>0:
                deltaTime = nanoTime-nanoTimes[k-1]
                current_bandwidth = kByte/deltaTime*1000000
                # the value of data is in byte, the time is in ns. To have kBytes/s, I need to multiply for 10^6
                dataTrace.append(current_bandwidth)
            k += 1
    dt = nanoTimes[-1]-nanoTimes[0]
    print(f"{kBytes}/{dt}")
    bw = kBytes/dt*1000000 
    print("For the test with ID: ", id, "the estimated bandwidth is: ", bw, "kByte/s")
    return bw, dataTrace, nanoTimes


def udp_bandwidth(id, lines):
    """
    estimates the bandwidth for a udp connections.
    It requires two inputs: 
    - id of the test
    - lines to take data
    """
     # read the file row for row
    nanoTimes = 0
    kBytes = 0
    dataTrace = []
    k = 0
    time = []
    for line in lines:
        # clean each row from spaces and so on and divide the row in single values 
        row = line.rstrip().split(',')
        # take just the id necessary
        if row[0] == str(id):
            # compute bandwidth
            nanoTime = float(row[2])
            kByte = float(row[3])
            nanoTimes += nanoTime
            time.append(nanoTimes)
            kBytes += kByte
            current_bandwidth = kByte/nanoTime*1000000
            dataTrace.append(current_bandwidth)
            k += 1
    print(f"{kBytes}/{nanoTimes}")

    bw = kBytes/nanoTimes*1000000 
    print("For the test with ID: ", id, "the estimated bandwidth is: ", bw, "kByte/s")
    return bw, dataTrace, time


def define_dataframe(type, lines):
    info_test = []
    for line in lines:
        row = line.rstrip().split(',')
        if len(row)>=6:
            info_test.append(row)  
    dataFrame_init = pd.DataFrame(info_test)
    dataFrame = dataFrame_init[dataFrame_init[9]==type]
    df_sender = dataFrame[1]
    df_sender=df_sender.drop_duplicates()
    df_receiver = dataFrame[5]
    df_receiver=df_receiver.drop_duplicates()
    dataFrame_fin = pd.DataFrame(0, index=df_sender, columns=df_receiver )

    # analysis of data flows based on sender's ip address
    for i, j in dataFrame.iterrows():
        send = j[1]
        rec = j[5]
        dataFrame_fin.loc[send, rec] += 1

    return dataFrame_fin, dataFrame


def idx_test(dataframe, dataFrame):
    """
    associates an index for each test performed
    """
    test_string = dataFrame.to_string(header=False, index=False, index_names=False).split('\n')
    vals = [','.join(ele.split()) for ele in test_string]
    dataframe = dataframe.applymap(lambda x: [])
    df2 =  dataFrame
    df2[12]= [ [] for x in range(df2.shape[0]) ]  
    for  j in vals:
        row_in=j.rstrip().split(',')       
        for k, line in enumerate(lines):        
            if (str(j.rstrip()) == str(line.rstrip())):
                row=lines[k+1].rstrip().split(',')
                id = row[0]
                dataframe.loc[row_in[1], row_in[5]].append(id)

    return dataframe




# insert the name of the file CSV 
csv_file = "16-08/perfect_channel_1_2_ues/measure_bw_obs_side.csv"
# open files CSV
file = open(csv_file, 'r') 
# generation of file with indexes
file2 = open("16-08/perfect_channel_1_2_ues/generated_bw.csv", "w")


i = 0
stri = ''
for line in file:
    row = line.rstrip().split(',')
    if len(row)!=4:
        i += 1
        stri = line
    else:
        stri = str(i) + ',' + row[0] + ',' +  row[1] + ',' + row[2] + ',' +  row[3] + '\n'
    file2.write(stri)

file.close()
file2.close()



file2 = open("16-08/perfect_channel_1_2_ues/generated_bw.csv", "r")
lines = file2.readlines()

# It is necessary to see how many clients are in the network --> filtering based on keyword 
# But I need to find all the possible keywords used


# It just save the lines where the data related  to each measurement are written
info_test = []
for line in lines:
    row = line.rstrip().split(',')
    if len(row)>=6:
        info_test.append(row)  
dataFrame_init = pd.DataFrame(info_test)
#print(dataFrame_init)

dataFrame = dataFrame_init[11]
dataFrame=dataFrame.drop_duplicates()
clients = dataFrame.values.tolist()
# Now I have the keywords


i = 0
list_index_header = []
for line in lines:
    row = line.rstrip().split(',')
    if len(row)>=6:
        list_index_header.append(i)
    i +=1

lines_clients = []
i = 0

for client in clients:
    lines_clients.append([])
    i += 1
    print('There is ', client)

i = 0

for i in range(len(list_index_header)):
    row = lines[list_index_header[i]].rstrip().split(',')
    if row[11] in clients:
        idx_client = clients.index(row[11])

    if i == len(list_index_header)-1:
        delta_lines = len(lines) - list_index_header[i]
    else:
        delta_lines = list_index_header[i+1]-list_index_header[i]
    for j in range(delta_lines-1):
        temp = lines[j+list_index_header[i]]     
        lines_clients[idx_client].append(temp)
    




# dataframe created is based on ip addresses 
# to read the direction of the communication is: from value on row to value on column
# the values in these df are the number of tests for each measuraments
id_client = int(input('Insert 1 for client 1 or 2 for client 2: '))
lines_cl =lines_clients[id_client-1]
tcp_dt, dataFrame_tcp = define_dataframe('TCPBandwidth',lines_cl)
udp_dt, dataFrame_udp = define_dataframe('UDPBandwidth',lines_cl)


for index in tcp_dt.index:
    for col in tcp_dt.columns:
        if tcp_dt.loc[index, col] != 0:
            print('The tests from ' + index + ' to ' + col + ' using TCP are' , tcp_dt.loc[index, col])

for index in udp_dt.index:
    for col in udp_dt.columns:
        if udp_dt.loc[index, col] != 0:
            print('The tests from ' + index + ' to ' + col + ' using UDP are' , udp_dt.loc[index, col])


tcp_idx = idx_test(tcp_dt, dataFrame_tcp)
udp_idx = idx_test(udp_dt, dataFrame_udp)


print('The tests from Client to Observer using TCP have indices: '+str(list(set(tcp_idx.loc['Client', 'Observer']))))
print('The tests from Observer to Server using TCP have indices: '+str(list(set(tcp_idx.loc['Observer', 'Server']))))
print('The tests from Observer to Client using TCP have indices: '+str(list(set(tcp_idx.loc['Observer', 'Client']))))
print('The tests from Server to Observer using TCP have indices: '+str(list(set(tcp_idx.loc['Server', 'Observer']))))
print('The tests from Client to Observer using UDP have indices: '+str(list(set(udp_idx.loc['Client', 'Observer']))))
print('The tests from Observer to Server using UDP have indices: '+str(list(set(udp_idx.loc['Observer', 'Server']))))
print('The tests from Observer to Client using UDP have indices: '+str(list(set(udp_idx.loc['Observer', 'Client']))))
print('The tests from Server to Observer using UDP have indices: '+str(list(set(udp_idx.loc['Server', 'Observer']))))


# insert the id of the test 
flag = True
while flag:
    target_value = int(input("Insert the id of the test: "))
    if (tcp_idx.applymap(lambda x: str(target_value) in x).values.any()):
        bw_tcp, dataTrace, time = tcp_bandwidth(target_value, lines_cl)
        Time = [(time[i]-time[0])*1e-9 for i in range(len(time))]
        # Estimation of the bandwidth
        estimated_bandwidth = []
        alfa = 7/8#0.8
        for i,j in enumerate(dataTrace):   
            if i==0:
                bw_est = j
            else:
                bw_est = dataTrace[i-1]*alfa +(1-alfa)*j
            estimated_bandwidth.append(bw_est)
        dataTrace_ = [val*8 for val in dataTrace]
        estimated_bandwidth_ = [val*8 for val in estimated_bandwidth]
        plt.figure(1)
        plt.plot(Time[:-1], dataTrace_, label =f'Current bandwidth' )
        #plt.plot(Time[:-1], estimated_bandwidth_, label =f'Estimated bandwidth' )
        plt.xlabel('Time [s]')
        plt.ylabel('Bandwidth [kbps]')
        plt.legend()
        plt.title('Bandwidth')
        plt.grid('on')
        plt.figure(2)
        plt.hist(dataTrace_, label =f'Current bandwidth' )
        plt.ylabel('Number of times')
        plt.xlabel('Bandwidth [kbps]')
        plt.legend()
        plt.title('Bandwidth histogram')
        plt.grid('on')
        plt.show()
    elif (udp_idx.applymap(lambda x: str(target_value) in x).values.any()):
        bw_udp, dataTrace, time = udp_bandwidth(target_value, lines_cl)
        # Estimation of the bandwidth
        estimated_bandwidth = []
        alfa = 7/8#0.8
        for i,j in enumerate(dataTrace):   
            if i==0:
                bw_est = j
            else:
                bw_est = dataTrace[i-1]*alfa +(1-alfa)*j
            estimated_bandwidth.append(bw_est)
        plt.figure(1)
        plt.plot([t*1e-9 for t in time], [val*8 for val in dataTrace], label =f'Current bandwidth' )
        #plt.plot([t*1e-9 for t in time], [val*8 for val in estimated_bandwidth], label =f'Estimated bandwidth' )
        plt.xlabel('Time [s]')
        plt.ylabel('Bandwidth [kbps]')
        plt.legend()
        plt.title('Bandwidth')
        plt.grid('on')
        plt.figure(2)
        a,b, c = plt.hist([val*8 for val in dataTrace], label =f'Current bandwidth', bins=50 )
        plt.ylabel('Number of times')
        plt.xlabel('Bandwidth [kbps]')
        plt.legend()
        plt.title('Bandwidth histogram')
        plt.grid('on')
        plt.show()
    else:
        print('ERROR - INDEX NOT FOUND')
    choice = str(input('Do you want to continue? Y/N'))
    if choice=='N':
        flag=False

