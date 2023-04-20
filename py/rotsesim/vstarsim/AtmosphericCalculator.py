# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 17:57:39 2023

@author: Zachary McIlroy
"""

# import sys
# sys.path.append("..")

import Star
import configparser
import Wind
import Precipitation
import Transparency
import datetime
from datetime import timedelta
import UtilityFunctions


class AtmosphericCalculator:
    def __init__(self, stars : list[Star]):
        
        # Config file parser object
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # Config Values
        self.__longitude = float(config["ObservationLocationInfo"]["longitude"])
        self.__latitude = float(config["ObservationLocationInfo"]["latitude"])                            
        self.__startTime = datetime.datetime.strptime(config["SimulationDateRange"]["start_date"], '%m/%d/%Y %H:%M:%S')
        self.__windThreshold = float(config["FilteringParameters"]["windThreshold"])
        self.__precipThreshold = float(config["FilteringParameters"]["precipThreshold"])
        self.__baseURL = config["APICall"]["baseURL"]
        self.__hourly = config["APICall"]["hourly"]
        self.__field_center_ra = float(config["FieldOfViewData"]["field_center_ra"])
        self.__field_center_dec = float(config["FieldOfViewData"]["field_center_dec"])                            
        self.__fov = float(config["FieldOfViewData"]["fov"])
        self.__StarsArray = stars
        
        
        # This pulls the data from the first star. The start time and end time will be the same for all stars and that is all that is needed for the API call
        starData = self.__StarsArray[0].getData()
        self.__endTime = self.__startTime + timedelta(days=starData['star_age_day'].iloc[-1])
        
        # This is a future improvement so that the simulation can run on a start time and end time specified i nthe config file
        #self.__endTime = datetime.datetime.strptime(config["SimulationDateRange"]["end_date"], '%m/%d/%Y %H:%M:%S')
        
        #This is the call for the API method which is stored in the Utility Functions class
        self.__data = UtilityFunctions.UtilityFunctions.weatherAPI(self.__startTime, self.__endTime, self.__baseURL, self.__latitude, self.__longitude, self.__hourly) 
        
        # Method call for previous cloud generator method. See cloud generator class for more documentation
        #self.__cloudsForAllTime = CloudGenerator.CloudGenerator.generateCloudsForAllTime(self.__data, self.__field_center_ra, self.__field_center_dec, self.__fov)
        
        
        # For every star, the filters are run
        for star in self.__StarsArray:
            
            # Filters all observations where precipitation is above a certain threshold
            star.setData(Precipitation.Precipitation.precipTrimmer(star, self.__startTime, self.__precipThreshold, self.__data))
            print(star.getData())
            
            # Filters all observations where windspeed is above a certain threshold
            star.setData(Wind.Wind.windTrimmer(star, self.__startTime, self.__windThreshold, self.__data))
            print(star.getData())
            
            # Filters all observations where cloud coverage covers the star
            # Completes the transparency process for the first star and returns an adjustment list to increase efficiency
            if self.__StarsArray.index(star) == 0:
                returnedData, adjustmentList = Transparency.Transparency.firstTransparencyAdjustment(star, self.__startTime, self.__data, self.__field_center_ra, self.__field_center_dec, self.__fov)
                star.setData(returnedData)
            
            # All other stars are then evaluated using the adjustment list returned by the previous method
            else:
                star.setData(Transparency.Transparency.transparencyAdjuster(star, self.__startTime, self.__data, adjustmentList, self.__field_center_ra, self.__field_center_dec, self.__fov))
            print(star.getData()) 
    
    # Getter for the stars array that is stored within this object
    def getStarsArray(self):
       return self.__StarsArray
   
    
   