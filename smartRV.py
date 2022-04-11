#!/usr/bin/python3
# /etc/init.d/smartRV.py
### BEGIN INIT INFO
# Provides:          smartRV
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INF

from cgitb import text
from gpiozero import CPUTemperature
import time
import os
import schedule
import adafruit_dht
import board
import RPi.GPIO as GPIO
import datetime
import sys
import pyttsx3

date = datetime.datetime.now()
original_stdout = sys.stdout # Save a reference to the original standard output
dhtDevice = adafruit_dht.DHT11(board.D4)
language = 'en'
highHumidity = 35
highTemp = 83
medHumidity = 35
medTemp = 83
autoPowerOn = 85 
callSign = "W R F R 8 8 6"
tld="com.au"
gennyRunning = 0
snooze = 10
enableDTMF = 1

RELAY_PTT_GPIO = 17
RELAY_GENSTART_GPIO = 27
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setup(RELAY_PTT_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.setup(RELAY_GENSTART_GPIO, GPIO.OUT) # GPIO Assign mode
engine = pyttsx3.init()

def listenForDTMF() :
    if enableDTMF == 1 :
        it = "rtl_fm -M wbfm -f 146520000 -s 22050 | timeout {} multimon-ng -t raw -a FMSFSK -a AFSK1200 -a DTMF /dev/stdin > DTMF.txt &"
        os.system(it)
        print("listening")

def allRelaysHIGH() :
        print("All Relays going HIGH(off)")
        GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # out
        GPIO.output(RELAY_GENSTART_GPIO, GPIO.HIGH) # out
        
def gennyStatus() :
    if GPIO.input(26):
        print("Generator is ON")
        gennyRunning = 1
    else:
        print("Generator is OFF")
        gennyRunning = 0

def callsign() :
    try:
        date = datetime.datetime.now()
        text = "Hello, This is an automated reporting system, this is {}.".format(callSign)
        print(text)
        GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
        time.sleep(.5)                
        speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
        os.system(speak)        
        time.sleep(.5)
        GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # out
        log = "{}, {}".format(date, text)
        xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
        os.system(xmitLog)
    except:
        allRelaysHIGH
        do_start 

def startGenny() :
    gennyStatus()
    try:
        if gennyRunning == 0 :
            print("Starting Genny")
            GPIO.output(RELAY_GENSTART_GPIO ,GPIO.LOW) # on
            print("Cranking 1 seconds")
            time.sleep(1)
            GPIO.output(RELAY_GENSTART_GPIO, GPIO.HIGH) # on
            GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # out
            time.sleep(.5)
            print("Done Cranking, wait 30 seconds for power")
            time.sleep(.5)
            GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # out
            time.sleep(32)
            gennyStatus()
            if gennyRunning == 0 :
                text = "good ole genny failed to start fall back is one minute and another attempt is made"
                print(text)
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)
                date = datetime.datetime.now()
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak)                
                time.sleep(.5)
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # out
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
            elif gennyRunning == 1 :
                text = "genny has started monitoring will remain at one minute intervals untill temp is normal"
                print(text)
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)
                date = datetime.datetime.now()
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak)   
                os.system("mpg123 -q -o alsa:hw:1,0 text.mp3")
                time.sleep(.5)
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # out
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
    except:
        allRelaysHIGH
        do_start

def do_start() :
        listenForDTMF()
        allRelaysHIGH()
        schedule.every(2).minutes.do(readTemp)
        schedule.every(550).seconds.do(callsign)
        #listenForDTMF()
        #allRelaysHIGH()
        readTemp()


def readTemp() :
    allRelaysHIGH()
    while 1:
        try:
            temperature_c = dhtDevice.temperature
            temperature_c = int(temperature_c)
            temperature_f = temperature_c * (9 / 5) + 32
            temperature_f = int(temperature_f)
            humidity = dhtDevice.humidity
            gennyStatus()
            if temperature_f < medTemp :
                if gennyRunning == 0 :
                    text = "Hello, This is an automated reporting system, current conditions inside rosebud explorer the temperature is {}. humidity is {} percent, this is {}".format(temperature_f, humidity, callSign)
                else:
                    text = "Hello, This is an automated reporting system, current conditions inside rosebud explorer the temperature is {}. humidity is {} percent. The generator is running This is {}".format(temperature_f, humidity, callSign)
                print(text)
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)      
                date = datetime.datetime.now()          
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak)         
                time.sleep(.5)
                date = datetime.datetime.now()
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # off
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
                break
            elif temperature_f < highTemp and temperature_f > medTemp :
                if gennyRunning == 0 :
                    text = "Hello, This is an automated reporting system, current conditions inside rosebud explorer the temperature is {}. humidity is {} percent. this is getting warm! Fortunatlety the generator is running This is {}".format(temperature_f, humidity, callSign)
                else :
                    text = "Hello, This is an automated reporting system, current conditions inside rosebud explorer the temperature is {}. humidity is {} percent. this is getting warm! warning, generator is off This is {}".format(temperature_f, humidity, callSign)
                print(text)
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)                
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak) 
                date = datetime.datetime.now()
                time.sleep(.5)
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # off
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
            elif temperature_f > highTemp and gennyRunning == 0 :
                text = "Hello, This is an automated reporting system, the conditions inside rosebud explorer the temperature is {} humidity is percent {} the generator is starting fallback is 30 seconds".format(temperature_f, humidity)
                print(text1)               
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)                
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak)       
                date = datetime.datetime.now()      
                time.sleep(2)
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak) 
                date = datetime.datetime.now()
                time.sleep(.5)
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # off
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
                startGenny()
            elif temperature_f > highTemp and gennyRunning == 1 :
                text = "Hello, This is an automated reporting system, the conditions inside rosebud explorer the temperature is {} humidity is percent {} the generator is running. reporting is set to one minute This is {}".format(temperature_f, humidity, callSign)
                print(text1)
                GPIO.output(RELAY_PTT_GPIO, GPIO.LOW) # on
                time.sleep(.5)                
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                os.system(speak)
                date = datetime.datetime.now()
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
                os.system(speak)
                date = datetime.datetime.now()             
                time.sleep(2)
                text = "repeating, repeating This is an automated reporting system, the conditions inside rosebud explorer the temperature is {} humidity is percent {} the generator is running. reporting is set to one minute This is {}".format(temperature_f, humidity, callSign)
                speak = 'espeak -s 125 "{}" > /dev/null 2>&1'.format(text)
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                os.system(xmitLog)
                os.system(speak) 
                date = datetime.datetime.now()             
                time.sleep(.5)
                log = "{}, {}".format(date, text)
                xmitLog = "echo {} >> /home/pi/monitor/xmit.log".format(log)
                GPIO.output(RELAY_PTT_GPIO, GPIO.HIGH) # off.
        except:    
            allRelaysHIGH()
            readTemp()

do_start()

while 1:
    schedule.run_pending()
    time.sleep(1)


