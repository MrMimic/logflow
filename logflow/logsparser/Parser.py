# Copyright 2020 BULL SAS All rights reserved #
from logflow.logsparser.Cardinality import Cardinality
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Pattern import Pattern
from typing import Dict, List

# TODO: move the saving part of the pattern here.

class Parser:
    """The parser takes a dataset and computes its patterns.

    Args:
        dataset (Dataset): dataset for computing the patterns.
    """

    def __init__(self, dataset : Dataset):
        self.dataset = dataset
        self.counter_general_per_cardinality = self.dataset.counter_general_per_cardinality
        self.dict_patterns : Dict[int, Dict[int, List[Pattern]]] = {}

    def detect_pattern(self) -> dict:
        """Detect the patterns of the dataset and return the dict of patterns.

        Returns:
            dict: dict of patterns computed.
        """
        id = 0
        for cardinality in self.counter_general_per_cardinality:
            dict_patterns_local = Cardinality(self.counter_general_per_cardinality[cardinality], cardinality).compute()
            # Associate one id to each pattern
            for len_pattern in dict_patterns_local:
                for i in range(len(dict_patterns_local[len_pattern])):
                    dict_patterns_local[len_pattern][i].id = id
                    id += 1
            self.dict_patterns[cardinality] = dict_patterns_local
        return self.dict_patterns
