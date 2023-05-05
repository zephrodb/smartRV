#!/usr/bin/python3
from ast import And
import logging
from os import system
import tkinter
from turtle import up
from unittest import result
from smbus2 import SMBus
import yaml
import RPi.GPIO as GPIO
#from smbus import *
import sys
import time
import espeakng
import paho.mqtt.client as mqtt
import threading
from tkinter import *
import tkinter.font as font
from Adafruit_I2C import Adafruit_I2C
from MCP23017 import MCP23017
import board
import datetime
bus = SMBus(1)

class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp
class setupPins:
    def __init__(self, temp1_in, ptt_out, radioCharger1_out, radioCharger2_out):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ptt_out, GPIO.OUT)


class setupRelays:
    def __init__(self, ptt_out, gen1Start_out, chargerEnable_out, inverterEnable_out, relayHatBus, relayHatAddress, radioCharger_out):
        with SMBus(1) as bus:
            bus.write_byte_data(relayHatAddress, ptt_out, 0x00)
            bus.write_byte_data(relayHatAddress, gen1Start_out, 0x00)    
            bus.write_byte_data(relayHatAddress, chargerEnable_out, 0x00)
            bus.write_byte_data(relayHatAddress, inverterEnable_out, 0x00)
        ## make sure we arent dead keying
        GPIO.output(ptt_out, GPIO.HIGH)
       

class radio:
    def __init__(self, callSign, DTMFOperStatus, relayHatBus, relayHatAddress, ptt_out, radioCharger1_out, radioCharger2_out):
        self.callSign = callSign
        self.DTMFOperStatus = DTMFOperStatus
        self.relayHatBus = relayHatBus
        self.relayHatAddress = relayHatAddress
        self.ptt_out = ptt_out
        self.radioCharger1_out = radioCharger1_out
        self.radioCharger2_out = radioCharger2_out
        self.esng = espeakng.Speaker()
    def pttDown(self):
        logging.info("PTT Down")
        GPIO.output(self.ptt_out, GPIO.LOW)
        time.sleep(.75)
    def pttUp(self):
        logging.info("PTT UP")
        GPIO.output(self.ptt_out, GPIO.HIGH)
    def sendRadioMessage(self, msg):
        time.sleep(1)
        cs = " " + self.callSign
        msg = msg+" "+cs
        self.esng.voice='en-us'
        self.esng.speed = 100
        tones = "echo {} | minimodem -t 1200 -f /tmp/temp.wav".format(msg)
        system(tones)
        radio.pttDown(self)
        logging.info("Sending: " + msg)
        print("Saying " +msg )
        self.esng.say(msg, wait4prev=True)
        print("Voice Done, sending TONES")
        time.sleep(5)
        system("aplay /tmp/temp.wav")
        time.sleep(.200)
        radio.pttUp(self)
    def sendCallsign(self):
        msg = "Operated by {} ".format(self.callSign)
        radio.sendRadioMessage(self, msg)

class powerControl:
    def __init__(self, gen1Name, gen2Name, gen1Start_out, gen1Stop_out, gen2Enable_out, inverterEnable_out, chargerEnable_out, relayHatBus, relayHatAddress, numberOfTries, callSign, gen1Run_in=False, fuelLevel=0):
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
        self.relayHatBus = SMBus(1)
        self.relayHatAddress = relayHatAddress
        self.buttonFont = font.Font(family='Helvetica', size=24)
        self.inverterStatus = readIO.readPin(10)
        self.numberOfTries = 0
        self.callSign = callSign
    def checkGen1Status():
        if readIO.readPin(8) == 0:
            return True
        else:
            if readIO.readPin(8) == 1:
                return False
    def startGen1(self):
        if powerControl.checkGen1Status() == False :
            #logging.info(msg + " " + self.Name)
            #Run starter for .XX Seconds
            print("Running Starter for 5s")
            logging.info("Running Starter, 5s")
            bus.write_byte_data(0x10, 3, 0xFF)            
            time.sleep(5)
            #Stop starter/system is remote start safe. wont overrun
            bus.write_byte_data(0x10, 3, 0x00)            
            i = 1
            while i < 25 : 
                if powerControl.checkGen1Status() == False :
                    time.sleep(1)
                    i += 1
                    print("Waiting for Power " + str(i) + " of 25s")
                    logging.info("Waiting on power from Generator, 25s")
                elif(powerControl.checkGen1Status() == True) :
                    logging.info("Generator Started")
                    return
                if self.numberOfTries <= 2:
                    self.numberOfTries += 1
                    print("Number of Tries = " + str(self.numberOfTries) + " out of 3")
                    logging.info("Number of Tries = " + str(self.numberOfTries) + " out of 3")
                    powerControl.startGen1(self)
                else :
                    radio.sendRadioMessage(self, "Generator Failed to start after 3 tries. ")
                    logging.error("Generator Failed to start")
        elif powerControl.checkGen1Status() == True :
            msg = "Unable to start generator, it is already running"
            logging.warn("unable to start gernerator, running already")
            #logging.info(msg + " " + self.Name)
            return msg
        return
    def stopGen1(self):
        if powerControl.checkGen1Status() == True:
            msg = "Stopping Generator"
            logging.info(msg)
            bus.write_byte_data(0x10, 2, 0xFF)
            time.sleep(5)
            bus.write_byte_data(0x10, 2, 0x00)
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            logging.warn(msg)
            return msg
    def stopGen2(self):
        if self.checkGen1Status() == True:
            msg = "stopping generator"
            #logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually stop genny
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            #logging.info(msg + " " + self.Name)
            return msg
    def inverter_toggle(self):
        inverterStatus = readIO.readPin(10)
        print("Current Status = (1=off/0=on) " + str(readIO.readPin(10)))
        #self.button8=Button(window, height = 5, width = 15, bg='#0052cc', fg='#ffffff')
        print("Toggle Inverter")
        logging.info("Current Status = (1=off/0=on) " + str(readIO.readPin(10)))
        logging.info("Toggling Inverter")
        print()
        if readIO.readPin(10) == 1:
            #turn on inverter
            print("Geting Turned On")
            logging.info("Turning on Inverter")
            bus.write_byte_data(0x10, 4, 0xFF)
            time.sleep(4)
            print("New Status = (1=off/0=on)" + str(readIO.readPin(10))) 
            if readIO.readPin(10) == 0:           
                self.button8.configure(bg='green')
                self.button8['text'] = "Inverter (ON)"
                logging.info("inverter On")
            else:
                self.button8.configure(bg='yellow')
                self.button8['text'] = "Inverter (FAIL?)"
                logging.warn("Inverter failed to start")
        elif readIO.readPin(10) == 0:
            #turn off inverter
            print("Total Turn Off")
            logging.info("Turning off Inverter")
            bus.write_byte_data(0x10, 4, 0x00)
            time.sleep(3)            
            print("New Status = (1=off/0=on)" + str(readIO.readPin(10)))
            if readIO.readPin(10) == 1:           
                self.button8.configure(bg='#0052cc', fg='#ffffff',)
                self.button8['text'] = "Inverter"
                logging.info("Inverter Off")
            else: 
                self.button8.configure(bg='red')
                self.button8['text'] = "Inverter (Switch?)"
                logging.warn("Inverter is still on. Maybe the switch?")
class mqtt_sub:
    def __init__(self, mqtt_feed, mqtt_host, mqtt_password, mqtt_port, mqtt_username, buttonDown7, setTemp ):
        self.mqtt_feed = mqtt_feed
        self.mqtt_host = mqtt_host
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.logFont = font.Font(family='Helvetica', size=8)
        self.buttonFont = font.Font(family='Helvetica', size=24)
        self.button12 = Button(height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button7 = Button(height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button6 = Button(height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button18 = Button(height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.logFont)
        self.buttonDown7 = buttonDown7
        self.relayHatAddress=1
        self.relayHatBus=1
        self.esng = espeakng.Speaker()
        self.ptt_out = configParams["ptt_out"]
        self.callSign = configParams["callSign"]
        self.numberOfTries = 0
        self.setTemp = setTemp
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
        print("MQTT Subbed")
        print("Connected with result code: ", str(rc))
    def updateLogBox(self):
        fileHandle = open ( 'smartRV.log',"r" )
        lineList = fileHandle.readlines(-1)
        fileHandle.close()
        print(lineList[1])
        print(" ")
        self.button18['text'] = lineList[1]
        self.button18.configure(bg='white', fg='#ffffff')
        self.button18.grid(row=3,column=1)  
    def on_message(self, client, userdata, msg):
        global buttonDown9
        payld = str(msg.payload)
        if 't_0' in payld:
            if 'temp_F' in payld:
                temp_f = payld.split("=")[2]
                temp_f = temp_f.strip(" '")
            elif "RH" in payld:
                rh = payld.split("=")[2]   
                rh = rh.strip(" '")
            elif "HI" in payld:
                self.hi = payld.split("=")[2]   
                self.hi = self.hi.strip(" '")
                self.hi = str(self.hi)
                self.f_hi = float(self.hi)
                self.i_hi = int(self.f_hi)
                self.button12Txt = "Heat Index = " + self.hi
                #print(self.button12Txt)
                if self.i_hi > 89 :
                    self.button12=Button(height = 5, width = 15, bg='red', fg='#ffffff', font=self.buttonFont)
                    self.button12['text'] = self.button12Txt
                    self.button12.grid(row=4,column=0)
                elif self.i_hi <= 90 :
                    self.button12=Button(height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
                    self.button12['text'] = self.button12Txt
                    self.button12.grid(row=4,column=0)
                self.setTempSpanUp = setTemp
                self.setTempSpanUp += 1.5
                self.setTempSpanDn = setTemp 
                self.setTempSpanDn -= 1.5
                print(setTemp)
                print(buttonDown9)
                if buttonDown9 == 1 :
                    self.Name = "checkThermostat"
                    if self.f_hi > self.setTempSpanUp :
                        print("temp hi")
                        if powerControl.checkGen1Status == False :
                            powerControl.startGen1(self)
                            print(msg)
                            msg = "A/C Not running but commanded. Starting"
                            logging.info(msg + " " + self.Name)
                        else :
                            print(msg)
                            logging.info(str(msg) + " " + self.Name)
                            msg = "A/C is commanded and running. No action"
                    elif self.f_hi < self.setTempSpanDn :
                        print("temp hi")
                        if powerControl.checkGen1Status == True :
                            powerControl.stopGen1(self)
                            msg = "A/C is NOT commanded. Gen running. Stopping"
                            logging.info(msg + " " + self.Name)
                            print(msg)
        elif ("ZVEI1: 1E010ED51380E8" in payld) :
                msg = "RC: Lights OFF"
                print(msg)
                mcp.pinMode(3, mcp.OUTPUT)            
                mcp.output(3, mcp.HIGH)
                logging.info(msg)
                self.updateLogBox()
                time.sleep(3)
                radio.sendRadioMessage(self, "Turning off Lights")
                self.button7.configure(bg='#0052cc', fg='#ffffff')
        elif ("ZVEI1: 1E0101D51380E8" in payld) :
                msg = "RC: Lights ON"
                print(msg)
                mcp.pinMode(3, mcp.OUTPUT)            
                mcp.output(3, mcp.LOW)      
                logging.info(msg)
                time.sleep(3)
                radio.sendRadioMessage(self, "Turning on Lights") 
                self.button7.configure(bg='green')                         
        elif ("ZVEI1: 1E020ED51380E8" in payld) :
                msg = "RC: Stop Generator"
                print(msg)
                logging.info(msg)
                time.sleep(3)
                radio.sendRadioMessage(self, "Stopping Generator")                            
                powerControl.stopGen1(self) 
        elif ("ZVEI1: 1E0201D51380E8" in payld) :
                self.numberOfTries = 0
                msg = "RC: Start Generator"
                logging.info("RC: Start Generator")
                time.sleep(3)
                radio.sendRadioMessage(self, "Starting Generator")                  
                print(msg)
                powerControl.startGen1(self)                 
        elif ("ZVEI1: 1E030ED51380E8" in payld) :
                logging.info("RC: Get A/C SetTemp")
                time.sleep(3)                
                radio.sendRadioMessage(self, "Current A C set temperature is " + str(setTemp) + "Degrees interior temperature is " + self.hi + "Degrees,,,")  
        elif ("ZVEI1: 1E0301D51380E8" in payld) :
                msg = "RC: Set A/C SetTemp Down"
                print(msg)
                logging.info(msg)
                gui.acDown      
                time.sleep(3)
                radio.sendRadioMessage(self, "Current A C set temperature is now" + str(setTemp))        
        elif ("ZVEI1: 1E0302D51380E8" in payld) :
                msg = "RC: Set A/C SetTemp UP"
                logging.info(msg)
                gui.acUp  
                time.sleep(3)
                radio.sendRadioMessage(self, "Current A C set temperature is now" + str(setTemp))        
        elif ("ZVEI1: 1E0303D51380E8" in payld) :
                print("Get Current Temp")
                logging.info("RC: Get A/C SetTemp")
                logging.info("   Current Temp: " + temp_f)
                time.sleep(3)
                radio.sendRadioMessage(self, "Current ambient temperature is " + str(temp_f) + "interior temperature is " + str(self.hi))                              
        elif ("ZVEI1: 1E040ED51380E8" in payld) :
                print("Step OFF")
                mcp.pinMode(1, mcp.OUTPUT)
                mcp.output(1, mcp.HIGH)
                self.button6.configure(bg='#0052cc', fg='#ffffff')
        elif ("ZVEI1: 1E0401D51380E8" in payld) :
                print("Step ON")
                mcp.pinMode(1, mcp.OUTPUT)
                mcp.output(1, mcp.LOW)               
                self.button6.configure(bg='green')
        elif ("/feed/solar/solarPower" in payld) :
                msg = "Solar Power "+ payld
                logging.info(msg)
                self.button18['text'] = msg
                self.button18.configure(bg='white', fg='#ffffff')
                #self.button18.grid(row=3,column=1)  


        # else :
        #     mqtt_sub.updateLogBox(self)


window = Tk()
#window.geometry('1280x1024')
window.title("Glass Control Panel")
window.attributes('-fullscreen',True)
T = Text(window, height = 1, width = 17)
class gui:
    def __init__(self, window, hi, setTemp): 
        mqtt_thread = threading.Thread(target=mqtt_sub.connect(mqtt_))
        mqtt_thread.start()
        mqtt_thread.join()
        self.buttonFont = font.Font(family='Helvetica', size=24) 
        self.logfont =  font.Font(family='Helvetica', size=9)
        self.hi = hi
        self.inverterStatus = inverterStatus
        self.setTemp = setTemp
        global buttonDown0
        buttonDown0 = 0
        self.buttonDown0 = buttonDown0
        global buttonDown1
        buttonDown1 = 0
        self.buttonDown1 = buttonDown1
        global buttonDown2
        buttonDown2 = 0
        self.buttonDown2 = buttonDown2
        global buttonDown3
        buttonDown3 = 0
        self.buttonDown3 = buttonDown3
        global buttonDown4
        buttonDown4 = 0
        self.buttonDown4 = buttonDown4
        global buttonDown5
        buttonDown5 = 0
        self.buttonDown5 = buttonDown5
        global buttonDown6
        buttonDown6 = 0
        self.buttonDown6 = buttonDown6
        global buttonDown7
        buttonDown7 = 0
        self.buttonDown7 = buttonDown7
        global buttonDown8
        buttonDown8 = 0  
        self.buttonDown8 = buttonDown8
        global buttonDown9     
        # buttonDown9 = 0
        self.buttonDown9 = buttonDown9
        global buttonDown10
        buttonDown10 = 0
        self.buttonDown10 = buttonDown10
        global buttonDown11
        buttonDown11 = 0
        self.buttonDown11 = buttonDown11
        global buttonDown12
        buttonDown12 = 0
        self.buttonDown12 = buttonDown12
        global buttonDown13
        buttonDown13 = 0
        self.buttonDown13 = buttonDown13
        mcp.pinMode(7, mcp.OUTPUT)

        self.button0=Button(window, text="RV Enable",
        command=self.rvEnable, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button0.grid(row=1,column=0, pady=12, padx=11)

        self.button1=Button(window, text="Kitchen Light",
        command=self.kitchenLight, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button1.grid(row=1,column=1, pady=12, padx=11)

        if powerControl.checkGen1Status() == False :
            self.button2=Button(window, text="Generator START",
            command=self.genStart, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        elif powerControl.checkGen1Status() == True :
            self.button2=Button(window, text="STARTING",
            command=self.genStart, height = 5, width = 15, bg='green', fg='#ffffff', font=self.buttonFont)
        self.button2.grid(row=1,column=2, pady=12, padx=11)

        self.button3=Button(window, text="Exterior Lights",
        command=self.outsideLights, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button3.grid(row=1,column=3, pady=12, padx=11)

        self.button4=Button(window, text="Water Heater",
        command=self.waterHeater, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button4.grid(row=2,column=0, pady=12, padx=11)

        self.button5=Button(window, text="Water Pump",
        command=self.waterPump, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button5.grid(row=2,column=1, pady=12, padx=11)

        self.button6=Button(window, text="Step",
        command=self.step, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button6.grid(row=2,column=2, pady=12, padx=11)

        self.button7=Button(window, text="Porch Light",
        command=self.porchLight, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button7.grid(row=2,column=3, pady=12, padx=11)
        
        if readIO.readPin(10) == 1:
            self.button8=Button(window, text="Inverter",
            command=self.inverter, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
            self.button8.grid(row=3,column=0, pady=12, padx=11)
        else:
            self.button8=Button(window, text="Inverter (ON)",
            command=self.inverter, height = 5, width = 15, bg='green', fg='#ffffff', font=self.buttonFont)
            self.button8.grid(row=3,column=0, pady=12, padx=11)

        self.button9=Button(window, text="A/C Enable",
        command=self.acStart, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button9.grid(row=4,column=1, pady=12, padx=11)

        self.button10=Button(window, text="Temp Down",
        command=self.acDown, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button10.grid(row=4,column=2, pady=12, padx=11)

        self.button11=Button(window, text="Temp Up",
        command=self.acUp, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button11.grid(row=4,column=3, pady=12, padx=11)

        self.button12=Button(window, text="Heat Index = " +hi, height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button12.grid(row=4,column=0, pady=12, padx=11)
        
        s_setTemp = str(setTemp)
        button13Txt = "AC Set Temp = " +s_setTemp
        self.button13=Button(window, text=button13Txt,  height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont)
        self.button13.grid(row=3,column=3, pady=12, padx=11)

        self.button14=Button(window, text="", height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button14.grid(row=5,column=0, pady=12, padx=11)
        
        if readIO.readPin(11) == 0:
            self.button15=Button(window, text="EXT GEN (ON)", height = 5, width = 15, bg='green', fg='#ffffff', font=self.buttonFont, state="disabled")
            self.button15.grid(row=5,column=1, pady=12, padx=11)
        else:
            self.button15=Button(window, text="EXT GEN", height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
            self.button15.grid(row=5,column=1, pady=12, padx=11)

        self.button16=Button(window, text="", height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button16.grid(row=5,column=2, pady=12, padx=11)        

        self.button17=Button(window, text="", height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.buttonFont, state="disabled")
        self.button17.grid(row=5,column=3, pady=12, padx=11)     

        self.button18=Button(window, text="", height = 5, width = 15, bg='#0052cc', fg='#ffffff', font=self.logfont)
        self.button18.grid(row=3,column=1, pady=12, padx=11)



        window.mainloop()

    def rvEnable(self):
        if self.buttonDown0 == 0 :
            self.buttonDown0 = 1
            self.button0.configure(bg='green')
        elif self.buttonDown0 == 1 :
            self.button0.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown0 = 0
    def kitchenLight(self):
        if self.buttonDown1 == 0 :
            mcp.pinMode(0, mcp.OUTPUT)
            mcp.output(0, mcp.LOW)
            self.buttonDown1 = 1
            logging.info("Kitchen Light On")
            self.button1.configure(bg='green')
        elif self.buttonDown1 == 1 :
            mcp.pinMode(0, mcp.OUTPUT)
            mcp.output(0, mcp.HIGH)
            logging.info("Kitchen Light Off")
            self.button1.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown1 = 0
    def genStart(self):
        if powerControl.checkGen1Status() == False :
            powerControl.startGen1(gen1)
            if powerControl.checkGen1Status() == True :
                self.button2['text'] = "Generator (ON)"
                logging.info("Generator is ON")
                self.button2.configure(bg='green')
            elif powerControl.checkGen1Status() == False :
                self.button2['text'] = "Generator (Start Fail)"
                logging.info("Fail to start generator")
                self.button2.configure(bg='yellow')
        if powerControl.checkGen1Status() == True :
            powerControl.stopGen1(self)
            if powerControl.checkGen1Status() == False :
                self.button2['text'] = "Generator START"
                logging.info("Commanding Generator Start")
                self.button2.configure(bg='#0052cc', fg='#ffffff')
            elif powerControl.checkGen1Status() == True :
                self.button2['text'] = "Generator (Stop Fail)"
                logging.info("Generator Stop Failure")
                self.button2.configure(bg='red', fg='#ffffff')
    def outsideLights(self):
        if self.buttonDown3 == 0 :
            mcp.pinMode(6, mcp.OUTPUT)
            mcp.output(6, mcp.LOW)
            self.buttonDown3 = 1
            logging.info("Outside lights on")
            self.button3.configure(bg='green')
        elif self.buttonDown3 == 1 :
            mcp.pinMode(6, mcp.OUTPUT)
            mcp.output(6, mcp.HIGH)
            logging.info("Outside lights Off")
            self.button3.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown3 = 0
    def waterHeater(self):
        if self.buttonDown4 == 0 :
            mcp.pinMode(4, mcp.OUTPUT)
            mcp.output(4, mcp.LOW)
            self.buttonDown4 = 1
            logging.info("Water Heater On")
            self.button4.configure(bg='green')
        elif self.buttonDown4 == 1 :
            mcp.pinMode(4, mcp.OUTPUT)
            mcp.output(4, mcp.HIGH)
            logging.info("Water Heater Off")
            self.button4.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown4 = 0
    def waterPump(self):
        if self.buttonDown5 == 0 :
            mcp.pinMode(5, mcp.OUTPUT)
            mcp.output(5, mcp.LOW)
            self.buttonDown5 = 1
            logging.info("Water Pump On")
            self.button5.configure(bg='green')
        elif self.buttonDown5 == 1 :
            mcp.pinMode(5, mcp.OUTPUT)
            mcp.output(5, mcp.HIGH)
            logging.info("Water Pump Off")
            self.button5.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown5 = 0
    def step(self):
        if self.buttonDown6 == 0 :
            mcp.pinMode(1, mcp.OUTPUT)
            mcp.output(1, mcp.LOW)
            self.buttonDown6 = 1
            logging("Step On")
            self.button6.configure(bg='green')
        elif self.buttonDown6 == 1 :
            mcp.pinMode(1, mcp.OUTPUT)            
            mcp.output(1, mcp.HIGH)
            logging.info("Step Off")
            self.button6.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown6 = 0
    def porchLight(self):
        if self.buttonDown7 == 0 :
            print("This should be 0: " +str(self.buttonDown7))
            mcp.pinMode(3, mcp.OUTPUT)            
            mcp.output(3, mcp.LOW)
            self.buttonDown7 = 1
            logging.info("Porch Light On")
            self.button7.configure(bg='green')
        elif self.buttonDown7 == 1 :
            print("This should be 1: " +str(self.buttonDown7))
            mcp.pinMode(3, mcp.OUTPUT)
            mcp.output(3, mcp.HIGH)
            logging.info("Porch Light Off")
            self.button7.configure(bg='#0052cc', fg='#ffffff')
            self.buttonDown7 = 0
    def inverter(self):
        logging.info("Inverter Toggle Called")
        powerControl.inverter_toggle(self)
    def acStart(self):
        global buttonDown9
        print(buttonDown9)
        if buttonDown9 == 0 :
            buttonDown9 = 1
            logging.info("A/C Enabled")
            self.button9.configure(bg='green')
        elif buttonDown9 == 1 :
            self.button9.configure(bg='#0052cc', fg='#ffffff')
            logging.info("A/C Disabled")
            buttonDown9 = 0
            if powerControl.checkGen1Status == True :
                powerControl.stopGen1(self)
    def acDown(self):
        self.setTemp -= 1
        global setTemp
        setTemp = self.setTemp
        self.s_setTemp = str(self.setTemp)
        logging.info("A/C Temp Down "+ self.s_setTemp)
        self.button13Txt = "AC Set Temp = " +self.s_setTemp
        self.button13['text'] = self.button13Txt
    def acUp(self):
        self.setTemp += 1
        global setTemp
        setTemp = self.setTemp
        self.s_setTemp = str(self.setTemp)
        logging.info("A/C Temp Up "+ self.s_setTemp)
        self.button13Txt = "AC Set Temp = " +self.s_setTemp
        self.button13['text'] = self.button13Txt
    def updateHI(self, hi):
        i_hi = float(hi)
        i_hi = int(i_hi)
        self.button12Txt = "Heat Index = " +str(hi)
        #print(self.button12Txt)

        if i_hi >> 89 :
            self.button12['bg'] ='red'
            self.button12['text'] = self.button12Txt
        elif i_hi <= 90 :
            self.button12['bg'] ='green'
            self.button12['text'] = self.button12Txt

class readIO:
    def __init__(self, mcp, pin):
        self.pin = pin
        i = 8
        while i <=15 :
            mcp.pinMode(i, mcp.INPUT)
            mcp.pullUp(i, 0)      
            i += 1       
                      
    def readPin(pin):
        mcp = MCP23017(address = 0x24, num_gpios = 16)
        ret = mcp.currentVal(pin)
        return ret

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
                    configParams['relayHatAddress'],
                    configParams['numberOfTries'],
                    configParams['callSign'])
        gen2 = powerControl(configParams['gen2Name'],
                    configParams['gen1Start_out'],
                    configParams['gen1Run_in'],
                    configParams['gen1Stop_out'],
                    configParams['gen2Name'],
                    configParams['gen2Enable_out'],
                    configParams['chargerEnable_out'],
                    configParams['relayHatBus'],
                    configParams['relayHatAddress'],
                    configParams['numberOfTries'],
                    configParams['callSign'])
        inverter = powerControl(configParams['inverterSense'],
                    configParams['gen1Name'],
                    configParams['gen1Start_out'],
                    configParams['gen1Run_in'],
                    configParams['gen1Stop_out'],
                    configParams['gen2Name'],
                    configParams['gen2Enable_out'],
                    configParams['chargerEnable_out'],
                    configParams['relayHatBus'],
                    configParams['relayHatAddress'],
                    configParams['numberOfTries'],
                    configParams['callSign'])
        charger = powerControl(configParams['gen1Name'],
                    configParams['gen1Start_out'],
                    configParams['gen1Run_in'],
                    configParams['gen1Stop_out'],
                    configParams['gen2Name'],
                    configParams['gen2Enable_out'],
                    configParams['chargerEnable_out'],
                    configParams['relayHatBus'],
                    configParams['relayHatAddress'],
                    configParams['numberOfTries'],
                    configParams['callSign'])    
        pins = setupPins(configParams['temp1_in'],
                    configParams['ptt_out'],
                    configParams['radioCharger1_out'],
                    configParams['radioCharger2_out'])  
        mqtt_ = mqtt_sub(configParams['mqtt_feed'],
                    configParams['mqtt_host'],
                    configParams['mqtt_password'],
                    configParams['mqtt_port'],
                    configParams['mqtt_username'],
                    buttonDown7 = 0,
                    setTemp=82 )            
    setupPins(22, 27, 20, 21)
    inverterStatus = 0
    hi = "0"
    setTemp = 82
    pin = 0
    c0deTime = 0
    global buttonDown0
    buttonDown0 = 0
    global buttonDown1
    buttonDown1 = 0
    global buttonDown2
    buttonDown2 = 0
    global buttonDown3
    buttonDown3 = 0
    global buttonDown4
    buttonDown4 = 0
    global buttonDown5
    buttonDown5 = 0
    global buttonDown6
    buttonDown6 = 0
    global buttonDown7
    buttonDown7 = 0
    global buttonDown8
    buttonDown8 = 0  
    global buttonDown9     
    buttonDown9 = 0
    global buttonDown10
    buttonDown10 = 0
    global buttonDown11
    buttonDown11 = 0
    global buttonDown12
    buttonDown12 = 0
    global buttonDown13
    buttonDown13 = 0
    mcp = MCP23017(address = 0x24, num_gpios = 16) # MCP2301
    gui(window, hi, setTemp)
    mqtt_thread = threading.Thread(target=mqtt_sub.connect(mqtt_))
    gui_thread = threading.Thread(target=gui(window, hi, setTemp))    
    mqtt_thread.start()
    gui_thread.start()
    gui_thread.join()
    mqtt_thread.join()