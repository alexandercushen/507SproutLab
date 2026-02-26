#!/usr/bin/env python3
'''
This is the scheduler and controller for any analysis or file manipulation being done behind the scenes.
This creates the plots, checks the homepage images, and any other sophisticated features.
It runs 1 min after the app.py scheduler, so at 1 and 31 mins past tbe hour.
Perhaps in the future this will be automatically called by app.py, but for now I want dev control.
There should also be a button on the "analysis" page that manually refreshes everything
Lightweight functions can live here, but any detailed analysis will be stored as individual scripts in scripts/
'''

def check_homepage_image_brightness():

