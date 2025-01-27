import time
import paho.mqtt.client as mqtt
from MCP23017 import MCP23017

class mqttPub:
    def __init__(self, mqtt_topic, mqtt_broker, mqtt_password, mqtt_port, mqtt_user):
        self.mqtt_topic = mqtt_topic
        self.mqtt_broker = mqtt_broker
        self.mqtt_password = mqtt_password
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user

        self.client = mqtt.Client()
        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)

    def publish(self, msg):
        self.client.publish(self.mqtt_topic, msg)

class readIO:
    def __init__(self, address=0x24, num_gpios=16):
        self.mcp = MCP23017(address=address, num_gpios=num_gpios)
        for pin in range(8, 16):
            self.mcp.pinMode(pin, self.mcp.INPUT)
            self.mcp.pullUp(pin, 0)

    def readPin(self, pin):
        if 8 <= pin <= 15:
            return self.mcp.currentVal(pin)
        else:
            raise ValueError("Pin number must be between 8 and 15.")

class go:
    def __init__(self, reader, publisher):
        self.reader = reader
        self.publisher = publisher

    def run(self):
        while True:
            for pin in range(8, 16):
                pin_state = self.reader.readPin(pin)
                print(f"Pin {pin} state: {'HIGH' if pin_state else 'LOW'}")
                self.publisher.publish(f"Pin {pin} state: {'HIGH' if pin_state else 'LOW'}")
            time.sleep(2)

if __name__ == "__main__":
    mqtt_publisher = mqttPub(
        mqtt_topic="home/switch/state",
        mqtt_broker="your_mqtt_broker_address",
        mqtt_password="your_password",
        mqtt_port=1883,
        mqtt_user="your_username"
    )

    reader = readIO()
    controller = go(reader, mqtt_publisher)
    controller.run()