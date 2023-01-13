
import cv2
import numpy as np
import easyocr
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytesseract
import re
# from matplotlib import pyplot as plt
# alpr = Alpr('us','C:/openalpr_64/openalpr.conf','C:/openalpr_64/runtime_data')
class ANPRDetector(QThread):
     number_plate = pyqtSignal(str,np.ndarray)
     numbers = []
     def __init__(self, parent, img):
        super(QThread, self).__init__(parent)
        self.faceCascade = cv2.CascadeClassifier('./assets/haarcascade_indian_plate_number.xml')
        self.img = img

     def run(self):
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            grayvehi = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            
            faces = self.faceCascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors = 5, minSize=(30,30))
            vehical = self.faceCascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors = 5, minSize=(30,30))
            # print(vehical)
            plate = []
            for (x,y,w,h) in faces:
                cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
                plate = gray[y: y + h, x: x + w]
                # plate = cv2.blur(plate,ksize=(20,20))
                # put the blurred plate into the original image
                # gray[y: y+h, x:x+w] = plate

            vehi = []
            for (x,y,w,h) in vehical:
                x = x - 300
                y = y - 300
                w = w + 600
                h = h + 600
                cv2.rectangle(grayvehi,(x,y),(x+w,y+h),(255,0,0),2)
                vehi = grayvehi[y: y+h, x:x+w]
            # print(len(vehi))
            # cv2.imwrite(f"./assets/vehi.jpg", vehi)    
            
            # print("faces", faces)
            if len(plate)>0 and vehi.size!=0 and plate.size!=0:
                # print("plate", plate)
                nn = np.random.randint(100)
                print("vehi ===>", vehi.size)
                cv2.imwrite(f"./assets/image.jpg", vehi)
                # reader = easyocr.Reader(['en'], gpu=False, quantize=False)
                pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
                text = pytesseract.image_to_string(plate)
                print("texttexttext ", text)
                text = text.strip().replace(" ", "").replace("  ", "").replace('"', "").replace("*", "")
                if text!=None and text!='' and text.isspace()==False and text not in self.numbers:
                    self.number_plate.emit(text,vehi)
                    self.numbers.append(text)
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

     def isValidLicenseNo(self,str):

        # Regex to check valid
        # Indian driving license number
        regex = ("^(([A-Z]{2}[0-9]{2})" +
                "( )|([A-Z]{2}-[0-9]" +
                "{2}))((19|20)[0-9]" +
                "[0-9])[0-9]{7}$")
        
        # Compile the ReGex
        p = re.compile(regex)

        # If the string is empty
        # return false
        if (str == None):
            return False

        # Return if the string
        # matched the ReGex
        if(re.search(p, str)):
            return True
        else:
            return False