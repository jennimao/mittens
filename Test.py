from BluetoothTest import serial_device
import time
import serial

startMarker = '<' #60
endMarker = '>' #62

def sendToArduino(my_str, device):
    new_str = '<' + str(len(my_str)) + my_str + '>'
    new_str = new_str.encode('latin-1')
    print(new_str)
    device.write(new_str)

def recvFromArduino(ser):
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  byteCount = -1 # to allow for the fact that the last increment will be one too many
  
  # wait for the start character
  while x != startMarker: 
    x = ser.read()
    x = x.decode('latin-1')
    #print("Read:", x)
    #print("start marker:", startMarker)
  
  # save data until the end marker is found
  while x != endMarker:
    #print("Read2 ", x)
    #print("end marker:", endMarker)
    if x != startMarker:
      ck = ck + x 
      byteCount += 1
    x = ser.read()
    x = x.decode('latin-1')
  
  #print("msg:", ck)
  return(ck)

my_device = serial.Serial("/dev/cu.usbmodem14301", 9600)
#my_device.waitForArduino()
while True:
    sendToArduino("7", my_device)
    data = recvFromArduino(my_device)
    print(data)
    time.sleep(0.1)
    sendToArduino("8", my_device)
    data = recvFromArduino(my_device)
    print(data)
    #data = my_device.recvFromArduino()
    #print(data)
    time.sleep(0.1)




