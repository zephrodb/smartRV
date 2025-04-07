import paho.mqtt.client as mqtt
import Adafruit_I2C as I2C
from MCP23017 import MCP23017



# MCP23017 default I2C address
MCP23017_ADDRESS = 0x24

# MCP23017 register addresses
IODIRA = 0x00  # I/O direction register for port A
IODIRB = 0x01  # I/O direction register for port B
GPIOA = 0x12   # GPIO register for port A
GPIOB = 0x13   # GPIO register for port B


# Define the MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC = "homeassistant/switch/#"
USERNAME = "mqtt_user"
PASSWORD = "mqtt_user"

def on_connect(client: mqtt.Client, userdata: dict, flags: dict, rc: int) -> None:
    """Callback for when the client receives a connection response from the server."""
    if rc == 0:
        print("Connected successfully")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with result code {rc}")
        print("Connection failed, attempting to reconnect...")
        client.reconnect()

def on_message( client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    #print(f"Topic: {msg.topic} | Message: {msg.payload.decode()}")
    payload = msg.payload.decode()
    
    if "homeassistant/switch/" in msg.topic and "set" in msg.topic:
        device = msg.topic.lstrip("homeassistant/switch/")
        print(device)
        print(payload)
        pin = device.lstrip("Sensor0x24p")
        pin = pin.rstrip("/set")
        print(pin)
        if payload == "ON":
            print("ON")
            setPin(pin).on()
        elif payload == "OFF":
            print("OFF")
            # Implement the logic for turning off the pin


class setPin:
    def __init__(self, pin, address=0x24, num_gpios=16):
        self.mcp = MCP23017(address = 0x24, num_gpios = 16) # MCP2301
        self.pin = pin
        
    def on(self):
        if self.pin == "8":
            self.mcp.write1(GPIOB, 1)
            print("Set 8 High")

        elif self.pin == "9":
            self.mcp.write2(GPIOB, 1)
            print("Set 9 High")

        elif self.pin == "10":
            #inverter
            self.mcp.pinMode(4, self.mcp.OUTPUT)            
            self.mcp.output(4, self.mcp.HIGH)
            print("Set 4 High")

        elif self.pin == "11":
            self.mcp.write4(GPIOB, 1)
            print("Set 11 High")

        elif self.pin == "12":
            self.mcp.write5(GPIOB, 1)
            print("Set 12 High")

        elif self.pin == "13":
            self.mcp.write6(GPIOB, 1)
            print("Set 13 High")

        elif self.pin == "14":
            self.mcp.write7(GPIOB, 1)
            print("Set 14 High")

        elif self.pin == "15":
            self.mcp.write8(GPIOB, 1)
            print("Set 15 High")


    def off(self):
        if self.pin == "10":
            #inverter
            self.mcp.pinMode(4, self.mcp.OUTPUT)            
            self.mcp.output(4, self.mcp.LOW)
            print("Set 4 High")



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