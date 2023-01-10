
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt, QRegExp, QThread
from PyQt5.QtGui import QColor
from functools import partial

class SearchTab(QWidget):
    def __init__(self, parent):
         super(QWidget, self).__init__(parent)
         grid_layout = QGridLayout()

         form_layout = self.createForm()
         grid_layout.addLayout(form_layout,0,0)


         vbox_widget = QWidget(self)
         self.searchLabel = QVBoxLayout(vbox_widget)
         search_label = QLabel()
         search_label.setText("Search Results")
         vbox_widget.setStyleSheet("background-color: grey;")
         self.searchLabel.addWidget(search_label)
         

         grid_layout.addWidget(vbox_widget, 1,0)

         table_layout = self.createTableView()
         grid_layout.addWidget(table_layout, 2,0)


         self.setLayout(grid_layout)

        
    def createForm(self):
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        searchButton = QPushButton('Search Record', self)
        searchButton.setStyleSheet("QPushButton:pressed { background-color: grey;color:black; }" "QPushButton { border: 2px solid grey; padding:5px; border-radius:5px }")
        # searchButton.setAutoFillBackground(True)
        # palette = searchButton.palette()
        # palette.setColor(QPalette.Button, QColor(255, 0, 0)) # red button color
        # searchButton.setPalette(palette)
        searchButton.clicked.connect(partial(self.searchrecord))
        from_date_picker = QDateEdit()
        from_date_picker.setCalendarPopup(True) 

        to_date_picker = QDateEdit()
        to_date_picker.setCalendarPopup(True) 

        layout.addRow(QLabel("From Date"), from_date_picker)
        layout.addRow(QLabel("To Date"), to_date_picker)
        layout.addRow(QLabel("Vehical Number"), QLineEdit())
        layout.addRow(None, searchButton)
        # layout.addRow(self.pathLabel,pathConfig)
        # layout.addRow(None, self.loading)
        # layout.addRow(None, self.error)

        # self.loading.setHidden(True)
        # self.error.hide()
        
        return layout

    def createTableView(self):
        self.table = QTableWidget(0,4)
        self.table.setStyleSheet("border-bottom: 2px solid grey;border-left: 2px solid grey;border-right: 2px solid grey;")
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(["SL NO.","DATE","CAMERA NAME","VEHICALE NUMBER"])

        return self.table

    def searchrecord(self):
        print('search')