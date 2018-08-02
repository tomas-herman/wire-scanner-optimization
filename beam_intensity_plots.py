import os
import sys
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import collections
import seaborn as sns
from matplotlib import rcParams
from matplotlib.pyplot import figure


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
						

# color_list = ["black", "blue", "orange", "green", "yellow", "magenta", "purple", "red", "maroon"]
color_list = sns.color_palette("hls", 9)
filter_list = ["0% cardboard", "20%", "5%", "2%", "0.5%", "0.2%", "100% no filter", "0% metal" ]

run = [1,2,4]
filter = [0,1,2,3,4,5,6,7]
ring = "R2"
plane = "H"
speed = "15"
measured_data_dict = collections.defaultdict(list)
mean_bct_sum = 0
mean_bct_length = 0
mean_bct_sum_sum = 0
mean_bct_length_length = 0


for r in run:
	folder_profiles = os.path.join(os.getcwd(), ring + plane + "_speed_" + str(speed) + "_Run_" + str(r) + "_profiles")
	folder_intensity = os.path.join(os.getcwd(), ring + plane + "_speed_" + str(speed) + "_Run_" + str(r) + "_intensity")
	for filt in filter:

		sigmas = []
		sigmas_erros = []
		pms = []
		bcts = []

		counter = 1 #set to 1 normally
		shot_max = 2 #set to 2 normally

		while counter <= shot_max:
			for folder in os.listdir("."):
				if folder.startswith(ring + plane):
					if "Speed"+str(speed) in folder:
						if "Filter"+str(filt) in folder:
							if "Run"+str(r) in folder:
								# print(folder)
								files = glob.glob(os.path.join(folder,"*.txt")) 
								#files = glob.glob(os.path.join(os.getcwd(),folder,"*.txt"))  # if location of data is in different folder 
								# print(files) 
								# print(" ")
								for f in files:
									shot = f[f.find('shot') + 4: f.find('shot') + 7].strip("_")
									# print(shot)
									# print(shot_max)
									if shot_max < int(shot): 
										shot_max = int(shot)
									if int(shot) == counter:
										
										pm = f[f.find('pm') + 2: f.find('pm') + 6].strip("_")
										# print(pm)
										if int(pm) > 40:

											# Accesing intensity for given shot ---------------------------------------------------------------------------------------
											files_bct = glob.glob(os.path.join(folder+"/bct","*.txt")) 
											for f_bct in files_bct:
												
												shot_bct = f_bct[f_bct.find('shot') + 4: f_bct.find('shot') + 7].strip("_")
												
												if int(shot_bct) == counter:
													data_bct = get_column(f_bct)
													data_time = np.asarray(data_bct[1])
													data_bct = np.asarray(data_bct[0])

													times = []
													bcts = []

													for t,bct in zip(data_time,data_bct):
														bcts.append(bct)
														times.append(t)
														if t == 796:
															bct_at_796 = bct



													plt.figure(1)
													plt.plot(times, bcts, label="intensity", color="black")
													# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
													plt.title("Filter: " + filter_list[filt] + ", PM gain: " + str(pm) + ", Intensity at 796 ms: " + str(round(bct_at_796,3)))

													plt.xlabel('Time [ms]')
													plt.ylabel(r'Intensity [???]')

													if not os.path.exists(folder_intensity):
														print("Creating folder: " + folder_intensity)
														os.makedirs(folder_intensity)

													plt.savefig(os.path.join(folder_intensity, "intensity_filter_" + filter_list[filt] + "_shot_" + shot + ".png"), bbox_inches='tight')
													plt.clf()
													

										counter += 1
													

