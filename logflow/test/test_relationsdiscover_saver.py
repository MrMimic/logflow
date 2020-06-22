import unittest
import torch.multiprocessing
from unittest.mock import mock_open, patch
from logflow.relationsdiscover.Saver import Saver
from logflow.relationsdiscover.Model import LSTMLayer
import pickle

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.lock = torch.multiprocessing.get_context('spawn').Lock()
        self.model = LSTMLayer(num_classes=5)


    @patch('os.path.isfile')    
    def test_saver_no_file(self, mock_isfile):
        mock_isfile.return_value = False
        self.saver = Saver("test", "./", 3, self.lock)
        read_data = ""
        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            self.saver.save(self.model)

    @patch('os.path.isfile')    
    def test_saver_file(self, mock_isfile):
        mock_isfile.return_value = True
        self.saver = Saver("test", "./", 3, self.lock)
        read_data = pickle.dumps({"LSTM": {3:self.model.state_dict()}})
        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            self.saver.save(self.model)

    @patch('os.path.isfile')    
    def test_saver_file_empty(self, mock_isfile):
        mock_isfile.return_value = True
        self.saver = Saver("test", "./", 3, self.lock)
        read_data = pickle.dumps({})
        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            self.saver.save(self.model)

    @patch('os.path.isfile')    
    def test_load_file(self, mock_isfile):
        mock_isfile.return_value = True
        self.saver = Saver("test", "./", 3, self.lock)
        read_data = pickle.dumps({"LSTM": {3:self.model.state_dict()}})
        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            model = self.saver.load(self.model)
            self.assertIsInstance(model, LSTMLayer)

    @patch('os.path.isfile')    
    def test_load_no_file(self, mock_isfile):
        mock_isfile.return_value = False
        self.saver = Saver("test", "./", 3, self.lock)
        read_data = pickle.dumps({"LSTM": {3:self.model.state_dict()}})
        mockOpen = mock_open(read_data=read_data)
        with self.assertRaises(Exception):
            with patch('builtins.open', mockOpen):
                self.saver.load(self.model)