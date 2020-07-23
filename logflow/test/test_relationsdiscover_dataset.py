import unittest
from unittest.mock import mock_open, patch
from logflow.relationsdiscover.Dataset import Dataset
import pickle
import tempfile
import h5py

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.data_test = "1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123\n1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123"
        self.size = 10

    def test_create_dataset_void(self):
        # No data
        with self.assertRaises(Exception):
            dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", size=self.size)

    @patch('os.path.isfile')    
    def test_create_model_void(self, mock_isfile):
        mock_isfile.side_effect = [True, False]
        # No data
        with self.assertRaises(Exception):
            dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", size=self.size)

    @patch('os.path.isfile')    
    def test_create_dataset(self, mock_isfile):
        mock_isfile.return_value = True
        # With data
        # with patch('builtins.open', mock_open(read_data=-1)) as m:
        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", size=self.size)
        self.assertEqual(dataset.path_model_w2v, "model_test/DKRZ_test_model.lf")
        self.assertEqual(dataset.path_list_classes, "data_test/DKRZ_test_embedding.lf")

    @patch('os.path.isfile')  
    def test_creating_cardinalities(self, mock_isfile):
        mock_isfile.return_value = True
        # with patch('builtins.open', mock_open(read_data=-1)) as m:
        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", size=self.size)
        dataset.counter = {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}
        dataset.creating_cardinalities()
        self.assertEqual(len(dataset.set_cardinalities_available), 6)
        self.assertEqual(len(dataset.list_cardinalities), 6)

    @patch('os.path.isfile') 
    def test_loadfiles(self, mock_isfile):
        mock_isfile.return_value = True
        # with size
        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test")
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        dataset.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            dataset.loading_files()
        tf.close()
        self.assertEqual(len(dataset.list_classes ), 5)

        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", size=2)
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        dataset.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            dataset.loading_files()
        tf.close()
        self.assertEqual(len(dataset.list_classes ), 2)

    @patch('os.path.isfile')
    def test_all(self, mock_isfile):
        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test")
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        dataset.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            dataset.run()

    @patch('os.path.isfile')
    def test_all_one_model(self, mock_isfile):
        dataset = Dataset(path_model="model_test/", path_data="data_test/", name_dataset="DKRZ_test", one_model=True)
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        dataset.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            dataset.run()
