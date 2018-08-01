import datetime
import numpy as np
import pyjapc
import os
import re
import sys
import time
import warnings

# Settings
user = "PSB.USER.MD3"
ring = "R2"

speeds = [15]
runs = [2]
filters = [7]
planes = ["H"]

# Start pyjapc
japc = pyjapc.PyJapc()
japc.setSelector(user)
japc.rbacLogin()

for p in planes:
    plane = p
    for s in speeds:
        for r in runs:
            for f in filters:
    
                wire_speed = str(s)
                ctime = 796
                filt = f
                pm = 50
                run = r
    
    
                # Time of the measurement
                time_stamp = time.strftime("%Y_%m_%d_%H_%M_%S")
                print(" ")
                print(">> Script launched at:", time_stamp)
                print(" ")
    
                # Create folder
                folder = os.path.join(os.getcwd(), ring + plane + '_' + "Filter" + str(filt) + '_' + "Speed" + str(wire_speed) + "_" + "Run" + str(run) + "__" + time_stamp)
    
                if not os.path.exists(folder):
                    os.makedirs(folder)
    
    
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
                    #print(">> Photomultiplier gain set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#gain"))
                    print(">> Photomultiplier gain set to (not measured!):", pm)
                    print(">> Filter set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#pmFilter"))
                    print(">> Run: " + str(r))
                    print(">> Ring and plane: " + ring + plane)
    
    
                def get_profile(ring, plane, folder, ctime, shot):
                    try:
                        l=0
                        data_x = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1")
                        data_y = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projDataSet1")
                        data_z = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#ctrTStampSet1")
    
                        with open(os.path.join(folder, "profile_" + ring + "_" + plane + "_time" + str(ctime)  + "_speed" + str(wire_speed) + "_filter" + str(filt) + "_shot" + str(int(callback.counter/3)) + "__" + "_pm" + str(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#gain")) + "__" + ".txt"), 'w') as fout:
                            for i, j, k in zip(data_x, data_y, data_z):
                                if l < 3: 
                                    print(i, j, k)
                                    l += 1
                                fout.write("{:.12E}".format(i) + "  " + "{:.12E}".format(j) + "  " + "{:.12E}".format(k) + '\n')
                        return 1
                    except TypeError:
                        print('>> No WS data. Waiting for next cycle.')
                        return 0
    
                def record_bct(ring, ctime):
                    if not os.path.exists(os.path.join(folder, "bct")):
                        os.makedirs(os.path.join(folder, "bct"))
                    folder_bct = os.path.join(folder, "bct")
                    param_bct = ["B" + ring + ".BCT-ST/Samples#samples", "B" + ring + ".BCT-ST/Samples#firstSampleTime", "B" + ring + ".BCT-ST/Samples#samplingTrain"]
    
                    with open(os.path.join(folder_bct, "BCT_" + ring + "_" + str(ctime) + "_shot" + str(int(callback.counter/3)) + "__" ) + ".txt", "w") as bct_file:
                        intensity = japc.getParam("B" + ring + ".BCT-ST/Samples#samples")
                        first_sample_time = japc.getParam("B" + ring + ".BCT-ST/Samples#firstSampleTime")
                        sample_train = japc.getParam("B" + ring + ".BCT-ST/Samples#samplingTrain")
                        acq_time = np.linspace(first_sample_time, first_sample_time + len(intensity) - 1, len(intensity))
    
                        for i, t in zip(intensity, acq_time):
                            bct_file.write("%s %s \n" % (i, t))
    
    
                # Callback function
                def callback(param_name, new_value):
                    global pm
                    callback.counter += 1
                    print('')
                    print('>> Shot', callback.counter)
                    #get_profile(ring, plane, folder, ctime, callback.counter)
                    #set_ws_params(ring, plane, time_stamp, ctime, 4, 1000, wire_speed)
    
                    if callback.counter % 3 == 1:
                        #print(callback.counter)
                        #get_profile(ring, plane, folder, ctime, callback.counter)
                        print('')
                        print('>> Setting parameters for a new scan')
                        set_ws_params(ring, plane, time_stamp, ctime, filt, pm, wire_speed)
                    elif callback.counter % 3 == 2:
                        print('')
                        print(">> Excecuting scan")
                        #print(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1"))
                        #set_ws_params(ring, plane, time_stamp, ctime, 4, 1000, wire_speed)
                        #pm += 10
                    else:
                        print('')
                        print(">> Reading data")
                        get_profile(ring, plane, folder, ctime, callback.counter)
                        record_bct(ring, ctime)
                        pm += 50
                        #print(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1"))
                    
                   
                japc.subscribeParam("B" + ring + ".BCT-ST/Samples", callback)
                japc.startSubscriptions()
    
    
                callback.counter = 0
    
    
                while pm <= 1001:
                    time.sleep(0.5)
                else:
                    time.sleep(1)
                    print('')
                    print(">> Finished measuring with this setting.")
    
                japc.stopSubscriptions()
                japc.clearSubscriptions()
print('')
sys.exit(">> Finished measuring.")

