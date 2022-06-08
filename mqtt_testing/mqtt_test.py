#!/usr/bin/python
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("/feeds/stats")  # Subscribe to the topic “digitest/test1”, receive any messages published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    payld = str(msg.payload)
    #print("Message received-> " + msg.topic + " " + payld)  # Print a received msg
    if 't_0' in payld:
        if 'temp_F' in payld:
            temp_f = payld.split("=")[2]
            print("Temp F     = " + temp_f.strip(" '"))
        elif "RH" in payld:
            rh = payld.split("=")[2]   
            print("Humidity   = " + rh.strip(" '")) 
        elif "HI" in payld:
            hi = payld.split("=")[2]   
            print("Heat Index = " + hi.strip(" '")) 


client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
client.username_pw_set("dale", "paleale")
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect('127.0.0.1', 1883)
client.loop_forever()  # Start networking daemon