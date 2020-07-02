import unittest
from unittest.mock import mock_open, patch
# import sys
# sys.path.append('./code/logsparser/')
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Journal import Journal
from logflow.logsparser.Pattern import Pattern

def split_function(line):
    try:
        return line.strip().split()[0]
    except:
        return "1"

def sort_function(list_lines):
    return sorted(list_lines, key=lambda line: split_function(line))

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.parser = Dataset.parser_message
        self.path = "fake_path"
        self.path_list = ["fake_path", "fake_path", "fake_path"]
        self.data_test = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        self.line = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        self.pattern = Pattern(cardinality=6, pattern_word=["session", "User"], pattern_index=[1,4])
        self.pattern.id = 1
        self.pattern2 = Pattern(cardinality=6, pattern_word=["Home", "Other"], pattern_index=[1,4])
        self.pattern2.id = 2
        self.pattern3 = Pattern(cardinality=6, pattern_word=["Cat", "Users"], pattern_index=[1,4])
        self.pattern3.id = 3
        self.dict_patterns = {
            7:{2:[self.pattern, self.pattern2, self.pattern3]}
        }
        self.dict_patterns_2 = {
            7:{2:[self.pattern, self.pattern2, self.pattern3], 1:[self.pattern, self.pattern2, self.pattern3]}
        }

    def test_descriptors(self):
        message = Dataset.parser_message(self.line)
        self.assertEqual(message, ['pam_unix(sshd:session):', 'session', 'closed,', 'for1', 'User', 'Root/1', '123'])
        self.assertEqual(Journal.static_filter_word("home"), "home")
        self.assertEqual(Journal.static_filter_word("Home/"), "11105")
        self.assertEqual(Journal.static_filter_word("home1"), "01015")
        self.assertEqual(Journal.static_filter_word("home/"), "01105")
        self.assertEqual(Journal.static_filter_word("Home/1"), "11116")
        self.assertEqual(Journal.static_filter_word("123"), "NB")
        self.assertEqual(Journal.static_filter_word("12.3"), "NB")

    def test_count_log(self):
        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:      
            journal = Journal(path=self.path, parser_message=self.parser,  associated_pattern=False)      
            journal.run()
            self.assertEqual(len(journal.counter_logs), 1)
            self.assertEqual(len(journal.dict_message), 0)
            self.assertEqual(len(journal.dict_words_descriptors), 0)
            journal = Journal(path=self.path, parser_message=self.parser, large_file=True, pointer=2)
            self.assertEqual(journal.pointer, 2)

            journal = Journal(path=self.path, parser_message=self.parser,  associated_pattern=True, dict_patterns=self.dict_patterns)
            journal.run()
            self.assertEqual(len(journal.list_patterns), 3)
        
        # Test sorting
        data_to_sort = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): Cat closed, for1 Users Root/1 123\n1530388397 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388398 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): Home closed, for1 Other Root/1 123"
        with patch('builtins.open', mock_open(read_data=data_to_sort)) as m:      
            journal = Journal(path=self.path, parser_message=self.parser, associated_pattern=True, sort_function=sort_function, dict_patterns=self.dict_patterns)
            journal.run()
            self.assertListEqual(journal.list_patterns, [1,2,3])
        with patch('builtins.open', mock_open(read_data=data_to_sort)) as m:      
            journal = Journal(path=self.path_list, parser_message=self.parser, associated_pattern=True, sort_function=sort_function, dict_patterns=self.dict_patterns)
            journal.run()
            self.assertListEqual(journal.list_patterns, [1,2,3,1,2,3,1,2,3])


        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:      
            journal = Journal(path=self.path_list, parser_message=self.parser,  associated_pattern=False)      
            journal.run()
            self.assertEqual(len(journal.counter_logs), 1)
            self.assertEqual(len(journal.dict_message), 0)
            self.assertEqual(len(journal.dict_words_descriptors), 0)

            journal = Journal(path=self.path, parser_message=self.parser, large_file=True, pointer=2)
            self.assertEqual(journal.pointer, 2)

            journal = Journal(path=self.path_list, parser_message=self.parser,  associated_pattern=True, dict_patterns=self.dict_patterns)
            journal.run()
            self.assertEqual(len(journal.list_patterns), 9)

        with patch('builtins.open', mock_open(read_data=self.data_test)) as m:
            journal = Journal(path=self.path_list, parser_message=self.parser,  associated_pattern=False)
            journal.run()
            self.assertEqual(len(journal.counter_logs), 1)
            self.assertEqual(len(journal.dict_message), 0)
            self.assertEqual(len(journal.dict_words_descriptors), 0)
            
            journal = Journal(path=self.path, parser_message=self.parser, large_file=True, pointer=2)
            self.assertEqual(journal.pointer, 2)

            journal = Journal(path=self.path, parser_message=self.parser,  associated_pattern=True, dict_patterns=self.dict_patterns)
            journal.run()
            self.assertEqual(len(journal.list_patterns), 3)

            journal = Journal(path=self.path, parser_message=self.parser,  associated_pattern=True, dict_patterns=self.dict_patterns_2)
            journal.run()
            self.assertEqual(len(journal.list_patterns), 3)

        with patch('builtins.open', mock_open(read_data=1)) as m:
            journal = Journal(path=self.path, parser_message=self.parser)
            journal.read_file()

        with patch('builtins.open', mock_open(read_data=1)) as m:
            journal = Journal(path=self.path_list, parser_message=self.parser)
            journal.read_file()