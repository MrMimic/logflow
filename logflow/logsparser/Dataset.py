# Copyright 2020 BULL SAS All rights reserved #
from loguru import logger
from multiprocessing import Pool
from logflow.logsparser.Journal import Journal
from tqdm import tqdm # type: ignore
from collections import Counter
import random
import string
import h5py # type: ignore
import word2vec # type: ignore
import pickle
from typing import List, Dict

class Dataset:
    """A dataset is an object containing the data. It uses the Journal class for the reading, the parsing of the logs. It is used for the saving of logs, patterns and parsed files
    
     Args:
            list_files (list): List of the logs file to read. Each element of the list is a path to a file.
            dict_patterns (dict, optional): Patterns previously detected by the first step. If default, the dict is created and the dataset computes the patterns. If provided, the dataset uses the patterns to associate each line of the file to a pattern.. Defaults to {}.
            path_data (str, optional): Path to the data. Defaults to "".
            saving (bool, optional): Saving the patterns to generate the embeddings. Defaults to False.
            name_dataset (str, optional): Name of the patterns to save. Defaults to "".
            path_model (str, optional): Path of the folder to save the patterns. Defaults to "".
            concat (bool, optional): Process a chunck of files per thread instead of one file per thread. Increase the performance due to the poor multiprocessing performance of Python. Defaults to True.
            parser_function (function, optional): Function to split the log entry and get the message part. Defaults to "", means split according to space and uses the words after the 9th position.
    
    """
    def __init__(self, list_files : list, dict_patterns={}, path_data="", saving=False, name_dataset="", path_model="", concat=True, parser_function=""):
        assert list_files != []
        self.list_journal : List[str] = []
        self.list_files = list_files
        self.counter_general_per_cardinality : Dict[int, Dict[set, int]] = {}
        self.dict_patterns = dict_patterns
        self.path_data = path_data
        self.path_model = path_model
        self.saving = saving
        self.concat = concat
        if name_dataset == "":
            self.name_dataset = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
        else:
            self.name_dataset = name_dataset
        if parser_function == "":
            self.parser_function = Dataset.parser_message
        else:
            self.parser_function = parser_function
        if len(self.dict_patterns) > 0:
            self.list_patterns : List[str] = []
            self.read_files_associating()
        else:
            self.read_files_parsing(concat=self.concat)


    def read_files_parsing(self, multithreading=True, concat=True, nb_files_per_chunck=50):
        """Read the files and compute the patterns.

        If a first step, the function merges the list of files into a list of chunck. Each chunck contains nb_files_per_chunck files. It is done to
        increase the performance due to pickle/unpickle poor performance between process using Python.

        This function executes the run() method of the Journal class for each chunck of files.
        
        Note that we only provide a multithreading implementation for the moment.

        Args:
            multithreading (bool, optional): Use the multithreading implementation. Defaults to True.
            concat (bool, optional): Use a chunck of files per thread instead of one file per thread. Defaults to True.
            nb_files_per_chunck (int, optional): Number of files per chunck. Defaults to 50.
        """
        if multithreading:
            logger.info("Multithreading is activated, using all CPUs available")
            if concat:
                self.list_files = [self.list_files[i:i + nb_files_per_chunck] for i in range(0, len(self.list_files), nb_files_per_chunck)]
                logger.info("Starting " +str(len(self.list_files))+ " chunks")
            else:
                self.list_files = [self.list_files]
            self.list_journal = [Journal(path=path, parser_message=self.parser_function) for path in self.list_files]
            nb_logs = 0
            nb_counter = 0
            with Pool() as mp:
                for journal in tqdm(mp.imap_unordered(Dataset.execute, self.list_journal), total=len(self.list_journal)):
                    for entry in journal.counter_logs:
                        # A cardinality describes the number of words in a line of log.
                        self.counter_general_per_cardinality.setdefault(len(entry), {})
                        # We keep only one entry per line of descriptors
                        self.counter_general_per_cardinality[len(entry)].setdefault(entry, 0)
                        # We add the number of this line of descriptors to count the words.
                        self.counter_general_per_cardinality[len(entry)][entry] += journal.counter_logs[entry]
                        nb_logs += journal.counter_logs[entry]
            for value in self.counter_general_per_cardinality:
                nb_counter += len(self.counter_general_per_cardinality[value])
            logger.debug("Parser " + str(nb_logs) + " logs with " + str(nb_counter) + " counter and " + str(len(self.counter_general_per_cardinality)) + " cardinalities")

    def read_files_associating(self, multithreading=True, concat=True, nb_files_per_chunck=50):
        """Read the files and associate one pattern to each line of the files.

        If a first step, the function merges the list of files into a list of chunck. Each chunck contains nb_files_per_chunck files. It is done to
        increase the performance due to pickle/unpickle poor performance between process using Python.

        This function executes the run() method of the Journal class for each chunck of files.
        
        Note that we only provide a multithreading implementation for the moment.

        Args:
            multithreading (bool, optional): [Use the multithreading implementation]. Defaults to True.
            concat (bool, optional): [Use a chunck of files per thread instead of one file per thread]. Defaults to True.
            nb_files_per_chunck (int, optional): [Number of files per chunck]. Defaults to 50.
        """
        if multithreading:
            logger.info("Multithreading is activated, using all CPUs available")
            if concat:
                self.list_files = [self.list_files[i:i + nb_files_per_chunck] for i in range(0, len(self.list_files), nb_files_per_chunck)]
                logger.info("Starting " +str(len(self.list_files))+ " chunks")
            self.list_journal = [Journal(path=path, parser_message=self.parser_function, associated_pattern=True, dict_patterns=self.dict_patterns) for path in self.list_files]
            with Pool() as mp:
                for journal in tqdm(mp.imap_unordered(Dataset.execute, self.list_journal), total=len(self.list_journal)):
                    self.list_patterns += journal.list_patterns
        if self.saving:
            assert self.path_data != ""
            # h5py is more optimized than classical pickle
            f = h5py.File(self.path_data + self.name_dataset + ".lf", "w")
            f.create_dataset('list_patterns', data=self.list_patterns)
            f.close()
            # pickle is a better classical way
            with open(self.path_model + self.name_dataset + "_model.lf", "wb") as output_file:
                dict_model = {}
                dict_model["dict_patterns"] = self.dict_patterns
                dict_model["counter_patterns"] = Counter(self.list_patterns)
                pickle.dump(dict_model, output_file)

    @staticmethod
    def parser_message(line : str) -> List[str]:
        """Split the line of log and return the message part

        Args:
            line (str): the line of log

        Returns:
            list: the message part of the line represented as a list of words.
        """
        message_split = line.strip().split()
        return message_split[9:]

    @staticmethod
    def execute(journal : Journal) -> Journal:
        """Execute the run() function of the Journal class. It uses for the multithreading implementation.

        Args:
            journal (Journal): A journal to process

        Returns:
            Journal: A processed journal
        """
        journal.run()
        return journal
