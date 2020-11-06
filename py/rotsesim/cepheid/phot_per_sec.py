#these lines import various libraries to use
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import csv
import random
import itertools

import pandas as pd

from astropy.io import fits
from astropy.table import Table, join
from astropy.io.ascii import write, read
from scipy.optimize import curve_fit, leastsq
from scipy.stats import chisquare
from scipy.stats import norm, cauchy, chisquare

inputcsv = pd.read_csv('C4.1_period730.csv') #tells the script which csv file to use as a source of input data; the csv file must be in the same directory as this script

Rstar = inputcsv['Rstar'] #identifies the column for the Radius of the star


Teff = inputcsv['Teff'] #identifies the column for the T_effective of the star

star_age = inputcsv['star_age_day'] #identifies the column for the time of each input data point


h = 6.626*10**-34  #Planck's constant in J s

c = 2.998*10**8 #speed of light in vaccuum in m/s

k = 1.381*10**-23 #Boltzmann's constant in m^2 kg / s^2 K

dlt_lambda = 0.5 #wavelength range in nm

R_star = 2.78*10**10 #40 times solar radius (measured in meters); is supposed to be a test radius of a star and can be changes at will

D = 10*(9.4544928*10**15) #distance between star and earth (in meters); first number is number of light years; second number is conversion factor from light years to meters

A_star_to_earth = 4*np.pi*D**2 #surface area of sphere whose radius extends from star to earth

A_CCD = (27.6*10**-3)**2 #area of ROTSE-III rectangular CCD (27.6 mm by 27.6 mm) given in m^2

#Planck blackbody radiation law with the following modifications:
#1. multiplied by surface area of star, divided by surface area of sphere from star to earth, and multiplied by area of CCD to account for how many photons will be detected by a CCD on earth (which could be very far away from the star)
#2. divded by E = hc/lambda to obtain the number of photons at each wavelength lambda
#3. multiplied by dlt_lambda, which will give a range of wavelengths centered aroun lambda (i.e. if lambda = 500 nm and dlt_lambda = 0.5 nm, the function will detect the number of photons emitted between 499.5 nm to 500.5 nm)

def Phot(l, R, T):
	P = (4*np.pi*(R**2)/A_star_to_earth)*A_CCD*(8*np.pi*h*c**2)*(1/l**5)*(1/(np.exp(h*c/(k*T*l)) - 1))*dlt_lambda/(h*c/l)
	return P


#creates an output text file called output1.txt where the first column is the radius of the star, the second column is the effective temperature of the star, and the third column is the number of photons/second in each wavelength of light, starting at 299 nm and ending at 1001 nm
#this means that for each pair of Rstar and Teff, there will be around 700 values of photons
file=open("output1.txt", "a")

for a, b in zip(Rstar, Teff):
	for i in range(299, 1001):
		photon_in_each_lambda = str(Phot(i*10**-9, a, b))
		a_str = str(a)
		b_str = str(b)
		file.write(a_str + "\t" + b_str + "\t" + photon_in_each_lambda + "\n")

file.close()

#creates an output text file called output2.txt where the first column is the radius of the star, the second column is the effective temperature of the star, and the third column is the total number of photons/second emitted for each associated Rstar and Teff (i.e. it sums the 700 or so data points from each Rstar and Teff pair and stores them next to the associated Rstar and Teff from which they were generated
file=open("output2.txt", "a")

for a, b in zip(Rstar, Teff):
	output_of_func = []
	for i in range(299, 1001):
		Phot_output = Phot(i*10**-9, a, b)
		output_of_func.append(Phot_output)
	Phot_sum = sum(output_of_func)
	photons_sum_str = str(Phot_sum)
	a_str = str(a)
	b_str = str(b)
	file.write(a_str + "\t" + b_str + "\t" + photons_sum_str + "\n")
file.close()

