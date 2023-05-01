# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 21:52:31 2023

@author: George Pantelimon
"""


import pandas as pd


class Star:
    """
        This is the star class, whose object contains all information about the specific simulated star it represents.
        
        Attributes
        ----------
        self.__ra : float
            The RA of the star  
            
        self.__dec : float
            The Declination of the star  
            
        data: pd.DataFrame
            Contains all the data for a specific star. In the code we will work on this dataframe for the mast part (taking values and adding columns that show elevastion of the star at those times or if it is nighttime for example)
        
        originalData : pd.DataFrame
            The DataFrame containing all the original data from MESA in case we need this information at some point (requested by Dr. Kehoe)
            
        interpolatedData : pd.DataFrame
            Represnts a dataframe containing the output of the Scheduler. This is what will be used by the other components of the simulation (such as the atmpospheric simulator
            The data is assigned to this dataframe in the RotseIIIScheduler class.                                                                                                                                   )
    """
    def __init__(self, ra : float, dec : float, df : pd.DataFrame):
            self.__ra = ra
            self.__dec = dec
            self.__data = df
            self.__originalData = df
            self.__interpolatedData = pd.DataFrame()
            
    def getRA(self):
       return self.__ra
         
    def setRA(self, newRA):
       self.__ra = newRA
   
    def getDec(self):
       return self.__dec
         
    def setDec(self, newDec):
       self.__dec = newDec    
    
    def getData(self):
        return self.__data
         
    def setData(self, newData):
       self.__data = newData  
     
    def getOriginalData(self):
       return self.__originalData
   
    def getInterpolatedData(self):
        return self.__interpolatedData
         
    def setInterpolatedData(self, newData):
       self.__interpolatedData = newData  


    def setOriginalData(self, newOriginalData): ## this will not be used to change the original data from the star simulation but to add columns that show what was filtered out in the modified dataset
        """
            This will not be used to change the original data from the star simulation but to add columns that show what 
            was filtered out in the modified dataset.
            
            Parameters
            ----------
            newOriginalData : pd.DataFrame
                The Original data but with added new columns that show what data was filtered out or freshly calculated info (elevation for example)         
            
        """
        self.__OriginalData = newOriginalData           