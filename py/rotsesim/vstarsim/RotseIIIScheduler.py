# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 20:12:46 2023

@author: George Pantelimon
"""

import pandas as pd
import ephem
import datetime
import Star
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
from zoneinfo import ZoneInfo
import AstronomicalCalculator

class RotseIIIScheduler:
    def ScheduleObservations(data: pd.DataFrame, startDate: datetime, endDate: datetime, star: Star, obsLocationLatitude, obsLocationLongitude, timeZone, elevationThreshold, verbose, obsLocationElevation : float):
        """
            This functions is scheduling observations based on how ROTSE III would. It is scheduling 4 observations at 1 minute
            intervals around the time of the highest elevation of the star (2 on each side of that time).
            And then it schedules another 4 observations 3 hours after the highest elevation time, also at 1 minute intervals.
            
            Parameters
            ----------
            data : pd.DataFrame
                The DataFrame containing all observations of the star (with all the observable properties) that survived previous
                filtration.
            
            obsLocationLatitude : str
                Latitude of the observation location
                
            obsLocationLongitude : str
                Longitude of the observation location
                
            star : Star
                The star object we are currently looking at
            
            start_date: datetime
                This application is simulating observing a star over a specific range of dates. start_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
                
            end_date: datetime
                This application is simulating observing a star over a specific range of dates. end_date is the left extremity of this range.
                This variable contains information about the current month, day, year, time, timezone.
                
            elevationThreshold : float
                All simulated data where elevation is below the threshold will be filtered out.
                
            timeZone : ZoneInfo
                We need this to apply it to the highest elevation time. When we perform operation with dates, we need both of them
                to have a timezone (offset-aware) or both of them to not have a timezone (offset-unaware). Since start_date has
                a timezone from the config file (usually UTC) I opted to attacch the same timezone to the highest elevation time
                since it makes sense to do so.
                
            elevationThreshold: float
                The elevation threshold in degrees that is used to filter out observations when the star's altitude is below a certain value
                above the horizon.
                
            verbose : bool
                Determines whether we plot some data or not. Comes from the config file.

            obsLocationElevation : float
                Elevation of the observation location
                
            Returns
            -------
            DataFrame
                A DataFrame that contains all the interpolated/extrapolated information baed on the data for each day. The dataframe
                containt the time in days on one column and the luminosity in ergs/cm^2/s in another column.
            
        """
        # obsTimes = list()
        data['CurrentTime'] = pd.to_datetime(data['CurrentTime'])  # Convert 'CurrentTime' column from string to datetime
        currentDate = data.iloc[0]['CurrentTime'] # Initialize currentDate with the date of the first simulated obvservation by MESA (left after we applied the other filters)
        lastDate = data.iloc[-1]['CurrentTime']   # Initialize lastDate with the date of the last simulated obvservation by MESA (left after we applied the other filters)
        obs = ephem.Observer() # initialize the observing location object
        obs.lat = str(obsLocationLatitude)
        obs.lon = str(obsLocationLongitude)
        obs.elevation = obsLocationElevation
        i = 0 # this counter is used for plots
        df = pd.DataFrame(columns=['star_age_day', 'luminosity']) # create a dataframe with 2 columns: the time in days after the start_date and the luminosity. We'll store the observations we schedule in here

        while currentDate < lastDate: # goes through all the observations from MESA that survived our previous filtering 
            obs.date = currentDate
            currentDateData = data[data['CurrentTime'].dt.date == currentDate.date()] # gets only the simulated data for the current day we are looking at

            if len(currentDateData) >= 2: # if there are more than 2 points so we can interpolate / extrapolate
                #create a star object at the coordinates of the star we are currently looking at (will be used to find elevation)    
                starEphemObject = ephem.FixedBody()
                starEphemObject._ra = ephem.degrees(str(star.getRA()))
                starEphemObject._dec = ephem.degrees(str(star.getDec()))
                start_time = obs.previous_setting(ephem.Sun()).datetime() ## calculate last sunset
                end_time = obs.next_rising(ephem.Sun()).datetime() ## calculate next sunrise
                t = start_time # initialize t as the time when the night started
                highest_elevation = -float('inf') # set the gihest elevation to a very small number

                # Finding the highest elevation
                while t <= end_time: # while it's night, calculate highest elevation and the time when it happens in that night
                    obs.date = t
                    starEphemObject.compute(obs)
                    elevation = ephem.degrees(starEphemObject.alt) # found elevation for current time t
                    if elevation > highest_elevation: # if elevation is higher than the previous maximum, replace value of maximum and store the time when that maximum was reached
                        highest_elevation = elevation
                        highest_elevation_time = t
                    t = t + datetime.timedelta(minutes=5)

                #cs = CubicSpline(currentDateData["star_age_day"], currentDateData["luminosity"], extrapolate = True)
                interpolationFunction = interp1d(currentDateData["star_age_day"], currentDateData["luminosity"], kind='linear', fill_value="extrapolate") #create the interpolation function based on the data for the current day
                highest_elevation_time = highest_elevation_time.replace(tzinfo=timeZone) # associate the timezone from the config file with the highest elevation time (necessary to perform calculations)

                # Calculate observation times
                def calc_obs_time(offset, base_time=highest_elevation_time, start_date=startDate): # based on the highest elevation time (called base_time here), we calculate the time in days after the start date for the offsets in the offest variable
                #example: if highest elevation time is 2003/1/5 5:00 AM, then we'll schedule observations at 4:58, 4:59, 5:01 and 5:02 and then 3 hours after at 7:58, 7:59, 8:01 and 8:02
                    return ((base_time + datetime.timedelta(minutes=offset)) - start_date).total_seconds() / 86400

                scheduledObservations = [calc_obs_time(offset) for offset in [-2, -1, 1, 2, 178, 179, 181, 182]] # creates an array with the indicated observation times in units of days after start date
                
                #Check if it's night when we schedule the observations
                is_night = lambda x: AstronomicalCalculator.AstronomicalCalculator.IsNight(obsLocationLatitude, obsLocationLongitude, startDate + datetime.timedelta(days=x), obsLocationElevation) # lambda function to check whether it is night when the observation is scheduled
                scheduledObservations = list(filter(is_night, scheduledObservations)) # apply the lambda function to get the 
                
                #Check if the star is above the horizon when we schedule the observations
                is_above_horizon = lambda x: AstronomicalCalculator.AstronomicalCalculator.CalculateElevation(obsLocationLatitude, obsLocationLongitude, startDate + datetime.timedelta(days=x), str(star.getRA()), str(star.getDec()), obsLocationElevation) > 10
                scheduledObservations = list(filter(is_above_horizon, scheduledObservations))
                
                #interpolate/extrapolate to get the luminosities for the scheduled observations
                calculatedLuminosities = interpolationFunction(scheduledObservations)

                #Just plotting the MESA data that was left after previous filtration (outside of this class) and the interpolated/extrapolated data
                if(verbose):
                    if i <= 180 and i>= 170:
                        fig, ax = plt.subplots(figsize=(6.5, 4))
                        ax.plot(currentDateData["star_age_day"], currentDateData["luminosity"], 'o', label='data')
                        ax.plot(scheduledObservations, calculatedLuminosities, 'o', label='interpolated')
                        ax.legend(loc='lower left', ncol=2)
                        ax.set_ylim(8e+17,12e+17)
                        plt.show()
                    
            #Set the currentDate to the next day after the one we finished processing
            currentDate = currentDate + datetime.timedelta(days=1)
            i = i+1 #day counter that we use as an indicator for what to plot. Irrelevant for the simulation itself.
            tempdf = pd.DataFrame({'star_age_day': scheduledObservations, 'luminosity': calculatedLuminosities})
            df = pd.concat([df, tempdf], ignore_index=True)

        return df

            

            
            
            
                
            
            
    