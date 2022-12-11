
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt, QRegExp, QThread
from PyQt5.QtGui import QRegExpValidator
import time
# from onvif import ONVIFCamera, ONVIFError
from threading import Thread
import asyncio
from functools import partial

class SettingsTab(QWidget):
    
    def __init__(self, parent, maintab):
        super(QWidget, self).__init__(parent)
        self.cameraList = [{'id': 1, 'name': 'CAM-1', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 2, 'name': 'CAM-2', 'ip': '192.168.1.251', 'user': 'admin', 'pass': 'admin123'},
        {'id': 3, 'name': 'CAM-3', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 4, 'name': 'CAM-4', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 5, 'name': 'CAM-5', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 17, 'name': 'CAM-17', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 6, 'name': 'CAM-7', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 7, 'name': 'CAM-8', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 8, 'name': 'CAM-9', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 9, 'name': 'CAM-10', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 10, 'name': 'CAM-11', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 11, 'name': 'CAM-12', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 12, 'name': 'CAM-13', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 13, 'name': 'CAM-14', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 14, 'name': 'CAM-15', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 15, 'name': 'CAM-16', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'},
        {'id': 16, 'name': 'CAM-17', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'}]

        self.main = maintab

        # parent.setCentralWidget(central_widget)
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipValidator = QRegExpValidator(ipRegex, self)   

        self.nameInput = QLineEdit()
        self.ip = QLineEdit()
        self.ip.setValidator(ipValidator)      
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.saveButton = QPushButton('Save Camera', self)
        
        self.saveButton.clicked.connect(self.saveCamera)
        self.loading = QLabel("Connecting.....")
        self.error = QLabel("")
        lay = QGridLayout()

        # lay.addWidget(QtWidgets.QTextEdit(),0,0)

        self.table = QTableWidget(0,8)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["SL NO.","CAMERA NAME","CAMERA ADDRESS(IP)","USER NAME","PASSWORD","STATUS","ACTION","RECORDING"])

        lay.addWidget(QTextEdit(), 0,1)

        lay.addLayout(self.createForm(),0,0)

        for rowPosition, item in enumerate(self.cameraList):
            self.table.insertRow(rowPosition)
            connectbtn = QPushButton('Connect')
            disconnectbtn = QPushButton('Disonnect')
            startRecording = QPushButton('START')

            data = self.main.create_video_thread({"name":item['name'], "id":rowPosition+1,"ip":item['ip'],
            "user":item['user'],
            "pass":item['pass'], "thread":None})
            
            connectbtn.clicked.connect(partial(self.connectCamera,data, rowPosition))

            disconnectbtn.clicked.connect(partial(self.disconnectCamera,data, rowPosition))
            
            startRecording.clicked.connect(partial(self.startRecord,data,rowPosition))

            idItem = QTableWidgetItem(str(item['id']))
            idItem.setTextAlignment(Qt.AlignHCenter)

            nameItem = QTableWidgetItem(str(item['name']))
            nameItem.setTextAlignment(Qt.AlignHCenter)

            ipItem = QTableWidgetItem(str(item['ip']))
            ipItem.setTextAlignment(Qt.AlignHCenter)


            userItem = QTableWidgetItem(str(item['user']))
            userItem.setTextAlignment(Qt.AlignHCenter)

            passItem = QTableWidgetItem(str(item['pass']))
            passItem.setTextAlignment(Qt.AlignHCenter)

            statusItem = QLabel("Not Connected")
            statusItem.setAlignment(Qt.AlignHCenter)

            self.table.setItem(rowPosition , 0, idItem)
            self.table.setItem(rowPosition , 1, nameItem)
            self.table.setItem(rowPosition , 2,  ipItem)
            self.table.setItem(rowPosition , 3,  userItem)
            self.table.setItem(rowPosition , 4,  passItem)
            self.table.setCellWidget(rowPosition, 5,statusItem)
            self.table.setCellWidget(rowPosition, 6,connectbtn)
            self.table.setCellWidget(rowPosition, 7,startRecording)

            

        lay.addWidget(self.table, 1,0,1,2)
        
        # .setStyleSheet("""
        # QFormLayout 
        # { 
        #     background-color : grey;
        #     padding: 10px; 
        # }
        # """)

        self.setLayout(lay)

    def createForm(self):
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        # nameInput.setStyleSheet("""
        # QLineEdit 
        # { 
        #     width: 180px;
        #     height: 50px 
        # }
        # """)

        layout.addRow(QLabel("Camera Name"), self.nameInput)
        layout.addRow(QLabel("Camera Address (IP)"), self.ip)
        layout.addRow(QLabel("User Name(ID)"), self.username)
        layout.addRow(QLabel("Password"), self.password)
        layout.addRow(None, self.saveButton)
        layout.addRow(None, self.loading)
        layout.addRow(None, self.error)

        self.loading.setHidden(True)
        self.error.hide()

        # time.sleep(10)
        # loading.setHidden(False)
        

        return layout
        

    def startRecord(self,data, rowPosition):
        startRecording = QPushButton('STOP')
        startRecording.clicked.connect(partial(self.stopRecord,data,rowPosition))
        self.table.setCellWidget(rowPosition, 7,startRecording)
        self.main.startRecording(data)

    def stopRecord(self,data, rowPosition):
        startRecording = QPushButton('START')
        startRecording.clicked.connect(partial(self.startRecord,data,rowPosition))
        self.table.setCellWidget(rowPosition, 7,startRecording)
        self.main.stopRecording(data)

    def startThreadSaveCamera(self):
        objThread = Thread(target=self.saveCamera, args=())
        objThread.start()

    def saveCamera(self):
        if self.ip.text()=="" or self.nameInput.text()=="" or self.username.text()=="" or self.password.text()=="":
            self.error.setText("All fields are required!")
            self.error.show()
            return

        
            
        self.error.hide()
        print('Hello',self.ip.text())
        self.loading.setHidden(False)
        self.saveButton.hide() 
        try:
            # thread = Thread(target = ONVIFCamera(self.ip.text(), 80, self.username.text(), self.password.text()))
            # thread.start()
            # thread.join()
            # mycam = await ONVIFCamera(self.ip.text(), 80, self.username.text(), self.password.text())
            # image_service = mycam.create_devicemgmt_service()
            # print(image_service.GetHostname())
            
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            connectbtn = QPushButton('Connect')
            disconnectbtn = QPushButton('Disonnect')
            startRecording = QPushButton('START')

            data = self.main.create_video_thread({"name":self.nameInput.text(), "id":rowPosition+1,"ip":self.ip.text(),
            "user":self.username.text(),
            "pass":self.password.text(), "thread":None})
            
            
            connectbtn.clicked.connect(partial(self.connectCamera,data,rowPosition))

            disconnectbtn.clicked.connect(partial(self.disconnectCamera,data,rowPosition))

            startRecording.clicked.connect(partial(self.startRecord,data,rowPosition))

            idItem = QTableWidgetItem(str(rowPosition+1))
            idItem.setTextAlignment(Qt.AlignHCenter)

            nameItem = QTableWidgetItem(self.nameInput.text())
            nameItem.setTextAlignment(Qt.AlignHCenter)

            ipItem = QTableWidgetItem(self.ip.text())
            ipItem.setTextAlignment(Qt.AlignHCenter)


            userItem = QTableWidgetItem(self.username.text())
            userItem.setTextAlignment(Qt.AlignHCenter)

            passItem = QTableWidgetItem(self.password.text())
            passItem.setTextAlignment(Qt.AlignHCenter)

            statusItem = QLabel("Not Connected")
            statusItem.setAlignment(Qt.AlignHCenter)

            
            self.table.setItem(rowPosition , 0, idItem)
            self.table.setItem(rowPosition , 1, nameItem)
            self.table.setItem(rowPosition , 2, ipItem)
            self.table.setItem(rowPosition , 3, userItem)
            self.table.setItem(rowPosition , 4, passItem)
            # self.table.setItem(rowPosition , 5, QTableWidgetItem("Not Connected"))
            # self.table.setItem(rowPosition , 6, QTableWidgetItem(connectbtn))
            self.table.setCellWidget(rowPosition, 5,statusItem)
            self.table.setCellWidget(rowPosition, 6,connectbtn)
            self.table.setCellWidget(rowPosition, 7,startRecording)
            # disconnectbtn.hide()
            # self.table.setCellWidget(rowPosition, 6,disconnectbtn)
            
            self.main.create_video_thread({"id":rowPosition+1,"ip":self.ip.text(),
            "user":self.username.text(),
            "pass":self.password.text(), "thread":None})

            self.ip.setText("")
            self.username.setText("")
            self.nameInput.setText("")
            self.password.setText("")
        except:
            # print(type(e), e.__str__()) 
            self.error.setText("")
            self.error.show()
        
        self.loading.setHidden(True)
        self.saveButton.show()  
        # self.saveButton.show()
        # self.loading.setHidden(True)
        # 192.168.1.250

    def connectCamera(self, data, rowPosition):
        self.error.hide()
        print("connectCamera", data['thread'].videoimage)
        isAdded = self.main.add_camera(data)
        print("isAdded", isAdded)
        if isAdded==False:
            self.error.setStyleSheet("""
            QLabel 
            {
            color:red;
            }
            """)
            self.error.setText("Maximum Camera limit reached,\n only 4 Cameras can be add at a time.")
            self.error.show()
            return
        
        disconnectbtn = QPushButton('Disonnect')
        disconnectbtn.clicked.connect(partial(self.disconnectCamera,data,rowPosition))
        self.table.setCellWidget(rowPosition, 6,disconnectbtn)
        statusItem = QLabel("Connected")
        statusItem.setAlignment(Qt.AlignHCenter)
        self.table.setCellWidget(rowPosition, 5,statusItem)
    
    def disconnectCamera(self, data,rowPosition):
        print("disconnectCamera ", data)
        self.error.hide()
        statusItem = QLabel("Not Connected")
        statusItem.setAlignment(Qt.AlignHCenter)
        connectbtn = QPushButton('Connect')
        connectbtn.clicked.connect(partial(self.connectCamera,data,rowPosition))
        self.table.setCellWidget(rowPosition, 6,connectbtn)
        self.table.setCellWidget(rowPosition, 5,statusItem)
        self.main.remove_camera(data)



        