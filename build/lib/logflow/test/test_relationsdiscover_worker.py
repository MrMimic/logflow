from unittest.mock import mock_open, patch
from logflow.relationsdiscover.Worker import Worker
from logflow.relationsdiscover.Worker_per_cardinality import Worker_single
from logflow.relationsdiscover.Cardinality import Cardinality
from logflow.relationsdiscover.Model import LSTMLayer
import tempfile
import h5py
from unittest.mock import mock_open, patch
import pickle
import unittest
import torch

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.list_cardinalities = [Cardinality(3, "", ""), Cardinality(4, "", ""), Cardinality(5, "", "")]
        self.lock = torch.multiprocessing.get_context('spawn').Lock()
        self.model = LSTMLayer(num_classes=5)

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
        #with self.assertRaises(Exception):
        worker.train(resume=True)

    def test_train_path_monoprocess(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        # No file
        with self.assertRaises(Exception):
            worker.train(resume=True)

    def test_test_no_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="", name_dataset="", cardinalities_choosen=[3,4])
        #with self.assertRaises(Exception):
        worker.test()

    def test_test_path_resume(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4])
        # No file
        #with self.assertRaises(Exception):
        worker.test()

    def test_test_path_monoprocess(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        # No file
        with self.assertRaises(Exception):
            worker.test()

    @patch('logflow.relationsdiscover.Worker_per_cardinality.Worker_single.train')     
    def test_static_train(self, mock_model):
        # To be check and add execute test tests.
        mock_model.return_value = None
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        worker1 = Worker_single(cardinality=self.list_cardinalities[0], path_model="/", name_dataset="/", lock=worker.lock)
        worker2 = Worker_single(cardinality=self.list_cardinalities[1], path_model="/", name_dataset="/", lock=worker.lock)
        Worker.execute_train(0, worker1, worker2)

    @patch('logflow.relationsdiscover.Worker_per_cardinality.Worker_single.test')     
    def test_static_test(self, mock_model):
        mock_model.return_value = None
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        worker1 = Worker_single(cardinality=self.list_cardinalities[0], path_model="/", name_dataset="/", lock=worker.lock)
        worker2 = Worker_single(cardinality=self.list_cardinalities[1], path_model="/", name_dataset="/", lock=worker.lock)
        Worker.execute_test(0, worker1, worker2)

    # Without patch, for failing to load files   
    def test_static_train_fail(self):
        # To be check and add execute test tests.
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        worker1 = Worker_single(cardinality=self.list_cardinalities[0], path_model="/", name_dataset="/", lock=worker.lock)
        worker2 = Worker_single(cardinality=self.list_cardinalities[1], path_model="/", name_dataset="/", lock=worker.lock)
        Worker.execute_train(0, worker1, worker2)
     
    def test_static_test_fail(self):
        worker = Worker(self.list_cardinalities, path_model="/", name_dataset="/", cardinalities_choosen=[3,4], multithreading=False)
        worker1 = Worker_single(cardinality=self.list_cardinalities[0], path_model="/", name_dataset="/", lock=worker.lock)
        worker2 = Worker_single(cardinality=self.list_cardinalities[1], path_model="/", name_dataset="/", lock=worker.lock)
        Worker.execute_test(0, worker1, worker2)