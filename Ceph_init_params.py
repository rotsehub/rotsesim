import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import scipy.integrate as integrate
import scipy.special as special
import random

L = float(input("Enter luminosity of star in solar luminosity units (Suggested values are between 500-45000): "))

Y = float((random.randint(25, 31))/100)

Z = float(np.random.normal(0.02, 0.005)) #AAW 04.12.20; made Z = variable number whose mean is 0.02 and std of 0.005, rather than a fixed value of Z = 0.02

X = float(1 - (Y + Z))

# original M-L relationship: L = float(10**(0.72 + 3.35*np.log10(M) + 1.36*np.log10(Y/0.28) - 0.34*np.log(Z/0.02)))

M = float(10**((1/3.35)*(np.log10(L) - 0.72 - 1.36*np.log10(Y/0.28) + 0.34*np.log10(Z/0.02))))

#original data: Teff_theoretical = float(-0.047135*L + 5915.741956)
# original data: sigma = 449.98

R_sol = float(696340000) #radius of sun in meters

R = R_sol*10**( (np.log10(M) + (np.random.normal(0.09, 0.03))) / (np.random.normal(0.48, 0.03)) )

sigma = 5.670374419*10**-8 #Joules*meters**-2*s**-1*K**-4

L_sol = 3.827*10**26 #luminosity of the sun in watts
L_star = L*L_sol

Teff_actual = float( (L_star/(sigma*4*np.pi*R**2))**0.25 )

#Teff_theoretical = float(-0.052*L + 6500)
#sigma = 300
#Teff_actual = float(np.random.normal(Teff_theoretical, sigma))

print( "M =", M )
print("L =", L )
print( "T_eff =", Teff_actual ) 
print( "X =", X )
print( "Z =", Z )
