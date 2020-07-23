import unittest
from unittest.mock import mock_open, patch
# import sys
# sys.path.append('./code/logsparser/')
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Journal import Journal
from logflow.logsparser.Pattern import Pattern
import os
import random
import string

def parser_function(line):
    message_split = line.strip().split()
    return message_split[9:]

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.parser = Dataset.parser_message
        self.path = "fake_path"
        self.data_test = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        self.data_test_2 = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1"
        self.list_files = ["fake_path1", "fake_path2", "fake_path3"]
        self.pattern = Pattern(cardinality=6, pattern_word=["session", "User"], pattern_index=[1,4])
        self.dict_patterns = {
            7:{2:[self.pattern]}
        }

    def test_dataset(self):
        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], nb_cpu=40)
            self.assertEqual(dataset.nb_cpu, 40)

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'])
            self.assertEqual(len(dataset.counter_general_per_cardinality), 1)
            self.assertEqual(len(dataset.counter_general_per_cardinality[7]), 1)
            self.assertEqual(len(dataset.list_files), 1)

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], concat=False)
            self.assertEqual(len(dataset.counter_general_per_cardinality), 1)
            self.assertEqual(len(dataset.counter_general_per_cardinality[7]), 1)
            self.assertEqual(len(dataset.list_files), 1)
        
        with patch('builtins.open', mock_open(read_data=self.data_test_2)) as m:
            dataset = Dataset(['test'])
            self.assertEqual(len(dataset.counter_general_per_cardinality), 2)
            self.assertEqual(len(dataset.counter_general_per_cardinality[7]), 1)
            self.assertEqual(len(dataset.counter_general_per_cardinality[6]), 1)
            self.assertEqual(len(dataset.list_files), 1)

        with patch('builtins.open', mock_open(read_data=self.data_test_2)) as m:
            dataset = Dataset(['test'], parser_function=parser_function)
            self.assertEqual(len(dataset.counter_general_per_cardinality), 2)
            self.assertEqual(len(dataset.counter_general_per_cardinality[7]), 1)
            self.assertEqual(len(dataset.counter_general_per_cardinality[6]), 1)
            self.assertEqual(len(dataset.list_files), 1)

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], dict_patterns=self.dict_patterns)
            journal = Journal(parser_message=Dataset.parser_message, path=['test'], associated_pattern=False, dict_patterns = {}, large_file=False, pointer=-1, encoding="utf-8")
            self.assertIsInstance(dataset.execute(journal), Journal)
 
        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data="./")
            self.assertTrue(os.path.isfile("./"+str(dataset.name_dataset)+".lf"))
            os.remove("./"+str(dataset.name_dataset)+".lf")
            self.assertFalse(os.path.isfile("./"+str(dataset.name_dataset)+".lf"))

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            random_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
            dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data="./", name_dataset=random_name)
            self.assertTrue(os.path.isfile("./"+str(dataset.name_dataset)+".lf"))
            os.remove("./"+str(dataset.name_dataset)+".lf")
            self.assertFalse(os.path.isfile("./"+str(dataset.name_dataset)+".lf"))

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data="./", output="logpai")
            self.assertListEqual(dataset.list_patterns, [{'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}, {'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}, {'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}])

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data="./", output="logpai", multithreading=False)
            self.assertListEqual(dataset.list_patterns, [{'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}, {'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}, {'Content': ['011023', 'session', '01107', '01014', 'User', '11116', 'NB'], 'EventId': -1, 'EventTemplate': ' * session * * User *'}])