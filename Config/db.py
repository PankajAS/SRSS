from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import os

class SESDatabase:
    con = None
    def __init__(self):
        print("")

    def createDb(self):
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        # if os.path.isfile("SESDatabase")==False:
        #     self.con.setDatabaseName("SESDatabase")
        self.con.setDatabaseName("SESDatabase")
        self.con.open()
        print(self.con.tables())
        return self.con

    def getDbInstance(self):
        if self.con==None:
            self.createDb()
        return self.con

    def createCameraTable(self):
        if "cameras" in self.con.tables() or self.con.isOpen()==False:
            print("Table Already there")
            return
        createTableQuery = QSqlQuery(self.con)
        createTableQuery.exec(
            """
            CREATE TABLE cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                name VARCHAR(40) NOT NULL,
                ip VARCHAR(50),
                username VARCHAR(40) NOT NULL,
                password VARCHAR(40) NOT NULL
            )
            """
        )
        
        self.con.commit()
        print(self.con.tables())
    
    def createSettingsTable(self):
        if "settings" in self.con.tables() or self.con.isOpen()==False:
            print("Table Already there")
            return
        createTableQuery = QSqlQuery(self.con)
        createTableQuery.exec(
            """
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                recordingpath VARCHAR(40) NOT NULL
            )
            """
        )
        
        self.con.commit()
        print("created-settings: ", createTableQuery.lastError().text())
        print(self.con.tables())
    
    def addDataToSettingsTable(self, id,path):
        if self.con.isOpen()==False:
            self.con.open()
        query = QSqlQuery(self.con)
        result = query.exec(
         f"""INSERT INTO settings (id, recordingpath)
         VALUES ('{id}', '{path}')""")
        print("inserted-settings: ", query.lastError().text())
        self.con.commit()
        print(self.con.tables())

    def addDataToCameraTable(self, id,name,ip,user,password):
        if self.con.isOpen()==False:
            self.con.open()
        query = QSqlQuery(self.con)
        result = query.exec(
         f"""INSERT INTO cameras (id, name, ip, username, password)
         VALUES ('{id}', '{name}', '{ip}', '{user}', '{password}')""")
        print("inserted", query.lastError().text())
        self.con.commit()
        print(self.con.tables())

    def getCameraRecords(self):
        records = []
        query = QSqlQuery()
        query.prepare("SELECT * FROM cameras")
        query.exec()

        while query.next():
            print(query.value(1))
            records.append({"id":query.value(0),"name":query.value(1),"ip":query.value(2), "user":query.value(3),"pass":query.value(4)})
        print(records)
        return records
    
    def getSettingsRecords(self):
        records = []
        query = QSqlQuery()
        query.prepare("SELECT * FROM settings")
        query.exec()

        while query.next():
            print(query.value(1))
            records.append({"id":query.value(0),"recordingpath":query.value(1)})
        print(records)
        return records

    def deleteCamera(self,id):
        if self.con.isOpen()==False:
            self.con.open()
        query = QSqlQuery(self.con)
        result = query.exec(
         f"""DELETE FROM cameras where id={id}""")
        print("deleted-Camera", query.lastError().text())
        self.con.commit()

        # print("data",query.record().field(1).name())