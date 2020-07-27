from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Parser import Parser
from logflow.logsparser.Embedding import Embedding
from logflow.logsparser.Journal import Journal

from os import listdir
from os.path import isfile

def parser_function(line):
    return line.strip().split()[4:]

if __name__== "__main__":
    path_logs = "data/Windows/"
    list_files = []
    for file in listdir(path_logs):
        if "x" in file:
            list_files.append(path_logs + "/" + file)

    # Find the patterns
    dataset = Dataset(list_files=list_files, parser_function=parser_function)
    patterns = Parser(dataset).detect_pattern()
    Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Windows", path_model="model/", parser_function=parser_function, output="logpai") # Write the dataset



