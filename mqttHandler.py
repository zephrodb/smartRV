#~/usr/bin/python3
from Adafruit_I2C import Adafruit_I2C
from MCP23017 import MCP23017
import paho.mqtt.client as mqtt
from smbus2 import SMBus
import yaml
import RPi.GPIO as GPIO


class MQTTSubscriber:
    def __init__(self, mqtt_topic, mqtt_broker, mqtt_password, mqtt_port, mqtt_user ):
        self.mqtt_topic = mqtt_topic
        self.mqtt_broker = mqtt_broker
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
    def on_connect(self, client, userdata, flags, rc):
        print("MQTT Subbed")
        print("Connected with result code: ", str(rc))        
    def connect(self):
        try:
            client = mqtt.Client("rosebud_mqtt")  
            client.username_pw_set(self.mqtt_user, self.mqtt_password)
            client.on_message = self.on_message
            client.on_connect = self.on_connect
            client.connect(self.mqtt_broker, self.mqtt_port)
            client.subscribe(self.mqtt_topic)
            print("subscribing to topic : "+self.mqtt_topic)        
            client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
        



if __name__ == "__main__":
    
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(levelname)s %(message)s',
    #                     filename='smartRV.log',
    #                     filemode='a+')
    # logging.info('Starting SmartRV...')

    with open(r'./config.yaml') as configFile:
        configParams = yaml.load(configFile, Loader=yaml.FullLoader) #converting text to a dict(in-memory k,v store)



        mqtt_ = MQTTSubscriber(configParams['mqtt_topic'],
                    configParams['mqtt_broker'],
                    configParams['mqtt_password'],
                    configParams['mqtt_port'],
                    configParams['mqtt_user'])   

    MQTTSubscriber.connect("null")