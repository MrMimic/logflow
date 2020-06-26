from logflow.relationsdiscover.Model import LSTMLayer
import unittest
import tempfile
import h5py
from unittest.mock import mock_open, patch
import pickle
import torch
if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')

class UtilTest(unittest.TestCase):

    def test_learn(self):
        model = LSTMLayer(num_classes=5).to(device)
        x = torch.zeros([128,30,20])
        x = x.to(device)
        output = model(x)
        self.assertEqual(len(output), 128)

    def test_test(self):
        model = LSTMLayer(num_classes=5, test=True).to(device)
        model.eval()
        x = torch.zeros([128,30,20])
        x = x.to(device)
        output = model(x)
        self.assertEqual(len(output), 2)