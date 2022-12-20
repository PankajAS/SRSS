import cv2

from threading import Thread
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
import numpy as np
import os
# from Utils.ANPRDetector import ANPRDetector
import urllib

# Video capture thread
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QPixmap, int)
    detect_pixmap_signal = pyqtSignal(np.ndarray)
    error_single = pyqtSignal(str, int)

    def __init__(self, parent, url=None, flag=None, cam_id=None, videoimage=None):
        super(QThread, self).__init__(parent)
        self.url = url
        self.images = []
        self.flag = flag
        self.cap = None
        self.cam_id = cam_id
        self.frame = None
        self.videoimage = videoimage
        # self.anpr = ANPRDetector()
        # self.videoimage.image.setScaledContents(True)
        self.disply_width = videoimage.width
        self.display_height = videoimage.height
        self.isRecording = False
        self.daemon = True
        # self.video_stream_widget = RTSPVideoWriterObject(self.cap,self.update, self.frame, self.flag)
        # print(self.url, self.cam_id)

    def run(self):
        # capture from ip cam
        # os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="rtsp_transport;udp"
        self.loop = True
        self.cap = cv2.VideoCapture(self.url)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # print(self.cap)
        self.update()
        
#        self.update()
    def stopThread(self):
        self.loop = False
    
    def recordingConfig(self, path):
        self.video_stream_widget = RTSPVideoWriterObject(self.cap,self.update, self.frame, self.flag,path)
    
    def update(self):
        while self.loop:
            # cv2.waitKey(1)
            ret, cv_img = self.cap.read()
            # print('running', ret, self.flag)
            # print(ret)
            if ret==False or ret==None:
                print(self.flag, 'Failed to load')
                self.error_single.emit(self.flag + " Failed to Load",self.cam_id)
                self.loop = False
                # self.change_pixmap_signal.emit(cv_img1, self.flag)

            if ret:
                # self.anpr.startDetectNumberPlate(cv_img)
                # self.thread = Thread(target=self.anpr.startDetectNumberPlate, args=(cv_img))
                # self.thread.daemon = True
                # self.thread.start()
                if len(self.images)==100:
                    # img = cv2.imread("./assets/cars.jpeg")
                    # print("Run", type(self.images[0]))
                    self.detect_pixmap_signal.emit(cv_img)
                    # self.anpr.startDetectNumberPlate(self.images)
                    # thread = Thread(target=self.anpr.startDetectNumberPlate, args=(cv_img,))
                    # thread.daemon = True
                    # thread.start()
                    self.images = []
                if self.isRecording==True:
                    cv_img1 = cv2.circle(cv_img, (10, 20), radius=3, color=(0, 0, 255), thickness=-1)
                    # cv_img1 = cv2.putText(cv_img, "", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                    qt_img = self.convert_cv_qt(cv_img1)
                    self.change_pixmap_signal.emit(qt_img, self.cam_id)
                else:
                    qt_img = self.convert_cv_qt(cv_img)
                    self.change_pixmap_signal.emit(qt_img, self.cam_id)
                # self.change_pixmap_signal.emit(cv_img1, self.cam_id)
                # self.videoimage.image.setScaledContents(True)
                # self.videoimage.image.setPixmap(qt_img)
                self.images.append(cv_img)
                if self.isRecording==True:
                    self.video_stream_widget.save_frame(cv_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # print(self.disply_width, self.display_height)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
                

# Recording Video
class RTSPVideoWriterObject(object):
    def __init__(self, capture, update, frame, flag,path):
        
        self.frame = frame
        self.flag = flag
        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = 600 #int(capture.get(3))
        self.frame_height = 480 #int(capture.get(4))
        
        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output_video = cv2.VideoWriter(f'{path}/{self.flag}.avi', self.codec, 10, (self.frame_width, self.frame_height))
        # Start the thread to read frames from the video stream
        # self.thread = Thread(target=update, args=())
        # self.thread.daemon = True
        # self.thread.start()

    def save_frame(self, frame):
        # Save obtained frame into video output file
        vidout=cv2.resize(frame,(self.frame_width, self.frame_height))
        self.output_video.write(vidout)

