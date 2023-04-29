# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 18:49:27 2023

@author: Zachary McIlroy
"""

# The cloud object is very simple and only contains one attribute: a list of two x coordinates and two y coordinates that create the rectangular shape
# of the cloud
class Cloud:
    def __init__(self, points : [float]):
            self.__points = points

    def getPoints(self):
       return self.__points
         
    def setPoints(self, newPoints):
       self.__points = newPoints