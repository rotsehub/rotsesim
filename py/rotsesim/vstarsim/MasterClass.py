# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 21:04:57 2023

@author: Zachary McIlroy
"""

import ObservationTimes
import AtmosphericCalculator
import pandas as pd
import matplotlib.pyplot as plt


# This class serves to increase abstraction of the program so that only the top level of code need be interacted with for it to run
class MasterClass:
    def __init__(self):
        # This object serves to call the observations times class which filters on day/night and elevation
        observationTimesObj = ObservationTimes.ObservationTimes()
        starsFilteredOnObservation = observationTimesObj.getStarsArray()

        
        # This object serves to call the atmospheric calculator class which filters on precipitation, windspeed, and cloud coverage
        atmosphericCalculatorObj = AtmosphericCalculator.AtmosphericCalculator(starsFilteredOnObservation)
        starsFilteredOnAtmosphere = atmosphericCalculatorObj.getStarsArray()
        
        
        # Plotting parameters
        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True
        headers = ['star_age_day', 'luminosity'] 
    
        # Dataframe consisting of the original data
        orginalData = pd.read_csv('OutputWithDigitsGood1234.csv', header = 0, low_memory=False)
        
    
        # Plot of original data
        orgincalDataPlot = orginalData.plot.line(x = 'star_age_day', y = 'luminosity', marker = 'o')
        #orgincalDataPlot.set_xlim(2150,2230)
        
        
MasterClassObject = MasterClass()  


