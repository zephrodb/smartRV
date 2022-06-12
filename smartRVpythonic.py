#!/usr/bin/python3
#from email import message
import logging
from os import system
from turtle import up
import yaml
#import adafruit_dht
import RPi.GPIO as GPIO
import smbus
import sys
import time
from espeakng import ESpeakNG
#import random 
#import argparse
import paho.mqtt.client as mqtt
import threading
from tkinter import *


class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp
class setupPins:
    def __init__(self, temp1_in, ptt_out, radioCharger1_out, radioCharger2_out):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(temp1_in, GPIO.IN)
        GPIO.setup(ptt_out, GPIO.OUT)
        GPIO.setup(radioCharger1_out, GPIO.OUT)
        GPIO.setup(radioCharger2_out, GPIO.OUT)


class setupRelays:
    def __init__(self, ptt_out, gen1Start_out, chargerEnable_out, inverterEnable_out, relayHatBus, relayHatAddress, radioCharger_out):
        smbus.SMBus(relayHatBus).write_byte_data(relayHatAddress, ptt_out, 0x00)
        relayHatBus.write_byte_data(relayHatAddress, gen1Start_out, 0x00)    
        relayHatBus.write_byte_data(relayHatAddress, chargerEnable_out, 0x00)
        relayHatBus.write_byte_data(relayHatAddress, inverterEnable_out, 0x00)
        ## always start charging on startup. we can turn it off later.
        GPIO.output(radioCharger_out, GPIO.LOW)
        GPIO.output(radioCharger_out, GPIO.LOW)
        ## make sure we arent dead keying
        GPIO.output(ptt_out, GPIO.HIGH)
        ## do we really want to stop the gen on init? not for me...
        #relayHatBus.write_byte_data(gen1Stop_out, ptt_out, 0x00)
        #relayHatBus.write_byte_data(gen2Enable_out, ptt_out, 0x00)        

class radio:
    def __init__(self, callSign, DTMFOperStatus, relayHatBus, relayHatAddress, ptt_out, radioCharger1_out, radioCharger2_out):
        self.callSign = callSign
        self.DTMFOperStatus = DTMFOperStatus
        self.relayHatBus = relayHatBus
        self.relayHatAddress = relayHatAddress
        self.ptt_out = ptt_out
        self.radioCharger1_out = radioCharger1_out
        self.radioCharger2_out = radioCharger2_out
    def pttDown(self):
        GPIO.output(self.radioCharger1_out, GPIO.HIGH)
        GPIO.output(self.radioCharger2_out, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.ptt_out, GPIO.LOW)
    def pttUp(self):
        GPIO.output(self.ptt_out, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.radioCharger1_out, GPIO.LOW)
        GPIO.output(self.radioCharger2_out, GPIO.LOW)
    def enableDTMF(self):
        self.DTMFOperStatus = True
    #this is a method on the radio object
    def disableDTMF(self):
        self.DTMFOperStatus = False
    def sendRadioMessage(self, msg):
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
        radio.sendRadioMessage(self, msg)

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

class mqtt_sub:
    def __init__(self, mqtt_feed, mqtt_host, mqtt_password, mqtt_port, mqtt_username):
        self.mqtt_feed = mqtt_feed
        self.mqtt_host = mqtt_host
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        
    def connect(self):
        self.client = mqtt.Client("rosebud_mqtt")  
        self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.connect(self.mqtt_host, self.mqtt_port)
        self.client.subscribe("/feeds/stats")
        print("subscribing to topic : "+self.mqtt_feed)        
        self.client.loop_start()
        
    def on_connect(self, client, userdata, flags, rc):
        rc = rc
        print("CONNECTED")
        print("Connected with result code: ", str(rc))

    
    def on_message(self, client, userdata, msg):
        payld = str(msg.payload)
        if 't_0' in payld:
            if 'temp_F' in payld:
                temp_f = payld.split("=")[2]
                temp_f = temp_f.strip(" '")
                # print(temp_f)
            elif "RH" in payld:
                rh = payld.split("=")[2]   
                rh = rh.strip(" '")
                # print(rh)
            elif "HI" in payld:
                hi = payld.split("=")[2]   
                hi = hi.strip(" '")

                hi = str(hi)
                # print(hi)
                self.button12=Button(window, text="Heat Index = " +hi, height = 5, width = 15)
                self.button12.grid(row=4,column=0)
                gui.updateHI(self, hi)

window = Tk()
window.geometry('800x600')
window.title("Glass Control Panel")
T = Text(window, height = 1, width = 17)
    

class gui:
    def __init__(self, window, hi, setTemp): 
        mqtt_thread = threading.Thread(target=mqtt_sub.connect(mqtt_))
        mqtt_thread.start()
        mqtt_thread.join()
        
        self.hi = hi
        self.setTemp = setTemp
        self.buttonDown0 = 0
        self.buttonDown1 = 0
        self.buttonDown2 = 0
        self.buttonDown3 = 0
        self.buttonDown4 = 0
        self.buttonDown5 = 0
        self.buttonDown6 = 0
        self.buttonDown7 = 0
        self.buttonDown8 = 0        
        self.buttonDown9 = 0
        self.buttonDown10 = 0
        self.buttonDown11 = 0
        self.buttonDown12 = 0
        self.buttonDown13 = 0

        self.button0=Button(window, text="RV Enable",
        command=self.rvEnable, height = 5, width = 15)
        self.button0.grid(row=1,column=0)

        self.button1=Button(window, text="Kitchen Light",
        command=self.kitchenLight, height = 5, width = 15)
        self.button1.grid(row=1,column=1)

        self.button2=Button(window, text="Generator Start",
        command=self.genStart, height = 5, width = 15)
        self.button2.grid(row=1,column=2)

        self.button3=Button(window, text="Exterior Lights",
        command=self.outsideLights, height = 5, width = 15)
        self.button3.grid(row=1,column=3)

        self.button4=Button(window, text="Water Heater",
        command=self.waterHeater, height = 5, width = 15)
        self.button4.grid(row=2,column=0)

        self.button5=Button(window, text="Water Pump",
        command=self.waterPump, height = 5, width = 15)
        self.button5.grid(row=2,column=1)

        self.button6=Button(window, text="Step",
        command=self.step, height = 5, width = 15)
        self.button6.grid(row=2,column=2)

        self.button7=Button(window, text="Porch Light",
        command=self.porchLight, height = 5, width = 15)
        self.button7.grid(row=2,column=3)

        self.button8=Button(window, text="Inverter",
        command=self.inverter, height = 5, width = 15)
        self.button8.grid(row=3,column=0)

        self.button9=Button(window, text="A/C Start",
        command=self.acStart, height = 5, width = 15)
        self.button9.grid(row=4,column=1)

        self.button10=Button(window, text="Temp Down",
        command=self.acDown, height = 5, width = 15)
        self.button10.grid(row=4,column=2)

        self.button11=Button(window, text="Temp Up",
        command=self.acUp, height = 5, width = 15)
        self.button11.grid(row=4,column=3)

        self.button12=Button(window, text="Heat Index = " +hi, height = 5, width = 15)
        self.button12.grid(row=4,column=0)

        self.button13=Button(window, text=setTemp, height = 5, width = 15)
        self.button13.grid(row=3,column=3)


        window.mainloop()

    def rvEnable(self):
        if self.buttonDown0 == 0 :
            self.buttonDown0 = 1
            self.button0.configure(bg='green')
        elif self.buttonDown0 == 1 :
            self.button0.configure(bg='#D9D8D7')
            self.buttonDown0 = 0
    def kitchenLight(self):
        if self.buttonDown1 == 0 :
            self.buttonDown1 = 1
            self.button1.configure(bg='green')
        elif self.buttonDown1 == 1 :
            self.button1.configure(bg='#D9D8D7')
            self.buttonDown1 = 0
    def genStart(self):
        if self.buttonDown2 == 0 :
            self.buttonDown2 = 1
            self.button2.configure(bg='green')
        elif self.buttonDown2 == 1 :
            self.button2.configure(bg='#D9D8D7')
            self.buttonDown2 = 0
    def outsideLights(self):
        if self.buttonDown3 == 0 :
            self.buttonDown3 = 1
            self.button3.configure(bg='green')
        elif self.buttonDown3 == 1 :
            self.button3.configure(bg='#D9D8D7')
            self.buttonDown3 = 0
    def waterHeater(self):
        if self.buttonDown4 == 0 :
            self.buttonDown4 = 1
            self.button4.configure(bg='green')
        elif self.buttonDown4 == 1 :
            self.button4.configure(bg='#D9D8D7')
            self.buttonDown4 = 0
    def waterPump(self):
        if self.buttonDown5 == 0 :
            self.buttonDown5 = 1
            self.button5.configure(bg='green')
        elif self.buttonDown5 == 1 :
            self.button5.configure(bg='#D9D8D7')
            self.buttonDown5 = 0
    def step(self):
        if self.buttonDown6 == 0 :
            self.buttonDown6 = 1
            self.button6.configure(bg='green')
        elif self.buttonDown6 == 1 :
            self.button6.configure(bg='#D9D8D7')
            self.buttonDown6 = 0
    def porchLight(self):
        if self.buttonDown7 == 0 :
            self.buttonDown7 = 1
            self.button7.configure(bg='green')
        elif self.buttonDown7 == 1 :
            self.button7.configure(bg='#D9D8D7')
            self.buttonDown7 = 0
    def inverter(self):
        if self.buttonDown8 == 0 :
            self.buttonDown8 = 1
            self.button8.configure(bg='green')
        elif self.buttonDown8 == 1 :
            self.button8.configure(bg='#D9D8D7')
            self.buttonDown8 = 0
    def acStart(self):
        if self.buttonDown9 == 0 :
            self.buttonDown9 = 1
            self.button9.configure(bg='green')
        elif self.buttonDown9 == 1 :
            self.button9.configure(bg='#D9D8D7')
            self.buttonDown9 = 0
    def acDown(self):
        self.setTemp -= 1
        self.button13['text'] = self.setTemp
        #self.button13=Button(self.window, text=self.setTemp, height = 5, width = 15)
    def acUp(self):
        self.setTemp += 1
        self.button13['text'] = self.setTemp
    def updateHI(self, hi):
        i_hi = float(hi)
        i_hi = int(i_hi)
        if i_hi >> 89 :
            self.button12['text'] = "Heat Index = " +hi
            self.button12['bg'] ='red'
        elif i_hi <= 90 :
            self.button12['text'] = "Heat Index = " +hi
            self.button12['bg'] ='green'


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
                    configParams['ptt_out'],
                    configParams['radioCharger1_out'],
                    configParams['radioCharger2_out'])

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
        pins = setupPins(configParams['temp1_in'],
                        configParams['ptt_out'],
                        configParams['radioCharger1_out'],
                        configParams['radioCharger2_out'])  
        mqtt_ = mqtt_sub(configParams['mqtt_feed'],
                            configParams['mqtt_host'],
                            configParams['mqtt_password'],
                            configParams['mqtt_port'],
                            configParams['mqtt_username'])            
        
    setupPins(22, 27, 20, 21)
    #setupRelays(relays)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
    # make sure we arent dead keying
    GPIO.output(27, GPIO.HIGH)
    
    # while True:
    #     i=1
    #     while i < 7 :
    #         print()
    #         i += 1
    #     radio.sendCallsign(rad)
    hi = "0"
    setTemp = 82
    gui(window, hi, setTemp)

    mqtt_thread = threading.Thread(target=mqtt_sub.connect(mqtt_))
    gui_thread = threading.Thread(target=gui(window, hi, setTemp))    
    mqtt_thread.start()
    gui_thread.start()
    gui_thread.join()
    mqtt_thread.join()

    

    
