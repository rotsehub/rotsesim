# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 13:25:24 2023

@author: Zachary McIlroy
"""

# import sys
# sys.path.append("..")

from datetime import datetime, timedelta
import pandas as pd
import Star
import UtilityFunctions

class Precipitation:
    
    # This method takes the API dataset as an input and compares the precip value at each star observation time to the precip threshold value from the config
    # file
    def precipTrimmer(star : Star, startTime: datetime, precipThreshold: float, data: pd.DataFrame):
        starData = star.getData()
        
        # This for loop iterates through every row in starData that is left after previous filters have been applied
        for index, row in starData.iterrows():
            
            # This will be switched out for UTC time given by George. Need to work with him next week
            currentDate = startTime + timedelta(days=row['star_age_day'])
            roundedDate = UtilityFunctions.UtilityFunctions.roundToHour(currentDate)
            
            # This index is the number of hours from the startTime's day at the 0th hour. For example, the fourth day at 3 PM would be 3*24 + 15 = 87
            # This is used as the API data is returned with one row for every hour and this provides an efficient way to retrieve the API data rather
            # than comparing the datetime values every time
            hourIndex = (roundedDate.date() - startTime.date()).days*24 + roundedDate.hour
            
            # If the precipitation at this time is above the threshold value from the config file, the observation is dropped
            if float(data['hourly']['precipitation'][hourIndex]) >= precipThreshold:
                starData.drop(index, axis = 0, inplace = True)
        return starData