#!/usr/bin/env python3

import adafruit_dht
import board
import os
from datetime import datetime
import time
import csv

# If your sensor is on GPIO 4:
dhtDevice = adafruit_dht.DHT11(board.D14)

#try:
#    temp_c = dhtDevice.temperature
#    humidity = dhtDevice.humidity
#    print(f"Temp: {temp_c}C, Humidity: {humidity}%")
#except RuntimeError as error:
    # Errors are common with DHT sensors, just keep trying
#    print(error.args[0])

def get_reading():
    try:
        # Attempt to read data
        temp_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        
        if humidity is not None and temp_c is not None:
            print(f"Temp: {temp_c:.1f}C, Humidity: {humidity}%")
            save_to_log(temp_c, humidity)

    except RuntimeError as error:
        # DHT sensors are notoriously glitchy; just ignore common read errors
        pass 
    except Exception as e:
        # Only print serious errors
        if "message queue" not in str(e):
            print(f"Unexpected error: {e}")
    finally:
        # This is the "Magic" part: 
        # It closes the pulseio process so the message queue doesn't get lost
        dhtDevice.exit()

def save_to_log(temp, humidity):
    log_path = os.path.join('data', 'temp_humi_log.csv')
    
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    
    # Check if file exists to determine if we need to write the header
    file_exists = os.path.isfile(log_path)
    
    now = datetime.now()
    
    # Prepare the data row
    # Format: Year, Month, Day, Hour, Min, Sec, Unix, Temp, Humi
    row = [
        now.year, 
        now.month, 
        now.day, 
        now.hour, 
        now.minute, 
        now.second, 
        int(time.time()), 
        round(temp, 2), 
        round(humidity, 2)
    ]
    
    # 'a' means Append mode - it adds to the end of the file
    with open(log_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        
        # Write header only if the file is brand new
        if not file_exists:
            writer.writerow(['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second', 'Unix', 'Temp', 'Humidity'])
            
        writer.writerow(row)

if __name__ == "__main__":
    get_reading()
