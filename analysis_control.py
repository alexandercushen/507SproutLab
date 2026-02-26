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
from PIL import Image, ImageDraw
import os
import subprocess
import matplotlib.pyplot as plt
from scripts.utils import get_matching_files


''' -------SUPPORTING SCRIPTS --------'''
def add_moon_decal(img):
    
    draw = ImageDraw.Draw(img)
    
    # 2. Position and Size
    x, y = 2000, 80
    size = 400
    
    # 3. DEFINE COLORS
    navy_blue = (20, 24, 54)      # The dark blue background disk
    moon_yellow = (255, 255, 200) # The pale yellow crescent
    
    # 4. DRAW THE BACKGROUND DISK
    # This is the solid dark blue circle that stays behind the moon
    draw.ellipse([x, y, x + size, y + size], fill=navy_blue)
    
    # 5. CREATE THE CRESCENT MASK
    # We create a temporary grayscale image (L) to act as a stencil
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    
    # The 'Visible' part of the stencil (White)
    mask_draw.ellipse([0, 0, size, size], fill=255)
    
    # The 'Bite' taken out of the stencil (Black)
    # Moving it right (size * 0.3) creates the crescent
    bite_offset = int(size * 0.3)
    mask_draw.ellipse([bite_offset, -5, size + bite_offset, size + 5], fill=0)
    
    # 6. APPLY THE YELLOW CRESCENT
    # Create a solid yellow square the size of the moon
    yellow_layer = Image.new('RGB', (size, size), moon_yellow)
    
    # Paste the yellow layer onto the main image at (x, y) 
    # BUT only through the mask holes
    img.paste(yellow_layer, (x, y), mask)
    
    return img

''' ------ MAIN ANALYSIS SCRIPTS -------'''

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
    #image_path = os.path.join('data/images/', 'img_20260221_234937.jpg')
    
    if os.path.exists(image_path):
        
        # Read image
        img = Image.open(image_path)
        img_array = np.array(img)
    
    else:
        print("ERROR: static/homepage.jpg not found.")
        return
    
    # Compute brightness
    avg_brightness = np.mean(img_array)
    
    # Decide what to do
    if avg_brightness>threshold:
        print("Current homepage image is well lit, no action necessary.")
        return
    
    else:
        print("Current homepage image has the lights off! Fixing that...")
        
        files = get_matching_files("data/images", "*.jpg")
        current_image = files[-1]
        prior_image = files[-2]
        
        # Open and edit image
        img = Image.open(prior_image)
        img = add_moon_decal(img)
        
        # Save and delete
        img.save('static/homepage.jpg')
        subprocess.run(['rm -rf', current_image], check=True)
        
        # Run again to make sure this one is accepted
        check_homepage_image_brightness()
        
        return

def main():
    
    check_homepage_image_brightness()
    
if __name__ == "__main__":
    main()
    