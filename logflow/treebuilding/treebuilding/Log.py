# Copyright 2020 BULL SAS All rights reserved #
from loguru import logger
from logflow.logsparser import Journal
from logflow.logsparser import Pattern
from typing import List

class Log:
    """Represents a line of log.

    Args:
        line (str): the line
        index_line (int, optional): index of the line in the file. Defaults to -1.
    """

    def __init__(self, line : str, index_line=-1, parser_function=""):
        self.line = line
        self.message : List[str] = []
        self.pattern = Pattern.Pattern(0, [], [])
        self.pattern.id = -1
        self.vector = -1
        self.usable = True
        self.slice : List[List[float]] = []
        self.index_line = index_line
        self.index_slice : List[int] = []
        self.cardinality = -2
        self.parser_function = parser_function
        if self.line != "-1":
            self.preprocess_line()
        self.severity = ""
        self.weight = -1

    def preprocess_line(self):
        """Split the message part of the line
        """
        if self.parser_function == "":
            line_split = self.line.strip().split()
            if len(line_split) > 9:
                self.message = line_split[9:]
            else:
                self.usable = False
                logger.warning(str("Log: " + str(line_split) + "is not usable due to exception"))
        else:
            self.message = self.parser_function(self.line)

    def __str__(self) -> str:
        """Return a string representation of the log

        Returns:
            str: string representation.
        """
        return self.line
