from logflow.treebuilding.Inference import Inference
from logflow.treebuilding.Log import Log
from logflow.logsparser.Pattern import Pattern
from logflow.relationsdiscover.Model import LSTMLayer
from unittest.mock import mock_open, patch, Mock
import unittest
import torch
import numpy as np
if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')


class UtilTest(unittest.TestCase):
    def setUp(self):
        self.model = LSTMLayer(num_classes=1).to(device)
        self.list_model = {1:self.model.state_dict(), 2:self.model.state_dict(), 3:self.model.state_dict()}

    def test_create(self):
        inference = Inference(self.list_model)

    def test_proba(self):
        inference = Inference(self.list_model)
        output = inference.probability([2.0, 2.0, 4.0])
        self.assertListEqual(list(output), [0.25, 0.25, 0.5])

    def test_inference_false(self):
        default_pattern = Pattern(0, [], [])
        default_pattern.id = -1
        inference = Inference(self.list_model)
        x = np.zeros((30,20))
        log = Log("test")
        log.cardinality = 1
        log.pattern = default_pattern
        output = inference.test(x, log)
        self.assertListEqual(output, [-1])

    def test_inference_true(self):
        default_pattern = Pattern(0, [], [])
        default_pattern.id = 0
        inference = Inference(self.list_model)
        x = np.zeros((30,20))
        log = Log("test")
        log.cardinality = 1
        log.pattern = default_pattern
        log.index_slice = [log]*30
        output = inference.test(x, log)
        self.assertIsInstance(output, list)