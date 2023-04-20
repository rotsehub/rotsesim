# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 16:42:51 2023

@author: Zachary McIlroy
"""

# import sys
# sys.path.append("..")

from datetime import datetime, timedelta
import pandas as pd
import Star
import UtilityFunctions
import CloudGenerator

class Transparency:
    
    
    # This method does the transparency adjustment for the first star. This is done in order to increase accuracy and efficiency as new clouds should not
    # be generated for every star if they are within the same sky
    def firstTransparencyAdjustment(star : Star, startTime: datetime, data: pd.DataFrame, field_center_ra : float, field_center_dec : float, fov : float):

        starData = star.getData()
        
        # This list will be the parameter that is passed to the other adjustment method and will hold the time and what to do for any star in the 
        # current FOV at that time
        adjustmentList = pd.DataFrame(columns = ['hourIndex', 'adjustment'])
        adjustmentList.set_index('hourIndex', inplace=True)
        
        # This for loop iterates through every row in starData that is left after previous filters have been applied
        for index, row in starData.iterrows():
            
            # This will be switched out for UTC time given by George. Need to work with him next week
            currentDate = startTime + timedelta(days=row['star_age_day'])
            roundedDate = UtilityFunctions.UtilityFunctions.roundToHour(currentDate)
            
            # This index is the number of hours from the startTime's day at the 0th hour. For example, the fourth day at 3 PM would be 3*24 + 15 = 87
            # This is used as the API data is returned with one row for every hour and this provides an efficient way to retrieve the API data rather
            # than comparing the datetime values every time
            hourIndex = (roundedDate.date() - startTime.date()).days*24 + roundedDate.hour
                
            weatherCode = float(data['hourly']['weathercode'][hourIndex])
            
            # Boolean to check if the FOV is covered completely by clouds
            coveredFov = False
            
            # Boolean to check for partial coverage
            partialCoverage = False
            
            # This if statement takes weather codes that are known to be mtched with high cloud coverage or a cloud coverage over 80% and drops the
            # star's row at this time and adds the 'drop' value for adjustment to the adjustment list
            if (weatherCode >= 52 and weatherCode != 71) or weatherCode in [49,47,45,43,39,37,35,34,33,29,28,27,26,25,17,16,12,9,8,4,3] or float(data['hourly']['cloudcover'][hourIndex]) > 80:
                starData.drop(index, axis = 0, inplace = True)
                
                # A new dictionary is made and then converted to a dataframe so that the concat() function can be used later
                newRow = {'hourIndex': hourIndex, 'adjustment': 'drop'}
                newRowDF = pd.DataFrame([newRow])
                
            # This else statement covers the weathercode 0 which is associated with clear skies
            elif weatherCode == 0:
                
                # A new dictionary is made and then converted to a dataframe so that the concat() function can be used later
                newRow = {'hourIndex': hourIndex, 'adjustment': 'do nothing'}
                newRowDF = pd.DataFrame([newRow])
                
            # If none of the above conditions are true, then clouds are at this point generated
            else:
                clouds = CloudGenerator.CloudGenerator.generateClouds(float(data['hourly']['cloudcover'][hourIndex]))
                
                # This takes the center of the fov and finds the four x and y values that make up its rectangular shape
                fovPoints = [field_center_ra - fov/2, field_center_dec - fov/2, field_center_ra + fov/2, field_center_dec + fov/2]
                
                # This checks if the fov is not covered by clouds, fully covered, or partially covered
                for cloud in clouds:
                    cloudPoints = cloud.getPoints()  
                    if cloudPoints[0]>=fovPoints[2] or cloudPoints[2]<=fovPoints[0] or cloudPoints[3]<=fovPoints[1] or cloudPoints[1]>=fovPoints[3]:
                        pass
                    elif fovPoints[0] >= cloudPoints[0] and fovPoints[1] >= cloudPoints[1] and fovPoints[2] <= cloudPoints[2] and fovPoints[3] <= cloudPoints[3]:
                        coveredFov = True
                        break
                    else:
                        partialCoverage = True
                
                # This if/else block updates the adjustment list based on the fov coverage
                # FOV completely covered
                if coveredFov:
                    starData.drop(index, axis = 0, inplace = True)
                    newRow = {'hourIndex': hourIndex, 'adjustment': 'drop'}
                    newRowDF = pd.DataFrame([newRow])
                    
                # FOV completely clear
                elif not coveredFov and not partialCoverage:
                    newRow = {'hourIndex': hourIndex, 'adjustment': 'do nothing'}
                    newRowDF = pd.DataFrame([newRow])
                    
                # FOV partially covered. In this case, the star will now be checked against each cloud to see if any of them cover it
                else:
                    starRA = star.getRA()
                    starDec = star.getDec()
                    
                    # Boolean to keep track of if the star is covered by any cloud
                    starCovered = False
                    for cloud in clouds:
                        cloudPoints = cloud.getPoints()
                        if starRA >= cloudPoints[0] and starRA <= cloudPoints[2] and starDec >= cloudPoints[1] and starDec <= cloudPoints[3]:
                            starData.drop(index, axis = 0, inplace = True)
                            starCovered = True
                            break
                        
                    # If the star is not covered, its luminosity value is adjusted to represent the state of the sky. If 70% of the sky is covered, it is 
                    # likely that 70% of the star's light will not get to the ROTSE telescope even if it is not covered by any cloud
                    if not starCovered:
                        row['luminosity'] *= 1 - (float(data['hourly']['cloudcover'][hourIndex]))/100
                        
                        # Flux will also be adjusted for this value, the proper column name is just needed
                        #row['flux'] *= (float(data['hourly']['cloudcover'][hourIndex]))/100
                    
                    # This is the code that would reference the separate method that was created to reduce repeated code. However, it is untested
                    #starData = Transparency.starAdjustment(star, data, adjustmentList, hourIndex, index, row)
                    
                    # The adjustment list is updated with the cloud array so that any additional stars in the FIV can then be evaluated against the same
                    # cloud set
                    newRow = {'hourIndex': hourIndex, 'adjustment': clouds}
                    newRowDF = pd.DataFrame([newRow])
                    
            # Adjustment list is then updated with the newest row
            pd.concat([adjustmentList, newRowDF], ignore_index=True)
        return starData, adjustmentList
    
    
    
    
    
    
    # This method is then used for any additional star after the first and takes the adjustment list as an input
    def transparencyAdjuster(star : Star, startTime : datetime, data : pd.DataFrame, adjustmentList : pd.DataFrame, field_center_ra : float, field_center_dec : float, fov : float):
        starData = star.getData()
        
        # This for loop iterates through every row in starData that is left after previous filters have been applied
        for index, row in starData.iterrows():
            
            # This will be switched out for UTC time given by George. Need to work with him next week
            currentDate = startTime + timedelta(days=row['star_age_day'])
            roundedDate = UtilityFunctions.UtilityFunctions.roundToHour(currentDate)
            
            # Refer to hour index documentation above
            hourIndex = (roundedDate.date() - startTime.date()).days*24 + roundedDate.hour
                
                
            # This if/else block performs actions based on whatever is in the adjustment list
            if adjustmentList['adjustment'][hourIndex] == 'drop':
                starData.drop(index, axis = 0, inplace = True)
            elif adjustmentList['adjustment'][hourIndex] == 'do nothing':
                pass
            
            # If the FOV is not completely clear or covered, each cloud is evaluated against the star's location to see if any of them cover it
            else:
                starRA = star.getRA()
                starDec = star.getDec()
                
                # Boolean to keep track of if the star is covered by any cloud
                starCovered = False
                for cloud in adjustmentList['adjustment'][hourIndex]:
                    cloudPoints = cloud.getPoints()
                    if starRA >= cloudPoints[0] and starRA <= cloudPoints[2] and starDec >= cloudPoints[1] and starDec <= cloudPoints[3]:
                        starData.drop(index, axis = 0, inplace = True)
                        starCovered = True
                        break
                    
                # If the star is not covered, its luminosity value is adjusted to represent the state of the sky. If 70% of the sky is covered, it is 
                # likely that 70% of the star's light will not get to the ROTSE telescope even if it is not covered by any cloud
                if not starCovered:
                    row['luminosity'] *= (float(data['hourly']['cloudcover'][hourIndex]))/100
                    
                    # Flux will also be adjusted for this value, the proper column name is just needed
                    #row['flux'] *= (float(data['hourly']['cloudcover'][hourIndex]))/100
                    
                # This is the code that would reference the separate method that was created to reduce repeated code. However, it is untested
                #starData = Transparency.starAdjustment(star, data, adjustmentList, hourIndex, index, row)
                
        return starData
    
    
    # Attempt to move redundant code to different method in order that there would not be code duplication. May revisit at some point
    # def starAdjustment(star : Star, data : pd.DataFrame, adjustmentList : pd.DataFrame, hourIndex : int, index : int, row : pd.Series):
    #     starData = star.getData()
    #     starRA = star.getRA()
    #     starDec = star.getDec()
    #     starCovered = False
    #     for cloud in adjustmentList['adjustment'][hourIndex]:
    #         cloudPoints = cloud.getPoints()
    #         if starRA >= cloudPoints[0] and starRA <= cloudPoints[2] and starDec >= cloudPoints[1] and starDec <= cloudPoints[3]:
    #             starData.drop(index, axis = 0, inplace = True)
    #             starCovered = True
    #             break
    #     if not starCovered:
    #         row['luminosity'] *= (float(data['hourly']['cloudcover'][hourIndex]))/100
    #         #row['flux'] *= (float(data['hourly']['cloudcover'][hourIndex]))/100
        
    #     return starData