import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

##########################################################
wCam, hCam = 640, 480
##########################################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.75, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
colorVol = (255,0,0)




while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) !=0:


        # Filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) //100

        if 200<area<950:
            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # print(area)
        # print(bbox)


        # Convert Volume
            volBar = np.interp(length, [20, 200], [400, 150])
            volPer = np.interp(length, [20, 200], [0, 100])
            # Reduce Resolution to make it smoother
            smoothness = 5
            volPer = smoothness * round(volPer/smoothness)
            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            # If pinky is down set Volume
            if not fingers[3]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)
    # Drawings
    cv2.rectangle(img,(50,150), (85,400), (255,0,0), 3)
    cv2.rectangle(img,(50, int(volBar)), (85,400), (255,0,0), cv2.FILLED)
    cv2.putText(img, f'{str(int(volPer))} %', (10,450), cv2.FONT_HERSHEY_PLAIN,3, (255,0,0), 3)

    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (350,50), cv2.FONT_HERSHEY_PLAIN,3, colorVol , 3)

    # Frame Rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN,3, (255,0,255), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)