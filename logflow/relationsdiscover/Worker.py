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
        one_model (bool, optional): use one global model instead of one model per cardinality.
        exclude_test (boolean, optional): exlude the testing step during the learning step. Can be use with the timer as stopping condition to have an exact duration.
        stoppingcondition (str, optional): 3 options: "earlystopping", "timer", "epoch". Earlystopping uses the increase of the macro f1 value accros multiples steps, timer uses a timer, and epoch uses a nb of epoch. Defaults to "earlystopping".
        condition_value (float, optional): value of the increase. Defaults to 0.005.
        condition_step (int, optional): number of steps. Defaults to 3.
        duration (int, optional): duration of the learning step in seconde. Defaults to 60.
        condition_epoch (int, optional): number of epochs to be done. Defaults to 3.
    """

    def __init__(self, list_cardinalities : List[Cardinality], batch_size=128, multithreading=True, path_model="", name_dataset="", cardinalities_choosen=[-1], one_model=False, exclude_test=False, stoppingcondition="earlystopping", condition_value = 0.005, condition_step=3, duration=5, condition_epoch=3):
        self.list_cardinalities = list_cardinalities
        self.batch_size = batch_size
        self.multithreading = multithreading
        self.workers : List[Worker_single]= []
        self.path_model= path_model
        self.name_dataset = name_dataset
        self.one_model = one_model
        self.exclude_test = exclude_test
        self.stoppingcondition = stoppingcondition
        self.condition_value = condition_value
        self.condition_step = condition_step
        self.duration = duration
        self.condition_epoch = condition_epoch
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
        if self.one_model:
            assert len(self.list_cardinalities) == 1
            self.workers.append(Worker_single(cardinality=self.list_cardinalities[0], batch_size=self.batch_size, path_model=self.path_model, name_dataset=self.name_dataset, lock=self.lock, exclude_test=self.exclude_test, stoppingcondition=self.stoppingcondition, condition_value = self.condition_value, condition_step=self.condition_step, duration=self.duration, condition_epoch=self.condition_epoch))
        else:
            for cardinality in self.list_cardinalities:
                self.workers.append(Worker_single(cardinality=cardinality, batch_size=self.batch_size, path_model=self.path_model, name_dataset=self.name_dataset, lock=self.lock, exclude_test=self.exclude_test, stoppingcondition=self.stoppingcondition, condition_value = self.condition_value, condition_step=self.condition_step, duration=self.duration, condition_epoch=self.condition_epoch))
        
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
            self.workers.append(Worker_single(cardinality=cardinality, batch_size=self.batch_size, lock=self.lock, path_model=self.path_model, name_dataset=self.name_dataset))
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
                except (IOError, ValueError):
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
                except (IOError, ValueError):
                    logger.critical("Cardinality " + str(worker.cardinality) + " Error when loading file")
                except:
                    logger.critical("Cardinality " + str(worker.cardinality) + "Unknown error")
            index += 1
