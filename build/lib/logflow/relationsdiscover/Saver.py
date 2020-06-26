# Copyright 2020 BULL SAS All rights reserved #
from logflow.relationsdiscover.Model import LSTMLayer
from logflow.relationsdiscover.Result import Result
import pickle
import os
from loguru import logger
from time import sleep
import random
import numpy as np # type: ignore

class Saver:
    """Save and load the model from a file.

    The file is saved as follow :
    file["LSTM"][cardinality] = model

    Args:
        name_model (str): name of the dataset
        path_model (str): path of the model to save
        cardinality (int, optional): cardinality to save. Defaults to -1.
        lock (int, optional): lock for the file. Defaults to -1.
    """
    def __init__(self, name_model :str, path_model : str, cardinality=-1, lock=-1):
        self.path = path_model + name_model + "_model.lf"
        self.cardinality = cardinality
        self.lock = lock

    def save(self, model : LSTMLayer, result : Result, condition="Test"):
        """Save the model

        Args:
            model (LSTMLayer): model to save
            result (Result): result to save
            condition (str): Test or train results to save
        """
        dict_cardinalities_model = {}
        self.lock.acquire()
        if os.path.isfile(self.path):
            with open(self.path, "rb") as output_file:
                logger.info("["+str(self.cardinality)+"] Loading: " + self.path)
                dict_cardinalities_model = pickle.load(output_file)
        try:
            dict_cardinalities_model["LSTM"][self.cardinality] = model.state_dict()
        except:
            dict_cardinalities_model["LSTM"] = {}
            dict_cardinalities_model["LSTM"][self.cardinality] = model.state_dict()
        # Keep only the latest version of the results
        try:
            dict_cardinalities_model["Result"]
        except:
            dict_cardinalities_model["Result"] = {}
        try:
            dict_cardinalities_model["Result"][self.cardinality]
        except:
            dict_cardinalities_model["Result"][self.cardinality] = {}
        if condition != "temp":
            dict_cardinalities_model["Result"][self.cardinality][condition] = result
        with open(self.path, "wb") as output_file:
            pickle.dump(dict_cardinalities_model, output_file)
        logger.info("["+str(self.cardinality)+"] Saving: " + self.path)
        self.lock.release()

    def load(self, model : LSTMLayer) -> LSTMLayer:
        """Load the model. Note that the model must be created before. This function loads only the parameters inside the model.
        
        Args:
            model (LSTMLayer): object to use for loading the model.

        Raises:
            Exception: the file is not found

        Returns:
            LSTMLayer: the loaded model
        """
        if os.path.isfile(self.path):
            self.lock.acquire()
            with open(self.path, "rb") as output_file:
                dict_cardinalities_model = pickle.load(output_file)
            model.load_state_dict(dict_cardinalities_model["LSTM"][self.cardinality])
            self.lock.release()
            return model
        else:
            logger.critical("Trying to load an unknown file: " + str(self.path))
            raise Exception("Trying to load an unknown file")