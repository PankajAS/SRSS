
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt, QRegExp, QThread
from PyQt5.QtGui import QColor
from functools import partial

class SearchTab(QWidget):
    def __init__(self, parent, db):
         super(QWidget, self).__init__(parent)
         grid_layout = QGridLayout()
         self.db = db

         form_layout = self.createForm()
         grid_layout.addLayout(form_layout,0,0)


         vbox_widget = QWidget(self)
         self.searchLabel = QVBoxLayout(vbox_widget)
         search_label = QLabel()
         search_label.setText("Search Results")
         vbox_widget.setStyleSheet("background-color: grey;")
         self.searchLabel.addWidget(search_label)
         

         grid_layout.addWidget(vbox_widget, 1,0)

         self.table_layout = self.createTableView()
         grid_layout.addWidget(self.table_layout, 2,0)


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
        self.from_date_picker = QDateEdit()
        self.from_date_picker.setCalendarPopup(True) 

        self.to_date_picker = QDateEdit()
        self.to_date_picker.setCalendarPopup(True)

        fd_label = QLabel("From Date")
        fd_label.setStyleSheet("padding-left: 15px;")

        to_label = QLabel("To Date")
        to_label.setStyleSheet("padding-left: 15px;")

        vh_label = QLabel("Vehical Number")
        vh_label.setStyleSheet("padding-left: 15px;")

        vhical_editor = QLineEdit()
        vhical_editor.setReadOnly(True)

        layout.addRow(fd_label, self.from_date_picker)
        layout.addRow(to_label, self.to_date_picker)
        layout.addRow(vh_label, vhical_editor)
        layout.addRow(None, searchButton)
        # layout.addRow(self.pathLabel,pathConfig)
        # layout.addRow(None, self.loading)
        # layout.addRow(None, self.error)

        # self.loading.setHidden(True)
        # self.error.hide()
        
        return layout

    def createTableView(self):
        table = QTableWidget(0,4)
        table.setStyleSheet("border-bottom: 2px solid grey;border-left: 2px solid grey;border-right: 2px solid grey;")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setHorizontalHeaderLabels(["SL NO.","DATE","CAMERA NAME","VEHICALE NUMBER"])

        return table

    def searchrecord(self):
        print('search', self.from_date_picker.date().toString("dd-MM-yyyy"))
        print('search', self.to_date_picker.date().toString("dd-MM-yyyy"))
        fromd = self.from_date_picker.date().toString("dd-MM-yyyy")
        fromt = self.to_date_picker.date().toString("dd-MM-yyyy")
        data = self.db.getVehicalsSearch(fromd,fromt,'')
        self.table_layout.setRowCount(0)
        for rowPosition, item in enumerate(data):
            print(rowPosition)
            row_c = self.table_layout.rowCount()
            self.table_layout.insertRow(row_c)
            sn = QTableWidgetItem(str(rowPosition+1))
            sn.setTextAlignment(Qt.AlignHCenter)

            date = QTableWidgetItem(item['date'])
            date.setTextAlignment(Qt.AlignHCenter)

            name = QTableWidgetItem(item['name'])
            name.setTextAlignment(Qt.AlignHCenter)

            number = QTableWidgetItem(item['number'])
            number.setTextAlignment(Qt.AlignHCenter)

            self.table_layout.setItem(rowPosition , 0, sn)
            self.table_layout.setItem(rowPosition , 1, date)
            self.table_layout.setItem(rowPosition , 2,  name)
            self.table_layout.setItem(rowPosition , 3,  number)
