import paho.mqtt.client as mqtt

# Define the MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC = "homeassistant/switch/#"
USERNAME = "mqtt_user"
PASSWORD = "mqtt_user"

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a connection response from the server."""
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    #print(f"Topic: {msg.topic} | Message: {msg.payload.decode()}")
    payload = msg.payload.decode()
    if "homeassistant/switch/" in msg.topic and "set" in msg.topic:
        device = msg.topic.lstrip("homeassistant/switch/")
        print(device)
        print(payload)
        if payload == "ON":
            print("ON")
        elif payload == "OFF":
            print("OFF")
def main():
    # Create an MQTT client instance
    client = mqtt.Client()

    # Set the username and password for the MQTT client
    client.username_pw_set(USERNAME, PASSWORD)

    # Assign the on_connect and on_message callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(BROKER, PORT, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()

if __name__ == "__main__":
    main()