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
from scipy.optimize import curve_fit


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

def gauss(x, a, b, c, d, e):
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2)) + d * x + e

def plot_profile(infile):
    global data_x
    global data_y
    global data_z
    global popt
    global perr

    data = get_column(infile)

    data_raw_x = np.asarray(data[0])
    data_raw_y = np.asarray(data[1])
    data_raw_z = np.asarray(data[0])  # ----------------For time dependent measurement -> !!!!Change data[0] to data[2]!!!! ---------------- 

    data_x_old = data_raw_x * 1e-3
    data_y_old = data_raw_y
    data_z_old = data_raw_z

    data_x = []
    data_y = []
    data_z = []

    for x,y,z in zip(data_x_old,data_y_old,data_z_old):
        if x > -30 and x < 0:
            data_x.append(x)
            data_y.append(y)
            data_z.append(z)

    mx = np.max(data_y)
    for i, j, k in zip(data_x, data_y, data_z):
    	if j == mx:
    		mu = i
    		mu2 = k

    # Gaussian fit
    popt, pcov = curve_fit(gauss, data_x, data_y, p0=[mx, mu, 2.6, 0, 0.01])
    # popt, pcov = curve_fit(gauss, data_z, data_y, p0=[mx, mu2, 0.2, 0, 0.2])  # ----------------For time dependent measurement----------------
    perr = np.sqrt(abs(np.diag(pcov))) # this is the error of the parameters sigma is second
   

# color_list = ["black", "blue", "orange", "green", "yellow", "magenta", "purple", "red", "maroon"]
# color_list = sns.color_palette("hls", 8)
color_list = plt.get_cmap('Dark2')
filter_list = ["0% cardboard", "20%", "5%", "2%", "0.5%", "0.2%", "100% no filter", "0% metal" ]

run = [1]
filter = [0,1,2,3,4,5,6,7]
# filter = [0,2,3,4,5,7]
# filter = [2,3,4,5]
# filter = [1,6]
ring = "R2"
speed = "15"
measured_data_dict = collections.defaultdict(list)
mean_bct_sum = 0
mean_bct_length = 0
mean_bct_sum_sum = 0
mean_bct_length_length = 0


for r in run:
	folder_profiles = os.path.join(os.getcwd(), ring + "_speed_" + str(speed) + "_Run_" + str(r) + "_profiles")
	for filt in filter:

		sigmas = []
		sigmas_areas = []
		pms = []
		bcts = []

		counter = 1 #set to 1 normally
		shot_max = 2 #set to 2 normally

		while counter <= shot_max:
			for folder in os.listdir("."):
				if folder.startswith(ring):
					if "Speed"+str(speed) in folder:
						if "Filter"+str(filt) in folder:
							if "Run"+str(r) in folder:
								files = glob.glob(os.path.join(folder,"*.txt")) 
								#files = glob.glob(os.path.join(os.getcwd(),folder,"*.txt"))  # if location of data is in different folder 
								for f in files:
									shot = f[f.find('shot') + 4: f.find('shot') + 7].strip("_")
								
									if shot_max < int(shot): 
										shot_max = int(shot)
									if int(shot) == counter:
										
										pm = f[f.find('pm') + 2: f.find('pm') + 6].strip("_")
										if int(pm) > 60:
											plot_profile(f)
											
											# ---------------------------------------Plotting individual profiles---------------------------------------
											# plt.figure(1)
											# # plt.plot(data_x, gauss(np.asarray(data_x), *popt), label="fit", lw=0.8, color='green')
											# # plt.plot(data_x, data_y, label="data", color="black")
											# plt.plot(data_z, gauss(np.asarray(data_z), *popt), label="fit", lw=0.8, color='green')  # ----------------For time dependent measurement----------------
											# plt.plot(data_z, data_y, label="data", color="black")  # ----------------For time dependent measurement----------------
											# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
											# plt.title("Filter: " + filter_list[filt] + ", PM gain: " + str(pm) + ", Sigma: " + str(round(abs(popt[2]),3)))

											# # plt.xlabel('Position [mm]')
											# plt.xlabel('Time [s]')  # ----------------For time dependent measurement----------------
											# plt.ylabel(r'Current [mA]')

											# if not os.path.exists(folder_profiles):
											# 	print("Creating folder: " + folder_profiles)
											# 	os.makedirs(folder_profiles)

											# plt.savefig(os.path.join(folder_profiles, "profile_filter_" + filter_list[filt] + "_shot_" + shot + ".png"), bbox_inches='tight')
											# plt.clf()
											# ---------------------------------------Plotting individual profiles---------------------------------------


											# -------------------------------------Accesing intensity for given shot ---------------------------------------------------------------------------------------
											files_bct = glob.glob(os.path.join(folder+"/bct","*.txt")) 
											for f_bct in files_bct:
												
												shot_bct = f_bct[f_bct.find('shot') + 4: f_bct.find('shot') + 7].strip("_")
												
												if int(shot_bct) == counter:
													data_bct = get_column(f_bct)
													data_time = np.asarray(data_bct[1])
													data_bct = np.asarray(data_bct[0])

													for t,bct in zip(data_time,data_bct):
														if t == 796:
															bcts.append(bct)
														
											pms.append(float(pm))
											if abs(popt[2]) < 10000:
												sigmas.append(abs(popt[2]))
												sigmas_areas.append(abs(popt[2]*popt[0]))
											else:
												print("One of the sigma values is too large!")
												sigmas.append(float('NaN'))
												sigmas_areas.append(float('NaN'))
												
										counter += 1
										
		measured_data_dict[(str(r),str(filt),"pms")] = pms 
		measured_data_dict[(str(r),str(filt),"sigmas")] = sigmas
		measured_data_dict[(str(r),str(filt),"sigmas_areas")] = sigmas_areas
		measured_data_dict[(str(r),str(filt),"bcts")] = bcts
		measured_data_dict[(str(r),str(filt),"avg_bcts")] = sum(bcts)/float(len(bcts))
		mean_bct_sum = mean_bct_sum + measured_data_dict[(str(r),str(filt),"avg_bcts")]
		mean_bct_length = mean_bct_length + 1

	mean_bct_sum_sum = mean_bct_sum_sum + mean_bct_sum
	mean_bct_length_length = mean_bct_length_length + mean_bct_length

mean_bct = mean_bct_sum_sum/mean_bct_length_length

for filt in filter:
	for r in run:	
		measured_data_dict[(str(r),str(filt),"sigmas_normalised")] = mean_bct * np.asarray(measured_data_dict[(str(r),str(filt),"sigmas")])/np.asarray(measured_data_dict[(str(r),str(filt),"bcts")])
		
#------------------------------------------------------------------------------------------Old ploting------------------------------------------------------------------------------------------
	# 	plt.figure(2)
	# 	# # For not normalised data---------------------------------
	# 	# plt.errorbar(measured_data_dict[(str(r),str(filt),"pms")], measured_data_dict[(str(r),str(filt),"sigmas")], yerr = measured_data_dict[(str(r),str(filt),"sigmas_errors")], color=color_list[filt], label='Wirescanner data filter: ' + filter_list[filt])
	# 	# plt.fill_between(np.asarray(measured_data_dict[(str(r),str(filt),"pms")]), np.asarray(measured_data_dict[(str(r),str(filt),"sigmas")])-np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_errors")]), np.asarray(measured_data_dict[(str(r),str(filt),"sigmas")])+np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_errors")]),facecolor=color_list[filt],alpha=0.5)
	# 	# # # For data normalised with intensity----------------------
	# 	# plt.errorbar(measured_data_dict[(str(r),str(filt),"pms")], measured_data_dict[(str(r),str(filt),"sigmas_normalised")], yerr = measured_data_dict[(str(r),str(filt),"sigmas_errors_normalised")], color=color_list[filt], label='Wirescanner data filter: ' + filter_list[filt])
	# 	# plt.fill_between(np.asarray(measured_data_dict[(str(r),str(filt),"pms")]), np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_normalised")])-np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_errors_normalised")]), np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_normalised")])+np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_errors_normalised")]),facecolor=color_list[filt],alpha=0.5)


	# 	# For scatter plot
	# 	if r == 1:
	# 		plt.scatter(measured_data_dict[(str(r),str(filt),"pms")], measured_data_dict[(str(r),str(filt),"sigmas_normalised")], s=20, color=color_list[filt], label='Filter: ' + filter_list[filt])
	# 	else:
	# 		plt.scatter(measured_data_dict[(str(r),str(filt),"pms")], measured_data_dict[(str(r),str(filt),"sigmas_normalised")], s=20, color=color_list[filt], label= None)
		
	# fig = plt.gcf()
	# fig.set_size_inches(15, 9)
	# plt.title("Profile dependance on PM gain for Filter: " + filter_list[filt] + ", Average beam intensity: " + str(round(mean_bct,3)) + " ???")
	# plt.xlabel('PM gain [%]')
	# plt.xticks(np.arange(0, 1051, step=50))
	# plt.ylabel(r'sigma [mm]')
	# plt.xlim([0,1050])
	# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)

	# # plt.show()
	# plt.savefig("sigma_on_pm_filter" + str(filt) + "_speed" + speed + ".png", bbox_inches='tight')
	# plt.clf()
#------------------------------------------------------------------------------------------Old ploting------------------------------------------------------------------------------------------

for filt in filter:
	sigmas_final = []
	sigmas_final_errors = []

	sigmas_areas_final = []
	sigmas_areas_final_errors = []

	pms_final = []
	pms_final_errors = []

	bcts_final = []
	bcts_final_errors = []
	for i in range (0,19):
		all_sigmas = []
		all_sigmas_areas = []
		all_pms = []
		all_bcts = []

		for r in run:
			all_sigmas.append(measured_data_dict[(str(r),str(filt),"sigmas_normalised")][i])
			all_sigmas_areas.append(measured_data_dict[(str(r),str(filt),"sigmas_areas")][i])			
			all_pms.append(measured_data_dict[(str(r),str(filt),"pms")][i])
			all_bcts.append(measured_data_dict[(str(r),str(filt),"bcts")][i])

		sigmas_final.append(np.mean(all_sigmas))
		sigmas_final_errors.append(np.std(all_sigmas,ddof=1))

		sigmas_areas_final.append(np.mean(all_sigmas_areas))
		sigmas_areas_final_errors.append(np.std(all_sigmas_areas,ddof=1))		

		pms_final.append(np.mean(all_pms))
		pms_final_errors.append(np.std(all_pms,ddof=1))

		bcts_final.append(np.mean(all_bcts))
		bcts_final_errors.append(np.std(all_bcts,ddof=1))
		
	measured_data_dict[(str(filt),"sigmas_final")] = sigmas_final
	measured_data_dict[(str(filt),"sigmas_final_errors")] = sigmas_final_errors

	measured_data_dict[(str(filt),"sigmas_areas_final")] = sigmas_areas_final
	measured_data_dict[(str(filt),"sigmas_areas_final_errors")] = sigmas_areas_final_errors

	measured_data_dict[(str(filt),"pms_final")] = pms_final
	measured_data_dict[(str(filt),"pms_final_errors")] = pms_final_errors

	measured_data_dict[(str(filt),"bcts_final")] = bcts_final
	measured_data_dict[(str(filt),"bcts_final_errors")] = bcts_final_errors

	plt.figure(3)
	plt.errorbar(measured_data_dict[(str(filt),"pms_final")], measured_data_dict[(str(filt),"sigmas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
	# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
	fig = plt.gcf()
	fig.set_size_inches(15, 9)
	plt.title("Profile dependance on PM gain." + " Average beam intensity: " + str(round(mean_bct,3)) + " ???")
	plt.xlabel('PM gain [%]')
	plt.xticks(np.arange(0, 1051, step=50))
	plt.ylabel(r'Sigma [mm]')
	# plt.ylabel(r'Sigma [s]')  # ----------------For time dependent measurement----------------
	plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
	# plt.savefig("sigma_on_pm_filter" + str(filt) + "_speed" + speed + ".png", bbox_inches='tight')
	# plt.clf()

	plt.figure(4)
	plt.errorbar(measured_data_dict[(str(filt),"bcts_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"bcts_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
	# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
	fig = plt.gcf()
	fig.set_size_inches(15, 9)
	plt.title("Profile * Amplitude dependance on intensity."  + " Average beam intensity: " + str(round(mean_bct,3)) + " ???")
	plt.xlabel('Intensity [???]')
	plt.ylabel(r'Sigma * Amplitude [mm * mA]')
	plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
	# plt.savefig("sigma_times_area_on_intensity_filter" + str(filt) + "_speed" + speed + ".png", bbox_inches='tight')
	# plt.clf()

	plt.figure(5)
	plt.errorbar(measured_data_dict[(str(filt),"pms_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
	# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
	fig = plt.gcf()
	fig.set_size_inches(15, 9)
	plt.title("Profile * Amplitude dependance on PM gain." + " Average beam intensity: " + str(round(mean_bct,3)) + " ???")
	plt.xlabel('PM gain [%]')
	plt.xticks(np.arange(0, 1051, step=50))
	plt.ylabel(r'Sigma * Amplitude [mm * mA]')
	plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
	# plt.savefig("sigma_times_area_on_pm_filter" + str(filt) + "_speed" + speed + ".png", bbox_inches='tight')
	# plt.clf()

plt.figure(3)
plt.savefig("all_sigma_on_pm" + "_speed" + speed + ".png", bbox_inches='tight')

# plt.figure(4)
# plt.savefig("all_sigma_times_area_on_intensity" + "_speed" + speed + ".png", bbox_inches='tight')

# plt.figure(5)
# plt.savefig("all_sigma_times_area_on_pm" + "_speed" + speed + ".png", bbox_inches='tight')

