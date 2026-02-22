#!/usr/bin/env python3

import adafruit_dht
import board

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
            # Here you would typically save to a database or JSON file
        
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

if __name__ == "__main__":
    get_reading()
