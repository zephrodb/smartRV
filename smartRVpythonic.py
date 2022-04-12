#!/c/Users/Jeremy/AppData/Local/Programs/Python/Python38-32/python
import logging
import yaml

class environmentThresholds:
    def __init__(self, highHumidity, highTemp, medHumidity, medTemp):
        self.highHumidity = highHumidity
        self.highTemp = highTemp
        self.medHumidity = medHumidity
        self.medTemp = medTemp

class radio:
    def __init__(self, callSign, enableDTMF):
        self.callSign = callSign
        self.enableDTMF = enableDTMF
    #this is a method on the radio object
    def enableDTMF(self):
        self.enableDTMF = True
    #this is a method on the radio object
    def disableDTMF(self):
        self.enableDTMF = False     

class generator:
    def __init__(self, gennyName, gennyRunning=False, fuelLevel=0):
        self.gennyRunning = gennyRunning
        self.fuelLevel = fuelLevel
        self.Name = gennyName

    def gennyStatus(self):
        #TODO need to add logic to actually check status
        return self.gennyRunning

    def startGenny(self):
        if self.gennyStatus() == False:
            msg = "starting generator"
            logging.info(msg + " " + self.Name)
            #TODO need to add logic to actually start genny
            return msg 
        else:
            msg = "generator already running"
            logging.info(msg + " " + self.Name) 
            return msg 

    def stopGenny(self):
        if self.gennyStatus():
            msg = "stopping generator"
            logging.info(msg + " " + self.Name) 
            #TODO need to add logic to actually stop genny
            return msg 
        else:
            msg = "generator not started"
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
                    configParams['enableDTMF']) 
        #assigning dict valuses to an object

        onBoardGenny = generator(gennyName=configParams['bigGennyName'])
        babyGenny = generator(gennyName=configParams['extraGennyName'])

    print(env.highHumidity)   
    print(rad.enableDTMF)
    print(rad.callSign)
    print(onBoardGenny.Name)
    msg = onBoardGenny.startGenny()
    print(msg)
    msg = onBoardGenny.stopGenny()
    print(msg)
     