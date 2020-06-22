# Copyright 2020 BULL SAS All rights reserved #
from logflow.treebuilding.Log import Log
from logflow.treebuilding.Parser import Parser
from logflow import logsparser
import sys
sys.modules['logsparser'] = logsparser
from loguru import logger
import pickle
import numpy as np # type: ignore

cardinality_max = 8

class Dataset:
    """A dataset is an object containing the data. It is used to load the files and to compute the window for each new prediction on a log.

    Args:
        path_model (str, optional): path to the model to load. Defaults to "".
        name_model (str, optional): name of the model to load. Defaults to "".
        index_line_max (int, optional): load only the lines with a lower index in the file. Avoid to load all the lines. Defaults to float("+inf").
        path_data (str, optional): path to the logs. Defaults to "".
        window_size (int, optional) : size of the window. Defaults to 30.
        parser_function (function, optional): Function to split the log entry and get the message part. Defaults to "", means split according to space and uses the words after the 9th position.
    """

    def __init__(self, path_model="", name_model="", index_line_max=float("+inf"), path_data="", window_size=30, parser_function=""):
        self.list_logs = []
        assert path_model != ""
        assert path_data != ""
        assert name_model != ""
        self.path_model = path_model
        self.name_model = name_model + "_model.lf"
        self.path_data = path_data
        self.index_line_max = index_line_max
        self.window_size = window_size
        self.parser_function = parser_function
        # self.load_files()
        # self.load_logs(index_line_max=index_line_max)

    def load_files(self):
        """Load the files including word2vec, LSTM, counter and patterns.
        """
        logger.info("Loading models file: " + self.path_model + self.name_model)
        with open(self.path_model + self.name_model, "rb") as output_file:
            dict_model = pickle.load(output_file)
        self.w2v = dict_model["word2vec"]
        self.counter_patterns = dict_model["counter_patterns"]
        self.dict_patterns = dict_model["dict_patterns"]
        self.LSTM = dict_model["LSTM"]
        self.parser = Parser(dict_patterns=self.dict_patterns, w2v=self.w2v, counter_patterns=self.counter_patterns)

    def load_logs(self):
        """Load the selected logs file up to the index_line_max.
        """
        index_line = 0
        with open(self.path_data, "r", encoding="latin-1") as file_logs:
            for line in file_logs:
                self.list_logs.append(Log(line=line, index_line=index_line, parser_function=self.parser_function))
                if index_line >=  self.index_line_max:
                    break
                index_line += 1
        
    def get_slice(self, index_line=-1):
        """Get the window associated with the line at the index_line.

        Args:
            index_line (int, optional): index of the line. Defaults to -1.

        Returns:
            Log: return the log object with the slice added. If an error occurs, return -1.
        """
        first_log = self.list_logs[index_line]
        # Just to be sure
        assert first_log.index_line == index_line
        index_inverted = index_line - 1 
        list_inputs = []
        list_index_inputs = []
        list_logs_selected = []
        # Get the pattern of the log
        self.parser.get_pattern(first_log)
        # Issue with the pattern
        if first_log.pattern.id == -1 :
            logger.error(str("Log: " + str(first_log.message) + " is not usable due to pattern"))
            return -1
        # Cardinality is higher than the higher cardinality learned during the learning step
        if first_log.cardinality >= cardinality_max:
            # logger.error(str("Log: " + str(first_log.message) + " is not usable due to cardinality higher than card max"))
            return -1
        # Get the embedding
        self.parser.get_w2v(first_log)
        if type(first_log.vector).__module__ != np.__name__:
            # logger.error(str("Log: " + str(first_log.message) + " is not usable due to word2vec"))
            return -1
        # Run until the window is filled
        while len(list_inputs) != self.window_size:
            # Get the previous log 
            log_previous = self.list_logs[index_inverted]
            # and its pattern
            self.parser.get_pattern(log_previous)
            # If the pattern is different from the selected log 
            if first_log.pattern.id != log_previous.pattern.id and log_previous.pattern.id != -1:
                # Get its embedding
                self.parser.get_w2v(log_previous)
                # If its embedding is valid
                if type(log_previous.vector).__module__ == np.__name__ :
                        # Add it to the window 
                        list_inputs.append(log_previous.vector)
                        list_index_inputs.append(index_inverted) 
                        list_logs_selected.append(log_previous)
            # Select the previous log
            index_inverted -= 1 
            # Padding
            if index_inverted < 0:
                if len(list_inputs) == 0:
                    logger.warning(str("List embedding empty: " +  str(first_log.message) + "is not usable due to slice"))
                    return -1 
                for _ in range(self.window_size - len(list_inputs)):
                    list_inputs.append(list_inputs[-1])
                    list_index_inputs.append(index_inverted)
        # If we have enough data, return the Log with the slice added.
        if len(list_inputs) == self.window_size:
            first_log.slice = list_inputs
            first_log.index_slice = list_index_inputs
            return first_log
        else:
            # Else, return -1
            logger.warning(str("Log: " + str (first_log.timestamp) + " " + str(first_log.message) + "is not usable due to slice"))
            return -1

    def show_selected_lines(self, index_line : int, range_line=100):
        """Show the selected and the range_line previous lines

        Args:
            index_line (int):the index of the selected line
            range_line (int, optional): number of previous lines to print. Defaults to 100.
        """
        logger.info("Selected lines are : ")
        for index in range(range_line, -1, -1):
            if index_line-index >= 0:
                print(self.list_logs[index_line-index])
  
