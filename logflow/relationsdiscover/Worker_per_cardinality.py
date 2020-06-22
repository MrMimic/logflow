# Copyright 2020 BULL SAS All rights reserved #
from logflow.relationsdiscover.Model import LSTMLayer
from logflow.relationsdiscover.StoppingCondition import StoppingCondition
from logflow.relationsdiscover.Result import Result
from logflow.relationsdiscover.Saver import Saver
from logflow.relationsdiscover.Cardinality import Cardinality
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
import numpy as np  # type: ignore
from loguru import logger
import torch
import torch.optim as optim
import torch.nn as nn
import threading
import random
# logger.add("./file_training.log")

class Worker_single():
    """A single worker is responsible for the creation of the dataloader, the learning/testing step and for saving files of one cardinality.

    Args:
        cardinality (Cardinality): the cardinality object containing the data.
        lock (threading.Lock): lock used for saving files in the same file for all cardinalities.
        batch_size (int, optional): size of the batch. Defaults to 128.
        path_model (str, optional): path to the model to save. Defaults to "".
        name_dataset (str, optional): name of the dataset. Defaults to "".
        batch_result (int, optional): show results each batch_result number of batchs. faults to 2000.
    """
    def __init__(self, cardinality: Cardinality, lock : threading.Lock, batch_size=128, path_model="", name_dataset ="", batch_result=2000):
        self.dataset = cardinality
        self.cardinality = self.dataset.cardinality
        self.batch_size = batch_size
        self.model = -1
        self.stopping_condition = StoppingCondition(method="earlystopping", condition_value = 0.005, condition_step=3)
        self.path_model = path_model
        self.name_dataset = name_dataset
        self.lock = lock
        self.saver = Saver(path_model=self.path_model, name_model=self.name_dataset, cardinality=self.cardinality, lock=self.lock)
        self.batch_result = batch_result

        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            logger.info("Starting learning on GPU")
        else:
            self.device = torch.device('cpu')
            logger.info ("Starting learning on CPU")


    def create_dataloader(self, validation_split=0.6, condition="Test", subsample=False, subsample_split=0.01) -> DataLoader: 
        """Create the dataloader for the learning/testing step.

        Args:
            validation_split (float, optional): ratio between the learning and the testing set. Defaults to 0.6.
            condition (str, optional): if Test the dataloader contains the test data. Else it contains the learning data. Defaults to "Test".
            subsample (bool, optional): use only a subsample of the data. Can be used for the learning and/or the testing step. Defaults to False.
            subsample_split (float, optional): ratio of the data to use. Defaults to 0.01.

        Returns:
            DataLoader: PyTorch dataloader corresponding to the previous features.
        """
        if not self.dataset.loaded :
            self.dataset.load_files()
            self.dataset.compute_position()
            self.size = len(self.dataset)
            logger.info("Cardinality: " + str(self.dataset.cardinality) + " size of dataset: " + str(self.size))
            logger.info("Nb of classes: " + str(self.dataset.number_of_classes))
        # Set the random seed to have always the same random value.
        random_seed = 42
        np.random.seed(random_seed)
        split = int(np.floor(validation_split * self.size))
        indices = list(range(self.size))
        np.random.shuffle(indices)
        if condition == "Test":
            indices = indices[:split]
        else:
            indices = indices[split:]
        if subsample:
            split = int(np.floor(subsample_split * len(indices)))
            np.random.shuffle(indices)
            indices = indices[:split]
        sampler = SubsetRandomSampler(indices)
        dataloader = DataLoader(self.dataset, batch_size=self.batch_size,
                                pin_memory=True, drop_last=True, num_workers=5,
                                sampler=sampler
                                )  # type: ignore
        return dataloader

    def load_model(self):
        """Load the learned model from a previous state

        Raises:
            e: file is not found
        """
        self.model = LSTMLayer(num_classes=self.dataset.number_of_classes).to(self.device)
        try:
            self.model = self.saver.load(model=self.model)
        except FileNotFoundError as e :
            logger.critical("No such file: "  +self.path_model + self.name_dataset + "_model.lf" + ".torch" )
            print("Raising: ", e)
            raise e 

    def train(self, validation_split=0.6, resuming=False):
        """Train the model

        Args:
            validation_split (float, optional): ratio between testing and learning set. Defaults to 0.6.
            resuming (bool, optional): resume the learning from a previous step. Not implemented yet. Defaults to False.
        """
        # Create the dataloader
        dataloader_train = self.create_dataloader(validation_split=validation_split, condition="train")
        if resuming:
            self.load_model()
        else:
            self.model = LSTMLayer(num_classes=self.dataset.number_of_classes, batch_size=self.batch_size).to(self.device)
        # Create the results
        result = Result(self.dataset, condition="Train")
        optimizer = optim.Adam(self.model.parameters())
        loss_fn = nn.CrossEntropyLoss()
        self.model.train()
        logger.info("Cardinality: " + str(self.cardinality) + " Starting the learning step")
        # Start the learning
        while not self.stopping_condition.stop():  
            for index_batch, batch in enumerate(dataloader_train):
                optimizer.zero_grad()
                label = batch['output']
                input_data = batch['input'].to(self.device)
                prediction = self.model(input_data)
                loss = loss_fn(prediction, label.to(self.device))
                loss.backward()
                optimizer.step()
                result.update(prediction, label)
                # Compute the results each 2000 batchs.
                if index_batch % self.batch_result == 0 and index_batch != 0:
                    result.computing_result(progress=index_batch/len(dataloader_train))
                    self.saver.save(model=self.model)
                    # Test only on a subsample
                    self.test(subsample=True, subsample_split=0.1)
            # At the end of one epoch, use the all testing test
            self.test()
            result.computing_result(reinit=True, progress=1)
            if self.stopping_condition.stop():
                logger.info("[Stopping] Cardinality: " + str(self.cardinality) + " " + str(self.stopping_condition) + " stopping learning step.")
            self.saver.save(model=self.model)
        # logger.info("[Test] Cardinality: " + str(self.cardinality) + " " + str(self.stopping_condition) + " stopping learning step.")
        # self.saver.save(model=self.model.state_dict())

    def test(self, validation_split=0.6, subsample=False, subsample_split=0.01):
        """Test the model

        Args:
            validation_split (float, optional): ratio between testing and learning set. Defaults to 0.6.
            subsample (bool, optional): if False, use all the available data, if True, use only a ratio of the data (subsample_split*data). Defaults to False.
            subsample_split (float, optional): ratio of the data to use. Defaults to 0.01.
        """
        dataloader_test = self.create_dataloader(validation_split=validation_split, condition="Test", subsample=subsample, subsample_split=0.01)
        result = Result(self.dataset, condition="Test", subsample=subsample)
        if self.model == -1:
            self.load_model()
        self.model.eval()
        self.conf_matrix = torch.zeros(self.dataset.number_of_classes, self.dataset.number_of_classes)
        for index_batch, batch in enumerate(dataloader_test):
            label = batch['output']
            input_data = batch['input'].to(self.device)
            prediction = self.model(input_data)
            result.update(prediction, label)
            if index_batch % self.batch_result == 0:
                result.computing_result(reinit=False, progress=index_batch/len(dataloader_test))
        self.model.train()
        result.computing_result(reinit=True, progress=1)    
        self.stopping_condition.update(result.microf1)
        self.stopping_condition.stop()