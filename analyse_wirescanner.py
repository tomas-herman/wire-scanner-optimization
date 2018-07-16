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
    global popt
    global perr

    data = get_column(infile)

    data_raw_x = np.asarray(data[0])
    data_raw_y = np.asarray(data[1])

    data_x_old = data_raw_x * 1e-3
    data_y_old = data_raw_y - min(data_raw_y)

    data_x = []
    data_y = []

    for x,y in zip(data_x_old,data_y_old):
        if x > -30 and x < 0:
            data_x.append(x)
            data_y.append(y)

    mx = np.max(data_y)
    for i, j in zip(data_x, data_y):
    	if j == mx:
    		mu = i;


    # Gaussian fit
    popt, pcov = curve_fit(gauss, data_x, data_y, p0=[mx, mu, 2.6, 0, 0.01])
    perr = np.sqrt(np.diag(pcov)) # this is the error of the parameters sigma is second
    sigma = abs(popt[2]) * 1e-3
    # fit = r"$\sigma={:.3f}\pm{:.3f}$".format(popt[2], perr[2])

    # em_d, em = get_emittance(ring, plane, ctime, sigma)

    # with open(filename, 'a') as output:
    #     output.write(str(ctime) + " " + "{:.4E}".format(em) + "\n")

    # with open(filename_d, 'a') as output:
    #     output.write(str(ctime) + " " + "{:.4E}".format(em_d) + "\n")

    # print('>> ctime =', ctime, ', emittance =', em, ', sigma =', abs(popt[2]))



# color_list = ["black", "blue", "orange", "green", "yellow", "magenta", "purple", "red", "maroon"]
color_list = sns.color_palette("hls", 7)
filter_list = ["0% cardboard", "20%", "5%", "2%", "0.5%", "0.2%", "100% no filter", "0% metal" ]

measured_data_dict = collections.defaultdict(list)


ring = "R2"
folder_profiles = os.path.join(os.getcwd(), ring + "_speed_15_" + "profiles")
filter = [0,2,3,4,5]
for filt in filter:

	sigmas = []
	sigmas_erros = []
	pms = []
	bcts = []

	counter = 1 #set to 1 normally
	shot_max = 2 #set to 2 normally

	while counter <= shot_max:
		for folder in os.listdir("."):
			if folder.startswith(ring):
				if "Filter"+str(filt) in folder:
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
							if int(pm) > 50:
								plot_profile(f)
								# print('>> sigma =', abs(popt[2]))
								# print(gauss(np.asarray(data_x), *popt))

								# # Plotting individual profiles-----------------------------------------------------------------------------------------
								# plt.figure(1)
								# plt.plot(data_x, gauss(np.asarray(data_x), *popt), label="fit", lw=0.8, color='green')
								# plt.plot(data_x, data_y, label="data", color="black")
								# plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)
								# plt.title("Filter: " + filter_list[filt] + " PM gain: " + str(pm))

								# if not os.path.exists(folder_profiles):
								# 	print("Creating folder: " + folder_profiles)
								# 	os.makedirs(folder_profiles)

								# plt.savefig(os.path.join(folder_profiles, "profile_filter_" + filter_list[filt] + "_shot_" + shot + ".png"), bbox_inches='tight')
								# plt.clf()

								# Accesing intensity for given shot ---------------------------------------------------------------------------------------
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
											
								pms.append(pm)
								if abs(popt[2]) < 4:
									sigmas.append(abs(popt[2]))
									sigmas_erros.append(abs(perr[2]))
								else:
									sigmas.append(float('NaN'))
									sigmas_erros.append(float('NaN'))

							counter += 1
									

	measured_data_dict[(str(filt),"pms")] = pms 
	measured_data_dict[(str(filt),"sigmas")] = sigmas
	measured_data_dict[(str(filt),"sigmas_erros")] = sigmas_erros
	measured_data_dict[(str(filt),"bcts")] = bcts
	measured_data_dict[(str(filt),"sigmas_normalised")] = np.array(sigmas)/np.array(bcts)
	measured_data_dict[(str(filt),"sigmas_erros_normalised")] = np.array(sigmas_erros)/np.array(bcts)	


	plt.figure(2)
	# # For not normalised data---------------------------------
	# plt.errorbar(measured_data_dict[(str(filt),"pms")], measured_data_dict[(str(filt),"sigmas")], yerr = measured_data_dict[(str(filt),"sigmas_erros")], color=color_list[filt], label='Wirescanner data filter: ' + filter_list[filt])
	# plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms")]), np.asarray(measured_data_dict[(str(filt),"sigmas")])-np.asarray(measured_data_dict[(str(filt),"sigmas_erros")]), np.asarray(measured_data_dict[(str(filt),"sigmas")])+np.asarray(measured_data_dict[(str(filt),"sigmas_erros")]),facecolor=color_list[filt],alpha=0.5)
	# # # For data normalised with intensity----------------------
	plt.errorbar(measured_data_dict[(str(filt),"pms")], measured_data_dict[(str(filt),"sigmas_normalised")], yerr = measured_data_dict[(str(filt),"sigmas_erros_normalised")], color=color_list[filt], label='Wirescanner data filter: ' + filter_list[filt])
	plt.fill_between(np.asarray(measured_data_dict[(str(filt),"pms")]), np.asarray(measured_data_dict[(str(filt),"sigmas_normalised")])-np.asarray(measured_data_dict[(str(filt),"sigmas_erros_normalised")]), np.asarray(measured_data_dict[(str(filt),"sigmas_normalised")])+np.asarray(measured_data_dict[(str(filt),"sigmas_erros_normalised")]),facecolor=color_list[filt],alpha=0.5)


	# For scatter plot
	# plt.scatter(measured_data_dict[(str(filt),"pms")], measured_data_dict[(str(filt),"sigmas")], s=9, color=color_list[filt], label='Wirescanner data filter: ' + filter_list[filt])



# font = {'family': 'serif', 'serif': ['computer modern roman']}
# plt.rc('font', **font)
# rcParams['figure.figsize'] = 4, 3
# params = {'text.latex.preamble': [r'\usepackage{siunitx}',r'\usepackage{mathrsfs}']}
# plt.rcParams.update(params)
# rcParams['legend.frameon'] = 'True'

fig = plt.gcf()
fig.set_size_inches(15, 9)
# plt.plot(data_x, gauss(data_x, popt[0], popt[1], popt[2]), label="fit", lw=0.8, color='green')
plt.title("Profile dependance on PM gain for different filters")
plt.xlabel('PM gain [%]')
plt.ylabel(r'sigma [mm]')
# plt.xlim([-30,30])
plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)

# plt.show()
plt.savefig('sigma_on_pm.png', bbox_inches='tight')






# evenly sampled time at 200ms intervals
# t = np.arange(0., 5., 0.2)
# t = np.asarray(data[1])

# red dashes, blue squares and green triangles
# plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')