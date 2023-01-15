
import cv2
import numpy as np
import easyocr
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytesseract
import re
import string
import random
from google.cloud import vision
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import InvalidArgument


# from matplotlib import pyplot as plt
# alpr = Alpr('us','C:/openalpr_64/openalpr.conf','C:/openalpr_64/runtime_data')
class ANPRDetector(QThread):
     number_plate = pyqtSignal(str,np.ndarray,str,str,str)
     numbers = []
     def __init__(self, parent, img,name,ip,user):
        super(QThread, self).__init__(parent)
        self.faceCascade = cv2.CascadeClassifier('./assets/haarcascade_indian_plate_number.xml')
        self.img = img
        self.name = name
        self.ip = ip
        self.user = user
        self.creds = Credentials.from_service_account_file("./assets/cameraapp-337712-e7d7029c95b5.json")
        self.client = vision.ImageAnnotatorClient(credentials=self.creds)

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
            print("SizeVehi ===>", vehi)
            print("SizePlate ===>", self.random_string_with_prefix("no-number",4))
            # cv2.imwrite(f"./assets/anpr.jpg", gray)
            # print("faces", faces)
            if len(plate)>0 and vehi.size!=0 and plate.size!=0:
                # print("plate", plate)
                nn = np.random.randint(100)
                print("vehi ===>", vehi.size)
                cv2.imwrite(f"./assets/image.jpg", vehi)
                # reader = easyocr.Reader(['en'], gpu=False, quantize=False)
                
                # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                # pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
                # text = pytesseract.image_to_string(plate)
                # print("texttexttext ", text)
                with open("./assets/image.jpg", "rb") as image_file:
                     content = image_file.read()

                # im = plate.tobytes()
                print(content)
                if content!=None:
                    try:
                        response = self.client.text_detection(image={'content': content})
                        texts = response.text_annotations
                        print("pre", texts)
                        if len(texts)>0:
                            text = texts[0].description
                        else:
                            text = None

                        # text = text.strip().replace(" ", "").replace("  ", "").replace('"', "").replace("*", "")
                        if text!=None and text!='' and text.isspace()==False and text not in self.numbers:
                            cv2.imwrite(f"./assets/{text}.jpg", vehi)
                            self.number_plate.emit(text,vehi, self.name,self.ip,self.user)
                            self.numbers.append(text)
                        else:
                            randomstr = self.random_string_with_prefix("no-number-",4)
                            cv2.imwrite(f"./assets/{randomstr}.jpg", vehi)
                            self.number_plate.emit(randomstr,vehi, self.name,self.ip,self.user)
                            self.numbers.append("----")
                    except InvalidArgument as e:
                        if e.code == 400:
                            print("Error: Missing image or features. Please make sure to pass an image and the correct features to the API.")
                        else:
                            print("Error:", e)
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

     def random_string_with_prefix(self,prefix:str, length:int):
        # Random string generator
        letters = string.ascii_letters
        result_str = prefix + ''.join(random.choice(letters) for i in range(length))
        return result_str
