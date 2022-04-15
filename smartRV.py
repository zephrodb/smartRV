#!/usr/bin/python
from email import message
import logging
import yaml
import adafruit_dht
import board
import RPi.GPIO as GPIO
import time
import os
from espeakng import ESpeakNG
import datetime

esng = ESpeakNG()
class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp
class setupPins:
    def __init__(self, Temp1Pin, Temp2Pin, BigGenRunSense, LittleGenRunSense, LowVSense, PTTRelayPin, bigGenStartRelayPin, bigGenEnableRelayPin, LittleGenEnableRelayPin, ChargerEnableRelayPin, InverterEnableRelayPin, CT1):
        try :
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(Temp1Pin, GPIO.IN)
            GPIO.setup(Temp2Pin, GPIO.IN)
            GPIO.setup(BigGenRunSense, GPIO.IN)
            GPIO.setup(LittleGenRunSense, GPIO.IN)
            GPIO.setup(LowVSense, GPIO.IN)
            GPIO.setup(CT1, GPIO.IN)
            GPIO.setup(PTTRelayPin, GPIO.OUT)
            GPIO.setup(bigGenStartRelayPin, GPIO.OUT)
            GPIO.setup(bigGenEnableRelayPin, GPIO.OUT)
            GPIO.setup(LittleGenEnableRelayPin, GPIO.OUT)
            GPIO.setup(ChargerEnableRelayPin, GPIO.OUT)
            GPIO.setup(InverterEnableRelayPin, GPIO.OUT)
        except:
            print("looks like we crapped out pants in setupPins")
            exit
        print("Setup Pins Done")

class allRelaysDeenergize:
    def __init__(self, PTTRelayPin, bigGenStartRelayPin, bigGenEnableRelayPin, LittleGenEnableRelayPin, ChargerEnableRelayPin, InverterEnableRelayPin):
        #pull down all the relays.
        GPIO.output(PTTRelayPin, GPIO.HIGH)
        GPIO.output(bigGenStartRelayPin, GPIO.HIGH)
        GPIO.output(bigGenEnableRelayPin, GPIO.HIGH)
        GPIO.output(LittleGenEnableRelayPin, GPIO.HIGH)
        GPIO.output(ChargerEnableRelayPin, GPIO.HIGH)
        GPIO.output(InverterEnableRelayPin, GPIO.HIGH)
        print("Relays all down")
class radio:
    def __init__(self, callSign, DTMFOperStatus, PTTRelayPin, freq):
        self.PTTRealyPin = PTTRelayPin
        self.callSign = callSign
        self.DTMFOperStatus = DTMFOperStatus
        self.freq = freq
    #this is a method on the radio object
    def enableDTMF(freq):
        #self.freq = freq
        DTMFOperStatus = True
        it = "rtl_fm -M wbfm -f {} -s 22050 | multimon-ng -t raw -a FMSFSK -a AFSK1200 -a DTMF /dev/stdin > DTMF.txt & ".format(freq)
        os.system(it)
        print("Listening to DTMF")


    #this is a method on the radio object
    def disableDTMF(self):
        self.DTMFOperStatus = False
    def xmit(self, xmitText, repeat):
        while repeat > 0 :
            esng.speed = 120
            xmitStart = datetime.datetime.now()
            GPIO.output(self.PTTRelayPin, GPIO.LOW) # xmit start
            time.sleep(1.5)                
            speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(xmitText)
            esng.say(xmitText)
            os.system(speak)        
            time.sleep(.5)
            GPIO.output(self.PTTRelayPin, GPIO.HIGH) # xmit end
            xmitEnd = datetime.datetime.now()
            logging.info(xmitStart + xmitEnd + xmitText)
            if repeat > 0 :
                repeat = repeat-1

class controlGenerators:
    def __init__(self, generatorEnableRelay, generatorStartRelay, gennyName, altCheckPin, PTTRelayPin) :
        self.enableRelay = generatorEnableRelay
        self.gennyName = gennyName
        self.pin = altCheckPin
        self.startRelay = generatorStartRelay
        self.PTTRelayPin = PTTRelayPin
    
    def genStatus(self) :
        output = GPIO.input(self.pin)
        if output == 0 :
            genRunning = True
            return True
        elif output == 1 :
            genRunning = False
            return False
    
    def stopGenerators(self, generatorEnableRelay, generatorStartRelay, gennyName, altCheckPin, PTTRelayPin) :
        self.generatorEnableRelay = generatorEnableRelay
        self.gennyName = gennyName
        self.pin = altCheckPin
        self.startRelay = generatorStartRelay
        self.PTTRelayPin = PTTRelayPin
        if controlGenerators.genStatus(self.pin) == True:
            msg = "stopping little generator"
            logging.info(msg)
            GPIO.output(generatorEnableRelay, GPIO.HIGH)
            time.sleep(5)
        else :
            msg = "Can't stop something not running. How did we get here?"
            logging.info(msg)
            return msg
        output = GPIO.input(self.pin)
        if output == 0 :
            genRunning = True
            msg = "{} generator failed to stop. Not good. What should we do now?".format(gennyName)
            logging.info(msg)
            radio.xmit(self.PTTRelayPin, msg, 1)
            return msg
        elif output == 1 :
            genRunning = False
            msg = "{} generator stopped".format(gennyName)
            logging.info(msg)
            radio.xmit(PTTRelayPin, msg, 1)
            return msg

class powerControl:
    def __init__(self, gennyName, startRelay, enableRelay, InverterEnableRelayPin, ChargerEnableRelayPin, crankTime, altCheckPin, fuelLevel=0 ): 
        self.fuelLevel = fuelLevel
        self.gennyName = gennyName
        self.startRelay = startRelay
        self.enableRelay = enableRelay
        self.inverterEnable = InverterEnableRelayPin    
        self.chargerEnable = ChargerEnableRelayPin
        self.crankTime = crankTime
        self.altCheckPin = altCheckPin
            
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='smartRV.log',
                        filemode='a+')
    logging.info('Starting SmartRV...')




    with open(r'./config.yaml') as configFile: 
        #using the with command with the open is a context manager
        # and will auto close after the operations are done
        # print(configFile.read()) #Reading file as text
        configParams = yaml.load(configFile, Loader=yaml.FullLoader) #converting text to a dict(in-memory k,v store) 

        env = environmentThresholds(configParams['highHumidity'],
                                    configParams['highTemp'],
                                    configParams['medHumidity'],
                                    configParams['medTemp']) 
        radio(configParams['DTMFOperStatus'],
                    configParams['callSign'],
                    configParams['PTTRelayPin'],
                    configParams['freq']) 
        bigGen = controlGenerators(configParams['bigGenEnableRelayPin'],
                        configParams['bigGenStartRelayPin'],
                        configParams['bigGenName'],
                        configParams['bigAltCheckPin'],
                        configParams['PTTRelayPin'])
        littleGen = controlGenerators(configParams['littleGenEnableRelayPin'],
                        configParams['littleGenStartRelayPin'],
                        configParams['littleGenName'],
                        configParams['littleAltCheckPin'],
                        configParams['PTTRelayPin'])                        
        setupPins(configParams['Temp1Pin'],
                configParams['Temp2Pin'],
                configParams['bigAltCheckPin'],
                configParams['littleAltCheckPin'],
                configParams['LowVSense'],
                configParams['PTTRelayPin'],
                configParams['bigGenStartRelayPin'],
                configParams['bigGenEnableRelayPin'],
                configParams['littleGenEnableRelayPin'],
                configParams['ChargerEnableRelayPin'],
                configParams['InverterEnableRelayPin'],
                configParams['CT1'])   
  
                    
    print(f"this is the big gen name {bigGen.gennyName}")
    print(bigGen.enableRelay, bigGen.startRelay, bigGen.gennyName, bigGen.pin, bigGen.PTTRelayPin)
    ###########
    # this works, but doesnt background
    # test it when you get a chance
    #radio.enableDTMF("462.7250M")
    
    ###########
    # this?
    # controlGenerators.stopGenerators(bigGen.enableRelay, bigGen.startRelay, bigGen.gennyName, bigGen.pin, bigGen.PTTRelayPin)
    # or this
    # controlGenerators.stopGenerators(bigGen)
    # wontwork

    
