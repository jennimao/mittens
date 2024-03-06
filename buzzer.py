import time
from pyfirmata import Arduino, util

# Connect to the Arduino board
board = Arduino('/dev/cu.usbmodem143301')

# Set the buzzer pin to output
board.digital[9].mode = 1

# Loop indefinitely
while True:
    # Turn on the buzzer
    board.digital[9].write(1)
    
    # Wait for 1 second
    time.sleep(1)
    
    # Turn off the buzzer
    board.digital[9].write(0)
    
    # Wait for another second
    time.sleep(1)