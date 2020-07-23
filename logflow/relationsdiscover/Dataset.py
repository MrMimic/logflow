# Copyright 2020 BULL SAS All rights reserved #
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import word2vec # type: ignore
import h5py # type: ignore
from collections import Counter
from loguru import logger
import os
import time
from multiprocessing import Pool
from tqdm import tqdm # type: ignore
from logflow.relationsdiscover.Cardinality import Cardinality
import pickle 
from typing import List

class Dataset:
    """Load the files and create the cardinalities

    Args:
        path_model (str, optional): path to the word2vec model. Defaults to "".
        path_data (str, optional): path to the data (list of patterns). Defaults to "".
        name_dataset (str, optional): name of the dataset to load. Defaults to "".
        size (int, optional): number of examples to load. Defaults to -1.
        one_model (bool, optional): use one global model instead of one model per cardinality.
    Raises:
        Exception: model file is not found
        Exception: data file is not found
    """

    def __init__(self, path_model="", path_data="", name_dataset="", size=-1, one_model=False):
        assert path_model != ""
        assert path_data != ""
        assert name_dataset != ""
        self.path_model = path_model
        self.path_data = path_data
        self.name_dataset = name_dataset
        self.path_model_w2v = self.path_model + self.name_dataset +"_model.lf"
        self.path_list_classes = self.path_data + self.name_dataset + "_embedding.lf"
        self.size = size
        self.one_model = one_model
        if not os.path.isfile(self.path_model_w2v):
            raise Exception(self.path_model_w2v + " is not a file")
        if not os.path.isfile(self.path_list_classes):
            raise Exception(self.path_list_classes + " is not a file")
        self.list_cardinalities = []

    def loading_files(self):
        """Load the data, the word2vec and the counter file.
        """
        logger.info("Loading word2vec model: " + self.path_model_w2v)
        with open(self.path_model_w2v, "rb") as file_model:
            dict_local = pickle.load(file_model)
        self.w2v = dict_local["word2vec"]
        self.counter = dict_local["counter_patterns"]
        logger.info("Loading list of classes: " + self.path_list_classes)
        with h5py.File(self.path_list_classes, 'r') as file_h5py:
            if self.size != -1:
                self.list_classes = file_h5py['list_classes'][:self.size]
            else:
                self.list_classes = file_h5py['list_classes'][()]
            
    def creating_cardinalities(self, min_cardinality=0, max_cardinality=float("+inf")):
        """Create the cardinality object for the learning step.

        Args:
            min_cardinality (int, optional): minimum value of cardinality to be selected. Defaults to 0.
            max_cardinality (float, optional): maximum value of cardinality to be selected. Defaults to float("+inf").
        """
        if self.one_model:
            list_cardinalities_available = []
            for event in self.counter:
                cardinality = len(str(self.counter[event]))
                min_cardinality = 3
                max_cardinality = 8
                if cardinality > min_cardinality and cardinality < max_cardinality:
                    list_cardinalities_available.append(cardinality)
            self.set_cardinalities_available = set(list_cardinalities_available)
            logger.info(str(len(self.set_cardinalities_available)) + " cardinalities available in this dataset")
            self.list_cardinalities.append(Cardinality(cardinality=0, path_w2v=self.path_model_w2v, path_list_classes=self.path_list_classes, size=self.size, one_model=self.one_model, set_cardinalities=self.set_cardinalities_available))
        else:
            list_cardinalities_available = []
            for event in self.counter:
                list_cardinalities_available.append(len(str(self.counter[event])))
            self.set_cardinalities_available = set(list_cardinalities_available)
            logger.info(str(len(self.set_cardinalities_available)) + " cardinalities available in this dataset")
            for cardinality in self.set_cardinalities_available:
                if cardinality > min_cardinality and cardinality < max_cardinality:
                    self.list_cardinalities.append(Cardinality(cardinality=cardinality, path_w2v=self.path_model_w2v, path_list_classes=self.path_list_classes, size=self.size))
        
    def run(self) -> List[Cardinality]:
        """Start the workflow for the multithreading implementation

        Returns:
            List[Cardinality]: list of the cardinalities created
        """
        self.loading_files()
        self.creating_cardinalities()
        return self.list_cardinalities
