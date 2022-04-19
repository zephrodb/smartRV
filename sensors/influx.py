#!/usr/bin/python



from lib2to3.pgen2 import token
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import argparse
import string
import time
import adafruit_dht
import board
import RPi.GPIO as GPIO
import datetime

influxToken = "7b49SrSv2O4V5r-v3BQk8v01F4sNTetIS5iNIv16SlpmmrdK2_Pi0nwnYBiqh32bCbF9O2drsJRw7IJkzSMsBQ=="
influxBucket = "data"
influxUrl = "http://localhost:8086"
influxOrg="smartRV"
influxClient = InfluxDBClient(url=influxUrl, token=influxToken, org="smartRV")
write_api = influxClient.write_api(write_options=SYNCHRONOUS)
query_api = influxClient.query_api()
Temp1Pin = 4
pin = 4
dhtDevice = adafruit_dht.DHT11(board.D4)
measurment = ""

temp1Sensor = "FrontTemp"


def readTemp() :
    while 1 :
        try:
            now = int(time.time_ns() )
            temp_c = dhtDevice.temperature
            temp_c = int(temp_c)
            temp_f = temp_c * (9 / 5) + 32
            temp_f = int(temp_f)
            humidity = int(dhtDevice.humidity)
            
            measurment = "temp1"
            data = Point(measurment) \
                .field("temp_f", temp_f) \
                .time(now)
            print(data)
            print()
            write_api.write(bucket=influxBucket, record=data)          

            data = Point(measurment) \
                .field("humidity", humidity) \
                .time(now)
            print()
            print(data)
            print()
            write_api.write(bucket=influxBucket, record=data)          
            time.sleep(1)
        except  Exception as e:
            print(e)
            time.sleep(10)
    exit    

readTemp()







