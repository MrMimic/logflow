import unittest
from unittest.mock import mock_open, patch, MagicMock
import sys
import os
import pickle
import tempfile, io
from logflow.logsparser.Embedding import Embedding
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Pattern import Pattern
import h5py

class fakeW2V:
    def __init__(self, vocab):
        self.vocab=vocab

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.data_test = "2 2 2"
        self.path_data = "./"
        self.path_model = "./"
        self.name_dataset = "test"
        self.pattern = Pattern(cardinality=6, pattern_word=["session", "User"], pattern_index=[1,4])
        self.pattern.id = 2
        self.dict_patterns = {
            7:{2:[self.pattern]}
        }

    def test_load(self):
        dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data=self.path_data, name_dataset=self.name_dataset)
        embedding = Embedding(loading=True, list_classes=[2,2,2], name_dataset=self.name_dataset, path_data=self.path_data, path_model=self.path_model)

        tf = tempfile.NamedTemporaryFile()
        f = h5py.File(tf, 'w')
        f.create_dataset("list_patterns", data=[1,2,3,4,5])
        f.close()
        embedding.path_h5py = tf.name
        embedding.load()
        self.assertEqual(len(embedding.list_classes), 5)
        embedding.start()

    def test_clear_list(self):
        embedding = Embedding(loading=False, list_classes=[2,2,2], name_dataset=self.name_dataset, path_data=self.path_data, path_model=self.path_model)
        output = embedding.clear_list(([1,2,3,4,1,1,2], [1,3,4]))
        self.assertListEqual([1,3,4,1,1], list(output))

    def test_embedding(self): #, mock_open): #, mock_pickle_load):
        # Create a fake dataset to store the data
        dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data=self.path_data, name_dataset=self.name_dataset)
        embedding = Embedding(loading=False, list_classes=[2,2,2], name_dataset=self.name_dataset, path_data=self.path_data, path_model=self.path_model)
        
        embedding.create_temporary_file()
        embedding.train()
        self.assertEqual(embedding.giant_str, "2 2 2")
        self.assertTrue(os.path.isfile("./"+str(embedding.name_dataset)+"_model.lf"))
        os.remove("./"+str(dataset.name_dataset)+"_model.lf")
        self.assertFalse(os.path.isfile("./"+str(embedding.name_dataset)+"_model.lf"))
        str_test = embedding.list_to_str(["a", "b", "c"])
        self.assertEqual(str_test, "a b c")

        self.assertTrue(os.path.isfile("./"+str(embedding.name_dataset)+".lf"))
        os.remove("./"+str(dataset.name_dataset)+".lf")
        self.assertFalse(os.path.isfile("./"+str(embedding.name_dataset)+".lf"))
        
        with patch('builtins.open', mock_open(read_data=pickle.dumps({"word2vec": fakeW2V([2])}))) as m:
            embedding.generate_list_embeddings()

        # With specific temporary folder
        dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data=self.path_data, name_dataset=self.name_dataset)
        embedding = Embedding(loading=False, list_classes=[2,2,2], name_dataset=self.name_dataset, path_data=self.path_data, path_model=self.path_model, dir_tmp="./")
        
        embedding.create_temporary_file()
        self.assertTrue(os.path.isfile(str(embedding.fp.name)))
        self.assertTrue(os.path.isfile(str(embedding.fp_model.name)))

        # Don't remove elems
        with patch('builtins.open', mock_open(read_data=pickle.dumps({"word2vec": fakeW2V([2])}))) as m:
            embedding.generate_list_embeddings()
            self.assertEqual(embedding.list_classes, [2, 2, 2])

        # Wrong words in vocab
        with patch('builtins.open', mock_open(read_data=pickle.dumps({"word2vec": fakeW2V([2, "test"])}))) as m:
            embedding.generate_list_embeddings()
            self.assertEqual(embedding.list_vocab, [2])

        # Remove elements
        with patch('builtins.open', mock_open(read_data=pickle.dumps({"word2vec": fakeW2V([2])}))) as m:
            embedding.list_chunck = ([[2,2], [2,3]])
            embedding.generate_list_embeddings()
            self.assertEqual(embedding.list_classes, [2, 2, 2])

        dataset = Dataset(['test'], dict_patterns=self.dict_patterns, saving=True, path_data=self.path_data, name_dataset=self.name_dataset)
        embedding = Embedding(loading=False, list_classes=[2,2,2], name_dataset=self.name_dataset, path_data=self.path_data, path_model=self.path_model)
        embedding.start()