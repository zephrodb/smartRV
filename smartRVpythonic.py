import logging
import yaml
import adafruit_dht
import board
import RPi.GPIO as GPIO

class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp
class setupPins:
    def __init__(Temp1Pin, Temp2Pin, BigGenRunSense, LittleGenRunSense, LowVSense, PTTRelayPin, BigGenStartRelayPin, BigGenEnableRelayPin, LittleGenEnableRelayPin, ChargerEnableRelayPin, InverterEnableRelayPin, CT1):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Temp1Pin, GPIO.IN)
        GPIO.setup(Temp2Pin, GPIO.IN)
        GPIO.setup(BigGenRunSense, GPIO.IN)
        GPIO.setup(LittleGenRunSense, GPIO.IN)
        GPIO.setup(LowVSense, GPIO.IN)
        GPIO.setup(CT1, GPIO.IN)
        GPIO.setup(PTTRelayPin, GPIO.OUT)
        GPIO.setup(BigGenStartRelayPin, GPIO.OUT)
        GPIO.setup(BigGenEnableRelayPin, GPIO.OUT)
        GPIO.setup(LittleGenEnableRelayPin, GPIO.OUT)
        GPIO.setup(ChargerEnableRelayPin, GPIO.OUT)
        GPIO.setup(InverterEnableRelayPin, GPIO.OUT)
        print("Setup Pins")

class allRelaysDeenergize:
    def __init__(PTTRelayPin, BigGenStartRelayPin, BigGenEnableRelayPin, LittleGenEnableRelayPin, ChargerEnableRelayPin, InverterEnableRelayPin):
        #pull down all the relays.
        GPIO.output(PTTRelayPin, GPIO.HIGH)
        GPIO.output(BigGenStartRelayPin, GPIO.HIGH)
        GPIO.output(BigGenEnableRelayPin, GPIO.HIGH)
        GPIO.output(LittleGenEnableRelayPin, GPIO.HIGH)
        GPIO.output(ChargerEnableRelayPin, GPIO.HIGH)
        GPIO.output(InverterEnableRelayPin, GPIO.HIGH)
        print("Relays all down")
class radio:
    def __init__(self, callSign, DTMFOperStatus, PTTRelayPin):
        self.callSign = callSign
        self.DTMFOperStatus = DTMFOperStatus
        self.PTTRelayPin = PTTRelayPin
    #this is a method on the radio object
    def enableDTMF(self):
        self.DTMFOperStatus = True
    #this is a method on the radio object
    def disableDTMF(self):
        self.DTMFOperStatus = False

class powerControl:
    def __init__(self, BigGennyName, LittleGennyName, BigGenStartRelayPin, BigGenEnableRelayPin, LittleGenEnableRelayPin, InverterEnableRelayPin, ChargerEnableRelayPin, BigGenRunning=False, fuelLevel=0,):
        self.BigGenRunning = BigGenRunning
        self.fuelLevel = fuelLevel
        self.BigName = BigGennyName
        self.LittleName = LittleGennyName
        self.BigGenStarter = BigGenStartRelayPin
        self.LittleGenEnable = LittleGenEnableRelayPin
        self.InverterEnable = InverterEnableRelayPin
        self.ChargerEnable = ChargerEnableRelayPin
        #Had to change the names here since this is the template
        #the onBoardGen object is the instance of the big gen
        #baby gen is for the little one
        self.RelayGenStartGPIO = BigGenStartRelayPin
        self.RelayGenEnableGPIO = BigGenEnableRelayPin
        self.RelayGenEnableGPIO = LittleGenEnableRelayPin
        self.RelayGenEnableGPIO = InverterEnableRelayPin
        self.RelayGenEnableGPIO = ChargerEnableRelayPin

    def checkBigGenStatus(self):
        #TODO need to add logic to actually check status
        return self.BigGenRunning

    def checkBigGenStatus(self):
        #TODO need to add logic to actually check status
        return self.BigGenRunning

    def startBigGen(self):
        if self.checkBigGenStatus() == False:
            msg = "starting generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually start genny
            return msg
        else:
            msg = "Unable to start generator, it is already running"
            logging.info(msg + " " + self.Name)
            return msg

    def stopBigGen(self):
        if self.checkBigGenStatus() == True:
            msg = "stopping generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually stop genny
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            logging.info(msg + " " + self.Name)
            return msg
    def stopLittleGen(self):
        if self.checkLittleGenStatus() == True:
            msg = "stopping generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually stop genny
            return msg
        else:
            msg = "Unable to stop generator, it is not running"
            logging.info(msg + " " + self.Name)
            return msg


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
        # print(configParams['highTemp']) #Printing specific parameter from dict

        env = environmentThresholds(configParams['highHumidity'],
                          configParams['highTemp'],
                          configParams['medHumidity'],
                          configParams['medTemp'])
        #assigning dict valuses to an object

        rad = radio(configParams['callSign'],
                    configParams['DTMFOperStatus'],
                    configParams['PTTRelayPin'])
        #assigning dict valuses to an object

        #the things that are read into the powerControl object are read in order. You can assign them all manually but it's not really necessary
        onBoardGenny = powerControl(configParams['BigGennyName'],
                                 configParams['BigGenStarter'],
                                 configParams['BigGenEnable'])
        babyGenny = powerControl(configParams['LittleGennyName'],
                              configParams['LittleGenEnable'])
        inverter = powerControl(configParams['InverterEnable'])
        charger = powerControl(configParams['ChargerEnable'])

    setupPins()
    allRelaysDeenergize()
    print(env.highHumidity)
    print(rad.DTMFOperStatus)
    print(rad.callSign)
    print(onBoardGenny.Name)
    msg = onBoardGenny.startGenny()
    print(msg)
    msg = onBoardGenny.stopGenny()
    print(msg)

    ### Look here, we're accessing the same property of the two different instances of the powerControl object
    print("Big Genny relay Start pin "+onBoardGenny.BigGenStartRelayPin)
    print("Big Genny relay enable pin "+onBoardGenny.BigGenEnableRelayPin)
    print("Little Genny relay enable pin "+babyGenny.LittleGenEnableRelayPin)
    print("Little Genny relay enable pin "+inverter.InverterEnableRelayPin)
    print("Little Genny relay enable pin "+charger.ChargerEnableRelayPin)
