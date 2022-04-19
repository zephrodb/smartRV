#!/usr/bin/python
from ina219 import INA219
from ina219 import DeviceRangeError
import time
from lib2to3.pgen2 import token
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from os import system, name
from distutils.log import error
from lib2to3.pgen2 import token


influxToken = "7b49SrSv2O4V5r-v3BQk8v01F4sNTetIS5iNIv16SlpmmrdK2_Pi0nwnYBiqh32bCbF9O2drsJRw7IJkzSMsBQ=="
influxBucket = "data"
influxUrl = "http://localhost:8086"
influxOrg="smartRV"
influxClient = InfluxDBClient(url=influxUrl, token=influxToken, org="smartRV")
write_api = influxClient.write_api(write_options=SYNCHRONOUS)
query_api = influxClient.query_api()
SHUNT_OHMS = 1

def read():
    ina = INA219(SHUNT_OHMS)
    ina.configure()
    voltage = ina.voltage()
    curent = ina.current()
    power = ina.power()
    shuntV = ina.shunt_voltage()
    sensor = "PiPower"
    print("Bus Voltage: %.3f V" % voltage)
    try:
        now = int( time.time_ns() )
        print("Bus Current: %.3f mA" % curent)
        print("Power: %.3f mW" % power)
        print("Shunt voltage: %.3f mV" % shuntV)
        measurment = "shunt1"
        data = Point(measurment) \
            .field("voltage", voltage) \
            .time(now)
        print()
        print(f'Line: {data.to_line_protocol()}')
        print()
        write_api.write(bucket=influxBucket, record=data)          
        data = Point(measurment) \
            .field("current", curent) \
            .time(now)
        print()
        print(f'Line: {data.to_line_protocol()}')
        print()
        write_api.write(bucket=influxBucket, record=data)          
        data = Point(measurment) \
            .field("power", power) \
            .time(now)
        print()
        print(f'Line: {data.to_line_protocol()}')
        print()
        write_api.write(bucket=influxBucket, record=data)          
        data = Point(measurment) \
            .field("shuntVoltage", shuntV) \
            .time(now)
        print()
        print(f'Line: {data.to_line_protocol()}')
        print()
        write_api.write(bucket=influxBucket, record=data)        
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resistor
        print(e)        




if __name__ == "__main__":
    while 1 :
        time.sleep(1)
        system('clear')
        read()
