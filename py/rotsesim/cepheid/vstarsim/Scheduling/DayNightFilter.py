# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:03:01 2023

@author: gigic
"""

import pandas as pd
import ephem
import datetime
from zoneinfo import ZoneInfo
import configparser
import numpy as np

class DayNightFilter:
    def filter_night_entries(df, start_date, end_date, latitude, longitude):
        """
            This functions is calculating the elevation of the star at the moment of each observation in the input dataframe.
            Then, it removes all observations below a threshold.
            
            Parameters
            ----------
            df : pd.DataFrame
                The DataFrame containing all observations of the star (with all the observable properties)   
                
            start_date: datetime
                This application is simulating observing a star over a specific range of dates. start_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
                
            end_date: datetime
                This application is simulating observing a star over a specific range of dates. end_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
            
            latitude : str
                Latitude of the observation location
                
            longitude : str
                Longitude of the observation location
                

            Returns
            -------
            DataFrame
                A modified DataFrame with all daytime observations removed and an extra column that says True if the current observation
                is during nighttime (which wil be true for all rows since we are removing all daytime observations)
            
        """
        
        ## Create the Observer object and assign coordinates of the observation location
        observer = ephem.Observer()
        observer.lat = latitude
        observer.lon = longitude
        
        ## Create a new column containing a boolean that shows whether it is day or night. Assign False initially.
        df['night_time'] = False
        df['CurrentTime'] = np.nan
        ## Go observation by observation
        for i, row in df.iterrows():
            ## Calculate the current time based on the start_date and the day offset from the simulation
            currentTime = start_date + datetime.timedelta(days=row['star_age_day'])
            df.at[i, 'CurrentTime'] = currentTime
            ## set the date at the observation location to be currentTime
            observer.date = currentTime # The currentTime is automatically converted to UTC (it knows how to do it because the start_date contains information about the timezone of the observation location. 
            # I would recommend just setting timezone to UTC directly in the config since this is what astronomers use anyway.

            ## Set the night_time column value equal to true for the current row if the previous_rising is NOT later than the previous_setting
            ## We had to resort to this condition because checking whether the current time is between the previous_setting and next_rising
            ## would always return true.
            if not(observer.previous_rising(ephem.Sun()) > observer.previous_setting(ephem.Sun())):            
                df.at[i, 'night_time'] = True
                # print(currentTime)
                
        ## Keep only the nighttime observations     
        df = df[df['night_time'] == True]
        return df