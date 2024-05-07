import cv2
import mediapipe as mp
import serial
import threading
import time
import math
import projection

#HEIGHT AND WIDTH OF COMPUTER CAMERA IN PIXELS
#height 720
#width 1280

# GLOBALS
measured_z = 0 #z from ultrasonic
lock = False #whether the hand is locked on the object or not
distance = 0 #distance between thumb and pointer
deltaX = 0 #difference of x in thumb between diff frames
deltaY = 0 #difference of y in thumb between diff frames
deltaZ = 0
start = (150,150) #top left corner of square
end = (350,350) #bottom right corner of square
BLUE = (255, 0, 0)
RED = (0, 255, 0)
GREEN = (255, 0, 255)

real_start = (4,7) #cm
real_end = (4 - 7, 0)
#real_end = (4 - 16.5, 7 - 11.9) #cm
square_z = 38.1 #cm #15 inches

##calibration constants for camera
#all in cm
Z_MEASUREMENT = 7.8
FOV_H = 9.4
FOV_V = 5.2

#Constants for rendering text
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
FONT_COLOR = (0, 0, 0)  # White color in BGR
THICKNESS = 2
   

#determines if the point (x,y) is on the border of the square   
def On_Square(start, end, x, y):
  grace_pixels = 15
  if abs(x - start[0]) < grace_pixels:
    return True
  if abs(x - end[0]) < grace_pixels:
    return True
  if abs(y - start[1]) < grace_pixels:
    return True
  if abs(y - end[1]) < grace_pixels:
    return True
  
  return False


# def On_Square_real(start, end, x, y):
#   grace_cm = 2
#   if abs(x - real_start[0]) < grace_cm:
#     return True
#   if abs(x - real_end[0]) < grace_cm:
#     return True
#   if abs(y - real_start[1]) < grace_cm:
#     return True
#   if abs(y - real_end[1]) < grace_cm:
#     return True
  
#   return False

def On_Square_real(start, end, x, y):
  grace_cm = 2
  if abs(x - start[0]) < grace_cm and ((abs(y - start[1]) < grace_cm) or y < start[1]) and ((abs(y - end[1]) < grace_cm) or y > end[1]):
    return True
  if abs(x - end[0]) < grace_cm and ((abs(y - end[1]) < grace_cm) or y > end[1]) and ((abs(y - start[1]) < grace_cm) or y < start[1]):
    return True
  if abs(y - start[1]) < grace_cm and ((abs(x - start[0]) < grace_cm) or x > start[0]) and ((abs(x - end[0]) < grace_cm) or x < end[0]):
    return True
  if abs(y - end[1]) < grace_cm and ((abs(x - start[0]) < grace_cm) or x > start[0]) and ((abs(x - end[0]) < grace_cm) or x < end[0]):
    return True
  
  return False


def renderSquare(real_start,real_end,square_z, image_width, image_height):
  plane_width = FOV_H * (square_z/Z_MEASUREMENT)
  plane_height = FOV_V * (square_z/Z_MEASUREMENT)

  pixel_sx = round(((image_width/plane_width)* real_start[0]) + (image_width * 0.5))
  pixel_ex = round(((image_width/plane_width)* real_end[0]) + (image_width * 0.5))
  pixel_sy = round(((image_height/plane_height)* real_start[1]) + (image_height * 0.5))
  pixel_ey = round(((image_height/plane_height)* real_end[1]) + (image_height * 0.5))

  return (pixel_sx,pixel_sy), (pixel_ex,pixel_ey)
  


#major method responsible for running the handtracking/rendering the images
def visionProcessing():
  global measured_z
  global lock
  global distance
  global deltaX
  global deltaY
  global start 
  global end
  global real_start
  global real_end
  global deltaZ
  global square_z
  
  #setting uo the media pipe handtracking utilities
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_hands = mp.solutions.hands


  #start of the loop for each frame
  cap = cv2.VideoCapture(0)
  with mp_hands.Hands(
      model_complexity=0,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5, max_num_hands=1) as hands:
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
      

      # constants for rendering text
      my_str_1 = ""
      my_str_2 = ""
      my_str_3 = ""
      my_str_4 = ""

      #variables to save pointer and thumb x,y
      thumb_x  = 0
      thumb_y = 0
      thumb_z = 0
      pointer_x = 0
      pointer_y = 0
      pointer_z = 0
      wrist_pos = list()
      
      # Draw the hand annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      on_square = True
      if results.multi_hand_landmarks:
        cx = 0
        cy = 0
        for hand_landmarks in results.multi_hand_landmarks:
          for ids, landmrk in enumerate(hand_landmarks.landmark):
            
            if ids == 5 or ids == 9 or ids == 13 or ids == 17: #if its the wrist landmark
              cx += landmrk.x 
              cy += landmrk.y

        cx /= 4
        cy /= 4

        plane_width = FOV_H * (measured_z/Z_MEASUREMENT)
        plane_height = FOV_V * (measured_z/Z_MEASUREMENT)
        
        cx_real = (cx * plane_width) - (0.5 * plane_width)
        cy_real = (cy * plane_height) - (0.5 * plane_height)
        wrist_pos = [cx_real,cy_real,measured_z]

        my_str_1 = "Pixel width, height:" + str(round(cx, 1)) + ", " + str(round(cy, 1))
        my_str_2 = "Real width, height, z:" + str(round(cx_real,1) )+ ", " + str(round(cy_real, 1)) + ", " + str(round(measured_z,1))
        
        for hand_landmarks in results.multi_hand_world_landmarks: 
          for ids, landmrk in enumerate(hand_landmarks.landmark):    
            if ids == 4 or ids == 8: #pointer and thumb
              #cx, cy = landmrk.x * image_width, landmrk.y*image_height
              #my_str_3 = "4 Pixel x, y:" + str(round(cx, 1)) + ", " + str(round(cy, 1))
              cx_real = wrist_pos[0] + landmrk.x * 100
              cy_real = wrist_pos[1] + landmrk.y * 100
              cz_real = wrist_pos[2] + landmrk.z * 100

              #projection.on_cube(cx_real,cy_real,cz_real)
              if not (On_Square_real(real_start, real_end, cx_real,cy_real) and abs(cz_real - square_z) > 2):
                on_square = False
              #on_square = On_Square(start,end, cx,cy)
              if ids == 4:
                thumb_x = cx_real
                thumb_y = cy_real
                #thumb_z = cz_real
                thumb_z = wrist_pos[2]
                my_str_4 = "Thumb Real width, height, z:" + str(round(cx_real,1) )+ ", " + str(round(cy_real, 1)) + ", " + str(round(measured_z,1))
              if ids == 8:
                pointer_x = cx_real
                pointer_y = cy_real
                pointer_z = cz_real

          if (lock and wrist_pos[2] < 100):
            new_dist = math.sqrt(math.pow((thumb_x - pointer_x),2) + math.pow((thumb_y - pointer_y),2) )#+ math.pow((thumb_z - pointer_z),2))
            if math.floor(abs(distance - new_dist)) < 3 :
              #start, end = recalc_req(thumb_x - deltaX,thumb_y - deltaY, start, end)  
              #start = (round(start[0] + thumb_x - deltaX), round(start[1] + thumb_y - deltaY))
              #end = (round(end[0] + thumb_x - deltaX), round(end[1] + thumb_y - deltaY))
              real_start = (round(real_start[0] + thumb_x - deltaX,1), round(real_start[1] + thumb_y - deltaY,1))
              real_end =  (round(real_end[0] + thumb_x - deltaX,1), round(real_end[1] + thumb_y - deltaY,1))
              square_z =  round(square_z + thumb_z - deltaZ,1)
              deltaX = thumb_x
              deltaY = thumb_y
              deltaZ = thumb_z
              color = BLUE
              distance = new_dist
            else:
              color = RED
              lock = False
              deltaX = 0
              deltaY = 0
              deltaZ = 0

          elif(on_square and wrist_pos[2] < 100):
            lock = True
            distance = math.sqrt(math.pow((thumb_x - pointer_x),2) + math.pow((thumb_y - pointer_y),2) )#+ math.pow((thumb_z - pointer_z),2))
            deltaX = thumb_x
            deltaY = thumb_y
            deltaZ = thumb_z
            color = BLUE
          else:
            color = RED
        for hand_landmarks in results.multi_hand_landmarks:
          for ids, landmrk in enumerate(hand_landmarks.landmark):
            mp_drawing.draw_landmarks(
              image,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=color, thickness=2))
     
      
      pixel_start, pixel_end = renderSquare(real_start,real_end,square_z, image_width,image_height) 
      print(pixel_start,pixel_end)
      cv2.rectangle(image, pixel_start, pixel_end, GREEN, 2)
      cv2.circle(image, (image_width//2, image_height//2) ,5, BLUE, 5)
      projected_points = projection.render_cube(image, 0, 0, 0)
      image_2 = cv2.flip(image, 1)
      my_str_3 = "Real start: (" + str(real_start[0]) + "," + str(real_start[1]) + "), Real end (" + str(real_end[0]) + "," + str(real_end[1]) + ")" + "z: " + str(square_z)
      cv2.putText(image_2, my_str_1, (50, 50),FONT, FONT_SCALE, FONT_COLOR, THICKNESS)
      cv2.putText(image_2, my_str_2, (50, 100),FONT, FONT_SCALE, FONT_COLOR, THICKNESS)
      cv2.putText(image_2, my_str_3, (50, 150),FONT, FONT_SCALE, FONT_COLOR, THICKNESS)
      cv2.putText(image_2, my_str_4, (50, 200),FONT, FONT_SCALE, FONT_COLOR, THICKNESS)
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



class Point:
  def __init__(self, x, y) -> None:
    self.x = x
    self.y = y

class Square:
  def __init__(self, topRight, topLeft, bottomRight, bottomLeft) -> None:
    self.topLeft = topLeft
    self.topRight = topRight
    self.bottomLeft = bottomLeft
    self.bottomRight = bottomRight










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