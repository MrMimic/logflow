# Copyright 2020 BULL SAS All rights reserved #
from logflow.logsparser.Journal import Journal
from logflow.logsparser import Pattern
from logflow.treebuilding.Log import Log
from loguru import logger
import numpy as np # type: ignore

class Parser:
    """Get the pattern and the embedding of a log.

    Args:
        dict_patterns (dict): dict of patterns
        w2v (dict): word2vec model
        counter_patterns (dict): dict of the cardinality of patterns.
    """

    def __init__(self, dict_patterns, w2v, counter_patterns):
        self.dict_patterns = dict_patterns
        self.default_pattern = Pattern.Pattern(0, [], [])
        self.w2v = w2v
        self.counter_patterns = counter_patterns

    def get_pattern(self, log : Log):
        """Get the pattern associated with a log. Uses the method of Journal from the logsparser.

        Args:
            log (Log): log to be associated with a pattern .
        """
        try:
            message = [Journal.static_filter_word(word) for word in log.message]
            log.pattern = Journal.find_pattern(message, self.dict_patterns, self.default_pattern)
            log.cardinality = len(str(self.counter_patterns[log.pattern.id]))
        except:
            logger.error(str("Log: " + str(log.message) + " is not usable due to pattern detection"))
            
    def get_w2v(self, log : Log):
        """Get the embedding associated with a log and its pattern. 

        Args:
            log (Log): log to be associated with the embedding.
        """
        try:
            log.vector = self.w2v[str(log.pattern.id)].astype(np.float32)
        except:
            logger.error(str("Log: " + str(log.message) + " is not usable due to word2vec"))
