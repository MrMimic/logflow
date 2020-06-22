# Copyright 2020 BULL SAS All rights reserved #
import torch.multiprocessing
from logflow.relationsdiscover.Worker_per_cardinality import Worker_single
from logflow.relationsdiscover.Cardinality import Cardinality
import os
from loguru import logger
from typing import List

class Worker:
    """Handle the learning and the testing of each worker_per_cardinality in a multithreading way. 

    Args:
        list_cardinalities (List[Cardinality]): list of the cardinality objects to be used.
        batch_size (int, optional): size of the batch. Defaults to 128.
        multithreading (bool, optional): use a multithreading implementation. Sequential implementation is not available yet. Defaults to True.
        path_model (str, optional): path to the model to save. Defaults to "".
        name_dataset (str, optional): name of the dataset. Defaults to "".
        cardinalities_choosen (List[int], optional): list of cardinalities to use. This list contains only the value of cardinalities to be used. [-1] means all cardinalities. Defaults to [-1].
    """

    def __init__(self, list_cardinalities : List[Cardinality], batch_size=128, multithreading=True, path_model="", name_dataset="", cardinalities_choosen=[-1]):
        self.list_cardinalities = list_cardinalities
        self.batch_size = batch_size
        self.multithreading = multithreading
        self.workers : List[Worker_single]= []
        self.path_model= path_model
        self.name_dataset = name_dataset
        if cardinalities_choosen != [-1]:
            list_cardinalities_tmp = []
            for cardinality in self.list_cardinalities:
                if cardinality.cardinality in cardinalities_choosen:
                    list_cardinalities_tmp.append(cardinality)
            self.list_cardinalities = list_cardinalities_tmp
        # Use a specific lock for the multithreading implementation
        self.lock = torch.multiprocessing.get_context('spawn').Lock()

    def train(self, resume=False):
        """Start the training

        Args:
            resume (bool, optional): resume from a previous training. Not implemented yet. Defaults to False.
        """
        self.workers = []
        if resume:
            assert self.path_model != ""
            assert self.name_dataset != ""
        for cardinality in self.list_cardinalities:
            self.workers.append(Worker_single(cardinality=cardinality, batch_size=self.batch_size, path_model=self.path_model, name_dataset=self.name_dataset, lock=self.lock))
        if self.multithreading:
            torch.multiprocessing.spawn(Worker.execute_train, args=(self.workers), daemon=False, nprocs=len(self.workers), join=True)
        else:
            for worker in self.workers:
                worker.train()

    def test(self):
        """Start the testing
        """
        self.workers = []
        for cardinality in self.list_cardinalities:
            self.workers.append(Worker_single(cardinality=cardinality, batch_size=self.batch_size, lock=self.lock))
        if self.multithreading:
            torch.multiprocessing.spawn(Worker.execute_test, args=(self.workers), daemon=False, nprocs=len(self.workers), join=True)
        else:
            for worker in self.workers:
                worker.test()

    @staticmethod
    def execute_test(i, *args):
        """Execute the test function for the multithreading implementation

        Args:
            i (int): value of the cardinality selected
            args (List[Worker_single]) : list of all the cardinalities
        """
        list_worker = args
        index = 0
        for worker in list_worker:
            if index == i:
                try:
                    worker.test()
                except IOError:
                    logger.critical("Cardinality " + str(worker.cardinality) + " Error when loading file")
            index += 1

    @staticmethod
    def execute_train(i, *args):
        """Execute the training function for the multithreading implementation

        Args:
            i (int): value of the cardinality selected
            args (List[Worker_single]) : list of all the cardinalities
        """
        list_worker = args
        index = 0
        for worker in list_worker:
            if index == i:
                try:
                    worker.train()
                except IOError:
                    logger.critical("Cardinality " + str(worker.cardinality) + " Error when loading file")
            index += 1
