# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)
        # 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyStaticMplCanvas(MyMplCanvas):
    """静态画布：一条正弦线"""
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """动态画布：每秒自动更新，更换一条折线。"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        # timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # 构建4个随机整数，位于闭区间[0, 10]
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()

class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.currentPath = sys.path[0]#程序运行的路径
        self.readConfig()#读取配置文件
        self.readData()#读取数据

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("程序主窗口")

        self.file_menu = QMenu('&文件', self)
        self.file_menu.addAction('&退出', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&帮助', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&关于', self.about)

        self.main_widget = QWidget(self)

        l = QVBoxLayout(self.main_widget)
        #sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        #l.addWidget(sc)
        l.addWidget(self.dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # 状态条显示2秒
        self.statusBar().showMessage("Supported by Xi'an Jiaotong Univesity", 2000)
        #设置定时器信号
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timerEvent)
        timer.start(1000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QMessageBox.about(self, "关于",
        """
信息设备运行评估云平台
        
国网重庆电力公司信通分公司
        
Copyright 2017 
        """
        )

    def readConfig(self):
        configFileName = self.currentPath+'/config.txt'
        colony = []
        machineInColony = {}
        lines = open(configFileName).readlines()
        self.IPMap = {}  # {ii: self.sampleList[ii] for ii in range(30)}
        self.IPMapInv = {}  # {self.sampleList[ii]:ii for ii in range(30)}
        self.dataPath = self.currentPath + '/Data'#数据默认地址
        ii = 0
        while (ii < len(lines)):
            if(lines[ii].strip()=='-dataDir'):#如果用户指定数据存放地址
                self.dataPath = lines[ii+1].strip()
                ii+=2
            if (lines[ii].strip() == '-colony'):
                colonyTemp = lines[ii + 1].strip()
                colony.append(lines[ii + 1].strip())
                machineInColony[lines[ii + 1].strip()] = []
                ii += 3
            while (ii < len(lines) and lines[ii].strip() != '-colony'):
                machineInColony[colonyTemp].append(lines[ii].strip())
                mapLen = len(self.IPMap)
                self.IPMap[mapLen] = lines[ii].strip()
                self.IPMapInv[lines[ii].strip()] = mapLen
                ii += 1
        self.colony = colony
        self.machineInColony = machineInColony

    def readData(self):
        dataPath = self.dataPath
        ipsData = {}
        for colonyTemp in self.colony:
            for ips in self.machineInColony[colonyTemp]:
                dataAllTemp = []
                dataLabels = []
                timeLabels = {}
                devsMap = {}
                try:
                    filePath = dataPath + '/' + ips + '-ram.txt'
                    dataRamTemp = open(dataPath + '/' + ips + '-ram.txt')
                    tableRamTemp = dataRamTemp.readlines()
                    tableRamTemp.pop(0)
                    dataLabels.append('ram')
                    devsMap['ram'] = len(devsMap)
                    dataRamTemp.close()
                except:
                    tableRamTemp = []
                try:
                    filePath = dataPath + '/' + ips + '-disk.txt'
                    dataDiskTemp = open(dataPath + '/' + ips + '-disk.txt')
                    tableDiskTemp = dataDiskTemp.readlines()
                    tableDiskTemp.pop(0)
                    dataDiskTemp.close()
                    stat = 0
                    for line in tableDiskTemp:
                        if (stat > 1000):
                            break
                        labelTemp = line.strip().split(',')[2]
                        if (not labelTemp in dataLabels):
                            dataLabels.append(labelTemp)
                            devsMap[labelTemp] = len(devsMap)
                except:
                    tableDiskTemp = []
                ipsInfo = [tableRamTemp, tableDiskTemp, dataLabels, devsMap]
                ipsData[ips] = ipsInfo
        self.ipsData = ipsData

    #timer fuction
    def timerEvent(self):
        self.dc.update_figure()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("信息设备运行评估云平台")
    aw.show()
    #sys.exit(qApp.exec_())
    app.exec_()
