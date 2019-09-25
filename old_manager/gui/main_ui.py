from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import sqlite3
import sys

from sql import sql


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()

        self.initDatabase()
        self.initUI()
        self.initSandbox()

        mainWidget = QtWidgets.QWidget()
        mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(mainWidget)
        self.setGeometry(50, 50, 800, 800)
        self.setWindowTitle('AutoManager')
        self.show()

        self.query()

    def initDatabase(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(sql.DATABASE)
        self.db.open()

    def initUI(self):
        self.model = QtSql.QSqlQueryModel()
        self.table = QtWidgets.QTableView()
        self.table.setModel(self.model)

        self.mainLayout.addWidget(self.table)

    def initSandbox(self):
        vbox = QtWidgets.QVBoxLayout()
        self.btnQuery = QtWidgets.QPushButton('Query')

        vbox.addWidget(self.btnQuery)

        self.mainLayout.addLayout(vbox)

        self.setSandboxSlots()

    def setSandboxSlots(self):
        self.btnQuery.clicked.connect(self.changeQuery)

    def query(self):
        query = 'SELECT p.PlayerId, s.Date, p.LastName, ' \
                'p.FirstName, p.Team, s.FantasyPoints FROM players AS p ' \
                'JOIN stats AS s ON p.PlayerId = s.PlayerId ' \
                'ORDER BY LOWER(p.LastName), p.FirstName, s.Date'

        self.model.setQuery(query, self.db)

    def changeQuery(self):
        query = 'SELECT p.PlayerId, s.Date, p.LastName, ' \
                'p.FirstName, p.Team, s.FantasyPoints FROM players AS p ' \
                'JOIN stats AS s ON p.PlayerId = s.PlayerId ' \
                'WHERE s.Date = "2018-10-28" ' \
                'ORDER BY LOWER(p.LastName), p.FirstName, s.Date'

        self.model.setQuery(query, self.db)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
