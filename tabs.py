# from PyQt5 import QtCore, QtGui, QtWidgets


# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)

#         central_widget = QtWidgets.QWidget()
#         self.setCentralWidget(central_widget)

#         self.m_w11 = QtWidgets.QWidget()
#         self.m_w12 = QtWidgets.QWidget()
#         self.m_w21 = QtWidgets.QWidget()
#         self.m_w22 = QtWidgets.QWidget()

#         lay = QtWidgets.QGridLayout(central_widget)

#         for w, (r, c) in zip(
#             (self.m_w11, self.m_w12, self.m_w21, self.m_w22),
#             ((0, 0), (0, 1), (1, 0), (1, 1)),
#         ):
#             lay.addWidget(w, r, c)
#         for c in range(2):
#             lay.setColumnStretch(c, 1)
#         for r in range(2):
#             lay.setRowStretch(r, 1)

#         lay = QtWidgets.QVBoxLayout(self.m_w11)
#         lay.addWidget(QtWidgets.QTextEdit())

#         lay = QtWidgets.QVBoxLayout(self.m_w12)
#         lay.addWidget(QtWidgets.QTableWidget(4, 4))

#         lay = QtWidgets.QVBoxLayout(self.m_w21)
#         lay.addWidget(QtWidgets.QLineEdit())

#         lay = QtWidgets.QVBoxLayout(self.m_w22)
#         lay.addWidget(QtWidgets.QLabel("Text", alignment=QtCore.Qt.AlignCenter))


# if __name__ == "__main__":
#     import sys

#     app = QtWidgets.QApplication(sys.argv)
#     w = MainWindow()
#     w.resize(640, 480)
#     w.show()
#     sys.exit(app.exec_())

# import cv2

# cap = cv2.VideoCapture("rtsp://admin:admin123@192.168.1.250:554",cv2.CAP_PROP_BUFFERSIZE)
# # cap.set(cv2.CAP_PROP_FPS, 10.0)
# ret, cv_img = cap.read()
# print(ret, cv_img)

# while True:
#     ret, cv_img = cap.read()
#     print(ret)

# import cv2
# def main(args):

#     #cap = cv2.VideoCapture(0) #default camera
#     cap = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.250:554') #IP Camera
    
#     while(True):
#         cap.grab()
#         ret, frame = cap.read()
#         frame=cv2.resize(frame, (960, 540)) 
#         cv2.imshow('Capturing',frame)
        
#         if cv2.waitKey(1) & 0xFF == ord('q'): #click q to stop capturing
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return 0

# if __name__ == '__main__':
#     import sys
#     sys.exit(main(sys.argv))

# import imagezmq

# sender = imagezmq.ImageSender(connect_to='rtsp://admin:admin123@192.168.1.250:554')

# print(sender)

# test_camera.py
#
# Open an RTSP stream and feed image frames to 'openalpr'
# for real-time license plate recognition.

import numpy as np
import cv2
from openalpr import Alpr


RTSP_SOURCE  = 'rtsp://admin:admin123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=1'
WINDOW_NAME  = 'openalpr'
FRAME_SKIP   = 15


def open_cam_rtsp(uri, width=1280, height=720, latency=2000):
    gst_str = ('rtspsrc location={} latency={} ! '
               'rtph264depay ! h264parse ! omxh264dec ! nvvidconv ! '
               'video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! '
               'videoconvert ! appsink').format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


def main():
    alpr = Alpr("us", "C:/openalpr_64/openalpr.conf", "C:/openalpr_64/runtime_data")
    print("alpr.is_loaded()")
    if not alpr.is_loaded():
        print('Error loading OpenALPR')
        sys.exit(1)
    alpr.set_top_n(3)
    #alpr.set_default_region('new')

    cap = open_cam_rtsp(RTSP_SOURCE)
    if not cap.isOpened():
        alpr.unload()
        sys.exit('Failed to open video file!')
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowTitle(WINDOW_NAME, 'OpenALPR video test')

    _frame_number = 0
    while True:
        ret_val, frame = cap.read()
        if not ret_val:
            print('VidepCapture.read() failed. Exiting...')
            break

        _frame_number += 1
        if _frame_number % FRAME_SKIP != 0:
            continue
        cv2.imshow(WINDOW_NAME, frame)

        results = alpr.recognize_ndarray(frame)
        for i, plate in enumerate(results['results']):
            best_candidate = plate['candidates'][0]
            print('Plate #{}: {:7s} ({:.2f}%)'.format(i, best_candidate['plate'].upper(), best_candidate['confidence']))

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    cap.release()
    alpr.unload()


if __name__ == "__main__":
    main()