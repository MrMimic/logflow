#!/usr/bin/python3
from typing import List

def parser_function(line: str) -> List[str]:
    """
    This function must pre-treat log lines and return the "message" part as a list of strings.
    """
    # Log line pre-treatment: lower case and that's all.
    # Numeric values should be kept, as well as parenthesis/brackets.
    line = line.lower()
    # In out case, 8 first items from a split line are date, level, etc.
    return line.strip().split()[8:]
