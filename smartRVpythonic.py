#!/usr/bin/python3
import logging
from os import system
import unittest
import yaml
import adafruit_dht
import board
import RPi.GPIO as GPIO
import smbus
import sys
import time
from espeakng import ESpeakNG
import random 
import SDL_Pi_INA3221
import influxdb_client
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS


class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp
class setupPins:
    def __init__(self, temp1_in, temp2_in, gen1Run_in, gen2Run_in, volt1_in, ptt_out, gen1Start_out, gen1Stop_out, gen2Enable_out, chargerEnable_out, inverterEnable_out, ct1_in):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(temp1_in, GPIO.IN)
        GPIO.setup(temp2_in, GPIO.IN)
        GPIO.setup(gen1Run_in, GPIO.IN)
        GPIO.setup(gen2Run_in, GPIO.IN)
        GPIO.setup(volt1_in, GPIO.IN)
        GPIO.setup(ct1_in, GPIO.IN)
        GPIO.setup(ptt_out, GPIO.OUT)
        GPIO.setup(gen1Start_out, GPIO.OUT)
        GPIO.setup(gen1Stop_out, GPIO.OUT)
        GPIO.setup(gen2Enable_out, GPIO.OUT)
        GPIO.setup(chargerEnable_out, GPIO.OUT)
        GPIO.setup(inverterEnable_out, GPIO.OUT)
        print("Setup Pins")

class allRelaysDeenergize:
    def __init__(self, ptt_out, gen1Start_out, gen1Stop_out, gen2Enable_out, chargerEnable_out, inverterEnable_out, relayHatBus, relayHatAddress):
        smbus.SMBus(relayHatBus).write_byte_data(relayHatAddress, ptt_out, 0x00)
        relayHatBus.write_byte_data(relayHatAddress, gen1Start_out, 0x00)
        relayHatBus.write_byte_data(relayHatAddress, chargerEnable_out, 0x00)
        relayHatBus.write_byte_data(relayHatAddress, inverterEnable_out, 0x00)
        #do we really want to stop the gen on init?
        #relayHatBus.write_byte_data(gen1Stop_out, ptt_out, 0x00)
        #relayHatBus.write_byte_data(gen2Enable_out, ptt_out, 0x00)        
        print("Relays all down")
class radio:
    def __init__(self, callSign, DTMFOperStatus, relayHatBus, relayHatAddress, ptt_out):
        self.callSign = callSign
        self.DTMFOperStatus = DTMFOperStatus
        self.ptt_out = ptt_out
        #self.msg = msg
        self.relayHatBus = relayHatBus
        self.relayHatAddress = relayHatAddress
    #this is a method on the radio object
    def pttDown(self):
        smbus.SMBus(1).write_byte_data(0x10, 1, 0xFF)

    def pttUp(self):
        smbus.SMBus(1).write_byte_data(0x10, 1,  0x00)

    def enableDTMF(self):
        self.DTMFOperStatus = True
    #this is a method on the radio object
    def disableDTMF(self):
        self.DTMFOperStatus = False
    def sendRadioMessage(self):
        esng = ESpeakNG(voice='en-us')
        esng.speed = 120
        tones = "echo {} | minimodem -t 1200 -f /tmp/temp.wav".format(msg)
        system(tones)
        radio.pttDown(self)
        time.sleep(.3)
        esng.say(msg, sync=True)
        print(msg)
        time.sleep(1)
        system("aplay /tmp/temp.wav")
        radio.pttUp(self)
    def sendCallsign(self):
        msg = "This is an automated reporting station and open repeater Operated by {}".format(self.callSign)
        radio.sendRadioMessage(msg)
class powerControl:
    def __init__(self, gen1Name, gen2Name, gen1Start_out, gen1Stop_out, gen2Enable_out, inverterEnable_out, chargerEnable_out, relayHatBus, relayHatAddress, gen1Run_in=False, fuelLevel=0,):
        self.gen1Run_in = gen1Run_in
        self.fuelLevel = fuelLevel
        self.gen1Name = gen1Name
        self.gen2Name = gen2Name
        self.gen1Start_out = gen1Start_out
        self.gen1Stop_out = gen1Stop_out
        self.gen2Enable_out = gen2Enable_out
        self.inverterEnable_out = inverterEnable_out
        self.chargerEnable_out = chargerEnable_out
        self.RelayGenStartGPIO = gen1Start_out
        self.RelayGen1EnableGPIO = gen1Stop_out
        self.RelayGen2EnableGPIO = gen2Enable_out
        self.RelayInverterEnableGPIO = inverterEnable_out
        self.RelayChargerEnableGPIO = chargerEnable_out
        self.relayHatBus = relayHatBus
        self.relayHatAddress = relayHatAddress


    def checkGen1Status(self):
        #TODO need to add logic to actually check status
        return self.gen1Run_in


    def startGen1(self):
        numOfTries = 0
        if self.checkGen1Status() == False & numOfTries < 3:
            msg = "starting generator"
            logging.info(msg + " " + self.Name)
            #Run starter for .XX Seconds
            self.relayHatBus.write_byte_data(self.relayHatAddress, self.gen1Start_out, 0xFF)
            time.sleep(.33)
            #Stop starter
            self.relayHatBus.write_byte_data(self.relayHatAddress, self.gen1Start_out, 0x00)
            return msg
        else:
            msg = "Unable to start generator, it is already running"
            logging.info(msg + " " + self.Name)
            return msg

    def stopGen1(self):
        if self.checkGen1Status() == True:
            msg = "stopping generator"
            logging.info(msg + " " + self.Name)
            self.relayHatBus.write_byte_data(self.relayHatAddress, self.gen1Stop_out, 0xFF)
            time.sleep(5)
            self.relayHatBus.write_byte_data(self.relayHatAddress, self.gen1Stop_out, 0x00)
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            logging.info(msg + " " + self.Name)
            return msg
    def stopGen2(self):
        if self.checkGen1Status() == True:
            msg = "stopping generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually stop genny
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            logging.info(msg + " " + self.Name)
            return msg

class powerMonitor:
    def __init__(self, shuntAddress, shunt1name, shunt2name, shunt3name, influxBucket, influxURL, influxToken, influxORG):
        self.shuntAddress = shuntAddress
        self.shunt1name = shunt1name
        self.shunt2name = shunt2name
        self.shunt3name = shunt3name
        self.influxORG = influxORG
        self.influxToken = influxToken
        self.influxURL = influxURL
        self.influxBucket = influxBucket
    def readBatteries(self):
        ina3221 = SDL_Pi_INA3221.SDL_Pi_INA3221(addr=0x43)
        busvoltage1 = ina3221.getBusVoltage_V(1)
        shuntvoltage1 = ina3221.getShuntVoltage_mV(1)
        current_mA1 = ina3221.getCurrent_mA(1)  
        loadvoltage1 = busvoltage1 + (shuntvoltage1 / 1000)
        busvoltage2 = ina3221.getBusVoltage_V(2)
        shuntvoltage2 = ina3221.getShuntVoltage_mV(2)
        current_mA2 = ina3221.getCurrent_mA(2)  
        loadvoltage2 = busvoltage2 + (shuntvoltage2 / 1000)
        busvoltage3 = ina3221.getBusVoltage_V(3)
        shuntvoltage3 = ina3221.getShuntVoltage_mV(3)
        current_mA3 = ina3221.getCurrent_mA(3)  
        loadvoltage3 = busvoltage3 + (shuntvoltage3 / 1000)

        print(f"{busvoltage1}, {shuntvoltage1}, {current_mA1}, {loadvoltage1}")
        influx.writeInflux(self, measurment="shuntvoltage1", unit="Volt", value=shuntvoltage1)
        influx.writeInflux(self, measurment="current_mA1", unit="mA", value=current_mA1)
        print(f"{busvoltage2}, {shuntvoltage2}, {current_mA2}, {loadvoltage2}")
        influx.writeInflux(self, measurment="shuntvoltage2", unit="Volt", value=shuntvoltage2)
        influx.writeInflux(self, measurment="current_mA2", unit="mA", value=current_mA2)
        print(f"{busvoltage3}, {shuntvoltage3}, {current_mA3}, {loadvoltage3}")
        influx.writeInflux(self, measurment="shuntvoltage3", unit="Volt", value=shuntvoltage3)
        influx.writeInflux(self, measurment="current_mA3", unit="mA", value=current_mA3)

class influx:
    def __init__(self,  influxBucket, influxURL, influxToken, influxORG ):
        #self.InfluxDBClient = InfluxDBClient
        self.influxBucket = influxBucket
        #self.write_api = InfluxDBClient.write_api(self, write_options=ASYNCHRONOUS)
        self.client = influxdb_client.InfluxDBClient(influxURL, influxToken, influxORG)
        self.influxORG = influxORG
        self.influxToken = influxToken
        self.influxURL = influxURL
    def writeInflux(self, measurment, unit, value):
        self.measurment = measurment
        self.unit = unit
        self.value = value
        self.now = int(time.time_ns() )
        self.data = Point(measurment) .field(self.unit, self.value) .time(self.now)
        print(self.data)
        write(bucket=self.influxBucket, org=self.influxORG, record=self.data)

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='smartRV.log',
                        filemode='a+')
    logging.info('Starting SmartRV...')

    with open(r'./config.yaml') as configFile:
        configParams = yaml.load(configFile, Loader=yaml.FullLoader) #converting text to a dict(in-memory k,v store)

        env = environmentThresholds(configParams['highHumidity'],
                          configParams['highTemp'],
                          configParams['medHumidity'],
                          configParams['medTemp'])

        rad = radio(configParams['callSign'],
                    configParams['DTMFOperStatus'],
                    configParams['relayHatBus'],
                    configParams['relayHatAddress'],
                    configParams['ptt_out'])

        gen1 = powerControl(configParams['gen1Name'],
                                 configParams['gen1Start_out'],
                                 configParams['gen1Run_in'],
                                 configParams['gen1Stop_out'],
                                configParams['gen2Name'],
                                configParams['gen2Enable_out'],
                                configParams['chargerEnable_out'],
                                configParams['relayHatBus'],
                                configParams['relayHatAddress'])
        gen2 = powerControl(configParams['gen2Name'],
                                 configParams['gen1Start_out'],
                                 configParams['gen1Run_in'],
                                 configParams['gen1Stop_out'],
                                configParams['gen2Name'],
                                configParams['gen2Enable_out'],
                                configParams['chargerEnable_out'],
                                configParams['relayHatBus'],
                                configParams['relayHatAddress'])
        inverter = powerControl(configParams['gen1Name'],
                                 configParams['gen1Start_out'],
                                 configParams['gen1Run_in'],
                                 configParams['gen1Stop_out'],
                                configParams['gen2Name'],
                                configParams['gen2Enable_out'],
                                configParams['chargerEnable_out'],
                                configParams['relayHatBus'],
                                configParams['relayHatAddress'])
        charger = powerControl(configParams['gen1Name'],
                                 configParams['gen1Start_out'],
                                 configParams['gen1Run_in'],
                                 configParams['gen1Stop_out'],
                                configParams['gen2Name'],
                                configParams['gen2Enable_out'],
                                configParams['chargerEnable_out'],
                                configParams['relayHatBus'],
                                configParams['relayHatAddress'])
        shunts = powerMonitor(configParams['shuntSensor1address'],
                                configParams['shunt1name'],
                                configParams['shunt2name'],
                                configParams['shunt3name'],
                                configParams['influxBucket'],
                                configParams['influxURL'],
                                configParams['influxToken'],
                                configParams['influxORG'])
        write = influx(configParams['influxBucket'],
                        configParams['influxURL'],
                        configParams['influxToken'],
                        configParams['influxORG'])                        

    while True:
        powerMonitor.readBatteries(shunts)
        time.sleep(1)

