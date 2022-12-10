
import cv2
import numpy as np
import easyocr
# from matplotlib import pyplot as plt

class ANPRDetector:
     def __init__(self):
        self.faceCascade = cv2.CascadeClassifier('./assets/haarcascade_russian_plate_number.xml')

     def startDetectNumberPlate(self, img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = self.faceCascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors = 5, minSize=(25,25))
            plate = []
            for (x,y,w,h) in faces:
                cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
                plate = gray[y: y+h, x:x+w]
                # plate = cv2.blur(plate,ksize=(20,20))
                # put the blurred plate into the original image
                gray[y: y+h, x:x+w] = plate
            print("faces", faces)
            if len(plate)>0:
                print("plate", plate)
                reader = easyocr.Reader(['en'])
                result = reader.readtext(plate)
                print("number", result)
            # results.append(result)
