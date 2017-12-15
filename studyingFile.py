import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MyWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(800,600)
        self.center()
        self.setWindowTitle('myApp')
        self.setToolTip('watch what')

    def closeEvent(self, event):
        reply = QMessageBox.question(self,'info',"sure to quit",\
                                     QMessageBox.Yes, QMessageBox.No)
        if reply==QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,\
                  (screen.height()-size.height())/2)

myApp = QApplication(sys.argv)
mywidget = MyWidget()
mywidget.show()
mywidget.statusBar().showMessage('ready')
sys.exit(myApp.exec_())