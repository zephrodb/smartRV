import time
from gps3 import gps3
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "mqtt.example.com"
MQTT_PORT = 1883
MQTT_TOPIC = "gps/speed"

# GPS Configuration
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))

client.on_connect = on_connect

try:
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            speed = data_stream.TPV['speed']  # Speed in m/s
            if speed is not None:
                speed_kmh = speed * 3.6  # Convert to km/h
                speed_mph = speed * 3600 * 0.000621371
                print(f"Speed: {speed_kmh:.2f} km/h")
                client.publish(MQTT_TOPIC, f"{speed_kmh:.2f}")
                print(f"Speed: {speed_mph:.2f} m/h")
                client.publish(MQTT_TOPIC, f"{speed_mph:.2f}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Terminating the script.")

finally:
    gps_socket.close()
    client.disconnect()