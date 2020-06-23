# Copyright 2020 BULL SAS All rights reserved #
from logflow.relationsdiscover.Cardinality import Cardinality
import torch
from loguru import logger

class Result:
    """Compute the results based on the predictions and the ground truth

    Args:
        cardinality (Cardinality): cardinality object.
        condition (str, optional): Testing or Training results. Use only for results display. Defaults to "Train".
        subsample (bool, optional): Results computed on subsample or not. Use only for results display. Defaults to False.
    """
    def __init__(self, cardinality : Cardinality, condition="Train", subsample=False):
        self.number_of_classes = cardinality.number_of_classes
        self.classes_learned = cardinality.set_classes_kept
        self.conf_matrix = torch.zeros(self.number_of_classes, self.number_of_classes)
        self.cardinality = cardinality.cardinality
        self.condition = condition
        self.subsample = subsample

    def update(self, preds : torch.Tensor, labels: torch.Tensor):
        """Update the confusion matrix according to the new predictions and labels

        Args:
            preds (torch.Tensor): predictions provided by the model
            labels (torch.Tensor): labels provided by the dataloader
        """
        preds = torch.argmax(preds, 1)
        for p, t in zip(preds, labels):
            self.conf_matrix[p, t] += 1
    
    def computing_result(self, progress=0, reinit=True, printing=True):
        """Compute the results

        Args:
            progress (int, optional): value of the progression. Only for display task. Defaults to 0.
            reinit (bool, optional): reset the matrix value. Defaults to True.
            printing (bool, optional): print the result. Defaults to True.
        """
        TP_matrix = self.conf_matrix.diag()
        self.micro_recall = 0
        self.micro_precision = 0
        self.global_TP = 0
        self.global_FN = 0
        self.global_FP = 0

        nb_classes = 0
        for c in range(self.number_of_classes):
            if c in self.classes_learned:
                nb_classes += 1
                idx = torch.ones(self.number_of_classes).byte()
                idx = idx.bool()
                idx[c] = False

                self.FP = self.conf_matrix[c, idx].sum().item()
                self.FN = self.conf_matrix[idx, c].sum().item()
                self.TP = TP_matrix[c].item()

                if self.TP + self.FP == 0:
                    precision = 0
                else:
                    precision = (self.TP / (self.TP + self.FP))
                if self.TP + self.FN == 0:
                    recall = 0
                else:
                    recall = (self.TP / (self.TP + self.FN))
                self.micro_precision += precision
                self.micro_recall += recall
                self.global_FN += self.FN
                self.global_FP += self.FP
                self.global_TP += self.TP

        if nb_classes == 0:
            self.micro_recall = 0
            self.micro_precision = 0
        else:
            self.micro_recall = self.micro_recall / nb_classes
            self.micro_precision = self.micro_precision / nb_classes
        
        if self.global_TP + self.global_FP == 0:
            self.macro_recall = 0
        else:
            self.macro_recall = self.global_TP / (self.global_TP + self.global_FP)
        if self.global_TP + self.global_FN == 0:
            self.macro_precision = 0
        else:
            self.macro_precision = self.global_TP / (self.global_TP + self.global_FN)
        if self.micro_precision  + self.micro_recall  == 0:
            self.microf1 = 0
        else:
            self.microf1 = 2*(self.micro_recall  * self.micro_precision ) / (self.micro_precision + self.micro_recall)
        if reinit:
            self.conf_matrix = torch.zeros(self.number_of_classes, self.number_of_classes)
        if printing:
            self.print_results(progress)

    def print_results(self, progress=0):
        """print the result

        Args:
            progress (int, optional): value of the progression. Defaults to 0.
        """
        str_result = " macro-precision " + str(int(self.macro_precision*10000)/100) +" micro-precision "+ str(int(self.micro_precision*10000)/100) +" macro-recall "+ str(int(self.macro_recall*10000)/100) +" micro-recall "+ str(int(self.micro_recall*10000)/100) + " micro-f1 " + str(int(self.microf1*10000)/100)
        if self.condition == "Train":
            logger.info("[Train] Cardinality: " + str(self.cardinality) + " Res:" + str_result + " Progress " + str(int(progress*10000)/100) +"%")
        else:
            logger.info("[Test] Cardinality: " + str(self.cardinality) + " Res:" + str_result + " Progress " + str(int(progress*10000)/100) +"%" + " on subsample: " + str(self.subsample))


import pickle
class Results:
    """Compute the results based on the results saved during the learning step by each cardinality.

    """
    def __init__(self, path_model : str, name_model : str):
        """[summary]
        Args:
            path_model (str): path to the model to load the results
            name_model (str): name of the model
        """

        self.path = path_model + name_model + "_model.lf"
        self.condition = ""

    def load_files(self):
        """load the associated files
        """
        with open(self.path, "rb") as output_file:
            dict_results = pickle.load(output_file)
        self.dict_results = dict_results["Result"]

    def compute_results(self, condition="Test"):
        """Compute the results

        Args:
            condition (str, optional): Compute the results for the testing or training step. Only "Train" and "Test" are accepted. Defaults to "Test".
        """
        nb_classes = 0
        self.micro_recall = 0
        self.micro_precision = 0
        self.global_TP = 0
        self.global_FN = 0
        self.global_FP = 0
        self.condition = condition
        for cardinality in self.dict_results:
            local_result = self.dict_results[cardinality][condition]
            TP_matrix = local_result.conf_matrix.diag()
            for c in range(local_result.number_of_classes):
                if c in local_result.classes_learned:
                    nb_classes += 1
                    idx = torch.ones(local_result.number_of_classes).byte()
                    idx = idx.bool()
                    idx[c] = False

                    self.FP = local_result.conf_matrix[c, idx].sum().item()
                    self.FN = local_result.conf_matrix[idx, c].sum().item()
                    self.TP = TP_matrix[c].item()

                    if self.TP + self.FP == 0:
                        precision = 0
                    else:
                        precision = (self.TP / (self.TP + self.FP))
                    if self.TP + self.FN == 0:
                        recall = 0
                    else:
                        recall = (self.TP / (self.TP + self.FN))
                    self.micro_precision += precision
                    self.micro_recall += recall
                    self.global_FN += self.FN
                    self.global_FP += self.FP
                    self.global_TP += self.TP
        if nb_classes == 0:
            self.micro_recall = 0
            self.micro_precision = 0
        else:
            self.micro_recall = self.micro_recall / nb_classes
            self.micro_precision = self.micro_precision / nb_classes
        
        if self.global_TP + self.global_FP == 0:
            self.macro_recall = 0
        else:
            self.macro_recall = self.global_TP / (self.global_TP + self.global_FP)
        if self.global_TP + self.global_FN == 0:
            self.macro_precision = 0
        else:
            self.macro_precision = self.global_TP / (self.global_TP + self.global_FN)
        if self.micro_precision  + self.micro_recall  == 0:
            self.microf1 = 0
        else:
            self.microf1 = 2*(self.micro_recall  * self.micro_precision ) / (self.micro_precision + self.micro_recall)

    def print_results(self):
        """Print the result
        """
        str_result = " macro-precision " + str(int(self.macro_precision*10000)/100) +" micro-precision "+ str(int(self.micro_precision*10000)/100) +" macro-recall "+ str(int(self.macro_recall*10000)/100) +" micro-recall "+ str(int(self.micro_recall*10000)/100) + " micro-f1 " + str(int(self.microf1*10000)/100)
        logger.info("Results for " + self.condition+ " are:" + str_result)
