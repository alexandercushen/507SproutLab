#!/usr/bin/env python3
import sys
import time
import os
import libcamera

os.environ["LIBCAMERA_LOG_LEVELS"] = "3"

from picamera2 import Picamera2

def main():
    # 1. Determine the filename
    # sys.argv[0] is the script name, sys.argv[1] is the first argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "image.jpg"

    # 2. Initialize and start Picamera2
    with Picamera2() as picam2:
        #picam2.set_property("Transform", "hv")
        #picam2.start()
    #ipicam2 = Picamera2()
        #picam2.configure(picam2.create_still_configuration())
        #picam2.start()

        # 1. Create a default configuration for a still image
        config = picam2.create_still_configuration()
        
        # 2. Set the transform in the configuration
        config["transform"] = libcamera.Transform(hflip=1, vflip=1)
        
        # 3. Apply the configuration and start
        picam2.configure(config)
        picam2.start()

        print(f"Capturing image to {filename}...")

        # 3. Give the sensor time to adjust exposure/white balance
        time.sleep(2)

        # 4. Capture and cleanup
        try:
            picam2.capture_file(filename)
            print("Done!")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            picam2.stop()

if __name__ == "__main__":
    main()
