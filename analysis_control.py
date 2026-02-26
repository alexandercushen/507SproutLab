#!/usr/bin/env python3
'''
This is the scheduler and controller for any analysis or file manipulation being done behind the scenes.
This creates the plots, checks the homepage images, and any other sophisticated features.
It runs 1 min after the app.py scheduler, so at 1 and 31 mins past tbe hour.
Perhaps in the future this will be automatically called by app.py, but for now I want dev control.
There should also be a button on the "analysis" page that manually refreshes everything
Lightweight functions can live here, but any detailed analysis will be stored as individual scripts in scripts/
'''

import numpy as np
from PIL import Image
import os
import subprocess
#import matplotlib.pyplot as plt
from scripts.utils import get_matching_files

def check_homepage_image_brightness(threshold = 50):
    '''
    This function checks the current homepage image (static/homepage.jpg) to see if the lights are on.
    If so, it does nothing.
    If not, it deletes the most recent image taken in data/images (which SHOULD be the same) image,
    and replaces homepage.jpg with the prior image. 
    It runs recursively until getting back to the last lit image.
    If it has overwritten a file, it will add a moon decal to the image.
    This will probably mess with how homepage.html identifies the time that image was taken...
    We will address this using static/homepage_metadata.json:
        
    import json

    # When you pick a "good" image
    original_timestamp = "Feb 25, 08:00 PM" # Get this from the filename or its mtime
    
    metadata = {"original_time": original_timestamp}
    with open('static/homepage_metadata.json', 'w') as f:
        json.dump(metadata, f)
        
    ...
    in app.py:
        
    def get_homepage_image_time():
    meta_path = os.path.join('static', 'homepage_metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            data = json.load(f)
            return data.get('original_time')
    return "No image found"

    '''
    
    image_path = os.path.join('static', 'homepage.jpg')
    image_path = os.path.join('data/images/', 'img_20260221_234937.jpg')
    
    if os.path.exists(image_path):
        
        # Read image
        img = Image.open(image_path)
        img_array = np.array(img)
    
        # 3. Convert back to an Image object (after you edit the array)
        # edited_img = Image.fromarray(img_array)
        # edited_img.save('static/homepage.jpg')
    
    else:
        print("ERROR: static/homepage.jpg not found.")
        return
    
    # Compute brightness
    avg_brightness = np.mean(img_array)
    
    if avg_brightness>threshold:
        print("Current homepage image is well lit, no action necessary.")
        return
    
    else:
        print("Current homepage image has the lights off! Fixing that...")
        
        images = get_matching_files("data/images", "*.jpg")
        current_image = images[-1]
        prior_image = images[-2]
        
        subprocess.run(['cp', prior_image, 'static/homepage.jpg'], check=True)
        subprocess.run(['rm -rf', current_image], check=True)
        
        # Run again to make sure this one is accepted
        check_homepage_image_brightness()
        
        return

def main():
    
    check_homepage_image_brightness()
    
if __name__ == "__main__":
    main()
    