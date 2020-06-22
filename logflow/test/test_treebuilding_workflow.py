from logflow.treebuilding.Dataset import Dataset
from logflow.treebuilding.Workflow import Workflow
from logflow.treebuilding.Log import Log
from logflow.logsparser.Pattern import Pattern
from logflow.relationsdiscover.Model import LSTMLayer
import unittest
from unittest.mock import mock_open, patch, Mock
import unittest
import pickle
import numpy as np
import logflow

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.model = LSTMLayer(num_classes=5)
        self.default_pattern = Pattern(0, [], [])
        self.list_model = {1:self.model.state_dict(), 2:self.model.state_dict(), 3:self.model.state_dict()}


        default_pattern1 = Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern(0, [], [])
        default_pattern3.id = 3
        m = Mock()
        m.side_effect = [default_pattern1, default_pattern2, default_pattern3]*30
        # Mock(return_value=self.default_pattern)
        logflow.logsparser.Journal.Journal.find_pattern = m
        #mock_get_pattern.return_value = 1
        read_data = pickle.dumps(
            {
            'word2vec': {
                "1": np.asarray([1]*20), "2": np.asarray([2]*20), "3": np.asarray([3]*20),"4": [4]*20, "5": [5]*20, "6": [6]*20, "7": [7]*20
                }, 
            'counter_patterns': {
                1:100, 2:100, 3:100, 4:100, 6:1000, 5:1000
                },
            "LSTM": {
                3:self.model.state_dict()
                } ,
            "dict_patterns": {
                
                } 
            })

        mockOpen = mock_open(read_data=read_data)
        with patch('builtins.open', mockOpen):
            self.dataset = Dataset(path_model="/", path_data="/", name_model="/")
            self.dataset.load_files()

        self.dataset.LSTM = self.list_model
        self.dataset.list_logs = []
        for i in range(30):
            self.dataset.list_logs.append(Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123", index_line=i))

    def test_create(self):
        workflow = Workflow(self.dataset)

    def test_workflow_working(self):
        workflow = Workflow(self.dataset)   
        workflow.detect_workflow(25)

    def test_workflow_working_with_child(self):
        m = Mock()
        m.side_effect = [[{"log":25, "weigth":10}, {"log":15, "weigth":10}],
        [{"log":25, "weigth":10}, {"log":15, "weigth":10}],
        [{"log":25, "weigth":10}, {"log":15, "weigth":10}],
        [{"log":25, "weigth":10}, {"log":15, "weigth":10}],
        [{"log":25, "weigth":10}, {"log":15, "weigth":10}]]
        logflow.treebuilding.Inference.Inference.test = m

        default_pattern1 = Pattern(0, [], [])
        default_pattern1.id = 1
        default_pattern2 = Pattern(0, [], [])
        default_pattern2.id = 2
        default_pattern3 = Pattern(0, [], [])
        default_pattern3.id = 3
        m_pattern = Mock()
        m_pattern.side_effect = [default_pattern1, default_pattern2, default_pattern3]*3000
        logflow.logsparser.Journal.Journal.find_pattern = m_pattern

        workflow = Workflow(self.dataset)   
        workflow.detect_workflow(25)