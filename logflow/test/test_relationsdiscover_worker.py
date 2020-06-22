from unittest.mock import mock_open, patch
from logflow.relationsdiscover.Worker import Worker
from logflow.relationsdiscover.Worker_per_cardinality import Worker_single
from logflow.relationsdiscover.Cardinality import Cardinality
import tempfile
import h5py
from unittest.mock import mock_open, patch
import pickle
import unittest

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.list_cardinalities = [Cardinality(3, "", ""), Cardinality(4, "", ""), Cardinality(5, "", "")]

    def test_creation(self):
        worker = Worker(self.list_cardinalities)

    def test_creation_no_cardinality(self):
        worker = Worker(self.list_cardinalities, path_model="", name_dataset="", cardinalities_choosen=[-1])
        self.assertEqual(len(worker.list_cardinalities), 3)
    
    def test_creation_no_cardinalities(self):
        worker = Worker(self.list_cardinalities, path_model="", name_dataset="", cardinalities_choosen=[3,4])
        self.assertEqual(len(worker.list_cardinalities), 2)

    def test_train_no_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="", name_dataset="", cardinalities_choosen=[3,4])
        with self.assertRaises(Exception):
            worker.train(resume=True)

    def test_train_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4])
        # No file
        with self.assertRaises(Exception):
            worker.train(resume=True)

    def test_train_path_monoprocess(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        # No file
        with self.assertRaises(Exception):
            worker.train(resume=True)

    def test_test_no_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="", name_dataset="", cardinalities_choosen=[3,4])
        with self.assertRaises(Exception):
            worker.test()

    def test_test_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4])
        # No file
        with self.assertRaises(Exception):
            worker.test()

    def test_test_path_monoprocess(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        # No file
        with self.assertRaises(Exception):
            worker.test()

    def test_static(self):
        # To be check and add execute test tests.
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        worker1 = Worker_single(cardinality=self.list_cardinalities[0], path_model="/", name_dataset="/", lock=worker.lock)
        worker2 = Worker_single(cardinality=self.list_cardinalities[1], path_model="/", name_dataset="/", lock=worker.lock)
        Worker.execute_train(1, [worker1, worker2])


    # Real test wtih fake data.
    # @patch('os.path.isfile')
    # def test_train_path_resume(self, mock_isfile):
    #     cardinality = Cardinality(3, "", "", size=2)
    #     read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
    #     mockOpen = mock_open(read_data=read_data)
    #     tf = tempfile.NamedTemporaryFile()
    #     f = h5py.File(tf, 'w')
    #     f.create_dataset("list_classes", data=[1,2,3,4,5])
    #     f.close()
    #     cardinality.path_list_classes = tf.name
    #     with patch('builtins.open', mockOpen):
    #         cardinality.load_files()

    #     cardinality_4 = Cardinality(4, "", "", size=2)
    #     read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
    #     mockOpen = mock_open(read_data=read_data)
    #     tf4 = tempfile.NamedTemporaryFile()
    #     f = h5py.File(tf4, 'w')
    #     f.create_dataset("list_classes", data=[1,2,3,4,5])
    #     f.close()
    #     cardinality_4.path_list_classes = tf4.name
    #     with patch('builtins.open', mockOpen):
    #         cardinality_4.load_files()

    #     cardinality_5 = Cardinality(5, "", "", size=2)
    #     read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
    #     mockOpen = mock_open(read_data=read_data)
    #     tf5 = tempfile.NamedTemporaryFile()
    #     f = h5py.File(tf5, 'w')
    #     f.create_dataset("list_classes", data=[1,2,3,4,5])
    #     f.close()
    #     cardinality_5.path_list_classes = tf5.name
    #     with patch('builtins.open', mockOpen):
    #         cardinality_5.load_files()

    #     # File provided
    #     with patch('builtins.open', mockOpen):
    #         worker = Worker(list_cardinalities=[cardinality, cardinality_4, cardinality_5], path_model="/", name_dataset="test", cardinalities_choosen=[3,4,5])
    #         worker.train(resume=False)

    #     tf.close()
    #     tf4.close()
    #     tf5.close()