from PyQt5.QtWidgets import QListWidget,QBoxLayout,QListWidgetItem, QWidget, QLabel, QGridLayout
from Config.cv import VideoThread
from Utils.VideoContainer import VideoImages
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5 import QtGui
import cv2
import numpy as np
from threading import Thread
from Utils.ANPRDetector import ANPRDetector
# from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from onvif import ONVIFCamera


class MainTab(QWidget):
     def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.cameraInstanceList = []
        self.video_threads = []
        self.tabs = []

        self.disply_width = 650
        self.display_height = 580
        
        self.image_label2 = QLabel("No Camera Available")
        self.image_label2.setAlignment(Qt.AlignCenter)
        self.image_label2.setStyleSheet("QLabel { background-color : black;color:white; }")
      #   self.image_label2.resize(self.disply_width, self.display_height)

        self.grid = QGridLayout(self)
        self.cameraGrid = QGridLayout(self)
        self.cameralist = QListWidget(self)
        self.anprView = QListWidget(self)
        self.header = QLabel('Camera List')
        self.header.setStyleSheet("QWidget { padding:5px; background-color : grey; color : white;max-height:20px;min-height:10px }")
        
        self.cameralist.setStyleSheet("QWidget { background-color : grey; color : white;max-width:200px;min-width:100px }")
        self.anprView.setStyleSheet("QWidget { background-color : grey; color : white;max-width:250px;min-width:100px }")
        self.grid.setSpacing(1)

        self.cameraGrid.addWidget(self.image_label2,1,1)

        self.grid.addLayout(self.cameraGrid, 2,2,2,2)


        listWidgetItem = QListWidgetItem("Number Plates")
        listWidgetItem.setTextAlignment(Qt.AlignHCenter)
        listWidgetItem.setBackground(QColor('#5A5A5A'))
        listWidgetItem.setSizeHint(QSize(100,30))
        
      #   self.cameralist.addItem(listWidgetItem)
        self.anprView.addItem(listWidgetItem)
        self.anprView.setItemWidget(listWidgetItem, self.header)

        self.grid.addWidget(self.anprView,2, 4, 2,1)
        self.grid.addWidget(self.cameralist,2, 1, 2,1)
        self.grid.addWidget(self.header,1, 1, 1,4)

        self.setLayout(self.grid)
        
     def stopRecording(self,data):
         print(data)
         data['thread'].isRecording = False
         print(data['thread'].isRecording)

     def startRecording(self,data, path):
         print(data)
         data['thread'].isRecording = True
         data['thread'].recordingConfig(path)

     def startAnpr(self,data):
         print(data)
         data['thread'].isAnpr = True

     def stopAnpr(self,data):
         print(data)
         data['thread'].isAnpr = False


     def add_camera(self, details):
         print(details)
         imageData = details['thread'].videoimage
         print("imageData", imageData.id)
         imageData.slot = len(self.cameraInstanceList)+1

         if len(self.cameraInstanceList)==0:
             self.cameraGrid.itemAt(0).widget().setParent(None)

         self.cameraInstanceList.append(imageData)

         listWidgetItem = QListWidgetItem(imageData.name)
         listWidgetItem.setSelected(True)
        
         self.cameralist.addItem(listWidgetItem)
         user = imageData.user
         password = imageData.password
         ip = imageData.ip

         rowCounts = self.grid.rowCount()
         colCounts = self.grid.columnCount()

         imageData.image.setText("Loading.....")
         imageData.image.setScaledContents(True)

         if len(self.cameraInstanceList)<=5:
            composite_list = [self.cameraInstanceList[x:x+2] for x in range(0, len(self.cameraInstanceList),2)]
         elif len(self.cameraInstanceList)>5 and len(self.cameraInstanceList)<=10:
            composite_list = [self.cameraInstanceList[x:x+4] for x in range(0, len(self.cameraInstanceList),4)]
         else:
            composite_list = [self.cameraInstanceList[x:x+5] for x in range(0, len(self.cameraInstanceList),5)]

         for i, d in enumerate(composite_list):
            for j in range(len(d)):
               self.cameraGrid.addWidget(d[j].image,i,j)


         for i, d in enumerate(composite_list):
            for j in range(len(d)):
               for th in self.video_threads:
                  print("video_threads=====>",d[j].width, d[j].height)
                  th['thread'].disply_width = d[j].width
                  th['thread'].display_height = d[j].height
         
         try:
            newthread = [d['thread'] for d in self.video_threads if d.get('id') == details.get('id')]
            print(newthread[0].url)
            newthread[0].change_pixmap_signal.connect(self.update_image)
            newthread[0].detect_pixmap_signal.connect(self.detect_plats)
            newthread[0].error_single.connect(self.error_update)
            newthread[0].start()
         except:
            print('Something went wrong!')
            return 0

         return 1


     @pyqtSlot(np.ndarray)
     def detect_plats(self,image):
         anpr = ANPRDetector(self, image)
         anpr.number_plate.connect(self.add_plats)
         anpr.start()
         print(image)
         

     @pyqtSlot(str)
     def add_plats(self,numberplate):
         listWidgetItem = QListWidgetItem(numberplate)
         listWidgetItem.setTextAlignment(Qt.AlignHCenter)
      #   self.cameralist.addItem(listWidgetItem)
         self.anprView.addItem(listWidgetItem)
         


     @pyqtSlot(str, object)
     def error_update(self,message, cam_id):
         # thread = [d['thread'] for d in self.video_threads if d.get('id') == cam_id]
         if len(self.cameraInstanceList)>0:
            data = [d for d in self.video_threads if d['id'] == cam_id]
            # if thread[0].isRunning():
            #    thread[0].terminate()
            print("error in: ", cam_id, data)
            if len(data)>0:
               data[0]['thread'].videoimage.image.setText(message)
               print("self.cameraInstanceList", self.cameraInstanceList)
               self.tabs[0].disconnectCamera(data[0], data[0]['id']-1)

     @pyqtSlot(QPixmap, object)
     def update_image(self,image_pixels, cam_id):
         # print(cam_id , '3713524926')
         thread = [d for d in self.cameraInstanceList if d.id == cam_id]
         if len(thread)>0:
            thread[0].image.setPixmap(image_pixels)
      
     def setTab(self, tab):
         self.tabs.append(tab)

     def create_video_thread(self, data):
         user  = data.get('user')
         id  = data.get('id')
         password  = data.get('pass')
         ip  = data.get('ip')
         data['slot'] = len(self.video_threads)+1


         # camera = ONVIFCamera(ip, 80, user, password)

         # media = camera.create_media_service()

         # profiles = media.GetProfiles()
         # for profile in profiles:
         #    if profile.VideoEncoderConfiguration.Resolution.Width <= 640:
         #       sub_stream_profile = profile
         #       break
         # stream_setup = {'Stream': 'RTP-Unicast', 'Transport': 'RTSP'}
         # rtsp_uri = media.GetStreamUri({'ProfileToken': sub_stream_profile.token, 'StreamSetup': stream_setup})

         # rtsp_uri.Uri = rtsp_uri.Uri[:7] + f'{user}:{password}@' + rtsp_uri.Uri[7:]


         image_label = QLabel("No Camera")
         image_label.setAlignment(Qt.AlignCenter)
         image_label.setStyleSheet("QLabel { background-color : black;color:white; }")
         # image_label.setScaledContents(True)
         print("datatoAddInitially ",data)
         videoimage = VideoImages(data.get('name'), user, image_label, ip,password,id)
         newthread = VideoThread(self,None, flag=data['name'], cam_id=id, videoimage=videoimage,ip=ip,user=user,password=password)
         # newthread = VideoThread(self,f'rtsp://{user}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=1', flag=data['name'], cam_id=id, videoimage=videoimage)
         data['thread'] = newthread
         print("afterThread ",newthread.cam_id)
         self.video_threads.append(data)
         return data
      
     def remove_camera(self, details):
         imageData = details['thread'].videoimage

         newthread = [d['thread'] for d in self.video_threads if d.get('id') == imageData.id]
         print(newthread)
         if newthread[0].isRunning():
            newthread[0].stopThread()
            newthread[0].quit()
            newthread[0].wait()


         index = next((index for index, d in enumerate(self.cameraInstanceList) if d.id == imageData.id), None)
         self.cameraInstanceList[:] = [d for d in self.cameraInstanceList if d.id != imageData.id]
         print("self.cameraInstanceList ", self.cameraInstanceList)

         if len(self.cameraInstanceList)<=0:
            self.cameraGrid.addWidget(self.image_label2,1,1)


         if self.cameraGrid.count()>0:
            self.cameraGrid.removeWidget(imageData.image)
            imageData.image.setParent(None)
        
         if index!=None:
            self.cameralist.takeItem(index)
         return "You are on right place!"
