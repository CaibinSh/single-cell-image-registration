#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 11:31:20 2018

@author: csheng
"""

# test imgreg

mydir = '/Users/csheng/Documents/python/imgreg/example/'

total_time_point = 2;
Posperplate = 1;
total_position = 2

import imgreg
imgreg.align(mydir,total_time_point,Posperplate,total_position)

# folders 'calibrated' and 'calibrate3' with cropped images should appear in mydir