#!/usr/bin/env python3

import adafruit_dht
import board

# If your sensor is on GPIO 4:
dhtDevice = adafruit_dht.DHT11(board.D14)

try:
    temp_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print(f"Temp: {temp_c}C, Humidity: {humidity}%")
except RuntimeError as error:
    # Errors are common with DHT sensors, just keep trying
    print(error.args[0])
