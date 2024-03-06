import cv2
import mediapipe as mp
import time
from pyfirmata import Arduino, util

# Connect to the Arduino board
board = Arduino('/dev/cu.usbmodem143301')

# Set the buzzer pin to output
board.digital[9].mode = 1


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
            print(ids, cx, cy, cz)
            # print (ids, cx, cy)
        
        color = (0, 0, 0)

        # upper right quadrant 
        if (hand_landmarks.landmark[9].x <= 0.5 and hand_landmarks.landmark[9].y <= 0.5):
            print("UPPER RIGHT RECTANGLE")
            color = (48, 48, 255) # red 
            ###################### 
            # buzzer
            ######################  
            
            board.digital[9].write(1)
            
            # Wait for another second
            time.sleep(1)
            
        elif (hand_landmarks.landmark[9].x < 0.5 and hand_landmarks.landmark[9].y > 0.5):
            print("LOWER RIGHT QUADRANT")
            color = (48, 255, 48) # green
            board.digital[9].write(0) # turn off the buzzer 

        elif (hand_landmarks.landmark[9].x > 0.5 and hand_landmarks.landmark[9].y < 0.5):
            print("UPPER LEFT QUADRANT")
            color = (192, 101, 21) # yellow 
            board.digital[9].write(0)

        else:
            print("LOWER LEFT QUADRANT")
            color = (0, 204, 255) # blue 
            board.digital[9].write(0)


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