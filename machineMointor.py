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
from PyQt5.QtWidgets import * #QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget

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

class DynamicDrawMachines(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        self.points = 100
        MyMplCanvas.__init__(self, *args, **kwargs)


    def compute_initial_figure(self):
        self.xData = list(range(self.points ))
        self.yData = [0]*self.points
        self.axes.plot(self.xData,self.yData,'b')
        self.axes.set_ylim([0,100])
        self.axes.set_xlim([0, self.points])
        self.axes.set_yticks(range(0,101,10))
        self.axes.grid(True)


    def update_figure(self):
        self.yData = self.yData[1:]+[random.randint(20, 80)]
        self.axes.plot(self.xData,self.yData,'b')
        self.axes.set_ylim([0, 100])
        self.axes.set_xlim([0, self.points])
        self.axes.set_yticks(range(0, 101, 10))
        self.axes.grid(True)
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

        H1 = QHBoxLayout(self.main_widget)
        self.ddm = DynamicDrawMachines(self.main_widget,width=5, height=4, dpi=100)
        H1.addWidget(self.ddm)

        #插入选择框
        V1 = QVBoxLayout(self.main_widget)
        self.chooseColonyLable = QLabel(u'集群')
        self.chooseColony = QComboBox()
        self.chooseColony.insertItems(1,self.colony)
        self.chooseColony.currentIndexChanged.connect(self.changeColony)
        self.chooseMachineLable = QLabel(u'机器IP')
        self.chooseMachine = QComboBox()
        self.chooseMachine.currentIndexChanged.connect(self.changeMachine)
        self.chooseDeviceLable = QLabel(u'机器设备')
        self.chooseDevice = QComboBox()
        self.useLocalData = QCheckBox('使用本地数据',self)
        self.useLocalData.toggle()
        self.useLocalData.stateChanged.connect(self.useLocalDataChange)
        V1.addWidget(self.chooseColonyLable)
        V1.addWidget(self.chooseColony)
        V1.addWidget(self.chooseMachineLable)
        V1.addWidget(self.chooseMachine)
        V1.addWidget(self.chooseDeviceLable)
        V1.addWidget(self.chooseDevice)
        V1.addWidget(self.useLocalData)
        self.outputsLable = QLabel(u'系统状况')
        self.outputsSysCon = QTextEdit()
        V1.addWidget(self.outputsLable)
        V1.addWidget(self.outputsSysCon)
        H1.addLayout(V1)




        #self.setLayout(V2)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # 状态条显示2秒
        self.statusBar().showMessage("Supported by Xi'an Jiaotong Univesity", 2000)
        #设置分辨率
        #self.setGeometry(300,300,600,600)
        #设置定时器
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timerEvent)
        timer.start(1000)# +1s

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
        self.localDataPath = self.currentPath + '/Data'#数据默认地址
        self.configDataPath = self.localDataPath
        self.readDataPath = self.localDataPath
        ii = 0
        while (ii < len(lines)):
            if(lines[ii].strip().decode('utf-8')=='-dataDir'):#如果用户指定数据存放地址
                self.configDataPath = lines[ii+1].strip().decode('utf-8')
                ii+=2
            if (lines[ii].strip() == '-colony'):
                colonyTemp = lines[ii + 1].strip().decode('utf-8')
                colony.append(lines[ii + 1].strip().decode('utf-8'))
                machineInColony[lines[ii + 1].strip().decode('utf-8')] = []
                ii += 3
            while (ii < len(lines) and lines[ii].strip().decode('utf-8') != '-colony'):
                machineInColony[colonyTemp].append(lines[ii].strip().decode('utf-8'))
                mapLen = len(self.IPMap)
                self.IPMap[mapLen] = lines[ii].strip().decode('utf-8')
                self.IPMapInv[lines[ii].strip().decode('utf-8')] = mapLen
                ii += 1
        self.colony = colony
        self.machineInColony = machineInColony

    def readJson(self):
        import json
        fileName = ''
        f = open(fileName)
        machineMap = json.load(f,encoding='utf-8')
        return  machineMap

    def readData(self):
        dataPath = self.readDataPath
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

    def changeColony(self):
        self.selectedColony = self.chooseColony.currentText()
        self.chooseDevice.clear()
        self.chooseMachine.clear()
        ipList = self.machineInColony[self.selectedColony]
        self.chooseMachine.insertItems(1,ipList)

    def changeMachine(self):
        self.selectedMachine = self.chooseMachine.currentText()
        self.chooseDevice.clear()
        if(len(self.chooseMachine)==0):
            return
        devList = self.ipsData[self.selectedMachine][2]
        self.chooseDevice.insertItems(1,devList)

    def useLocalDataChange(self,state):
        checkState = state
        if state == 2:
            self.readDataPath  = self.localDataPath
        else:
            self.readDataPath = self.configDataPath



    #timer fuction
    def timerEvent(self):
        self.ddm.update_figure()
        self.outputsSysCon.append(u"系统正常，哈哈哈哈哈哈")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("信息设备运行评估云平台")
    aw.show()
    #sys.exit(qApp.exec_())
    app.exec_()
