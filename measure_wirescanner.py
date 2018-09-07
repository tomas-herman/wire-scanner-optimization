import datetime
import numpy as np
import pyjapc
import os
import re
import sys
import time
import warnings

# Settings
user = "PSB.USER.LHC2A"
ring = "R2"
planes = ["V"] 
speeds = [10]
runs = [49,48]
filters = [0,2,3,4,5]


# Start pyjapc
japc = pyjapc.PyJapc()
japc.setSelector(user)
japc.rbacLogin()

for p in planes:
    plane = p
    for s in speeds:
        #if s == 15:
            #runs = [15,16]
        #if s == 10:
            #runs = [11,12,13,14,15,16,17] 
        for r in runs:
            #if s == 10:
                #if r == 16:
                    #filters = [1,2,3,4,5,6,7]
            #if s == 10:
                #if r == 17:
                    #filters = [0,1,2,3,4,5,6,7]
            #if s == 15:
                #if r == 21:
                    #filters = [3,4,5]
            #if s == 15:
                #if r == 22:
                    #filters = [0,2,3,4,5]              
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
                    try:
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
                        print(">> Photomultiplier voltage set to (not measured!):", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#voltage"))
                        print(">> Filter set to:", japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/SettingHV#pmFilter"))
                        print(">> Run: " + str(r))
                        print(">> Ring and plane: " + ring + plane)
                    except:
                        print('>> Someone else is using the wire scanner. Waiting for next cycle to set the parameters.')
                        callback.counter = callback.counter - 1
                        
    
    
                def get_profile(ring, plane, folder, ctime, shot):
                    global pm
                    try:
                        l=0
                        data_x = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projPositionSet1")
                        data_y = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#projDataSet1")
                        data_z = japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#ctrTStampSet1")
    
                        with open(os.path.join(folder, "profile_" + ring + "_" + plane + "_time" + str(ctime)  + "_speed" + str(wire_speed) + "_filter" + str(filt) + "_shot" + str(int(callback.counter/2)) + "__" + "_pm" + str(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#gain")) + "__" + "_voltage" + str(japc.getParam("B" + ring + ".BWS.2L1." + plane + "_ROT" + "/Acquisition#voltage")) + "__" + ".txt"), 'w') as fout:
                            for i, j, k in zip(data_x, data_y, data_z):
                                if l < 3: 
                                    print(i, j, k)
                                    l += 1
                                fout.write("{:.12E}".format(i) + "  " + "{:.12E}".format(j) + "  " + "{:.12E}".format(k) + '\n')
                        pm += 50                        
                        return 1
                    except TypeError:
                        print('>> No WS data. Repeating this settings in the next cycle.')
                        callback.counter = callback.counter - 2                  
                        return 0
    
                def record_bct(ring, ctime):
                    if not os.path.exists(os.path.join(folder, "bct")):
                        os.makedirs(os.path.join(folder, "bct"))
                    folder_bct = os.path.join(folder, "bct")
                    param_bct = ["B" + ring + ".BCT-ST/Samples#samples", "B" + ring + ".BCT-ST/Samples#firstSampleTime", "B" + ring + ".BCT-ST/Samples#samplingTrain"]
    
                    with open(os.path.join(folder_bct, "BCT_" + ring + "_" + str(ctime) + "_shot" + str(int(callback.counter/2)) + "__" ) + ".txt", "w") as bct_file:
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
    
                    if callback.counter % 2 == 1:
                        #print(callback.counter)
                        print('')
                        print('>> Setting parameters for a new scan')
                        set_ws_params(ring, plane, time_stamp, ctime, filt, pm, wire_speed)
                    elif callback.counter % 2 == 0:
                        print('')
                        print(">> Reading data")
                        record_bct(ring, ctime)
                        time.sleep(0.5)
                        get_profile(ring, plane, folder, ctime, callback.counter)
                    
                   
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

