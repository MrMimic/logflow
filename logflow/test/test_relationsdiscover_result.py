import unittest
from logflow.relationsdiscover.Result import Result
from logflow.relationsdiscover.Result import Results
from logflow.relationsdiscover.Cardinality import Cardinality
import torch
import math
import pickle
from unittest.mock import mock_open, patch

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.cardinality = Cardinality(3, "", "")
        self.cardinality.list_classes = [0,0,0,1,1,2]
        self.cardinality.counter= {0:100, 1:100, 2:100, 4:100, 6:1000, 5:1000}
        self.cardinality.compute_position()

    def test_creating(self):
        result = Result(self.cardinality)
        self.assertEqual(result.number_of_classes, 3)

    def test_update(self):
        result = Result(self.cardinality)
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])

        self.assertEqual(result.conf_matrix[0, 1], 1)
        self.assertEqual(result.conf_matrix[1, 0], 1)
        self.assertEqual(result.conf_matrix[1, 1], 1)
        self.assertEqual(result.conf_matrix[0, 0], 1)

    def test_compute(self):
        result = Result(self.cardinality)
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])

        result.computing_result()
        self.assertEqual(result.global_TP, 2)
        self.assertEqual(result.global_FP, 2)
        self.assertEqual(result.global_FN, 2)

        self.assertEqual(result.macro_precision, 0.50)
        self.assertEqual(result.macro_recall, 0.50)
        self.assertTrue(math.isclose(result.micro_recall, 1/3))
        self.assertTrue(math.isclose(result.micro_precision, 1/3))

    def test_no_class(self):
        result = Result(self.cardinality)
        result.number_of_classes = 0
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])
        result.computing_result()

        self.assertEqual(result.micro_precision, 0)
        self.assertEqual(result.micro_recall, 0)

    def test_print(self):
        result = Result(self.cardinality, "Test")
        result.number_of_classes = 0
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])
        result.computing_result()

        result = Result(self.cardinality)
        result.number_of_classes = 0
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])
        result.computing_result()

    def test_results_normal(self):
        result = Result(self.cardinality)
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])

        result_dump = pickle.dumps(
            {"Result": 
                { "1": {"Test":result, "Train":result},
                  "2": {"Test":result, "Train":result}
                }
            })
        mockOpen = mock_open(read_data=result_dump)
        with patch('builtins.open', mockOpen):
            results = Results(path_model="model/", name_model="Test")
            results.load_files()
            results.compute_results(condition="Test")

            self.assertEqual(results.global_TP, 4)
            self.assertEqual(results.global_FP, 4)
            self.assertEqual(results.global_FN, 4)

            self.assertEqual(results.macro_precision, 0.50)
            self.assertEqual(results.macro_recall, 0.50)
            self.assertTrue(math.isclose(results.micro_recall, 1/3))
            self.assertTrue(math.isclose(results.micro_precision, 1/3))
        results.print_results()
    
    def test_results_no_class(self):
        result = Result(self.cardinality)
        result.update(torch.Tensor([[0.4,0.3], [0.3,0.4], [0.4,0.3], [0.3,0.4]]), labels=[0,1,1,0])
        result.number_of_classes = 0
        result_dump = pickle.dumps(
            {"Result": 
                { "1": {"Test":result, "Train":result},
                  "2": {"Test":result, "Train":result}
                }
            })
        mockOpen = mock_open(read_data=result_dump)
        with patch('builtins.open', mockOpen):
            results = Results(path_model="model/", name_model="Test")
            results.load_files()
            results.compute_results(condition="Test")

            self.assertEqual(results.global_TP, 0)
            self.assertEqual(results.global_FP, 0)
            self.assertEqual(results.global_FN, 0)

            self.assertEqual(results.macro_precision, 0)
            self.assertEqual(results.macro_recall, 0)
            self.assertTrue(math.isclose(results.micro_recall, 0))
            self.assertTrue(math.isclose(results.micro_precision, 0))




