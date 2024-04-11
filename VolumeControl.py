import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

detector = htm.HandDetector()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

cTime = 0
pTime = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        print(lmList[4], lmList[8])
        # Index finger and thumb tip, circle and line
        x1 , y1 = lmList[4][1], lmList[4][2]
        x2 , y2 = lmList[8][1], lmList[8][2]
        # circle two points
        cx, cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        # length of line
        length = np.hypot(x2-x1, y2-y1)
        print(length)
        # Hand range 50 - 300
        # Volume Range -65 - 0
        vol = np.interp(length, [20, 200], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)
        volBar = np.interp(length, [20, 200], [400, 150])
        volPer = np.interp(length, [20, 200], [0, 100])
        # button effect
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
        
        
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)