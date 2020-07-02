import unittest
from unittest.mock import mock_open, patch
import sys
# import h5py
# sys.path.append('./code/logsparser/')
import os
from logflow.logsparser.Embedding import Embedding
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Pattern import Pattern
from logflow.logsparser.Parser import Parser

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.counter_general = {7: {('011023', 'session', '01107', '01014', 'User', '11116', 'NB'): 3}}
        self.data_test = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"

    def test_parser(self):
        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            dataset = Dataset(['test'])
            self.parser = Parser(dataset)
            dict_patterns = self.parser.detect_pattern()
            self.assertEqual(len(dict_patterns), 1)
            self.assertEqual(len(dict_patterns[7]), 1)
            self.assertIsInstance(dict_patterns[7][7], list)
            self.assertIsInstance(dict_patterns[7][7][0], Pattern)