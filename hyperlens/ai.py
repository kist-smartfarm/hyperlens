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