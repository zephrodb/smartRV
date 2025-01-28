##!/usr/bin/python

import smbus
#import go
#from ast import And
import logging
from os import system
import yaml
import time
import paho.mqtt.client as mqtt
from Adafruit_I2C import Adafruit_I2C
from MCP23017 import MCP23017



class mqttPub:
    def __init__(self, mqtt_topic, mqtt_broker, mqtt_password, mqtt_port, mqtt_user):
        self.mqtt_topic = mqtt_topic
        self.mqtt_broker = mqtt_broker
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        #self.msg = msg

        self.client = mqtt.Client()
        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
        #client.on_connect = on_connect
        # Connect to the MQTT broker
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)

    def publish(self, msg, pin):
            self.msg = msg
            self.pin = pin
            self.full_mqtt_topic = self.mqtt_topic+"switch/Sensor0x24p"+str(self.pin)+"/state"
            # Publish the switch state
            #print(self.full_mqtt_topic, self.msg)
            self.client.publish(self.full_mqtt_topic, self.msg)

# class readIO:
#     def __init__(self, address=0x24, num_gpios=16):
#         self.mcp = MCP23017(address=address, num_gpios=num_gpios)
#         #self.pin = pin
#         for port in range(0, 15):
#             self.mcp.pinMode(port, self.mcp.INPUT)
#             self.mcp.pullUp(port, 0)

#     def readPin(self, pin):
#         if 0 <= pin <= 15:
#             return self.mcp.currentVal(pin)
#         else:
#             raise ValueError("Pin number must be between 0 and 15.")

class readIO:
    def __init__(self, address=0x24, num_gpios=16):
        self.mcp = MCP23017(address=address, num_gpios=num_gpios)
        for pin in range(0, 16):
            self.mcp.pinMode(pin, self.mcp.INPUT)
            self.mcp.pullUp(pin, 0)

    def readPin(mcp, pin):
        pin = pin
        if 0 <= pin <= 15:
            return mcp.currentVal(pin)
        else:
            raise ValueError("Pin number must be between 0 and 15.")

class go:
    def __init__(self):
        pass
    def run():
        mcp = MCP23017(address=0x24, num_gpios=16)
        while True:
            i = 8
            while i <= 15 :
                pin = i
                rtn = readIO.readPin(mcp, pin)
                #print(rtn)
                #print("Pin: " + str(pin) + " Value: " + str(rtn))
                i +=1
                if rtn == 0:
                    ret = "on"
                elif rtn == 1:
                    ret = "off"
                else :
                    ret = 255
                time.sleep(.15)
                msg = str(ret)
                mqttPub.publish(msg, pin)
                #print(msg)

            time.sleep(2)   



if __name__ == "__main__":
    # Define the I2C bus number and the MCP23017 address
    I2C_BUS = 1
    MCP23017_ADDRESS = 0x24  # Default address, change if needed
    IODIRA = 0x00  # I/O direction register for port A

    # Initialize the I2C bus
    bus = smbus.SMBus(1)

    # Set all of port A to inputs
    bus.write_byte_data(0x24, IODIRA, 0xFF)


    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='mcpReader.log',
                        filemode='a+')
    logging.info('Starting mcpReader...')

    with open(r'./config.yaml') as configFile:
        configParams = yaml.load(configFile, Loader=yaml.FullLoader) #converting text to a dict(in-memory k,v store)
     
        mqttPub = mqttPub(configParams['mqtt_topic'],
                    configParams['mqtt_broker'],
                    configParams['mqtt_password'],
                    configParams['mqtt_port'],
                    configParams['mqtt_user'])


        





go.run()
