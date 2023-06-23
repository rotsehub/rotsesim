# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 17:57:39 2023

@author: Zachary McIlroy
"""

import configparser
import Star
import Wind
import Precipitation
import Transparency
import datetime
from datetime import timedelta
import UtilityFunctions
import matplotlib.pyplot as plt
from zoneinfo import ZoneInfo

class AtmosphericCalculator:
    def __init__(self, stars : list[Star]):
        
        # Config file parser object
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        ## Program parameters
        if(config["ProgramParameters"]["verbose"] == "True"):
            self.__verbose = True 
        else:
            self.__verbose = False
        
        # Config Values
        self.__longitude = float(config["ObservationLocationInfo"]["longitude"])
        self.__latitude = float(config["ObservationLocationInfo"]["latitude"])                            
        self.__startTime = datetime.datetime.strptime(config["SimulationDateRange"]["start_date"], '%m/%d/%Y %H:%M:%S')
        self.__windThreshold = float(config["FilteringParameters"]["windThreshold"])
        self.__precipThreshold = float(config["FilteringParameters"]["precipThreshold"])
        self.__maxCloudCoverage = float(config["FilteringParameters"]["maxCloudCoverage"])
        self.__firstCloudSizePercentage = float(config["CloudGenerationParameters"]["firstCloudSizePercentage"])
        self.__baseURL = config["APICall"]["baseURL"]
        self.__hourly = config["APICall"]["hourly"]
        self.__field_center_ra = float(config["FieldOfViewData"]["field_center_ra"])
        self.__field_center_dec = float(config["FieldOfViewData"]["field_center_dec"])                            
        self.__fov = float(config["FieldOfViewData"]["fov"])
        self.__StarsArray = stars
        self.__obsLocationTimeZone = config["ObservationLocationInfo"]["timeZone"]
        
        
        # This pulls the data from the first star. The start time and end time will be the same for all stars and that is all that is needed for the API call
        starData = self.__StarsArray[0].getInterpolatedData()
        self.__endTime = self.__startTime + timedelta(days=starData['star_age_day'].iloc[-1])
        
        # This is a future improvement so that the simulation can run on a start time and end time specified i nthe config file
        #self.__endTime = datetime.datetime.strptime(config["SimulationDateRange"]["end_date"], '%m/%d/%Y %H:%M:%S')
        
        #This is the call for the API method which is stored in the Utility Functions class
        self.__data = UtilityFunctions.UtilityFunctions.weatherAPI(self.__startTime, self.__endTime, self.__baseURL, self.__latitude, self.__longitude, self.__hourly) 
        
        # Method call for previous cloud generator method. See cloud generator class for more documentation
        #self.__cloudsForAllTime = CloudGenerator.CloudGenerator.generateCloudsForAllTime(self.__data, self.__field_center_ra, self.__field_center_dec, self.__fov)
        
        timeZone = ZoneInfo(self.__obsLocationTimeZone)
        self.__startTime = self.__startTime.replace(tzinfo=timeZone)
        #self.__end_date = self.__end_date.replace(tzinfo=timeZone)
        
        # For every star, the filters are run
        for star in self.__StarsArray:
            
            print(star.getInterpolatedData())
            plt.style.use('dark_background')
            print('start of atmospheric code')
            
            if(self.__verbose):
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('Before Precipitation')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
            
            # Filters all observations where precipitation is above a certain threshold
            star.setInterpolatedData(Precipitation.Precipitation.precipTrimmer(star, self.__startTime, self.__precipThreshold, self.__data))
            print(star.getInterpolatedData())
            
            if(self.__verbose):
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('After Precipitation')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
                
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('Before Wind')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
            
            # Filters all observations where windspeed is above a certain threshold
            star.setInterpolatedData(Wind.Wind.windTrimmer(star, self.__startTime, self.__windThreshold, self.__data))
            print(star.getInterpolatedData())
            
            if(self.__verbose):
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('After Wind')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
                
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('Before Cloud Coverage/Transparency')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
            
            # Filters all observations where cloud coverage covers the star
            # Completes the transparency process for the first star and returns an adjustment list to increase efficiency
            if self.__StarsArray.index(star) == 0:
                returnedData, adjustmentList = Transparency.Transparency.firstTransparencyAdjustment(star, self.__startTime, self.__data, self.__field_center_ra, self.__field_center_dec, self.__fov, self.__maxCloudCoverage, self.__firstCloudSizePercentage)
                star.setInterpolatedData(returnedData)
            
            # All other stars are then evaluated using the adjustment list returned by the previous method
            else:
                star.setInterpolatedData(Transparency.Transparency.transparencyAdjuster(star, self.__startTime, self.__data, adjustmentList, self.__field_center_ra, self.__field_center_dec, self.__fov))
            print(star.getInterpolatedData()) 
            
            if(self.__verbose):
                filteredData = star.getInterpolatedData()
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_xlim(2150,2200)
                ax.set_title('After Cloud Coverage/Transparency')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
                
                fig, ax = plt.subplots(figsize=(6.5, 4))
                ax.plot(filteredData["star_age_day"], filteredData["luminosity"], 'o', label='data', color='orange')
                ax.set_ylabel('Luminosity')
                ax.set_xlabel('Star Age (Days)')
                plt.show()
            #Output to a csv file
            star.getInterpolatedData().to_csv('AtmosphericOutput.csv', index=True)
            
    # Getter for the stars array that is stored within this object
    def getStarsArray(self):
       return self.__StarsArray
   
    
   