# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 19:21:18 2023

@author: George Pantelimon
"""


import ephem
import datetime
import numpy as np


class AstronomicalCalculator:
    def IsNight(latitude: str, longitude: str, currentTime: datetime, obsLocationElevation: float):
        """
            This functions calculates wheteher it is night time based on an onbservation location and the currentTime.
            
            Parameters
            ----------               
            latitude : str
                Latitude of the observation location
                
            longitude : str
                Longitude of the observation location
                
            currentTime : datetime
                The current date and time at the observation location (includes the timezone from the config file which is usually UTC)

            obsLocationElevation : float
                Elevation of the observation location
                
            Returns
            -------
            Bool
                True if it is night time and False if it is day time.            
        """
        observer = ephem.Observer()
        observer.lat = latitude
        observer.lon = longitude
        observer.date = currentTime
        observer.elevation = obsLocationElevation
        if not(observer.previous_rising(ephem.Sun()) > observer.previous_setting(ephem.Sun())):            
            return True
        else: 
            return False
        
    def CalculateElevation(latitude: str, longitude: str, currentTime: datetime, star_ra: str, star_dec: str, obsLocationElevation : float):
        """
            This functions calculates the elevation of a star in degrees at some time given as input.
            
            Parameters
            ----------               
            latitude : str
                Latitude of the observation location
                
            longitude : str
                Longitude of the observation location
                
            currentTime : datetime
                The current date and time at the observation location (includes the timezone from the config file which is usually UTC)
                
            star_ra : str
                The RA of the star.
                
            star_dec : str
                The Declination of the star

            obsLocationElevation : float
                Elevation of the observation location
                
            Returns
            -------
            float
                Returns the elevation of the star in degrees
            
        """
        observer = ephem.Observer()
        observer.lat = latitude
        observer.lon = longitude
        observer.date = currentTime
        observer.elevation = obsLocationElevation
        star = ephem.FixedBody()
        star._ra = ephem.degrees(str(star_ra))
        star._dec = ephem.degrees(str(star_dec))
        star.compute(observer)
        return np.degrees(star.alt)
        
        