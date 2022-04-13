#!/c/Users/Jeremy/AppData/Local/Programs/Python/Python38-32/python
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

class generator:
    def __init__(self, gennyName, BigGenStartRelayPin, BigGenEnableRelayPin, LittleGenEnableRelayPin, InverterEnableRelayPin, ChargerEnableRelayPin, gennyRunning=False, fuelLevel=0,): 
        self.gennyRunning = gennyRunning
        self.fuelLevel = fuelLevel
        self.Name = gennyName
        #Had to change the names here since this is the template
        #the onBoardGen object is the instance of the big gen
        #baby gen is for the little one
        self.RelayGenStartGPIO = BigGenStartRelayPin
        self.RelayGenEnableGPIO = BigGenEnableRelayPin
        self.RelayGenEnableGPIO = LittleGenEnableRelayPin
        self.RelayGenEnableGPIO = InverterEnableRelayPin
        self.RelayGenEnableGPIO = ChargerEnableRelayPin

    def checkGennyStatus(self):
        #TODO need to add logic to actually check status
        return self.gennyRunning

    def startGenny(self):
        if self.checkGennyStatus() == False:
            msg = "starting generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually start genny
            return msg 
        else:
            msg = "Unable to start generator, it is already running"
            logging.info(msg + " " + self.Name) 
            return msg 

    def stopGenny(self):
        if self.checkGennyStatus() == True:
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

        #the things that are read into the generator object are read in order. You can assign them all manually but it's not really necessary
        onBoardGenny = generator(configParams['bigGennyName'], 
                                 configParams['BigGenStartRelayPin'], 
                                 configParams['BigGenEnableRelayPin'])
        babyGenny = generator(configParams['extraGennyName'], 
                              configParams['LittleGenEnableRelayPin'])
        inverter = generator(configParams['InverterEnableRelayPin'])
        charger = generator(configParams['ChargerEnableRelayPin'])                              


    print(env.highHumidity)   
    print(rad.DTMFOperStatus)
    print(rad.callSign)
    print(onBoardGenny.Name)
    msg = onBoardGenny.startGenny()
    print(msg)
    msg = onBoardGenny.stopGenny()
    print(msg)
    GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
    # GPIO.setup(RELAY_PTT_GPIO, GPIO.OUT) # GPIO Assign mode

    ### Look here, we're accessing the same property of the two different instances of the generator object
    print("Big Genny relay Start pin "+onBoardGenny.BigGenStartRelayPin)
    print("Big Genny relay enable pin "+onBoardGenny.BigGenEnableRelayPin)
    print("Little Genny relay enable pin "+babyGenny.LittleGenEnableRelayPin)
    print("Little Genny relay enable pin "+inverter.InverterEnableRelayPin)
    print("Little Genny relay enable pin "+charger.ChargerEnableRelayPin)
    
    GPIO.setup(onBoardGenny.BigGenStartRelayPin, GPIO.OUT) # GPIO Assign mode  
    GPIO.setup(onBoardGenny.BigGenEnableRelayPin, GPIO.OUT) # GPIO Assign mode
    GPIO.setup(onBoardGenny.LittleGenEnableRelayPin, GPIO.OUT) # GPIO Assign mode  
    GPIO.setup(onBoardGenny.ChargerEnableRelayPin, GPIO.OUT) # GPIO Assign mode  
    GPIO.setup(onBoardGenny.InverterEnableRelayPin, GPIO.OUT) # GPIO Assign mode  
    GPIO.setup(rad.PTTRelayPin, GPIO.OUT) # GPIO Assign mode  



