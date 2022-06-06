import spectral
import pathlib 
import cv2
import numpy as np 

band = [42, 28, 6]

def loadImage(path):
    imagePath = pathlib.Path(path) 
    hsiImage = spectral.io.envi.open(imagePath.with_suffix('.hdr'),
                          imagePath.with_suffix('.raw'))
    rgbImage = spectral.get_rgb(hsiImage, band)
    rgbImage = (255*rgbImage).astype(np.uint8)
    rgbImage = cv2.cvtColor(rgbImage, cv2.COLOR_BGR2RGB)
    return (hsiImage, rgbImage)
