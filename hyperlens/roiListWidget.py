from PySide6 import QtWidgets, QtGui, QtCore
import util 

class RoiListSingleRectItem(QtWidgets.QWidget): 
    def __init__(self, name, parent=None, rectImage=None):
        super(RoiListSingleRectItem, self).__init__(parent)

        self.row = QtWidgets.QGridLayout()

        self.setLayout(self.row)

        self.rectItem : QtWidgets.QGraphicsRectItem = None
        self.rectImage = rectImage
        imageQLabel = QtWidgets.QLabel() 
    
        self.row.addWidget(imageQLabel, 0, 0, 2, 0)
        self.row.addWidget(QtWidgets.QLabel(name), 0, 1)
        self.row.addWidget(QtWidgets.QPushButton("Detail"), 1, 1)
        self.row.addWidget(QtWidgets.QPushButton("Delete"), 1, 2)

        self.row.setRowStretch(0, 2)
        self.row.setSpacing(8)
        if self.rectImage is not None: 
            qImage = util.image.convertCvImage2qImage(rectImage)
            pixmap = QtGui.QPixmap(qImage)
            pixmapHeight = int(self.height() * 1.1)
            pixmap = pixmap.scaled(pixmapHeight, pixmapHeight,
                                   QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation) 
            imageQLabel.setPixmap(pixmap)

class RoiListWidget(QtWidgets.QListWidget): 
    pass