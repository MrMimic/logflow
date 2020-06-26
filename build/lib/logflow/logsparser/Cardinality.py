# Copyright 2020 BULL SAS All rights reserved #
from collections import Counter
from logflow.logsparser.Pattern import Pattern
from loguru import logger
from typing import Dict, List

class Cardinality:
    """A cardinality is a length of line. The length is defined as the number of words. 

    Args:
        counter_general (dict): Counter of the different logs according in all the dataset.
        cardinality (int): Number of words
    """

    def __init__(self, counter_general : dict, cardinality : int):
        self.counter_general = counter_general
        self.cardinality = cardinality
        self.dict_words : Dict[int, Dict[str, int]] = {}
        for i in range(self.cardinality):
            self.dict_words.setdefault(i, {})
        self.list_pattern : List[Pattern] = []

    def counter_word(self):
        """Count the number of words according to their place in the log. 
        """
        for entry in self.counter_general:
            position = 0
            for word in entry:
                self.dict_words[position].setdefault(word,0)
                self.dict_words[position][word] += self.counter_general[entry]
                position += 1

    def detect_patterns(self):
        """Detect the pattern based on the maximum number of similar words.
        """
        for entry in self.counter_general:
            comparison_vector = [0]*self.cardinality
            position = 0
            entry = list(entry)
            # Once the dict_words is created, we get the number of entries with the same word by only one access to the dictionnary.
            for word in entry:
                comparison_vector[position] += self.dict_words[position][word]
                position += 1
            # We take the best subset of the similar words, i.e [10,10,2,2,2] keeps 2 as best subset.
            best_subset_words_number = Counter(comparison_vector).most_common(1)[0][0] # [(value, nb_value)]
            # We compute the index of the words kept
            best_subset_words_index = [i for i, e in enumerate(comparison_vector) if e == best_subset_words_number]
            # And the words theirself.
            best_subset_words_value = [entry[i] for i in best_subset_words_index]
            self.list_pattern.append(Pattern(self.cardinality, best_subset_words_value, best_subset_words_index))
        self.list_pattern = list(set(self.list_pattern))
        logger.debug("Cardinality: " + str(self.cardinality) + " found " + str(len(self.list_pattern)) + " patterns")

    def order_pattern(self):
        """Order the pattern by size to have a fast association between lines and patterns.
        """
        for pattern in self.list_pattern:
            self.dict_patterns.setdefault(len(pattern), [])
            self.dict_patterns[len(pattern)].append(pattern)

    def compute(self) -> Dict[int, List[Pattern]]:
        """Start the workflow for the multithreading implementation. 

        Returns:
            (dict): the dict of patterns detected.
        """
        self.counter_word()
        self.detect_patterns()
        self.dict_patterns : Dict[int, List[Pattern]]= {}
        self.order_pattern()
        return self.dict_patterns
