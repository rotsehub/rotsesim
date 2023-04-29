# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 22:43:00 2023

@author: Zachary McIlroy
"""

from datetime import datetime, timedelta
import requests


# This class serves to hold useful functions that may be used by other classes
class UtilityFunctions:
    
    # This method takes a datetime value and returns a value that has been rounded to the nearest hour
    def roundToHour(time : datetime):
        
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
        return (time.replace(second=0, microsecond=0, minute=0, hour=time.hour)
               +timedelta(hours=time.minute//30))
    
    # This method makes the API call and is built for the open-meteo API
    # Most of the parameters are self-explanatory, except for hourly, which is the specific columns of data specified in the config file that the user
    # wants to have returned by the API call
    def weatherAPI(startTime : datetime, endTime : datetime, baseURL: str, latitude: float, longitude: float, hourly: str):
        
        # Configure start and end times is ISO format
        startDate = startTime.date()
        endDate = endTime.date()
        
        # Build API Call
        ApiQuery = baseURL
        ApiQuery += 'latitude=' + str(latitude)
        ApiQuery += '&longitude=' + str(longitude)
        ApiQuery += '&start_date=' + str(startDate)
        ApiQuery += '&end_date=' + str(endDate)
        ApiQuery += '&hourly=' + hourly
        
        # Make API call and convert to json file
        r = requests.get(ApiQuery)
        data = r.json()
        
        return data