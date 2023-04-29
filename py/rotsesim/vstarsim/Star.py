# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 21:52:31 2023

@author: gigic
"""


import pandas as pd


class Star:
    def __init__(self, ra : float, dec : float, df : pd.DataFrame):
            self.__ra = ra
            self.__dec = dec
            self.__data = df
            self.__originalData = df

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