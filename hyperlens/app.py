import functools
import pathlib

from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from __main__ import *
from hsiView import hsiView
from roiListWidget import RoiListWidget, RoiListSingleRectItemWidget 

import cv2 

from util import hsi, ui, image
import ai as ai

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
        self.threadpool = QtCore.QThreadPool()

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
        fileMenu.addSeparator()
        #fileMenu.addAction(loadModelAction)
        #fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(closeHSIAction)
        fileMenu.addAction(exitAction)  

        self.statusBar().showMessage('Ready')

        self.hsiView = hsiView(self)
        self.setCentralWidget(self.hsiView)

        self.toolbar = QtWidgets.QToolBar("Tools")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setObjectName("Tools")

        self.normalPointerAction = buildAction(
            self.tr("Normal Pointer"), 
            self.onDragMode, 
            None, 
            QtGui.QIcon(str(pathlib.Path('hyperlens/icons/arrows-move.svg'))),
            self.tr("Normal Mode"), 
            False, 
            False, 
            False
        )
        
        self.singleRectanglePointerAction = buildAction(
            self.tr("Single Rectangle"), 
            self.onSingleRectangleMode, 
            None, 
            QtGui.QIcon(str(pathlib.Path('hyperlens/icons/square.svg'))), 
            self.tr("Select Single Patch for inference"), 
            True, 
            False, 
            False
        )

        self.toolbar.addAction(self.normalPointerAction)
        self.toolbar.addAction(self.singleRectanglePointerAction)

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

        #self.openHSI('../strawberry_hyper/Healthy05_irradiance.raw')

    def openHSI(self, targetHdrPath: pathlib.Path = None):
        if type(targetHdrPath) is str or type(targetHdrPath) is type(pathlib.Path): 
            targetHdrPath = pathlib.Path(targetHdrPath)
        else: 
            defaultFilePath = pathlib.Path("~/")
            targetHdrPath = pathlib.Path(
                str(
                    QtWidgets.QFileDialog.getOpenFileName(
                        self,
                        self.tr("Open .hdr File"), 
                        str(defaultFilePath), 
                        'HDR files (*.hdr)'
                    )[0]
                )
            )
        
        targetRawPath = targetHdrPath.with_suffix('.raw')
        if not targetRawPath.exists(): 
            QtWidgets.QMessageBox.information(
                self,
                self.tr("Error"), 
                f"No .raw pair for {str(targetHdrPath)}.", 
                QtWidgets.QMessageBox.Ok
            )
        else: 
            logger.info(f"opening {targetHdrPath.name} & {targetRawPath.name}")
            
            hsiImage, rgbImage = hsi.loadImage(str(targetHdrPath))
            qImage = image.convertCvImage2qImage(rgbImage)

            self.hsiView.setImage(QtGui.QPixmap(qImage))

            self.openedFileDict['raw'] = targetRawPath 
            self.openedFileDict['hdr'] = targetHdrPath 
            self.openedFileDict['rgbArr'] = rgbImage
            self.openedFileDict['hsiArr'] = hsiImage

            self.singleRectanglePointerAction.setEnabled(True)
            self.normalPointerAction.setEnabled(True)
        
    def onSingleRectCreated(self, rectItem: QtWidgets.QGraphicsRectItem, id):
        image = self.openedFileDict['rgbArr']
        x, y, w, h = rectItem.rect().getRect()
        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h) 
        rgbRoi = image[y1:y2, x1:x2,:]
        hsiRoi = self.openedFileDict['hsiArr'][y1:y2, x1:x2]

        item = self.addRoiSingleRectItem(rectItem, rgbRoi)
        item.setData(QtCore.Qt.UserRole, id)

        res = ai.ave_ndvi(hsiRoi, 0.31)
        logger.info(f"average : {res[0]} pixcel ratio : {res[1]}")
        if res[0] > 0.6 and res[1] > 0.7: 
            worker = ai.AiWorker(hsiRoi, item)
            worker.signal.inferenceFinished.connect(self.onInferenceFinished)
            self.threadpool.start(worker)
        else:
            self.onInferenceFinished({'Not Plant' : 1}, item)

    def onInferenceFinished(self, resDict, item: QtWidgets.QListWidgetItem): 
        logger.info(f'Inference result : {resDict}')
        id = item.data(QtCore.Qt.UserRole) 
        row = self.roiListView.itemWidget(item)
        row.setId(id)
        maxKey = max(resDict, key=resDict.get)
        row.setTitle(f" {maxKey} ({resDict[maxKey]:.3f})")

    def addRoiSingleRectItem(self, rectItem, rectImage): 
        item = QtWidgets.QListWidgetItem(self.roiListView)
        self.roiListView.addItem(item)
        row = RoiListSingleRectItemWidget('id', 'Inferencing...',self.roiListView, rectImage)
        item.setSizeHint(row.minimumSizeHint())
        self.roiListView.setItemWidget(item, row)
        return item

    def onSingleRectRemoved(self, item):
        pass 

    def onDragMode(self): 
        self.hsiView.setImageDragMode(True) 
        self.singleRectanglePointerAction.setChecked(False)

    def onSingleRectangleMode(self): 
        if self.hsiView._mode == self.hsiView.MODE_SINGLE_RECT:         
            self.hsiView.setSingleRectangleMode(False)
        else:
            self.hsiView.setSingleRectangleMode(True)

    def closeHSI(self): 
        closingFileName = self.openedFileDict['raw'].name
        logger.info(f"closing {closingFileName}")

        self.hsiView.setImage(None)
        
        self.openedFileDict.clear()
        self.roiListView.clear() 

        self.singleRectanglePointerAction.setDisabled(True)
        self.singleRectanglePointerAction.setChecked(False)
        self.normalPointerAction.setDisabled(True)
        #self.singleRectanglePointerAction.
        #QtGui.QAction().setChecked



    def closeEvent(self, event):
        logger.info(f"Exiting {self.appName} Goodbye.")
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        self.settings.setValue("window/state", self.saveState())
