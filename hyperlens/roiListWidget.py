from PySide6 import QtWidgets, QtGui, QtCore
import util 

class RoiListSingleRectItemWidget(QtWidgets.QWidget): 
    def __init__(self, id, title, parent=None, rectImage=None):
        super(RoiListSingleRectItemWidget, self).__init__(parent)

        self.row = QtWidgets.QGridLayout()

        self.setLayout(self.row)

        self.rectItem : QtWidgets.QGraphicsRectItem = None
        self.rectImage = rectImage
        self.imageQLabel = QtWidgets.QLabel() 
        self.id = id
        self.idQLabel = QtWidgets.QLabel(f'{id}')
        self.titleLabel = QtWidgets.QLabel(title)
        #self.detailButton = QtWidgets.QPushButton("Detail")
        self.deleteButton = QtWidgets.QPushButton("Delete")

        self.row.addWidget(self.idQLabel, 0, 0, 2, 1)
        self.row.addWidget(self.imageQLabel, 0, 1, 2, 1)
        self.row.addWidget(self.titleLabel, 0, 2, 1, 2)
        #self.row.addWidget(self.detailButton, 1, 2, 1, 1)
        self.row.addWidget(self.deleteButton, 1, 3, 1, 1)

        self.row.setRowStretch(0, 3)
        #self.row.setRowStretch(1, 2)

        self.row.setSpacing(8)

        if self.rectImage is not None: 
            qImage = util.image.convertCvImage2qImage(rectImage)
            pixmap = QtGui.QPixmap(qImage)
            pixmapHeight = int(self.height() * 1.1)
            pixmap = pixmap.scaled(pixmapHeight, pixmapHeight,
                                   QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation) 
            self.imageQLabel.setPixmap(pixmap)

        
    def setTitle(self, title): 
        self.titleLabel.setText(title)

    def setId(self, id): 
        self.idQLabel.setText(id)


class RoiListWidget(QtWidgets.QListWidget): 
    pass