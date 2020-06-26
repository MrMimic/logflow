# Copyright 2020 BULL SAS All rights reserved #
from loguru import logger
from collections import Counter
from logflow.logsparser.Pattern import Pattern
import time
from typing import Dict, List, Tuple

# TODO: Test performance of static vs method

class Journal:
    """A journal is a list of logs files. It reads, parses and associates the logs and the pattern.

    Args:
        parser_message (function): Function to split the message part of the line.
        path (str): path to the data
        associated_pattern (bool, optional): Associate or discover the patterns. Note that if associated_pattern is True, dict_patterns must be provided. Defaults to False.
        dict_patterns (dict, optional): Dict of the patterns for the association. Defaults to {}.
        large_file (bool, optional): Optimization for the reading of one large file. Not implemented yet. Defaults to False.
        pointer (int, optional): Optimization for the reading of one large file. Not implemented yet. Defaults to -1.
        encoding (str, optional): Encoding of the files read.  Defaults to "latin-1".
    """

    def __init__(self, parser_message, path : str , associated_pattern=False, dict_patterns = {}, large_file=False, pointer=-1, encoding="latin-1"):
        assert path != ""
        assert parser_message != ""
        if associated_pattern:
            assert dict_patterns != {}
        # self.list_logs = []
        self.path = path
        if large_file:
            assert pointer != -1
            self.pointer = pointer
        self.parser_message = parser_message
        self.encoding = encoding
        self.dict_words_descriptors : Dict[str, str]= {}
        self.dict_message : Dict[Tuple[str, ...], Tuple[str, ...]] = {}
        self.associated_pattern =  associated_pattern
        self.dict_patterns = dict_patterns

    def run(self):
        """Start the process
        """
        if not self.associated_pattern:
            # We discover the patterns
            self.counter_logs = {}
            self.dict_message = {}
            self.read_file()
            del self.dict_words_descriptors
            del self.dict_message
            self.dict_words_descriptors = {}
            self.dict_message = {}
        else:
            # We associate lines and patterns
            self.default_pattern = Pattern(0, [], [])
            self.dict_message_associated : Dict[Tuple[str, ...], int]= {}
            self.list_patterns = []
            self.read_file()

    def count_log(self, line : str):
        """Count the number of same entries according to their descriptors. for space and computation optimization.

        Example using 3 entries :
        "Connexion of user Marc"
        "Connexion of user Marc"
        "Application failure node [1,0,0,2,4]"
        
        Counter_logs will be : {"Connexion of user Marc":2, "Application failure node [1,0,0,2,4]", 1}.

        To avoid useless computation, we use a dictionnary of line and line's descriptors. We do not compute the descriptors each time for each line.

        Args:
            line (str): line of log to add to the counter.
        """
        # Parse the message to have the descriptors.
        message : List[str] = self.parser_message(line=line)
        if len(message) > 0:
            # Get the frozen message because python can't used list as dictionnary key.
            frozen_message : Tuple[str, ...] = tuple(message)
            if frozen_message in self.dict_message:
                 # If the message is already in the dict, get the associated descriptors and add +1
                self.counter_logs[self.dict_message[frozen_message]] += 1
            else:
                # Else, compute the descriptors, add the line and descriptors into the dict, and add the line of descriptors to the dict.
                frozen_message_descriptors = tuple([self.filter_word(word) for word in message])
                self.dict_message.setdefault(frozen_message, frozen_message_descriptors)
                self.counter_logs.setdefault(frozen_message_descriptors, 1)
                self.counter_logs[self.dict_message[frozen_message]] += 1

    def associate_pattern(self, line : str):
        """Associate a line with a pattern. Add this pattern to the list of patterns.

        Args:
            line (str): line to be associated.
        """
        # Parse the message
        message = [self.filter_word(word) for word in self.parser_message(line=line)]
        if len(message) > 0:
            frozen_message = tuple(message)
            if frozen_message in self.dict_message_associated:
                # If we have already seen the message, we know the pattern.
                self.list_patterns.append(self.dict_message_associated[frozen_message])
            else:
                # Else, compute it.
                best_pattern = Journal.find_pattern(message, self.dict_patterns, self.default_pattern)
                # if best_pattern.id == -1:
                #     print(message, best_pattern, line, frozen_message)
                self.dict_message_associated[frozen_message] = best_pattern.id
                self.list_patterns.append(best_pattern.id)
    
    def read_file(self):
        """Read the logs files.
        """
        if isinstance(self.path, str):
            # For only one file
            try:
                with open(self.path, "r", encoding=self.encoding) as file_open: 
                    if self.associated_pattern:
                        for line in file_open.readlines():
                            self.associate_pattern(line)
                    else:
                        for line in file_open.readlines():
                            self.count_log(line)
            except:
               logger.error("Error while reading the file: " +str(self.path))
        else:
            # For a list of files.
            for file_path in self.path:
                try:
                    with open(file_path, "r", encoding=self.encoding) as file_open: 
                        if self.associated_pattern:
                            for line in file_open.readlines():
                                self.associate_pattern(line)
                        else:
                            for line in file_open.readlines():
                                self.count_log(line)
                except:
                   logger.error("Error while reading the file: " +str(file_path))

    def filter_word(self, word : str) -> str:
        """Get the descriptors of the word

        Args:
            word (str): word to describe

        Returns:
            str: descriptors of the word. They use a string representation of a list.
        """
        if self.is_number(word):
            return "NB"
        elif word.isalpha() or len(word) == 1:
            return word
        else:
            if word in self.dict_words_descriptors:
                return self.dict_words_descriptors[word]
            vector = ["0"]*5
            number = False
            lower = False
            upper = False
            alnum = False
            for letter in word:
                if letter.isdigit():
                    vector[3] = "1"
                    number = True
                elif letter.islower():
                    vector[1] = "1"
                    lower = True
                elif letter.isupper():
                    vector[0] = "1"
                    upper = True
                elif not letter.isalnum():
                    vector[2] = "1"
                    alnum = True
                if number and lower and upper and alnum:
                    break
            vector[4] = str(len(word))
            str_vector = ''.join(vector)
            self.dict_words_descriptors.setdefault(word, str_vector)
            return str_vector

    def is_number(self, s : str) -> bool:
        """Detect if a string is a float.

        Args:
            s (str): string to parse

        Returns:
            bool: True if the string is a float, False else.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def find_pattern(message : List[str], dict_patterns : dict, default_pattern : Pattern) -> Pattern:
        """Find the pattern associated to a log.
        
        The best pattern is the pattern with the maximum common words with the line.
        
        Args:
            message (List[str]): list of the words of the message part of the log.
            dict_patterns (dict): the dict of patterns.
            default_pattern (Pattern): the default pattern.

        Returns:
            Pattern: the pattern associated to the line.
        """
        # TODO : check the computation time to create the default pattern each time.
        # Create a default pattern to compare it to the other ones to find the best pattern.
        default_pattern = Pattern(0, [], [])
        best_pattern = default_pattern
        # Get the patterns with the same cardinality as the line. The cardinality of a pattern is the cardinality used for finding this pattern and not this number of words.
        dict_patterns_size = dict_patterns[len(message)]
        # Get the descriptors
        # message = [Journal.static_filter_word(word) for word in message] #Already done
        # Begin by the bigger pattern to save time.
        #for len_ms in dict_patterns:
        for size_pattern in sorted(dict_patterns_size.keys(), reverse=True):
            for pattern in dict_patterns_size[size_pattern]:
                nb_word_match = 0
                # Compute the number of common words
                for i in range(len(pattern)):
                    if pattern.pattern_word[i] == message[pattern.pattern_index[i]]:
                        nb_word_match += 1
                # If we have more common words, then we have a new best pattern
                if nb_word_match > len(best_pattern):
                    best_pattern = pattern
            # If new size if lower than the size of the actual best pattern, stop the detection. 
            if len(best_pattern) > size_pattern:
                break
        # if "Applicability(ComponentAnalyzerEvaluateSelfUpdate)" in line:
        #     # print(line)
        #     for size in dict_patterns[7]:
        #         for pattern in dict_patterns[7][size]:
        #             print("Length:", 7, "Size: ", size, "Pattern: ", pattern)
        #     print(best_pattern, line, message, len(message))
        return best_pattern

    @staticmethod
    def static_is_number(s : str) -> bool:
        """Detect if a string is a float.

        Args:
            s (str): string to parse

        Returns:
            bool: True if the string is a float, False else.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def static_filter_word(word : str) -> str:
        """Get the descriptors of the word

        Args:
            word (str): word to describe

        Returns:
            str: descriptors of the word. They use a string representation of a list.
        """
        if Journal.static_is_number(word):
            return "NB"
        elif word.isalpha() or len(word) == 1:
            return word
        else:
            vector = ["0"]*5
            number = False
            lower = False
            upper = False
            alnum = False
            for letter in word:
                if letter.isdigit():
                    vector[3] = "1"
                    number = True
                elif letter.islower():
                    vector[1] = "1"
                    lower = True
                elif letter.isupper():
                    vector[0] = "1"
                    upper = True
                elif not letter.isalnum():
                    vector[2] = "1"
                    alnum = True
                if number and lower and upper and alnum:
                    break
            vector[4] = str(len(word))
            str_vector = ''.join(vector)
        return str_vector