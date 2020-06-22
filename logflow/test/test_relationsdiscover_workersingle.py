from unittest.mock import mock_open, patch
from logflow.relationsdiscover.Worker_per_cardinality import Worker_single
from logflow.relationsdiscover.Cardinality import Cardinality
from logflow.relationsdiscover.Model import LSTMLayer
import tempfile
import h5py
import pickle
import unittest
import torch.multiprocessing

class UtilTest(unittest.TestCase):
    @patch('os.path.isfile')
    def setUp(self, mock_isfile):
        self.lock = torch.multiprocessing.get_context('spawn').Lock()
        self.model = LSTMLayer(num_classes=5)
        
    def test_creation(self):
        cardinality = Cardinality(3, "", "", size=2)
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        cardinality.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            cardinality.load_files()
        self.cardinality = cardinality
        worker_single = Worker_single(cardinality = self.cardinality, lock=self.lock)
        tf.close()

    @patch('os.path.isfile')
    def test_create(self, mock_isfile):
        mock_isfile.return_value = True
        cardinality = Cardinality(3, "", "")
        read_data = pickle.dumps({'word2vec': {"1": [1]*20, "2": [2]*20, "3": [3]*20,"4": [4]*20,
        "5": [5]*20, "6": [6]*20, "7": [7]*20}, 'counter_patterns': {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6])
        f.close()
        cardinality.path_list_classes = tf.name
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}

        # Test
        with patch('builtins.open', mockOpen):
            #cardinality.load_files()
            worker_single = Worker_single(cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader()
            self.assertEqual(len(dataloader), 7) # 60% of 12
            self.assertTrue(worker_single.dataset.loaded)

        # Train
        # Avoid to create a new object
        worker_single.dataset.loaded = False
        with patch('builtins.open', mockOpen):
            #cardinality.load_files()
            worker_single = Worker_single(cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader(condition="Train")
            self.assertEqual(len(dataloader), 5) # 40% of 12

        worker_single.dataset.loaded = False
        with patch('builtins.open', mockOpen):
            #cardinality.load_files()
            worker_single = Worker_single(cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader(condition="Train", subsample=True, subsample_split=0.25)
            self.assertEqual(len(dataloader), 1) # 25% of 40% of 12
        
        tf.close()


    @patch('os.path.isfile')
    def test_load_model(self, mock_isfile):
        mock_isfile.return_value = True
        cardinality = Cardinality(3, "", "")
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
                } 
            })
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6])
        f.close()
        cardinality.path_list_classes = tf.name
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        with patch('builtins.open', mockOpen):
            worker_single = Worker_single(cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader()
            worker_single.load_model()

    @patch('os.path.isfile')
    def test_without_file(self, mock_isfile):
        mock_isfile.return_value = True
        cardinality = Cardinality(3, "", "")
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
                } 
            })
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6])
        f.close()
        cardinality.path_list_classes = tf.name
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        # No data
        with self.assertRaises(Exception):
            worker_single = Worker_single(cardinality = cardinality, lock=self.lock, batch_size=1)
            worker_single.load_model()

    @patch('os.path.isfile')
    def test_train_model(self, mock_isfile):
        mock_isfile.return_value = True
        cardinality = Cardinality(3, "", "")
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
                } 
            })
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6])
        f.close()
        cardinality.path_list_classes = tf.name
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        with patch('builtins.open', mockOpen):
            worker_single = Worker_single(batch_result=1, cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader()
            worker_single.train(resuming=False)
            worker_single.train(resuming=True)

    @patch('os.path.isfile')
    def test_test_model(self, mock_isfile):
        mock_isfile.return_value = True
        cardinality = Cardinality(3, "", "")
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
                } 
            })
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6])
        f.close()
        cardinality.path_list_classes = tf.name
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        with patch('builtins.open', mockOpen):
            worker_single = Worker_single(batch_result=1, cardinality = cardinality, lock=self.lock, batch_size=1)
            dataloader = worker_single.create_dataloader()
            worker_single.test()
