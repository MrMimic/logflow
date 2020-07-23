# Copyright 2020 BULL SAS All rights reserved #
from collections import Counter
from torch.utils.data import Dataset
import word2vec  # type: ignore
import h5py  # type: ignore
from loguru import logger
import time
import pickle
import numpy as np # type: ignore
DTYPE = np.float32
from typing import Dict, List, Any



class Cardinality(Dataset):
    """ A cardinality describes the number of examples per pattern. Each cardinality contains a 10 power examples. For example, the cardinality 7 contains all the patterns with 10^7 examples. It extendes
    the dataloader class of pytorch to be able the provide the data to the pytorch deep learning model.

    Args:
        cardinality (int): the value of the cardinality
        path_list_classes (str): path to the data. The data is the list of patterns to learn.
        path_w2v ([type]): path to the word2vec model. The word2vec model is used to turn a pattern into a vector. 
        size (int, optional): number of examples to use. Defaults to -1.
        one_model (bool, optional): use one global model instead of one model per cardinality.
        set_cardinalities (set, optional): use several cardinalities for the learning step of one model. Must be used with one_model.
    """

    def __init__(self, cardinality : int, path_list_classes : str, path_w2v, size=-1, one_model=False, set_cardinalities=()):
        self.cardinality = cardinality
        self.path_list_classes = path_list_classes
        self.size = size
        self.path_model_w2v = path_w2v
        self.number_of_classes = 0
        self.set_classes_kept = ()
        self.loaded = False
        self.size_windows = 30
        self.one_model = one_model
        self.set_cardinalities = set_cardinalities

    def compute_position(self):
        """Compute the position of each example in the initial list of patterns. Indeed, one cardinality learns only to predict the patterns with a specific cardinality. We store the index
        of each pattern with the right cardinality on the initial data to be able to provide it to the model during the learning step.
        """
        np_list_classes = np.asarray(self.list_classes)
        set_classes = np.unique(np_list_classes)
        list_classes_kept = []
        if self.one_model:
            for event in set_classes:
                cardinality = len(str(self.counter[event]))
                if cardinality in self.set_cardinalities:
                    list_classes_kept.append(event)
        else:
            for event in set_classes:
                cardinality = len(str(self.counter[event]))
                if cardinality == self.cardinality:
                    list_classes_kept.append(event)
        self.set_classes_kept = np.unique(list_classes_kept)
        ix = np.isin(np_list_classes, self.set_classes_kept)
        self.list_position = np.where(ix)[0]
        try:
            self.number_of_classes = max(self.set_classes_kept) + 1
        except:
            self.number_of_classes = 0
        self.loaded = True

    def load_files(self):
        """Load the data and the word2vec model.
        """
        logger.info("Loading file for cardinality: " + str(self.cardinality) + " " + str(self.path_list_classes))
        with h5py.File(self.path_list_classes, 'r') as file_h5py:
            if self.size != -1:
                self.list_classes = file_h5py['list_classes'][:self.size]
            else:
                self.list_classes = file_h5py['list_classes'][()]
        self.list_position = []
        with open(self.path_model_w2v, "rb") as file_model:
            dict_local = pickle.load(file_model)
        self.w2v = dict_local["word2vec"]
        self.counter = dict_local["counter_patterns"]

    def __len__(self) -> int:
        """Return the length of the data (the number of examples)

        Returns:
            int: length of the data.
        """
        return len(self.list_position)

    def __getitem__(self, idx : int) -> Dict[str, Any]:
        """Implement the get_item method used by the dataloader. For each pattern, we select the 30 previous patterns to learn to predict it. 30 is the size of the window.
        For each pattern in the window, the w2v method is then used to get the corresponding vector. Note that the previous selected pattern must be different from the pattern to predict.

        For example, with a window of 5. 
        
        Initial data : [10, 4, 5, 3, 10, 9, 5, 3, 5]. 

        The last pattern is the pattern to predict (5 here.)

        The window selected to predict this pattern is [4, 3, 10, 9, 3]. The logs corresponding to the pattern "5" are removed because we want to predict this pattern.

        Returns:
            dict: the pattern to predict and its vector
        """
        index_real = self.list_position[idx]
        list_embedding = np.zeros((self.size_windows, 20), dtype=DTYPE)
        index_add = 0
        output = self.list_classes[index_real]
        index = index_real - 1 
        while index_add != self.size_windows:
            # If we don't have
            if index < 0 and np.count_nonzero(list_embedding) == 0:
                return {'output':-1, 'input':[-1]}
            if index < 0:
                for i in range(self.size_windows - index_add):
                    list_embedding[index_add] = list_embedding[-1]
                    index_add += 1
                break
            # If pattern is different from the output.
            if self.list_classes[index] != output:
                list_embedding[index_add] = self.w2v[str(self.list_classes[index])]
                index_add += 1
            index -= 1
        return {'output':output, 'input':list_embedding}
