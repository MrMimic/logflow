# Copyright 2020 BULL SAS All rights reserved #
class Pattern:
    """Represents a pattern. A pattern is described by its cardinality (number of words of the associated line), its words and indexes of these words.

    Example :
    pattern_word = ["house", "cat"]
    pattern_index = ["3", "5"]
    Here, we are looking for the word "house" at the 3rd position and the word "cat" at the 5th position.

    Args:
        cardinality (int): Cardinality of the associated line.
        pattern_word (list): list of the pattern's words
        pattern_index (list): list of the pattern's indexes words
    """

    def __init__(self, cardinality : int, pattern_word : list, pattern_index : list):
        self.cardinality = cardinality
        self.pattern_word = pattern_word
        self.pattern_index = pattern_index
        self.pattern_str = ""
        self.id = -1
        position = 0
        for i in range(self.cardinality):
            if i in self.pattern_index:
                self.pattern_str += " " + self.pattern_word[position]
                position += 1
            else:
                self.pattern_str += " *"

    def __eq__(self, pattern_cmp : object) -> bool:
        """Compare two patterns. If the patterns have the same list of word and list of index, they are the same.

        Args:
            pattern_cmp (object): The pattern to compare.

        Returns:
            bool: True if the patterns are the same, else False.
        """
        if not isinstance(pattern_cmp, Pattern):
            return False
        if self.pattern_index == pattern_cmp.pattern_index and self.pattern_word == pattern_cmp.pattern_word:
            return True
        else:
            return False

    def __hash__(self) -> int:
        """Compute the hash based on the string representation with wildcard.

        Returns:
            hash: hash of the pattern
        """
        return hash(self.pattern_str)

    def __str__(self) -> str:
        """Compute the string representation

        Returns:
            str: string representation.
        """
        return "Id: " + str(self.id) + str(self.pattern_index) + str(self.pattern_word)

    def __len__(self) -> int:
        """Compute the length of a pattern. The length is the number of its words.

        Returns:
            int: length of the pattern.
        """
        return len(self.pattern_index)

    