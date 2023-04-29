# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:51:09 2023

@author: George Pantelimon
"""

import pandas as pd
import ephem
import datetime
import numpy as np

class ElevationFilter:
    def Filter_By_Elevation(df: pd.DataFrame, latitude: str, longitude: str, star_ra: float, star_dec:float, start_date: datetime, end_date: datetime, elevationThreshold: float, obsLocationElevation: float):
        """
            This functions is calculating the elevation of the star at the moment of each observation in the input dataframe.
            Then, it removes all observations below a threshold.
            
            Parameters
            ----------
            df : pd.DataFrame
                The DataFrame containing all observations of the star (with all the observable properties)         
            
            latitude : str
                Latitude of the observation location
                
            longitude : str
                Longitude of the observation location
                
            star_ra : float
                Right Ascension of the star
                
            star_dec : float
                Declination of the star
            
            start_date: datetime
                This application is simulating observing a star over a specific range of dates. start_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
                
            end_date: datetime
                This application is simulating observing a star over a specific range of dates. end_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
                
            elevationThreshold : float
                All simulated data where elevation is below the threshold will be filtered out.
                
            obsLocationElevation : float
                Elevation of the observation location

            Returns
            -------
            DataFrame
                A modified DataFrame with all observations below the threshold removed and an extra column showing the elevation for
                each row ( row = observation).
            
        """
        
        ## Create the Observer object and assign coordinates of the observation location
        observer = ephem.Observer()
        observer.lat = latitude
        observer.lon = longitude
        observer.elevation = obsLocationElevation
        ## Create the star object and assign RA and DEC coordinates to the object
        star = ephem.FixedBody()
        star._ra = ephem.degrees(str(star_ra))
        star._dec = ephem.degrees(str(star_dec))
        
        ## Create a new column filled with nulls, for elevation values
        df['elevation'] = np.nan
        
        ## Go observation by observation
        for i, row in df.iterrows():
            ## Calculate the current time based on the start_date and the day offset from the simulation
            currentTime = start_date + datetime.timedelta(days=row['star_age_day']) 
            ## set the date at the observation location to be currentTime
            observer.date = currentTime # The currentTime is automatically converted to UTC (it knows how to do it because the start_date contains information about the timezone of the observation location)
            
            ## Compute coordinates of the star based on the observation location coordinates and currentTime
            star.compute(observer)
            ## Adding the elevation value to the elevation column for the current row
            df.at[i, 'elevation'] = np.degrees(star.alt)
        #Remove all observations below the threshold    
        #df.to_csv('outputAllElevations.csv', index=True) # was used only for testing
        df = df[df['elevation'] > elevationThreshold]    
        return df