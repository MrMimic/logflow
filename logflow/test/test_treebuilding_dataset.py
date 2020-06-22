from logflow.treebuilding.Dataset import Dataset
from logflow.treebuilding.Parser import Parser
from logflow.logsparser import Pattern
from logflow.relationsdiscover.Model import LSTMLayer
import logflow
from unittest.mock import mock_open, patch, Mock
import unittest
import pickle
import numpy as np

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.model = LSTMLayer(num_classes=5)
        self.default_pattern = Pattern.Pattern(0, [], [])

    def test_create(self):
        with self.assertRaises(Exception):
            dataset = Dataset(path_model="", path_data="/", name_model="/")
        with self.assertRaises(Exception):
            dataset = Dataset(path_model="/", path_data="/", name_model="")
        with self.assertRaises(Exception):
            dataset = Dataset(path_model="/", path_data="", name_model="/")
        dataset = Dataset(path_model="/", path_data="/", name_model="/")

    def test_load_files(self):
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": [1]*20, "2": [2]*20, "3": [3]*20,"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })
        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()
        self.assertEqual(len(dataset.dict_patterns), 0)
        self.assertEqual(len(dataset.counter_patterns), 6)

    def test_load_logs(self):
        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # m = unittest.mock.MagicMock(name='open', spec=open)
        # m.return_value = iter(read_data)

        #with unittest.mock.patch('builtins.open', m):
        
        #mockOpen = mock_open(read_data=read_data)
        m = unittest.mock.mock_open(read_data=''.join(read_data_str))
        m.return_value.__iter__ = lambda self: self
        m.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', m):
            dataset = Dataset(path_model="/", path_data="/", name_model="/", index_line_max=1)
            dataset.load_logs()
        self.assertEqual(len(dataset.list_logs), 2)

        with patch('builtins.open', m):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_logs()
        self.assertEqual(len(dataset.list_logs), 3)

    #@patch('logflow.logsparser.Journal.Journal.find_pattern')
    def test_slice(self): #, mock_get_pattern):
        default_pattern1 = Pattern.Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern.Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern.Pattern(0, [], [])
        default_pattern3.id = 3
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": np.asarray([1]*20), "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()

        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # mockOpen = mock_open(read_data=read_data)
        mockOpen = unittest.mock.mock_open(read_data=''.join(read_data_str))
        mockOpen.return_value.__iter__ = lambda self: self
        mockOpen.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', mockOpen):
            dataset.load_logs()
        # Normal, return a log
        output = dataset.get_slice(2)
        self.assertIsInstance(output, logflow.treebuilding.Log.Log)
        dataset.show_selected_lines(2)

    #@patch('logflow.logsparser.Journal.Journal.find_pattern')
    def test_slice_w2v_issue(self): #, mock_get_pattern):
        default_pattern1 = Pattern.Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern.Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern.Pattern(0, [], [])
        default_pattern3.id = 3
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": [1]*20, "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()

        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # mockOpen = mock_open(read_data=read_data)
        mockOpen = unittest.mock.mock_open(read_data=''.join(read_data_str))
        mockOpen.return_value.__iter__ = lambda self: self
        mockOpen.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', mockOpen):
            dataset.load_logs()
        # Empty
        output = dataset.get_slice(2)
        self.assertEqual(output, -1)

    def test_slice_firt_log_issue(self): #, mock_get_pattern):
        default_pattern1 = Pattern.Pattern(0, [], [])
        default_pattern1.id = -1
        default_pattern2 = Pattern.Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern.Pattern(0, [], [])
        default_pattern3.id = 3
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": np.asarray([1]*20), "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()

        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # mockOpen = mock_open(read_data=read_data)
        mockOpen = unittest.mock.mock_open(read_data=''.join(read_data_str))
        mockOpen.return_value.__iter__ = lambda self: self
        mockOpen.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', mockOpen):
            dataset.load_logs()
        # Empty
        output = dataset.get_slice(2)
        self.assertEqual(output, -1)

    def test_slice_cardinality_issue(self): #, mock_get_pattern):
        default_pattern1 = Pattern.Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern.Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern.Pattern(0, [], [])
        default_pattern3.id = 3
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": np.asarray([1]*20), "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:100000000000, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()

        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # mockOpen = mock_open(read_data=read_data)
        mockOpen = unittest.mock.mock_open(read_data=''.join(read_data_str))
        mockOpen.return_value.__iter__ = lambda self: self
        mockOpen.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', mockOpen):
            dataset.load_logs()
        # Empty
        output = dataset.get_slice(2)
        self.assertEqual(output, -1)

    def test_slice_empty_issue(self): #, mock_get_pattern):
        default_pattern1 = Pattern.Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern.Pattern(0, [], [])
        default_pattern2.id = 1
        default_pattern3 = Pattern.Pattern(0, [], [])
        default_pattern3.id = 1
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": np.asarray([1]*20), "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            dataset = Dataset(path_model="/", path_data="/", name_model="/")
            dataset.load_files()

        read_data_str = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        # mockOpen = mock_open(read_data=read_data)
        mockOpen = unittest.mock.mock_open(read_data=''.join(read_data_str))
        mockOpen.return_value.__iter__ = lambda self: self
        mockOpen.return_value.__next__ = lambda self: next(iter(self.readline, ''))
        with patch('builtins.open', mockOpen):
            dataset.load_logs()
        # Empty
        output = dataset.get_slice(2)
        self.assertEqual(output, -1)


# @patch('foo.some_fn')
# def test_bar(mock_some_fn):
#     mock_some_fn.return_value = 'test-val-1'
#     tmp = bar.Bar()
#     assert tmp.method_2() == 'test-val-1'
#     mock_some_fn.return_value = 'test-val-2'
#     assert tmp.method_2() == 'test-val-2'

# import foo
# from unittest.mock import Mock
# foo.get_shard = Mock(return_value=11)


