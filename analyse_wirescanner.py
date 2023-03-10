import os
import sys
import re
import glob
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import collections
import seaborn as sns
import matplotlib.axes as ax
import scipy.stats as stat
from matplotlib import rcParams
from matplotlib.pyplot import figure
from scipy.optimize import curve_fit
import intervals as I


beam_list = ["BCMS", "LHC", "ISOHRS"]
fit_list = ["profile", "intensity"]
speed_list = [10,15]


for beam_item in beam_list:
	for fit_item in fit_list:
		for speed_item in speed_list:

			# beam = "BCMS"
			# beam = "LHC"
			# beam = "ISOHRS"

			beam = beam_item

			# fit = "profile"
			# fit = "intensity"

			fit = fit_item

			ring = "R2"
			plane = "H"
			# speed = 10

			speed = speed_item

			# rcParams['figure.figsize'] = 4, 2
			# params = {'text.latex.preamble': [r'\usepackage{siunitx}', r'\usepackage{mathrsfs}']}
			# plt.rcParams.update(params)
			# rcParams['legend.frameon'] = 'True'
			plt.rc('font', family='serif')
			plt.rc('xtick', labelsize='small')
			plt.rc('ytick', labelsize='small')
			plt.rc('ytick', labelsize='small')
			plt.rcParams['lines.markersize'] = 5

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

			def empirical(x, a, e, b, c, d):
			    return a * x * b * 1/c * d + e

			# def empirical(x, a, e, f, b, c, d):
			#     return a * x**(f) * b * 1/c * d + e

			def fit_intensity(pm, intensity, intensity_error, filter, speed, bct): # For normal fit
			# def fit_intensity(pm, intensity, filter, speed, bct): # For inclusive fit
			    global popt1
			    global perr1

			    # Empirical fit
			    try:
			    	popt1, pcov1 = curve_fit(lambda x, a, e: empirical(x, a, e, filter, speed, bct), pm, intensity, sigma = intensity_error)  # ----------------For time dependent measurement----------------
			    	# popt1, pcov1 = curve_fit(lambda x, a, e, f: empirical(x, a, e, f, filter, speed, bct), pm, intensity, sigma = intensity_error, p0 = [0.000000000000000000000006, 0.001, 7])  # ----------------For time dependent measurement----------------, bounds = ([0.00000000000000000000000005, -1, 6],[0.0000000000000000000005, 1, 8])
			    	# popt1, pcov1 = curve_fit(lambda x, a, e: empirical(x, a, e, filter, speed, bct), pm, intensity)  # ----------------For time dependent measurement----------------
			    	perr1 = np.sqrt(abs(np.diag(pcov1)))
			    except:
			    	print("")
			    	print("Fit of WS inensity failed.")
			    	print("")
			    	popt1[0] = float("NaN")
			    	popt1[1] = float("NaN")

			    	perr1[0] = float("NaN")
			    	perr1[1] = float("NaN")



			def plot_profile(infile):
			    global data_x
			    global data_y
			    global data_z
			    global popt
			    global perr

			    data = get_column(infile)

			    data_raw_x = np.asarray(data[0])
			    data_raw_y = np.asarray(data[1])
			    data_raw_z = np.asarray(data[2])  # ----------------For time dependent measurement -> !!!!Change data[0] to data[2]!!!! ---------------- 

			    data_x_old = data_raw_x * 1e-3
			    data_y_old = data_raw_y
			    data_z_old = data_raw_z

			    data_x = []
			    data_y = []
			    data_z = []

			    for x,y,z in zip(data_x_old,data_y_old,data_z_old):
				    if plane == "V":    
				        if x > -10 and x < 10:
				        	data_x.append(x)
				        	data_y.append(y)
				        	data_z.append(z)
				    if plane == "H":
				    	if beam == "BCMS":
				            if x > -25 and x < 0:
				            	data_x.append(x)
				            	data_y.append(y)
				            	data_z.append(z)
				    	if beam == "LHC":
				            if x > -25 and x < 0:
				            	data_x.append(x)
				            	data_y.append(y)
				            	data_z.append(z)
				    	if beam == "ISOHRS":
				            if x > -35 and x < 5:
				            	data_x.append(x)
				            	data_y.append(y)
				            	data_z.append(z)

			    mx = np.max(data_y)
			    for i, j, k in zip(data_x, data_y, data_z):
			    	if j == mx:
			    		mu = i
			    		mu2 = k

			    # Gaussian fit
			    try:
			    	# popt, pcov = curve_fit(gauss, data_x, data_y, p0=[mx, mu, 2.6, 0, 0.01])
			    	popt, pcov = curve_fit(gauss, data_z, data_y, p0=[mx, mu2, 0.2, 0, 0.2])  # ----------------For time dependent measurement----------------
			    except:
			    	print("")
			    	print("Fit of profile failed.")
			    	print("")
			    	popt[0] = float("NaN")
			    	popt[1] = float("NaN")
			    	popt[2] = float("NaN")
			    	popt[3] = float("NaN")
			    	popt[4] = float("NaN")
			    
			    # perr = np.sqrt(abs(np.diag(pcov))) # this is the error of the parameters sigma is second


			def chisquare(observed_values,expected_values, sigma_values):
			    test_statistic=0
			    for observed, expected, sigma in zip(observed_values, expected_values, sigma_values):
			        test_statistic+=(float(observed)-float(expected))**2/float(sigma)**2
			    return test_statistic

			   

			# color_list = ["black", "blue", "orange", "green", "yellow", "magenta", "purple", "red", "maroon"]
			# color_list = sns.color_palette("hls", 8)
			color_list = plt.get_cmap('Dark2')
			filter_list = ["0% cardboard", "20%", "5%", "2%", "0.5%", "0.2%", "100% no filter", "0% metal" ]
			filter_list1 = [1, 20, 5, 2, 0.5, 0.2, 100, 1]


			if plane == "H":
				if speed == 10:

					if beam == "BCMS":
						run = [9,10,11,12]
						# run = [4,5,6,7,8,9,10,11,12,13,14,15,16]
						# run = [7,8,9,10,11,12,13,14,15,16]

					if beam == "LHC":
						run = [31,33]

					if beam == "ISOHRS":
						run = [21,22] # remove 23 for ISOHRS speed 10


				if speed == 15:

					if beam == "BCMS":
						run = [9,13,16]
						# run = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
						# run = [8,9,10,11,12,13,14,15,16]

					if beam == "LHC":
						run = [31,32,33]

					if beam == "ISOHRS":
						run = [21,22,23]



			if plane == "V":
				if speed == 10:

					if beam == "BCMS":
						run = [41,42]
					
					if beam == "BCMS":
						run = [48,49]




			# filter = [0,1,2,3,4,5,6,7]
			filter = [0,2,3,4,5]
			measured_data_dict = collections.defaultdict(list)
			mean_bct_sum = 0
			mean_bct_length = 0
			mean_bct_sum_sum = 0
			mean_bct_length_length = 0


			for r in run:
				# folder_profiles = os.path.join(os.getcwd(), ring + plane + "_speed_" + str(speed) + "_Run_" + str(r) + "_profiles")
				folder_profiles = os.path.join(os.getcwd(), ring + plane + "_speed_" + str(speed) + "_Run_" + str(r) + "_profiles(time)")  # ----------------For time dependent measurement----------------
				for filt in filter:

					sigmas = []
					sigmas_areas = []
					pms = []
					volts = []
					bcts = []

					counter = 1 #set to 1 normally
					shot_max = 2 #set to 2 normally

					while counter <= shot_max:
						for folder in os.listdir("."):
							if folder.startswith(ring + plane):
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
													if "voltage" in f:
														volt = f[f.find('voltage') + 7: f.find('voltage') + 11].strip("_")
													else:
														volt = 1
													if int(pm) > 25:
														print("Run: " + str(r))
														print("Filter: " + str(filt))
														print("PM gain: " + str(pm))
														# print (volt)
														plot_profile(f)
														# print(*popt)
														
														# ---------------------------------------Plotting individual profiles---------------------------------------
														# plt.figure(1)
														# # plt.plot(data_x, gauss(np.asarray(data_x), *popt), label="fit", lw=0.8, color='green')
														# # plt.plot(data_x, data_y, label="data", color="black")
														# plt.plot(data_z, gauss(np.asarray(data_z), *popt), label="fit", lw=0.8, color='green')  # ----------------For time dependent measurement----------------
														# plt.plot(data_z, data_y, label="data", color="black")  # ----------------For time dependent measurement----------------
														# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
														# plt.title("Filter: " + filter_list[filt] + ", PM gain: " + str(pm) + ", Sigma: " + str(round(abs(popt[2]),3)) + ", Amplitude: " + str(round(abs(popt[0]),3)))

														# # plt.xlabel('Position [mm]')
														# plt.xlabel('Time [ms]')  # ----------------For time dependent measurement----------------
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
																		if bct > 10:
																			bcts.append(bct)
																		else:
																			print("Intensity recording failed")
																			bcts.append(float("NaN"))
																	
														pms.append(float(pm))
														volts.append(float(volt))
														if abs(popt[2]) < 4:
															sigmas.append(abs(popt[2]))
															sigmas_areas.append(abs(popt[2]*popt[0]))
														else:
															print("One of the sigma values is too large!")
															sigmas.append(float('NaN'))
															sigmas_areas.append(float('NaN'))
															
													counter += 1
													
					measured_data_dict[(str(r),str(filt),"pms")] = pms 
					measured_data_dict[(str(r),str(filt),"volts")] = volts 
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
				sigmas_areas_inclusive = []
				pms_inclusive = []
				for r in run:	
					measured_data_dict[(str(r),str(filt),"sigmas_normalised")] = mean_bct * np.asarray(measured_data_dict[(str(r),str(filt),"sigmas")])/np.asarray(measured_data_dict[(str(r),str(filt),"bcts")])
					measured_data_dict[(str(r),str(filt),"sigmas_areas_normalised")] = mean_bct * np.asarray(measured_data_dict[(str(r),str(filt),"sigmas_areas")])/np.asarray(measured_data_dict[(str(r),str(filt),"bcts")])
					sigmas_areas_inclusive.append(measured_data_dict[(str(r),str(filt),"sigmas_areas")])
					pms_inclusive.append(measured_data_dict[(str(r),str(filt),"pms")])
				measured_data_dict[(str(filt),"sigmas_areas_inclusive")] = sigmas_areas_inclusive
				measured_data_dict[(str(filt),"pms_inclusive")] = pms_inclusive


			for filt in filter:
				sigmas_final = []
				sigmas_final_errors = []

				sigmas_areas_final = []
				sigmas_areas_final_errors = []

				pms_final = []
				pms_final_errors = []

				volts_final = []
				volts_final_errors = []

				bcts_final = []
				bcts_final_errors = []

				filter_range = range(0,20)


				for i in filter_range:
					all_sigmas = []
					all_sigmas_areas = []
					all_pms = []
					all_volts = []
					all_bcts = []

					for r in run:
						# all_sigmas.append(measured_data_dict[(str(r),str(filt),"sigmas_normalised")][i])
						all_sigmas.append(measured_data_dict[(str(r),str(filt),"sigmas")][i]) #Not normalised sigma
						# all_sigmas_areas.append(measured_data_dict[(str(r),str(filt),"sigmas_areas_normalised")][i])	
						all_sigmas_areas.append(measured_data_dict[(str(r),str(filt),"sigmas_areas")][i])	#Not normalised sigma		
						all_pms.append(measured_data_dict[(str(r),str(filt),"pms")][i])
						all_volts.append(measured_data_dict[(str(r),str(filt),"volts")][i])
						all_bcts.append(measured_data_dict[(str(r),str(filt),"bcts")][i])

					sigmas_final.append(np.mean(all_sigmas))
					sigmas_final_errors.append(np.std(all_sigmas,ddof=1))

					sigmas_areas_final.append(np.mean(all_sigmas_areas))
					sigmas_areas_final_errors.append(np.std(all_sigmas_areas,ddof=1))		

					pms_final.append(np.mean(all_pms))
					pms_final_errors.append(np.std(all_pms,ddof=1))

					volts_final.append(np.mean(all_volts))
					volts_final_errors.append(np.std(all_volts,ddof=1))

					bcts_final.append(np.mean(all_bcts))
					bcts_final_errors.append(np.std(all_bcts,ddof=1))
					
				measured_data_dict[(str(filt),"sigmas_final")] = sigmas_final
				measured_data_dict[(str(filt),"sigmas_final_errors")] = sigmas_final_errors

				measured_data_dict[(str(filt),"sigmas_areas_final")] = sigmas_areas_final
				measured_data_dict[(str(filt),"sigmas_areas_final_errors")] = sigmas_areas_final_errors

				measured_data_dict[(str(filt),"pms_final")] = pms_final
				measured_data_dict[(str(filt),"pms_final_errors")] = pms_final_errors

				measured_data_dict[(str(filt),"volts_final")] = volts_final
				measured_data_dict[(str(filt),"volts_final_errors")] = volts_final_errors

				measured_data_dict[(str(filt),"bcts_final")] = bcts_final
				measured_data_dict[(str(filt),"bcts_final_errors")] = bcts_final_errors

			print(" "
				"<html><head><style>"
					"table, th, td {"
					    "border: 1px solid black;"
					    "border-collapse: collapse;"
					"}"
					"th, td {"
					    "padding: 5px;"
					    "text-align: center;"
					"}"
					"</style></head><body>"
					'<table width=700>'
					  "<tr>"
					    "<th colspan='4'>" + ring + " " + plane + ", Speed: " + str(speed) + ", Avg beam I: " + str(int(round(mean_bct))) + " &middot 10<sup>10</sup> protons" "</th>"
					  "<tr>"
					  	"<th> Filter </th>"
					    "<th> k </th>"
					    "<th> e </th>"
					    "<th> PM gain range </th>"
				  "</tr>	")

				

			for filt in filter:

				filter_range = [0,1025]

				if fit == "intensity":

					if plane == "H":
						if beam == "BCMS":
							if speed == 10:
									if filt == 1:
										filter_range = [25,125]
									if filt == 2:
										filter_range = [375,575]
									if filt == 3:
										filter_range = [175,1025]
									if filt == 4:
										filter_range = [375,1025]
									if filt == 5:
										filter_range = [475,1025]			

							if speed == 15:
								if filt == 1:
									filter_range = [25,175]
								if filt == 2:
									filter_range = [375,675]
								if filt == 3:
									filter_range = [275,1025]
								if filt == 4:
									filter_range = [475,1025]
								if filt == 5:
									filter_range = [575,1025]			

						if beam == "LHC": 
							if speed == 10:
								if filt == 2:
									filter_range = [25,225]
								if filt == 3:
									filter_range = [25,475]
								if filt == 4:
									filter_range = [225,1025]
								if filt == 5:
									filter_range = [475,1025]			

							if speed == 15:
								if filt == 2:
									filter_range = [25,275]
								if filt == 3:
									filter_range = [25,575]
								if filt == 4:
									filter_range = [225,1025]
								if filt == 5:
									filter_range = [275,1025]	

						if beam == "ISOHRS":
							if speed == 10:
								if filt == 2:
									filter_range = [25,75]
								if filt == 3:
									filter_range = [25,175]
								if filt == 4:
									filter_range = [125,625]
								if filt == 5:
									filter_range = [175,975]			

							if speed == 15:
								if filt == 2:
									filter_range = [25,75]
								if filt == 3:
									filter_range = [25,225]
								if filt == 4:
									filter_range = [275,1025]
								if filt == 5:
									filter_range = [325,1025]	


					if plane == "V":
						if beam == "BCMS":
							if speed == 10:
								if filt == 2:
									filter_range = [175,825]
								if filt == 3:
									filter_range = [175,925]
								if filt == 4:
									filter_range = [275,1025]
								if filt == 5:
									filter_range = [375,1025]

						if beam == "LHC": 
							if speed == 10:
								if filt == 2:
									filter_range = [75,175]
								if filt == 3:
									filter_range = [75,575]
								if filt == 4:
									filter_range = [275,1025]
								if filt == 5:
									filter_range = [325,1025]				



				# ---------------------------------------------------- Empiricla Fit ----------------------------------------------------
				# ----------------------------- Substracting cardboard -----------------------------
				fit_intensity(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], filter_list1[filt], speed, mean_bct)
				chi_test = chisquare((np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])])
				# --------------- For INCLUSIVE fit ---------------
				# fit_intensity(np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_inclusive")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_inclusive")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], filter_list1[filt], speed, mean_bct)
				# chi_test = 0
				# --------------- For voltage fit ---------------
				# fit_intensity(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], filter_list1[filt], speed, mean_bct)
				# chi_test = chisquare((np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])])
				
				# print(chi_test)
				# print("")
				# print("Filter: " + filter_list[filt])
				# print("K: " + str(popt1[0]))
				# print("")	
				# ---------------------------------------------------- Empiricla Fit ----------------------------------------------------

			#------------------------------------------------------------------------------------------Old ploting------------------------------------------------------------------------------------------
				plt.figure(2)
				# ----------------------------- Substracting cardboard -----------------------------
				plt.scatter(np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_inclusive")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_inclusive")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], color=color_list(filt), s = 10, label='Filter: ' + filter_list[filt])
				# plt.errorbar(measured_data_dict[(str(filt),"pms_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
				plt.plot(np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_inclusive")]), np.asarray(measured_data_dict[(str(filt),"pms_inclusive")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label=("k: " + str(round(popt1[0],8)) + "$\pm$" + str(round(perr1[0],8)) + "\n" + "e: " + str(round(popt1[1],5)) + "$\pm$" + str(round(perr1[1],5)) + "\n" + "$\chi^2$: " + str(round(chi_test,3))), lw=0.8, color=color_list(filt))
				# Without label ----------------
				# plt.plot(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label= None, lw=0.8, color=color_list(filt))
				# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
				fig = plt.gcf()
				fig.set_size_inches(15, 9)
				plt.title(ring + plane + ", " + str(speed) + " m/s " + ", Sigma $\cdot$ Amplitude on PM gain." + " Avg. beam I: " + str(int(round(mean_bct))) + "$ \cdot 10^{10}$ protons", fontsize=18)
				plt.xlabel('PM gain [%]', fontsize=14)
				plt.xticks(np.arange(0, 1051, step=50), fontsize=12)
				# plt.yticks(np.arange(-0.25, 4, step=0.25), fontsize=12) # For all data 
				plt.yticks(np.arange(-0.025, 0.35, step=0.025), fontsize=12) # For all data   # ----------------For time dependent measurement----------------
				# plt.yticks(np.arange(-0.25, 1, step=0.25)) # For sellected data
				# plt.ylabel(r'Sigma $\cdot$ Amplitude [mm * mA]', fontsize=14)
				plt.ylabel(r'Sigma $\cdot$ Amplitude [ms * mA]', fontsize=14)  # ----------------For time dependent measurement----------------
				plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
				plt.grid(b=None, which='major', axis='both', linewidth=0.3, linestyle="--", color="black") 
				# plt.savefig("sigma_times_area_on_pm_" + ring + plane + "_filter" + str(filt) + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.clf()
			# ------------------------------------------------------------------------------------------Old ploting------------------------------------------------------------------------------------------

				plt.figure(3)
				plt.errorbar(measured_data_dict[(str(filt),"pms_final")], measured_data_dict[(str(filt),"sigmas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_final_errors")], color=color_list(filt), fmt='o', label='Filter: ' + filter_list[filt])
				# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
				fig = plt.gcf()
				fig.set_size_inches(8.27, 4.135)
				plt.title(ring + plane + ", " + str(speed) + " m/s " + ", Sigma on PM gain." + " Avg. beam I: " + str(int(round(mean_bct))) + "$ \cdot$10$^{10}$ protons")
				plt.xlabel('PM gain [%]')
				plt.xticks(np.arange(0, 1051, step=50))
				# plt.yticks(np.arange(1.5, 3, step=0.5)) # For sellected data
				if beam == "BCMS":
					plt.yticks(np.arange(0.10, 0.29, step=0.01))
				if beam == "LHC":
					plt.yticks(np.arange(0.10, 0.475, step=0.025))
				if beam == "ISOHRS":
					plt.yticks(np.arange(0.10, 1, step=0.05)) # For all data   # ----------------For time dependent measurement----------------
				# plt.yticks(np.arange(0, 4, step=0.5), fontsize=12) # For all data
				# plt.ylabel(r'Sigma [mm]', fontsize=14)
				plt.ylabel(r'Sigma [ms]')  # ----------------For time dependent measurement----------------
				plt.legend(loc='best').get_frame().set_linewidth(0.5)
				plt.grid(b=None, which='major', axis='both', linewidth=0.3, linestyle="--", color="black") 
				# plt.savefig("sigma_on_pm_" + ring + plane + "_filter" + str(filt) + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.clf()

				# plt.figure(4)
				# plt.errorbar(measured_data_dict[(str(filt),"bcts_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"bcts_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
				# # plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
				# fig = plt.gcf()
				# fig.set_size_inches(15, 9)
				# plt.title(ring + plane + " Speed: " + str(speed) + ", Sigma $\cdot$ Amplitude on intensity."  + " Avg beam I: " + str(int(round(mean_bct))) + "$ \cdot 10^{10}$ protons", fontsize=18)
				# plt.xlabel('Intensity [$10^{10}$ protons]', fontsize=12)
				# plt.ylabel(r'Sigma $\cdot$ Amplitude [mm * mA]', fontsize=12)
				# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
				# plt.rc('grid', linestyle="-", color='black')
				# plt.grid(True)
				# plt.savefig("sigma_times_area_on_intensity_" + ring + plane + "_filter" + str(filt) + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.clf()

				plt.figure(5)
				# ----------------------------- Substracting cardboard -----------------------------
				plt.errorbar(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], xerr = np.asarray(measured_data_dict[(str(filt),"pms_final_errors")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], yerr = np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], color=color_list(filt), fmt='o', label='Filter: ' + filter_list[filt])
				# plt.errorbar(measured_data_dict[(str(filt),"pms_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
				# plt.plot(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label=("k: " + str(round(popt1[0],8)) + "$\pm$" + str(round(perr1[0],8)) + "\n" + "e: " + str(round(popt1[1],5)) + "$\pm$" + str(round(perr1[1],5)) + "\n" + "$\chi^2$: " + str(round(chi_test,3))), lw=0.8, color=color_list(filt))
				# Without label ----------------
				plt.plot(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"pms_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label= None, lw=0.8, color=color_list(filt))
				# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
				fig = plt.gcf()
				fig.set_size_inches(8.27, 4.135)
				plt.title(ring + plane + ", " + str(speed) + " m/s " + ", Sigma $\cdot$ Amplitude on PM gain." + " Avg. beam I: " + str(int(round(mean_bct))) + "$ \cdot$10$^{10}$ protons")
				plt.xlabel('PM gain [%]')
				# plt.xticks(rotation=50)
				plt.xticks(np.arange(0, 1051, step=50))
				# plt.yticks(np.arange(-0.25, 4, step=0.25), fontsize=12) # For all data 
				plt.yticks(np.arange(-0.025, 0.3, step=0.025)) # For all data   # ----------------For time dependent measurement----------------
				# plt.yticks(np.arange(-0.25, 1, step=0.25)) # For sellected data
				# plt.ylabel(r'Sigma $\cdot$ Amplitude [mm * mA]', fontsize=14)
				plt.ylabel(r'Sigma $\cdot$ Amplitude [ms * mA]')  # ----------------For time dependent measurement----------------
				plt.legend(loc='best').get_frame().set_linewidth(0.5)
				plt.grid(b=None, which='major', axis='both', linewidth=0.3, linestyle="--", color="black") 
				# plt.savefig("sigma_times_area_on_pm_" + ring + plane + "_filter" + str(filt) + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.clf()

				plt.figure(6)
				# ----------------------------- Substracting cardboard -----------------------------
				plt.errorbar(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], (np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final")])-np.asarray(measured_data_dict[(str(0),"sigmas_areas_final")]))[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], xerr = np.asarray(measured_data_dict[(str(filt),"volts_final_errors")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], yerr = np.sqrt(np.asarray(measured_data_dict[(str(filt),"sigmas_areas_final_errors")])**2 + np.asarray(measured_data_dict[(str(0),"sigmas_areas_final_errors")])**2)[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
				# plt.errorbar(measured_data_dict[(str(filt),"volts_final")], measured_data_dict[(str(filt),"sigmas_areas_final")], xerr = measured_data_dict[(str(filt),"pms_final_errors")], yerr = measured_data_dict[(str(filt),"sigmas_areas_final_errors")], color=color_list(filt), fmt='o', markersize=5, label='Filter: ' + filter_list[filt])
				# plt.plot(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label=("k: " + str(round(popt1[0],30)) + "$\pm$" + str(round(perr1[0],30)) + "\n" + "e: " + str(round(popt1[1],5)) + "$\pm$" + str(round(perr1[1],5)) + "\n" + "$\chi^2$: " + str(round(chi_test,3))), lw=0.8, color=color_list(filt))
				# plt.plot(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label=("k: " + str(round(popt1[0],30)) + "$\pm$" + str(round(perr1[0],30)) + "\n" + "e: " + str(round(popt1[1],5)) + "$\pm$" + str(round(perr1[1],5)) + "\n" + "f: " + str(round(popt1[2],3)) + "$\pm$" + str(round(perr1[2],3)) + "\n" + "$\chi^2$: " + str(round(chi_test,3))), lw=0.8, color=color_list(filt))
				# Without label ----------------
				# plt.plot(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], empirical(np.asarray(measured_data_dict[(str(filt),"volts_final")])[np.logical_and(filter_range[0]<np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"pms_final")])<filter_range[1])], *popt1, filter_list1[filt], speed, mean_bct), label= None, lw=0.8, color=color_list(filt))
				# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms_final")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])-np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]), np.asarray(measured_data_dict[(str(filt),"sigmas_final")])+np.asarray(measured_data_dict[(str(filt),"sigmas_final_errors")]),facecolor=color_list[filt],alpha=0.5)
				fig = plt.gcf()
				fig.set_size_inches(15, 9)
				plt.title(ring + plane + ", " + str(speed) + " m/s " + ", Sigma $\cdot$ Amplitude on PM gain." + " Avg. beam I: " + str(int(round(mean_bct))) + "$ \cdot 10^{10}$ protons", fontsize=18)
				plt.xlabel('PM voltage [V]', fontsize=14)
				# plt.xticks(np.arange(0, 1051, step=50), fontsize=12)
				# plt.yticks(np.arange(-0.25, 4, step=0.25), fontsize=12) # For all data 
				plt.yticks(np.arange(-0.025, 0.35, step=0.025), fontsize=12) # For all data   # ----------------For time dependent measurement----------------
				# plt.yticks(np.arange(-0.25, 1, step=0.25)) # For sellected data
				# plt.ylabel(r'Sigma $\cdot$ Amplitude [mm * mA]', fontsize=14)
				plt.ylabel(r'Sigma $\cdot$ Amplitude [ms * mA]', fontsize=14)  # ----------------For time dependent measurement----------------
				plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
				plt.grid(b=None, which='major', axis='both', linewidth=0.3, linestyle="--", color="black") 
				# plt.savefig("sigma_times_area_on_pm_" + ring + plane + "_filter" + str(filt) + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.clf()




				print(" "
				  "<tr>"
				  	"<th>" + filter_list[filt] + "</th>"
				    # "<td>" + str(round(popt1[0],30)) + "&plusmn" + str(round(perr1[0],30)) + "</td>" #voltage
				    "<td>" + str(round(popt1[0],8)) + "&plusmn" + str(round(perr1[0],8)) + "</td>" #gain
				    "<td>" + str(round(popt1[1],5)) + "&plusmn" + str(round(perr1[1],5)) + "</td>"
				    "<td>" + str(filter_range) + "</td>"
				  "</tr>")
				  
			print("</table></body></html>")

			# plt.figure(2)
			# # plt.savefig("all_sigma_times_area_on_pm_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')
			# plt.savefig("aaTEST__all_sigma(time)_times_area_on_pm_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')  # ----------------For time dependent measurement----------------

			plt.figure(3)
			if fit == "profile":
				# # plt.savefig("all_sigma_on_pm_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')
				plt.savefig("all_" + beam + "_sigma(time)_on_pm_" + ring + plane + "_speed" + str(speed) + ".pdf", bbox_inches='tight')  # ----------------For time dependent measurement----------------
			plt.clf()


			# # # # plt.figure(4)
			# # # # plt.savefig("all_sigma_times_area_on_intensity_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')

			plt.figure(5)
			if fit == "intensity":
				# plt.savefig("all_sigma_times_area_on_pm_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')
				plt.savefig("aFIT_all_" + beam + "_sigma(time)_times_area_on_pm_" + ring + plane + "_speed" + str(speed) + ".pdf", bbox_inches='tight')  # ----------------For time dependent measurement----------------
			plt.clf()

				# plt.figure(6)
				# # plt.savefig("all_sigma_times_area_on_pm_" + ring + plane + "_speed" + str(speed) + ".png", bbox_inches='tight')
				# plt.savefig("aFIT_all_" + beam + "_sigma(time)_times_area_on_q_voltage_" + ring + plane + "_speed" + str(speed) + ".pdf", bbox_inches='tight')  # ----------------For time dependent measurement----------------
			# plt.clf()

			# plt.show()
