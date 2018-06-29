import datetime
import numpy as np
import pyjapc
import os
import re
import sys
import time
import warnings

# Settings
user = str(sys.argv[1])
ring = str(sys.argv[2])
plane = str(sys.argv[3])
wire_speed = sys.argv[4]

ctime = 796
filt = 4
pm = 1000

# Time of the measurement
time_stamp = time.strftime("%Y_%m_%d_%H_%M_%S")
print(" ")
print(">> Script launched at:", time_stamp)
print(" ")

# Create folder
folder = os.path.join(os.getcwd(), ring + plane + '_' + time_stamp)

if not os.path.exists(folder):
	os.makedirs(folder)

# Start pyjapc
japc = pyjapc.PyJapc()
japc.setSelector(user)
japc.rbacLogin()

def is_header(line):
    return re.search(r'#|@|%|\$|&', line) is not None


def get_line(infile):
    with open(infile, 'r') as data:
        for line in data:
            if is_header(line):
                continue
            else:
                yield line.strip('\n').split()


def get_column(infile):
    start_line = get_line(infile).__next__()
    data_dict = {key: [] for key, item in enumerate(start_line)}
    for line in get_line(infile):
        for count, item in enumerate(line):
            data_dict[count].append(float(item))
    return data_dict


def set_ws_params(ring, plane, time_stamp, ctime, filt, pm, wire_speed):
    japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#acqDelay", ctime)
    # Speeds: 10 m/s = 1, 15 m/s = 2
    if wire_speed == '10':
        japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#wireSpeed", 1)
    elif wire_speed == '15':
        japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#wireSpeed", 2)
    japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#gain", pm)
    japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#pmFilter", filt)
    japc.setParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#mode", 1)
    print(">> ctime set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#acqDelay"))
    print(">> ctime in the wirescanner:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#acqDelay"))
    print(">> Wire speed set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Setting#wireSpeed"))
    print(">> Photomultiplier gain set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#gain"))
    print(">> Filter set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#pmFilter"))


def get_profile(ring, plane, folder, ctime, shot):
    try:
        l=0
        data_x = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1")
        data_y = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projDataSet1")
        with open(os.path.join(folder, "profile_" + ring + "_" + plane + "_" + str(ctime)  + "_" + str(shot) + ".txt"), 'w') as fout:
            for i, j in zip(data_x, data_y):
                if l < 3: 
                    print(i, j)
                    l = l+1
                fout.write("{:.12E}".format(i) + "  " + "{:.12E}".format(j) + '\n')
        return 1
    except TypeError:
        print('>> No WS data. Waiting for next cycle.')
        return 0


# Callback function
def callback(param_name, new_value):
    callback.counter += 1
    print('')
    print('>> Shot', callback.counter)
    #get_profile(ring, plane, folder, ctime, callback.counter)
    #set_ws_params(ring, plane, time_stamp, ctime, 4, 1000, wire_speed)

    if callback.counter % 3 == 1:
        #print(callback.counter)
        #get_profile(ring, plane, folder, ctime, callback.counter)
        print('>> Setting parameters for a new scan')
        set_ws_params(ring, plane, time_stamp, ctime, filt, pm, wire_speed)
        
    elif callback.counter % 3 == 2:
        print(">> Excecuting scan")
        #print(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1"))
        #set_ws_params(ring, plane, time_stamp, ctime, 4, 1000, wire_speed)
    else:
        print(">> Reading data")
        get_profile(ring, plane, folder, ctime, callback.counter)
        #print(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1"))
    
        
japc.subscribeParam("B" + ring + ".BCT-ST/Samples", callback)
japc.startSubscriptions()


callback.counter = 0
measures = 6



while callback.counter < measures:
    time.sleep(0.5)
else:
    time.sleep(1)
    sys.exit(">> Finished measuring.")

japc.stopSubscriptions()
japc.clearSubscriptions()

