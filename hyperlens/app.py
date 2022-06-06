import functools
import pathlib

from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from __main__ import *
from hsiView import hsiView
from roiListWidget import RoiListWidget, RoiListSingleRectItem 

import cv2 

from util import hsi, ui, image

class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        qApp, 
        appName, 
        config=None
    ):
        super(MainWindow, self).__init__()
        self.settings = QtCore.QSettings("labelme", "labelme")
        self.appName = appName
        self.qApp = qApp

        self.openedFileDict = {}

        self.initUI() 

        self.hsiView.SingleRectCreated.connect(self.onSingleRectCreated)
        self.hsiView.SingleRectCreated.connect(self.onSingleRectRemoved)
        
        logger.info(f"Hello, {self.appName}")

    def initUI(self):
        windowSize = self.settings.value("window/size", QtCore.QSize(600, 500))
        windowPosition = self.settings.value("window/position", QtCore.QPoint(0, 0))
        windowState = self.settings.value("window/state", QtCore.QByteArray())
        
        self.resize(windowSize)
        self.move(windowPosition)
        self.restoreState(windowState)

        buildAction = functools.partial(ui.buildAction, self)
        exitAction = buildAction(
            self.tr("&Exit"), 
            self.qApp.quit, 
            None,
            None, 
            self.tr(f"Exit {self.appName}")
        )

        openHSIAction = buildAction(
            self.tr("&Open HSI File"),
            self.openHSI,
            None,
            None,
            self.tr("Open HSI(Hyper Spectral Image)"),
        )

        loadModelAction = buildAction(
            self.tr("&Load Model"), 
            None, 
            None, 
            None, 
            self.tr("Load AI model for Hyper Spectral Image")
        )

        saveAction = buildAction(
            self.tr("&Save Result"), 
            None, 
            None, 
            None, 
            self.tr("Save Result")
        )

        closeHSIAction = buildAction(
            self.tr("&Close HSI File"), 
            self.closeHSI, 
            None, 
            None, 
            self.tr("Load AI model for Hyper Spectral Image")
        )

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu('&File')

        fileMenu.addAction(openHSIAction)
        fileMenu.addAction(loadModelAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(closeHSIAction)
        fileMenu.addAction(exitAction)

        self.statusBar().showMessage('Ready')

        self.hsiView = hsiView(self)
        self.setCentralWidget(self.hsiView)

        self.roiDock = QtWidgets.QDockWidget(self.tr("ROI List"), self)
        self.roiDock.setObjectName("RoiList")
        self.roiDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.roiDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable) 

        self.roiListView = RoiListWidget()
        self.roiDock.setWidget(self.roiListView)

        self.logDock = QtWidgets.QDockWidget(self)
        self.logDock.setObjectName("BottomDock")
        self.logDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable) 

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.roiDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)

        self.show()
        self.update()

        self.openHSI('../strawberry_hyper/Healthy05_irradiance.raw')

    def openHSI(self, targetHdrPath = None):
        if targetHdrPath is None:
            defaultFilePath = "~"
            targetHdrPath = pathlib.Path(
                str(
                    QtWidgets.QFileDialog.getOpenFileName(
                        self,
                        self.tr("Open .hdr File"), 
                        defaultFilePath, 
                        'HDR files (*.hdr)'
                    )[0]
                )
            )
        else: 
            targetHdrPath = pathlib.Path(targetHdrPath)

        targetRawPath = targetHdrPath.with_suffix('.raw')
        if not targetRawPath.exists(): 
            QtWidgets.QMessageBox.information(
                self,
                self.tr("Error"), 
                f"No .raw pair for {str(targetHdrPath)}.", 
                QtWidgets.QMessageBox.Ok
            )
            return
        
        logger.info(f"opening {targetHdrPath.name} & {targetRawPath.name}")
        
        hsiImage, rgbImage = hsi.loadImage(str(targetHdrPath))
        qImage = image.convertCvImage2qImage(rgbImage)

        self.hsiView.setImage(QtGui.QPixmap(qImage))

        self.openedFileDict['raw'] = targetRawPath 
        self.openedFileDict['hdr'] = targetHdrPath 
        self.openedFileDict['rgbArr'] = rgbImage
        self.openedFileDict['hsiArr'] = hsiImage

    def onSingleRectCreated(self, rectItem: QtWidgets.QGraphicsRectItem):
        image = self.openedFileDict['rgbArr']
        x, y, w, h = rectItem.rect().getRect()
        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h) 
        rectImage = image[y1:y2, x1:x2,:]
        self.addRoiSingleRectItem(rectItem, rectImage)
        
    def addRoiSingleRectItem(self, rectItem, rectImage): 
        item = QtWidgets.QListWidgetItem(self.roiListView)
        self.roiListView.addItem(item)
        row = RoiListSingleRectItem('test', self.roiListView, rectImage)
        item.setSizeHint(row.minimumSizeHint())
        self.roiListView.setItemWidget(item, row)

    def onSingleRectRemoved(self, item):
        pass 

    def closeHSI(self): 
        closingFileName = self.openedFileDict['raw'].name
        self.openedFileDict.clear()
        
        logger.info(f"closing {closingFileName}")

        self.hsiView.setImage(None)

    def closeEvent(self, event):
        logger.info(f"Exiting {self.appName} Goodbye.")
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        self.settings.setValue("window/state", self.saveState())
