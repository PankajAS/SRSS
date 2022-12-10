
from PyQt5.QtWidgets import QListWidget,QBoxLayout,QListWidgetItem, QWidget, QLabel, QGridLayout


class VideoImages:
     def __init__(self,name,user,image,ip,password,id):
        self.name = name
        self.id = id
        self.ip = ip
        self.password = password
        self.image = image
        self.user = user
        self.slot = 0
        self.height = image.height()
        self.width = image.width()