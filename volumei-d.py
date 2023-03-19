import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

#get the video input
cap = cv2.VideoCapture(0) 

#Detecting, initializing, and configuring the hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

#Accessing the speaker using pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

#Finding the volume range between the minimum and maximum volume
volMin, volMax = volume.GetVolumeRange()[:2]

#Capturing an image from our camera and converting it to an RGB image
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #Checking whether we have multiple hands in our input
    lmList = []
    if results.multi_hand_landmarks:
        #Creating a for loop to manipulate each hand
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy]) 
        mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    #Specifying the points of the thumb and middle finger we will use
    if lmList != []:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        #Drawing a circle between the tip of the thumb and the tip of the index finger
        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)  
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)  

        #Drawing a line between points 4 and 8
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

        #Finding the distance between points 4 and 8
        length = hypot(x2 - x1, y2 - y1)

        #Converting the hand range to the volume range
        vol = np.interp(length, [15, 220], [volMin, volMax])
        print(vol, length)

        #Setting the master volume
        volume.SetMasterVolumeLevel(vol, None)  

        #Displaying the video output used to interact with the user
        cv2.imshow('Image', img) 
        #Terminating the program
        if cv2.waitKey(1) & 0xff == ord('q'): 
          break
    