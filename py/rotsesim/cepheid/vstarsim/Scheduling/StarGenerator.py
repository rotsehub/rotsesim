# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 21:46:59 2023

@author: gigic
"""
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import Star
import os

class StarGenerator:
    def GenerateStars(field_center_ra: float, field_center_dec: float, fov: float, min_star_separation: float, excel_files_location: str, instaSolarLuminosity: float):
        """
            This functions is getting all csv files in a folder specified in the config file and then for each excel file (one excel file = one star)
            it reads the data, assigns coordinates to the star in the field of view and then creats a star object that is added to the array it returns.
            
            Parameters
            ----------
            field_center_ra : float
                The RA of the field center in degrees. This value comes from the config file
                
            field_center_dec: float
                The DEC of the field center in degrees. This value comes from the config file
                
            fov: float
                The size of the fov in degrees. This value comes from the config file
            
            min_star_separation: float
                The minimum separation between stars in degrees. This value comes from the config file
                
            excel_files_location: str
                Location of the excel files that contains the simulated data. This value comes from the config file
                
            instaSolarLuminosity: float
                A constant that represents the instant solar luminosity. This is used to convert the luminosity given my MESA to solar units.
            
            Returns
            -------
            Array of stars
                An array of star objects that contain the simulated data and the generated RA and DEC coordinates of the star.
            
        """
        stars = []
    
        for filename in os.listdir(excel_files_location): # go through each csv file (star)
            overlap = True
            f = os.path.join(excel_files_location, filename) # f is the full path that refers to the current file we are looking at

            df = pd.read_csv(f, header = 0, low_memory=False) # read the data from the csv
            df['luminosity'] = df['luminosity'] * instaSolarLuminosity ## convert the luminosity column to solar units
            df = df.dropna() ## remove empty rows
            while overlap == True: ## generate new coordinates until they don't overalp with other stars
                overlap = False
                radius = np.sqrt(random.uniform(0, (fov/2)**2)) ## picks a random radius within the fov
                azimuth = random.uniform(0, 2*np.pi) ## picks a random angle withing the fov
                
                
                # Convert polar coordinates to equatorial coordinates
                ra = field_center_ra + radius * np.cos(azimuth) ## get the ra from the radius and azimuth
                dec = field_center_dec + radius * np.sin(azimuth) ## get the dec from the radius and azimuth
                
                # Check if the new star overlaps with any existing stars
                for existing_star in stars:
                    separation = np.sqrt((existing_star.getRA() - ra)**2 + (existing_star.getDec() - dec)**2)
                    if separation < min_star_separation:
                        overlap = True ## set to true if the star overlap with other stars so that we know to pick new coordinates
                        break
                
                # If there is no overlap, add the new star to the list
                if not overlap:
                    stars.append(Star.Star(ra, dec, df))
        
        return stars
    
    def plot_stars(stars: list[Star]):
        """
            This functions is getting all csv files in a folder specified in the config file and then for each excel file (one excel file = one star)
            it reads the data, assigns coordinates to the star in the field of view and then creats a star object that is added to the array it returns.
            
            Parameters
            ----------
            stars: list[Star] 
                A list containing all star objects that were generated (the number should be equal to the number of inpu csv files).   
            
            Returns
            -------
                Nothing. It will jost plot the stars based on their RA and DEC coordinates in the simulated fov.         
        """
        ra = [star.getRA() for star in stars]
        dec = [star.getDec() for star in stars]
        plt.scatter(ra, dec)
        plt.xlabel("RA (deg)")
        plt.ylabel("Dec (deg)")
        plt.title("Simulated Sky")
        plt.show()