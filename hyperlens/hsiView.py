from PySide6 import QtCore, QtGui, QtWidgets

from loguru import logger 

class hsiScene(QtWidgets.QGraphicsScene): 
    singalMousePressed = QtCore.Signal(QtCore.QPointF)
    mode = None
    def __init__(self, parent): 
        super(hsiScene, self).__init__(parent) 

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        return super().mousePressEvent(event)

class hsiView(QtWidgets.QGraphicsView): 
    MODE_EMPTY = 0
    MODE_DRAG = 1
    MODE_SINGLE_RECT = 2

    SingleRectCreated = QtCore.Signal(QtWidgets.QGraphicsRectItem) 
    SingleRectRemoved = QtCore.Signal(QtWidgets.QGraphicsRectItem) 

    def __init__(self, parent): 
        super(hsiView, self).__init__(parent)
        self._zoom = 0
        self._scene = hsiScene(self)
        self._image = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._image)
        self._mode = self.MODE_EMPTY
        self.drawingItems = []
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame) 

    def hasImage(self):
        return self._mode != self.MODE_EMPTY

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._image.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasImage():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setImage(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._mode = self.MODE_DRAG
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._image.setPixmap(pixmap)
        else:
            self._mode = self.MODE_EMPTY
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._image.setPixmap(QtGui.QPixmap())
            for item in self.drawingItems: 
                self._scene.removeItem(item)
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasImage():
            if event.angleDelta().y() > 0:
                factor = 1.2
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        return super().mouseMoveEvent(event)
        
    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        self.addSingleRect(event)     
        return super().mousePressEvent(event) 

    def removeSingleRect(self, item : QtWidgets.QGraphicsRectItem): 
        if self.hasImage(): 
            self._scene.removeItem(item)
            self.SingleRectRemoved.emit(item)

    def addSingleRect(self, event):
        pos = self.mapToScene(event.pos())
        rectangle_length = 16
        rect = QtCore.QRect(pos.x() - rectangle_length / 2, 
                                               pos.y() - rectangle_length / 2, 
                                               rectangle_length, rectangle_length)
        if self._mode == self.MODE_SINGLE_RECT and self.hasImage() \
           and self.sceneRect().contains(rect):
            rectItem = self._scene.addRect(rect)
            rectItem.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
            rectItem.show() 
            self.SingleRectCreated.emit(rectItem)
            self.drawingItems.append(rectItem)
            logger.info(f"rectangle added on {pos}")

    def setImageDragMode(self, dragMode):
        if not self._image.pixmap().isNull():
            logger.info("Setting to Drag Mode")
            self._mode = self.MODE_DRAG
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        elif not dragMode:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def setSingleRectangleMode(self, srMode):
        if not srMode: 
            self._mode = self.MODE_DRAG
        elif not self._image.pixmap().isNull():
            logger.info("Setting to Single Rectangle Mode")
            self._mode = self.MODE_SINGLE_RECT