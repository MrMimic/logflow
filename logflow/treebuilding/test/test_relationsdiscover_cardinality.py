from logflow.relationsdiscover.Cardinality import Cardinality
import unittest
import tempfile
import h5py
from unittest.mock import mock_open, patch
import pickle

class UtilTest(unittest.TestCase):

    def test_compute_position(self):
        cardinality = Cardinality(3, "", "")
        cardinality.list_classes = [1,1,1,2,2,3,4,5,6]
        cardinality.counter= {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        cardinality.compute_position()
        self.assertEqual(len(cardinality.set_classes_kept), 3)
        self.assertEqual(list(cardinality.list_position), [3, 4, 5, 6])
        self.assertEqual(cardinality.number_of_classes, 5)

        self.assertEqual(len(cardinality), 4)

    def test_compute_position_void(self):
        cardinality = Cardinality(3, "", "")
        cardinality.list_classes = []
        cardinality.counter= {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        cardinality.compute_position()
        self.assertEqual(cardinality.number_of_classes, 0)

    @patch('os.path.isfile') 
    def test_loadfiles(self, mock_isfile):
        mock_isfile.return_value = True
        # without size
        cardinality = Cardinality(3, "", "")
        read_data = pickle.dumps({'word2vec': -1, 'counter_patterns': {"1":1, "10":10, "100":100, "1000":1000, "10000":10000, "100000":100000}})
        mockOpen = mock_open(read_data=read_data)
        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_classes", data=[1,2,3,4,5])
        f.close()
        cardinality.path_list_classes = tf.name
        with patch('builtins.open', mockOpen):
            cardinality.load_files()
        tf.close()
        self.assertEqual(len(cardinality.counter ), 6)
        self.assertEqual(len(cardinality.list_classes ), 5)

        # with size
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
        tf.close()
        self.assertEqual(len(cardinality.counter ), 6)
        self.assertEqual(len(cardinality.list_classes ), 2)

    def test_getitem(self):
        cardinality = Cardinality(3, "", "")
        cardinality.size_windows = 4
        cardinality.list_classes = [1,1,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,5,6]
        cardinality.counter = {1:10, 2:100, 3:100, 4:100, 6:1000, 5:1000}
        cardinality.w2v = {"1": [1]*20, "2": [2]*20, "3": [3]*20,"4": [4]*20,
        "5": [5]*20, "6": [6]*20, "7": [7]*20}
        cardinality.list_position = range(len(cardinality.list_classes))

        # Normal
        output_getitem = cardinality.__getitem__(len(cardinality.list_classes)-1)
        self.assertEqual(output_getitem['output'], 6)
        self.assertEqual(len(list(output_getitem['input'][0])), 20)
        self.assertEqual(len(list(output_getitem['input'])), 4)
        
        # Invalid
        output_getitem = cardinality.__getitem__(0)
        self.assertListEqual(list(output_getitem['input']), [-1])
        self.assertEqual(output_getitem['output'], -1)

        # Invalid due to the same pattern
        output_getitem = cardinality.__getitem__(1)
        self.assertEqual(output_getitem['output'], -1)
        self.assertListEqual(list(output_getitem['input']), [-1])
        self.assertEqual(output_getitem['output'], -1)

        # Padding
        output_getitem = cardinality.__getitem__(5)
        self.assertEqual(output_getitem['output'], 1)
        self.assertEqual(len(list(output_getitem['input'][0])), 20)
        self.assertEqual(len(list(output_getitem['input'])), 4)