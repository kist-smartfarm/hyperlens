from PySide6 import QtGui
import numpy as np 

def convertCvImage2qImage(rgbImage):
    height, width, channel = rgbImage.shape
    rgbImage = np.ascontiguousarray(rgbImage)
    qImage = QtGui.QImage(rgbImage.data, width, height, width * channel,
                            QtGui.QImage.Format_RGB888)
    return qImage
