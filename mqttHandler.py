#~/usr/bin/python3
from Adafruit_I2C import Adafruit_I2C
from MCP23017 import MCP23017
import paho.mqtt.client as mqtt
from smbus2 import SMBus
import yaml
#import RPi.GPIO as GPIO


class MQTTSubscriber:
    def __init__(self, mqtt_topic, mqtt_broker, mqtt_password, mqtt_port, mqtt_username):
        self.mqtt_topic = mqtt_topic
        self.mqtt_broker = mqtt_broker
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        print(self.mqtt_username, self.mqtt_password)
        client = mqtt.Client("rosebud_mqtt") 
        client.username_pw_set("mqtt_user", "self.mqtt_user")
    def on_connect(self, client):
        print("MQTT Subbed")
        #print("Connected with result code: ", str(rc)) 
        client.on_message = MQTTSubscriber.on_message       
    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    def connect(self, client):
        
        try:
            # print(self.mqtt_username, self.mqtt_password)

            client.connect("localhost")
            try:
                client.subscribe("homeassistant/switch/state/#")
                print("subscribing to topic : "+"homeassistant/switch/state/")
            except Exception as e:
                print(f"Failed to subscribe to topic homeassistant/switch/state/: {e}")
            client.loop_start()
            print("call loop.start")
            MQTTSubscriber.on_connect(self, client)
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
                    configParams['mqtt_username']
                    )   
    client = mqtt.Client("rosebud_mqtt")
    MQTTSubscriber.connect("null", client)
    client.username_pw_set("mqtt_user", "self.mqtt_user")
    client.on_message = MQTTSubscriber.on_message
    client.on_connect = MQTTSubscriber.on_connect