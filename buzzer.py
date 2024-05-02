from pyfirmata import Arduino, util
import time

# Define the pin connected to the buzzer
buzzer_pin = 9  # Change this to match the actual pin number you're using

# Connect to the Arduino
board = Arduino('/dev/cu.usbmodem143301')  # Change this to match the port where your Arduino is connected

# Set the pin mode to OUTPUT
board.digital[buzzer_pin].mode = 1

# Main loop to continuously buzz the buzzer
while True:
    board.digital[buzzer_pin].write(1)  # Turn the buzzer on 
    time.sleep(0.0000001)  # Wait for a short duration (adjust as needed for desired frequency)
    board.digital[buzzer_pin].write(0)  # Turn the buzzer off
    time.sleep(0.0000001)  # Wait for a short duration