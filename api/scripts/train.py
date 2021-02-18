
#!/usr/bin/python3
import datetime
import logging
import os
import pickle
import sys

# Get the log parsing function
script_path = os.path.dirname(os.path.realpath(__file__))
parsing_function_path = os.path.join(script_path, "..")
sys.path.append(parsing_function_path)
from log_parsing_function import parser_function

# Import logflow
sys.path.append("/home/code")
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Embedding import Embedding
from logflow.logsparser.Journal import Journal
from logflow.logsparser.Parser import Parser

# Create a dataset
data_path = "/home/data/"
log_file_list = [os.path.join(data_path, file) for file in os.listdir(data_path)]
logging.getLogger(__file__).info(f"Found {len(log_file_list)} log files to treat.")

# Use the parser function to get pattern found on the logs
dataset = Dataset(list_files=log_file_list, parser_function=parser_function)
patterns = Parser(dataset).detect_pattern()

# Save the patterns as a model
today = datetime.datetime.today()
file_name = f"{today.year}{today.month}{today.day}_{today.hour}{today.minute}{today.second}_logflow_model.pkl"
with open(os.path.join(os.sep, "home", "output", file_name), "wb") as handler:
    pickle.dump(patterns, handler, protocol=pickle.HIGHEST_PROTOCOL)
