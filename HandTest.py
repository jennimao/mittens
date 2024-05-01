import cv2
import mediapipe as mp
import serial
import threading
import time

# all threads can access this global variable
measured_z = 0



    #generate square

    #height 720
    #width 1280
def visionProcessing():
  global measured_z
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_hands = mp.solutions.hands

  #all in cm
  z_measurement = 7.8
  fov_h = 9.4
  fov_v = 5.2
  z_test = 30
  font = cv2.FONT_HERSHEY_SIMPLEX
  font_scale = 1
  font_color = (0, 0, 0)  # White color in BGR
  thickness = 2


  cap = cv2.VideoCapture(0)
  with mp_hands.Hands(
      model_complexity=0,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      results = hands.process(image)
      image_height, image_width, _ = image.shape
      #print("height", image_height)
      #print("width", image_width)
      # Draw the hand annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          for ids, landmrk in enumerate(hand_landmarks.landmark):
            if ids == 0:
              cx, cy = landmrk.x * image_width, landmrk.y*image_height
              
              plane_width = fov_h * (measured_z/z_measurement)
              plane_height = fov_v * (measured_z/z_measurement)
              
              cx_real = (landmrk.x * plane_width) - (0.5 * plane_width)
              cy_real = landmrk.y * plane_height - (0.5 * plane_height)

              my_str_1 = "Pixel width, height:" + str(round(cx, 1)) + ", " + str(round(cy, 1))
              my_str_2 = "Real width, height, z:" + str(round(cx_real,1) )+ ", " + str(round(cy_real, 1)) + ", " + str(round(measured_z,1))
              #print("Real width, height:", cx_real, cy_real)

          mp_drawing.draw_landmarks(
              image,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              mp_drawing_styles.get_default_hand_landmarks_style(),
              mp_drawing_styles.get_default_hand_connections_style())
        # for hand_landmarks in results.multi_hand_world_landmarks:
        #           # Here is How to Get All the Coordinates
        #   for ids, landmrk in enumerate(hand_landmarks.landmark):
        #       # print(ids, landmrk)
        #       #cx, cy = landmrk.x * image_width, landmrk.y*image_height
        #       id = ids
        #       if id == 4:
        #         print("Thumb top")
        #       if id == 8:
        #         print("pointer top")
        #       if id == 12:
        #         print("middle top")
        #       if id == 16:
        #         print("index top")
        #       if id == 20:
        #         print("pinkie top")
            
        #       if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
        #         #print("pixel adjusted:", cx, cy,)
        #         print("Raw (meters):", landmrk.x, landmrk.y, landmrk.z)
        #       # print (ids, cx, cy)
      # Flip the image horizontally for a selfie-view display.
      image_2 = cv2.flip(image, 1)
      cv2.putText(image_2, my_str_1, (50, 50),font, font_scale, font_color, thickness)
      cv2.putText(image_2, my_str_2, (50, 100),font, font_scale, font_color, thickness)
      cv2.imshow('MediaPipe Hands', image_2)
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()



def recvFromArduino():
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


#============================

def waitForArduino():

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

      while ser.inWaiting() == 0:
        pass
        
      msg = recvFromArduino()

      print (msg)
      

def myRunTest():
  numLoops = 20
  global measured_z
  smoothing_window = 5
  data = [None] * smoothing_window
  free_slot_ptr = 0
  iterations = 0
   #while n < numLoops:
  while True:

    while ser.inWaiting() == 0:
      pass
      
    dataRecvd = recvFromArduino()
    #print( "Data:", dataRecvd)
    split = dataRecvd.split(":")
    if len(split) > 1:

      duration = float(split[1])
      distance = duration * 0.0343

      if (distance != 0):
        distance = distance/2

      print( "Distance:", distance, "cm")


      data[free_slot_ptr] = distance

      if(free_slot_ptr == smoothing_window - 1):
        free_slot_ptr = 0
      
      else:
        free_slot_ptr += 1
    
      avg = 0
      
      if (iterations < smoothing_window):
        iterations += 1
        for i in range(iterations):
          avg += data[i]
        avg /= iterations
      else:
        for i in range(smoothing_window):
          avg += data[i]
        avg /= smoothing_window
      #print( "Smoothed Distance:", avg, "cm")
      measured_z = avg

    #print ("===========")


if __name__ =="__main__":
    
  #NOTE the user must ensure that the serial port and baudrate are correct
  #serPort = "/dev/ttyS80"
  serPort = "/dev/cu.usbmodem14301"
  baudRate = 9600
  ser = serial.Serial(serPort, baudRate)
  print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))
  startMarker = '<' #60
  endMarker = '>' #62

  #t1 = threading.Thread(target=visionProcessing)
  t2 = threading.Thread(target=myRunTest)

  #t1.start()
  t2.start()

  #t1.join()
  visionProcessing()
  t2.join()
 
  print("Done!")