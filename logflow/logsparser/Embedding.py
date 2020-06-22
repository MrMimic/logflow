# Copyright 2020 BULL SAS All rights reserved #
import word2vec # type: ignore
import os
import h5py # type: ignore
from loguru import logger
import tempfile
from multiprocessing import Pool
from collections import Counter
import pickle
from tqdm import tqdm # type: ignore
import time
import numpy as np # type: ignore
from itertools import repeat
from typing import List, Tuple

class Embedding:
    """Compute the embedding of each pattern based on the word2vec method. Here, each line is represented by the ID (integer) of its pattern.

    Note that the word2vec is based on the C++ google implementation. Then, we need to use a file and we cannot use directly the list_classes for the learning step. For best performance, we use
    temporary file to write the list_classes as a file and then remove it.

        Args:
            list_classes (list, optional): list of patterns. Defaults to [].
            loading (bool, optional): load the list of patterns from a file. Note that you must provide list_classes is loading is False. Defaults to False.
            name_dataset (str, optional): name of the dataset. Use for loading it. Defaults to "".
            path_data (str, optional): path to the dataset. Defaults to "".
            path_model (str, optional): path to the model. Defaults to "".
            dir_tmp (str, optional): path used for the temporary file. This path can be on SSD or RAM to better performance. Defaults to "/tmp/".
        """
    def __init__(self, list_classes=[], loading=False, name_dataset="", path_data="", path_model="", dir_tmp=""):
        self.loading = loading
        self.name_dataset = name_dataset
        self.path_data = path_data
        self.path_model = path_model
        self.dir_tmp = dir_tmp
        assert self.path_model != ""
        self.giant_str = ""
        self.list_classes = list_classes
        self.path_h5py = self.path_data + self.name_dataset + ".lf"

    def load(self):
        """Loads the files
        """
        logger.info("Loading file for embeddings: " + self.path_h5py)

        with h5py.File(self.path_h5py, 'r') as file_h5py:
            self.list_classes = file_h5py['list_patterns'][()]
        logger.info("Number of exemples for embeddings: " + str(len(self.list_classes)))

    def start(self):
        """Starts the process
        """
        self.create_temporary_file()
        if self.loading:
            self.load()
        else:
            assert self.list_classes != []
        self.train()
        self.new_list_classes = []
        self.generate_list_embeddings()

    def create_temporary_file(self):
        """Create the temporary files for the learning step
        """
        # For writting the list_classes as a file.
        if self.dir_tmp != "":
            self.fp = tempfile.NamedTemporaryFile(mode="w", dir=self.dir_tmp)
            self.fp_model = tempfile.NamedTemporaryFile(mode="w", dir=self.dir_tmp)
        else:
            self.fp = tempfile.NamedTemporaryFile(mode="w")
            self.fp_model = tempfile.NamedTemporaryFile(mode="w")
        logger.info("Temporary files are created: " + str(self.fp_model.name) + " , " + str(self.fp.name))

    def train(self):
        """Trains the word2vec model based on the list of patterns.
        """
        # Merge the list_classes (list of int) into a string for the writting.
        nb_files_per_chunck = int(len(self.list_classes) / (os.cpu_count() * 8))
        if nb_files_per_chunck < 1:
            nb_files_per_chunck = 2
        self.list_chunck = [self.list_classes[i:i + nb_files_per_chunck] for i in range(0, len(self.list_classes), nb_files_per_chunck)]
        list_str_tmp = []
        with Pool(os.cpu_count()) as mp:
            for res in tqdm(mp.imap(Embedding.list_to_str, self.list_chunck), total=len(self.list_chunck)):
                list_str_tmp.append(res)
        self.giant_str = ' '.join(e for e in list_str_tmp)
        with open(self.fp.name, 'w') as f:
            f.write(self.giant_str)
        # Start the learning
        logger.info("Starting training w2v: " + str(os.cpu_count()) + " threads")
        word2vec.word2vec(self.fp.name, self.fp_model.name, size=20,  verbose=True, threads=os.cpu_count(), binary=True)
        with open(self.path_model + self.name_dataset + "_model.lf", "rb") as input_file:
            dict_local = pickle.load(input_file)
        # Save the model
        dict_local["word2vec"] = word2vec.load(self.fp_model.name, kind="bin")
        with open(self.path_model + self.name_dataset + "_model.lf", "wb") as output_file:
            pickle.dump(dict_local, output_file)
        self.fp.close()
        self.fp_model.close()

    def generate_list_embeddings(self):
        """Filter the list of patterns according to the learned embeddings. The word2vec model requires at least a minimum of examples per word to be learned. We remove the words excluded of the word2vec learning.
        """
        with open(self.path_model + self.name_dataset + "_model.lf", "rb") as file_model:
            dict_model = pickle.load(file_model)
        self.w2v = dict_model["word2vec"]
        self.dict_issue = {}
        try:
            self.list_chunck
        except:
            nb_files_per_chunck = int(len(self.list_classes) / (os.cpu_count() * 2))
            if nb_files_per_chunck < 1:
                nb_files_per_chunck = 2
            self.list_chunck = [self.list_classes[i:i + nb_files_per_chunck] for i in range(0, len(self.list_classes), nb_files_per_chunck)]
        self.list_vocab = []
        # Build the list of vocab. If the word is not an integer, then it's not a valid ID. Remove it.
        for word in self.w2v.vocab:
            try:
                int(word)
                self.list_vocab.append(int(word))
            except:
                pass
        new_list_classes = []
        # Keep only the learned words during the word2vec learning step.
        with Pool(os.cpu_count()) as mp:
            for res in tqdm(mp.imap(Embedding.clear_list, zip(self.list_chunck, repeat(self.list_vocab))), total=len(self.list_chunck)):
                new_list_classes += res.tolist()
        logger.info(str(len(self.list_classes) - len(new_list_classes)) +  " elements are removed due to not enought examples")
        self.list_classes = new_list_classes
        f = h5py.File(self.path_data + self.name_dataset + "_embedding.lf", "w")
        f.create_dataset('list_classes', data=self.list_classes)
        f.close()

    @staticmethod
    def list_to_str(list_str : List[str]) -> str:
        """Merge a list of integer into a string.

        Args:
            list_str (list): list of integer

        Returns:
            str: string representation
        """
        return ' '.join(str(e) for e in list_str)

    @staticmethod
    def clear_list(args: Tuple[List[int], List[int]]) -> list:
        """Keep only the words from the list of vocab in the list of patterns.

        Args:
            args ((list, list)): The first argument is the list of patterns. The second is the list of vocab.

        Returns:
            list: list of patterns with only the words into the list of vocab. 
        """
        list_int, list_vocab = args
        return np.delete(list_int, np.where(np.isin(list_int, list_vocab, invert=True))[0])

