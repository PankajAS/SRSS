
import cv2
import numpy as np
import easyocr
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytesseract
# from matplotlib import pyplot as plt
# alpr = Alpr('us','C:/openalpr_64/openalpr.conf','C:/openalpr_64/runtime_data')
class ANPRDetector(QThread):
     number_plate = pyqtSignal(str)
     def __init__(self, parent, img):
        super(QThread, self).__init__(parent)
        self.faceCascade = cv2.CascadeClassifier('./assets/haarcascade_indian_plate_number.xml')
        self.img = img

     def run(self):
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            
            faces = self.faceCascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors = 5, minSize=(25,25))
            
            plate = []
            for (x,y,w,h) in faces:
                cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
                plate = gray[y: y+h, x:x+w]
                # plate = cv2.blur(plate,ksize=(20,20))
                # put the blurred plate into the original image
                gray[y: y+h, x:x+w] = plate
            # print("faces", faces)
            if len(plate)>0:
                # print("plate", plate)
                cv2.imwrite("./assets/image.jpg", plate)
                # reader = easyocr.Reader(['en'], gpu=False, quantize=False)
                text = pytesseract.image_to_string(plate)
                print("texttexttext ", text)
                text = text.strip().replace(" ", "")
                if text!=None and text!='' and text.isspace()==False:
                    self.number_plate.emit(text)
                # result = reader.readtext(plate)

                # with ThreadPoolExecutor() as executor:
                #     print("ThreadPoolExecutor")
                #     future = executor.submit(reader.readtext, plate)
                #     future.add_done_callback(self.handle_done)
                # print("result=======", result)
                # if len(result)>0:
                #     print("number=======", result[0][1])
                #     self.number_plate.emit(result[0][1])
            # results.append(result)
     
     def handle_done(self, future):
        print("handle_done===", future.result())
        text = future.result()
        self.number_plate.emit(text[0][1])
