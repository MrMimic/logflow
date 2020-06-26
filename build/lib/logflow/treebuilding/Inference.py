# Copyright 2020 BULL SAS All rights reserved #
import torch
import numpy as np # type: ignore
from logflow.relationsdiscover import Model
from logflow.treebuilding.Log import Log
from loguru import logger 
from typing import List

class Inference:
    """Manages the deep learning model, and run the inference through it.

    Args:
        models (List): list of the learned model to load.
    """

    def __init__(self, models : List):
        self.models = models
        for cardinality in self.models:
            if torch.cuda.is_available():
                logger.info("Using GPU")
                self.device = torch.device('cuda')
            else:
                logger.info("Using CPU")
                self.device = torch.device('cpu')
            save_model = self.models[cardinality]
            number_of_classes = save_model['fc0.bias'].shape[0] # Should be saved into the loaded file
            model = Model.LSTMLayer(num_classes=number_of_classes, batch_size=1, test=True).to(self.device)
            model.load_state_dict(save_model)
            model.eval()
            self.models[cardinality] = model

    def probability(self, x : List[float]) -> List[float]:
        """Compute probability (ie 0 =< proba =< 1) values for each sets of scores in x.

        Args:
            x (List[float]): list of values. Here, it is used at the output of the attention layer

        Returns:
            List[float]: list of probabilities
        """
        return x / np.sum(x)

    def test(self, data : List[List[float]], log : Log) -> List:
        """Run the inference through the model and return only the value greater than the threshold.

        Args:
            data (List[List[float]]): vector to be used as an input
            log (Log): log to predict

        Returns:
            List: list of the log with a weigth greater than the threshold. 
        """
        cardinality = log.cardinality
        tensor = torch.as_tensor([data]).to(self.device)
        tensor = tensor.float() # To be tested
        try:
            model = self.models[cardinality]
        except:
            logger.error("Trying to load a model with an excluded cardinality:" + str(cardinality))
            return [-1]
        # Run the inference
        output, attn_weights = model(tensor)
        topk_values = torch.topk(output, 1)[1].tolist()
        list_weight_attn = attn_weights.tolist()
        inference_pattern = topk_values[0][0]
        # Get the attention weigths.
        attn_weights = list_weight_attn[0]
        # If the prediction is wrong
        if inference_pattern != log.pattern.id:
            logger.error("Wrong prediction: " + str(inference_pattern) + " instead of [ pattern = '" + str(log.pattern.pattern_str) + "', message ='" + str(log.message) + "', id = " + str(log.pattern.id) + " ]")
            return [-1]
        # The prediction is right !
        else:
            sorted_weight = sorted(attn_weights, reverse=True)
            list_best_log = []
            # Get the probability
            probability = self.probability(attn_weights)
            # Compute the threshold
            threshold = np.mean(probability) + 2 *np.std(probability)
            # Get the value greater than the threshold.
            nb_value = len(list(filter(lambda x: x>threshold, probability)))
            nb_best_log = nb_value
            # Add these values to the list
            for index in range(nb_best_log):
                index_best = attn_weights.index(sorted_weight[index])
                best_log = log.index_slice[index_best]
                list_best_log.append({"log":best_log, "weigth": attn_weights[index_best]})
            return list_best_log

