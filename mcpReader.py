#!/usr/bin/python3
from ast import And
import logging
from os import system
#import tkinter
#from turtle import up
#from unittest import result
#from smbus2 import SMBus
#import smbus
import yaml
#import RPi.GPIO as GPIO
#from smbus import *
#import sys
import time
#import espeakng
import paho.mqtt.client as mqtt
#import threading
#from tkinter import *
#import tkinter.font as font
from Adafruit_I2C import Adafruit_I2C
from MCP23017 import MCP23017
#import board
#import datetime




class mqttSub:
    def __init__(self, mqtt_feed, mqtt_host, mqtt_password, mqtt_port, mqtt_username, i2cBus, mcpAddress, numGPIOS ):
        self.mqtt_feed = mqtt_feed
        self.mqtt_host = mqtt_host
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.i2cBus = i2cBus
        self.mcpAddress = mcpAddress
        self.numGPIOS = numGPIOS
        self.mcp = MCP23017(busnum=1, address=0x20, num_gpios=16)
        self.mcp.setup(0, MCP23017.IN)  # Example: Set pin 0 as input
    def on_connect(client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")
    def publish_pin_status(self, client, mqtt_feed):
        while True:
            self.client = client
            self.mqtt_feed = mqtt_feed
            pin_status = self.mcp.input(0)  # Read pin 0 status
            message = f"Pin 0 status: {'HIGH' if pin_status else 'LOW'}"
            client.publish(self.mqtt_feed, message)
            print(f"Published: {message}")
            time.sleep(5)  # Publish every 5 seconds

    def main(self, client):
        #self.client = client
        client.on_connect = on_connect
        client.connect(self.mqtt_host, self.mqtt_port, 60)
        client.loop_start()
        self.publish_pin_status()


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='mcpReader.log',
                        filemode='a+')
    logging.info('Starting SmartRV...')

    with open(r'./config.yaml') as configFile:
        configParams = yaml.load(configFile, Loader=yaml.FullLoader) #converting text to a dict(in-memory k,v store)
     
        mqtt = mqttSub(configParams['mqtt_feed'],
                    configParams['mqtt_host'],
                    configParams['mqtt_password'],
                    configParams['mqtt_port'],
                    configParams['mqtt_username'],
                    configParams['i2cBus'],
                    configParams['mcpAddress'],
                    configParams['numGPIOS'])  
