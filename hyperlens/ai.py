import os
import numpy as np
from tensorflow import keras
from keras.models import model_from_json
import pathlib 
from PySide6 import QtCore, QtWidgets
from loguru import logger

json_dir=pathlib.Path("_test/model.json_2")
h5_dir=pathlib.Path("_test/model_CNN_2.h5")

class_names=['Fruit_infected',
 'Fruit_asymtomatic',
 'Fruit_healthy',
 'Leaf_asymtomatic',
 'Leaf_healthy',
 'Leaf_infected']

def model_load(json_dir,h5_dir):
    with open(json_dir, "r") as json_file:
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = keras.models.model_from_json(loaded_model_json)
        loaded_model.load_weights(h5_dir)
    return loaded_model

def cnnInference(cube):
    if cube.shape[2]==161:
        cube=cube[:,:,5:-6]
    model=model_load(json_dir,h5_dir)
    X = cube.reshape(1, cube.shape[0]*cube.shape[1],cube.shape[2],1)
    res = model.predict(X)
    resDict = {} 
    for i, name in enumerate(class_names): 
        resDict[name] = res[0][i]
    return resDict

class aiWorkerSignals(QtCore.QObject):
    inferenceFinished = QtCore.Signal(dict, QtWidgets.QListWidgetItem) 

class AiWorker(QtCore.QRunnable):
    def __init__(self, cube, item) -> None:
        self.cube = cube
        self.qlistViewitem = item
        self.signal = aiWorkerSignals()
        super().__init__() 

    def run(self) -> None:
        timer = QtCore.QElapsedTimer()
        timer.start()
        resDict = cnnInference(self.cube)
        logger.info(f"Elapsed time : {timer.elapsed()}(ms) for inference")
        self.signal.inferenceFinished.emit(resDict, self.qlistViewitem)


def get_ndvi2(a):

    ndvi=(a[89]-a[60])/(a[89]+a[60])

    return ndvi

# a = cube thr = 0.31 
def ave_ndvi(a,thr):
    ndvi_arr=np.zeros(len(a[:][0])*len(a[0][:]))
    aa=a.reshape((len(a[:][0])*len(a[0][:]),a.shape[2]))
    thr_count=0
    
    for i in range((len(a[:][0])*len(a[0][:]))):
        ndvi_arr[i]=get_ndvi2(aa[i])
        if ndvi_arr[i] > thr:
            thr_count=thr_count+1
        
    #hr_ratio=thr_count/(len(a[:][0])*len(a[0][:])
    ave=np.mean(ndvi_arr)
    #print("average ndvi value of ROI is", ave)
    #print("ratio of pixels recognized as plants by NDVI is", thr_count/(len(a[:][0])*len(a[0][:])) )
    return ave, thr_count/(len(a[:][0])*len(a[0][:]))
