# Copyright 2020 BULL SAS All rights reserved #
# import sys
# sys.path.append(0, "/home/code/logflow")

# from logflow.logsparser.Dataset import Dataset
# from Parser import Parser
# from Embedding import Embedding
# from Journal import Journal
# from os import listdir
# from os.path import isfile


# path_logs = "../../data/DKRZ/"
# list_files = []
# for dir in listdir(path_logs):
#     if "2018" in dir:
#         if not isfile(path_logs + dir):
#             for file in listdir(path_logs + dir):
#                 if "m1" in file or "m2" in file:
#                     list_files.append(path_logs + dir + "/" + file)

# # list_files = list_files[:10000]
# patterns = Parser(Dataset(list_files=list_files)).detect_pattern()
# Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="../../data/", name_dataset="DKRZ", path_model="../../model/")
# Embedding(loading=True, name_dataset="DKRZ", path_data="../../data/", path_model="../../model/", dir_tmp="/UC5/tmp/")

# ## Only one line parser
# # Split the message part of the log
# line = "1527807661 2018 Jun  1 01:01:01 m20014 cron notice run-parts(/etc/cron.hourly) starting 0anacron"
# print("Line is: ", line)
# message = line.strip().split()[9:]
# print("Message is: ", message)
# # Filter the message according to the descriptors
# message_filter = [Journal.static_filter_word(word) for word in message]
# print("Descriptors are: ", message_filter)
# # Get the pattern
# pattern = Journal.find_pattern(message_filter, patterns)
# print("Pattern of the line: '", line, "' is ", pattern)

