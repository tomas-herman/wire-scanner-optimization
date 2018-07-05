import os
import sys
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
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



def gauss(x, a, b, c):
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2))

def plot_profile(infile):
    global data_x
    global data_y
    global popt

    data = get_column(infile)

    data_raw_x = np.asarray(data[0])
    data_raw_y = np.asarray(data[1])

    data_x = data_raw_x * 1e-3
    data_y = data_raw_y - min(data_raw_y)

    # Gaussian fit
    popt, pcov = curve_fit(gauss, data_x, data_y)
    perr = np.sqrt(np.diag(pcov))
    sigma = abs(popt[2]) * 1e-3
    # fit = r"$\sigma={:.3f}\pm{:.3f}$".format(popt[2], perr[2])

    # em_d, em = get_emittance(ring, plane, ctime, sigma)

    # with open(filename, 'a') as output:
    #     output.write(str(ctime) + " " + "{:.4E}".format(em) + "\n")

    # with open(filename_d, 'a') as output:
    #     output.write(str(ctime) + " " + "{:.4E}".format(em_d) + "\n")

    # print('>> ctime =', ctime, ', emittance =', em, ', sigma =', abs(popt[2]))





# data = get_column("R2H_2018_06_29_16_58_37/profile_R2_H_796_3.txt")

for folder in os.listdir("."):
	if folder.startswith("R1"):
		print(folder)
		files = glob.glob(os.path.join(folder,"*.txt")) 
		#files = glob.glob(os.path.join(os.getcwd(),folder,"*.txt"))  # if location of data is in different folder 
		# print(files) 
		# print(" ")
		for f in files:
			# plot_profile(f)
			pm = f[f.find('pm') + 2: f.find('pm') + 4].strip("_")
			print(pm)




plot_profile("R2H_2018_06_29_16_58_37/profile_R2_H_796_3.txt")


# font = {'family': 'serif', 'serif': ['computer modern roman']}
# plt.rc('font', **font)
# rcParams['figure.figsize'] = 4, 3
# params = {'text.latex.preamble': [r'\usepackage{siunitx}',r'\usepackage{mathrsfs}']}
# plt.rcParams.update(params)
# rcParams['legend.frameon'] = 'True'


plt.scatter(data_x, data_y, s=0.3, color='black', label='Wirescanner data')
plt.plot(data_x, gauss(data_x, popt[0], popt[1], popt[2]), label="fit", lw=0.8, color='green')
# plt.title(ring + plane + ', ct = ' + ctime + ' ms, ' + r'$\epsilon =$' + str(round(em * 1e6, 3)) + ' mm.mrad')
plt.xlabel('Position [mm]')
plt.ylabel(r'Intensity [$10^{10}$]')
# plt.xlim([-30,30])
plt.legend(loc='best', prop={'size': 10}).get_frame().set_linewidth(0.5)

print('>> sigma =', abs(popt[2]))

# evenly sampled time at 200ms intervals
# t = np.arange(0., 5., 0.2)
# t = np.asarray(data[1])

# red dashes, blue squares and green triangles
# plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')


# plt.ylabel("#events")
# plt.xlabel("ctime [ms]")
# plt.show()