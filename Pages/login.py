from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt, QSize
# from PyQt5 import QtCore, QtGui
from Pages.main import MainTab
from Pages.search import SearchTab
from Pages.settings import SettingsTab

class LoginForm(QWidget):
    def __init__(self,parent):
        super(QWidget, self).__init__(parent)
        # self.central_widget = QtGui.QStackedWidget()
        self.parent = parent
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignHCenter)

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Enter Passcode')
        

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.openTabs)

        layout.addRow(None, self.lineEdit_username)
        layout.addRow(None, button_login)

        # parent.setStyleSheet("""
        # QFormLayout 
        # { 
        #     margin:100px
        # }
        # """)
        # self.central_widget
        self.setLayout(layout)

    def openTabs(self):
            # Initialize tab screen
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet("""
            QTabBar::tab 
            { 
                background-color : grey;
                padding: 10px; 
                margin:1px;
                border-radius:5px;
            }
            QTabBar::tab:selected 
            { 
                background-color : black;
                color:white;
            }
            QTabWidget::pane {
                border: 0 solid white;
                margin: 0 -15px -15px -15px;
            }
            """)
            self.tab1 = MainTab(self)
            self.tab2 = SearchTab(self)
            self.tab3 = SettingsTab(self, self.tab1)
            self.login = LoginForm(self)
            self.tab1.setTab(self.tab3)
            self.tabs.resize(400,200)
            
            # Add tabs
            self.tabs.addTab(self.tab1,"Main")
            self.tabs.addTab(self.tab2,"Search")
            self.tabs.addTab(self.tab3,"Settings")
            
            
            # Create first tab
            self.tab1.layout = QVBoxLayout(self)
            # self.tab1.setLayout(self.grid)
        
            # Add tabs to widget
            self.parent.layout.addWidget(self.tab1)
            self.parent.setLayout(self.parent.layout)


