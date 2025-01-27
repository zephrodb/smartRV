import RPi.GPIO as GPIO
import time

# Set up GPIO pins for RF receiver
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)

# Define codes for remote commands
ON_CODE = "101010"
OFF_CODE = "010101"

def decode_signal(signal):
    # Implement signal decoding logic here
    return decoded_command

try:
    while True:
        if GPIO.input(5) == 0:
            received_signal = ""
            # Capture and decode RF signal
            command = decode_signal(received_signal)

            if command == ON_CODE:
                # Send command to turn on the heater
                pass
            elif command == OFF_CODE:
                # Send command to turn off the heater
                pass

        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()