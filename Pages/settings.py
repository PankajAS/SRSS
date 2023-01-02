
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt, QRegExp, QThread
from PyQt5.QtGui import QRegExpValidator
import time
# from onvif import ONVIFCamera, ONVIFError
from threading import Thread
import asyncio
from functools import partial
import uuid

class SettingsTab(QWidget):
    
    def __init__(self, parent, maintab, database):
        super(QWidget, self).__init__(parent)
        self.database = database
        self.cameraList = self.database.getCameraRecords()
        # Exmaple Record [{'id': 1, 'name': 'CAM-1', 'ip': '192.168.1.250', 'user': 'admin', 'pass': 'admin123'}]

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
        self.pathLabel =  QLabel("Path: -----")
        self.path =  None

        getSettings = self.database.getSettingsRecords()

        if len(getSettings)>0:
            self.path = getSettings[0]['recordingpath']
            self.pathLabel.setText(f"Path: {self.path}")
        
        self.saveButton.clicked.connect(self.saveCamera)
        self.loading = QLabel("Connecting.....")
        self.error = QLabel("")
        lay = QGridLayout()

        # lay.addWidget(QtWidgets.QTextEdit(),0,0)

        self.table = QTableWidget(0,10)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["SL NO.","CAMERA NAME","CAMERA ADDRESS(IP)","USER NAME","PASSWORD","STATUS","ACTION","RECORDING","DELETE","ANPR"])

        lay.addWidget(QTextEdit(), 0,1)

        lay.addLayout(self.createForm(),0,0)
        getSettings = self.database.getSettingsRecords()
        for rowPosition, item in enumerate(self.cameraList):
            self.table.insertRow(rowPosition)
            connectbtn = QPushButton('Connect')
            disconnectbtn = QPushButton('Disonnect')
            startRecording = QPushButton('START')
            delete = QPushButton('DELETE')
            anpr = QPushButton('ON')

            if len(getSettings)==0:
                data = self.main.create_video_thread({"name":item['name'], "id":item['id'],"ip":item['ip'],
                "user":item['user'],
                "pass":item['pass'], "thread":None})
            else:
                data = self.main.create_video_thread({"name":item['name'], "id":item['id'],"ip":item['ip'],
                "user":item['user'],
                "pass":item['pass'], "thread":None})
            
            connectbtn.clicked.connect(partial(self.connectCamera,data, rowPosition))

            disconnectbtn.clicked.connect(partial(self.disconnectCamera,data, rowPosition))
            
            startRecording.clicked.connect(partial(self.startRecord,data,rowPosition))
            delete.clicked.connect(partial(self.deleteRecord,data,rowPosition))
            anpr.clicked.connect(partial(self.onAnpr,data,rowPosition))


            idItem = QTableWidgetItem(str(rowPosition+1))
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
            self.table.setCellWidget(rowPosition, 8,delete)
            self.table.setCellWidget(rowPosition, 9,anpr)
            

        lay.addWidget(self.table, 1,0,1,2)

        self.setLayout(lay)

    def createForm(self):
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        pathConfig = QPushButton('Select Location', self)

        pathConfig.clicked.connect(partial(self.configVideoLocation))

        layout.addRow(QLabel("Camera Name"), self.nameInput)
        layout.addRow(QLabel("Camera Address (IP)"), self.ip)
        layout.addRow(QLabel("User Name(ID)"), self.username)
        layout.addRow(QLabel("Password"), self.password)
        layout.addRow(None, self.saveButton)
        layout.addRow(self.pathLabel,pathConfig)
        layout.addRow(None, self.loading)
        layout.addRow(None, self.error)

        self.loading.setHidden(True)
        self.error.hide()
        
        return layout
    
    def configVideoLocation(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderpath:
            self.error.setText("")
            self.error.hide()
            self.path = folderpath
            self.pathLabel.setText("Path: "+self.path)
            self.database.deleteSettings()
            self.database.addDataToSettingsTable(1,folderpath)
            print("configVideoLocation",self.path)

    def deleteRecord(self,data,id):
        print('deleteRecord', id)
        self.database.deleteCamera(data['id'])
        self.table.removeRow(id)
        self.main.remove_camera(data)
        print(self.cameraList)
        del self.cameraList[id-1]
    
    def onAnpr(self,data,rowPosition):
        offAnpr = QPushButton('OFF')
        offAnpr.clicked.connect(partial(self.offAnpr,data,rowPosition))
        self.table.setCellWidget(rowPosition, 9,offAnpr)
        self.main.startAnpr(data)

    def offAnpr(self,data,rowPosition):
        offAnpr = QPushButton('ON')
        offAnpr.clicked.connect(partial(self.onAnpr,data,rowPosition))
        self.table.setCellWidget(rowPosition, 9,offAnpr)
        self.main.stopAnpr(data)

    def startRecord(self,data, rowPosition):
        # getSettings = self.database.getSettingsRecords()
        # folderpath = None
        # if len(getSettings)==0:
        #     folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        #     self.path = folderpath
        #     self.database.addDataToSettingsTable(1,folderpath)
        # else:
        #     folderpath = getSettings[0]['recordingpath']
        
        if self.path==None:
            self.error.setText("Select Video Path")
            self.error.show()
            return
        #     self.configVideoLocation()
        # self.path = getSettings[0]['recordingpath']
        startRecording = QPushButton('STOP')
        startRecording.clicked.connect(partial(self.stopRecord,data,rowPosition))
        self.table.setCellWidget(rowPosition, 7,startRecording)
        self.main.startRecording(data,self.path)

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
            
            rowPosition = self.table.rowCount()
            id = uuid.uuid4().int & (1<<32)-1
            self.database.addDataToCameraTable(id,self.nameInput.text(),self.ip.text(),self.username.text(),self.password.text())
            self.cameraList.append({'id':id,'name':self.nameInput.text(),'ip':self.ip.text(),'user':self.username.text(),'pass':self.password.text()})
            self.table.insertRow(rowPosition)
            connectbtn = QPushButton('Connect')
            disconnectbtn = QPushButton('Disonnect')
            startRecording = QPushButton('START')
            delete = QPushButton('DELETE')
            anpr = QPushButton('ON')

            data = self.main.create_video_thread({"name":self.nameInput.text(), "id":id,"ip":self.ip.text(),
            "user":self.username.text(),
            "pass":self.password.text(), "thread":None})
            
            
            connectbtn.clicked.connect(partial(self.connectCamera,data,rowPosition))

            disconnectbtn.clicked.connect(partial(self.disconnectCamera,data,rowPosition))

            startRecording.clicked.connect(partial(self.startRecord,data,rowPosition))
            delete.clicked.connect(partial(self.deleteRecord,data,rowPosition))
            anpr.clicked.connect(partial(self.onAnpr,data,rowPosition))

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
            self.table.setCellWidget(rowPosition, 5,statusItem)
            self.table.setCellWidget(rowPosition, 6,connectbtn)
            self.table.setCellWidget(rowPosition, 7,startRecording)
            self.table.setCellWidget(rowPosition, 8,delete)
            self.table.setCellWidget(rowPosition, 9,anpr)

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
        # 192.168.1.250

    def connectCamera(self, data, rowPosition):
        # import pdb
        self.error.hide()
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
        index = next((index for (index, d) in enumerate(self.cameraList) if d["id"] == data['id']), None)
        print("index======",index, data['id'])
        #print("connectCamera", data['thread'].videoimage)
        # pdb.set_trace()
        disconnectbtn = QPushButton('Disonnect')
        disconnectbtn.clicked.connect(partial(self.disconnectCamera,data,index))
        self.table.setCellWidget(index, 6,disconnectbtn)
        statusItem = QLabel("Connected")
        statusItem.setAlignment(Qt.AlignHCenter)
        self.table.setCellWidget(index, 5,statusItem)
    
    def disconnectCamera(self, data,rowPosition):
        print("disconnectCamera ", data)
        self.error.hide()
        statusItem = QLabel("Not Connected")
        statusItem.setAlignment(Qt.AlignHCenter)
        connectbtn = QPushButton('Connect')
        index = next((index for (index, d) in enumerate(self.cameraList) if d["id"] == data['id']), None)
        connectbtn.clicked.connect(partial(self.connectCamera,data,index))
        self.table.setCellWidget(index, 6,connectbtn)
        self.table.setCellWidget(index, 5,statusItem)
        self.main.remove_camera(data)



        