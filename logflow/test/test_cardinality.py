import unittest
from unittest.mock import mock_open, patch
# import sys
# sys.path.append('./code/logsparser/')
from logflow.logsparser.Cardinality import Cardinality

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.counter_general = {7: {('011023', 'session', '01107', '01014', 'User', '11116', 'NB'): 3}}
        self.data_test = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"

    def test_cardinality(self):
        self.cardinality = Cardinality(counter_general=self.counter_general[7], cardinality=7)
        dict_patterns = self.cardinality.compute()
        self.assertEqual(len(self.cardinality.dict_words), 7)
        self.assertEqual(len(dict_patterns), 1)
        self.assertEqual(len(dict_patterns[7]), 1)
        self.assertIsInstance(dict_patterns[7], list)
        self.assertEqual(len(self.cardinality.list_pattern), 1)