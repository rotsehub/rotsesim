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
        stars = []
        for filename in os.listdir(excel_files_location):
            overlap = True
            f = os.path.join(excel_files_location, filename)

            df = pd.read_csv(f, header = 0, low_memory=False)
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
        ra = [star.getRA() for star in stars]
        dec = [star.getDec() for star in stars]
        plt.scatter(ra, dec)
        plt.xlabel("RA (deg)")
        plt.ylabel("Dec (deg)")
        plt.title("Simulated Sky")
        plt.show()