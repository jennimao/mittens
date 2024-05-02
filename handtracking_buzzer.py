import cv2
import mediapipe as mp
import time
from pyfirmata import Arduino, util

# Connect to the Arduino board
board = Arduino('/dev/cu.usbserial-14230')

thumb   = 2 
finger2 = 3
finger3 = 4
finger4 = 5
finger5 = 6
palm    = 7 

# have to find which landmark corresponds with which finger point 
# thumb tip = 4 
# index finger tip = 8
# middle finger tip = 12
# ring finger tip = 16
# pinky finger tip = 20
# middle finger base / upper mid palm = 9
landmarks = [4, 8, 12, 16, 20, 9]
buzzer_pins = [thumb, finger2, finger3, finger4, finger5, palm]

finger_landmarks_dict = dict(zip(landmarks, buzzer_pins))


# LOGIC: 
# loop through list of landmarks we are checking, if either one is in the upper quadrant, then buzz that specific buzzer 
# make it a dictionary, key = landmark, value = buzzer pin 
# ultimately, we will want to check the specific region that is specified by drawing shapes  
 

# create dictionary 
finger_landmark_dict = {}


# Set the buzzer pin to output
for pin in buzzer_pins:
  board.digital[pin].mode = 1
# create a pin for each finger + palm 

buzz_duration = 0.01
buzz_start_times = {pin: None for pin in buzzer_pins}  # Dictionary to store start times for each pin


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
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

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image_height, image_width, _ = image.shape
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        # Here is How to Get All the Coordinates
        for ids, landmrk in enumerate(hand_landmarks.landmark):
            # print(ids, landmrk)
            cx, cy, cz = landmrk.x, landmrk.y, landmrk.z
            if (ids == 20): 
                print(ids, cx, cy, cz)
            # print (ids, cx, cy)
        
        color = (0, 0, 0)


        for landmark_key in finger_landmarks_dict.keys():
          pin = finger_landmarks_dict[landmark_key]

          # upper right quadrant 
          if (hand_landmarks.landmark[landmark_key].x <= 0.5 and hand_landmarks.landmark[landmark_key].y <= 0.5):
              print("UPPER RIGHT QUADRANT")
              print("BUZZER PIN: ", pin)
              color = (48, 48, 255) # red 
              ###################### 
              # buzzer turns on 
              ######################  
    
              board.digital[pin].write(1)
              #time.sleep(0.02) 
              #board.digital[pin].write(0)
             
          elif (hand_landmarks.landmark[landmark_key].x < 0.5 and hand_landmarks.landmark[landmark_key].y > 0.5):
              print("LOWER RIGHT QUADRANT")
              print("BUZZER PIN: ", pin)
              color = (48, 255, 48) # green
              board.digital[pin].write(0) # turn off the buzzer 

          elif (hand_landmarks.landmark[landmark_key].x > 0.5 and hand_landmarks.landmark[landmark_key].y < 0.5):
              print("UPPER LEFT QUADRANT")
              print("BUZZER PIN: ", pin)
              color = (192, 101, 21) # yellow 
              board.digital[pin].write(0)

          else:
              print("LOWER LEFT QUADRANT")
              print("BUZZER PIN: ", pin)
              color = (0, 204, 255) # blue 
              board.digital[pin].write(0)
          
          
      

        # changes color based on where the hand is in space 
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=color, thickness=2))
    

    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()