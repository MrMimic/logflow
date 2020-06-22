# Copyright 2020 BULL SAS All rights reserved #
import numpy as np # type: ignore
from logflow.treebuilding.Inference import Inference
from logflow.treebuilding.Dataset import Dataset
from logflow.treebuilding.Tree import Tree
from logflow.treebuilding.Log import Log
from loguru import logger
import time

class Workflow: 
    """Computes the tree of correlations.

    Args:
        dataset (Dataset): dataset containing the data for the inference and the tree building.
    """

    def __init__(self, dataset : Dataset):
        self.dataset = dataset
        self.models = dataset.LSTM
        self.inference =  Inference(self.models)
    
    def get_tree(self, index_line : int):
        """Get the tree associated to the line at the index "index_line"

        Args:
            index_line (int): index of the line

        Returns:
            Exception: Index of the line is after the maximum loaded index.
        """
        if index_line > self.dataset.index_line_max:
            logger.error("Asking for a line after the last line loaded. Check your index_line_max")
            raise Exception("Asking for a line after the last line loaded. Check your index_line_max")
        self.detect_workflow(index_line)

    def detect_workflow(self, index_line : int) -> str:
        """Detect the workflow (i.e. the correlations tree)

        Args:
            index_line (int): index of the line

        Returns:
            str: representation of the three to be used with graphviz.
        """
        begin = time.time()
        local_tree = Tree()
        first_log = self.dataset.get_slice(index_line)
        # Add the first log to the tree
        if first_log != -1:
            local_tree.add_node(log=first_log, id=0, parent=-1, processed=False,  weight=0)
        else:
            return "-1"
        depth = 0
        id = 1
        continue_while = True
        nb_node_merged = 0
        nb_logs_analysed = 0
        # While the condition is valid
        while continue_while:
            continue_while = False
            # For all the nodes in the tree
            for index in range(len(local_tree)) :
                node = local_tree.get_node(index)
                # If node wasn't predicted
                if not node.processed:
                    continue_while = True
                    nb_logs_analysed += 1
                    # Get its correlations
                    list_best_log = self.inference.test(node.log.slice, node.log)
                    # No correlations
                    if list_best_log == [-1]:
                        invalid_log = Log("-1")
                        invalid_log.usable = False
                        local_tree.add_node(log=invalid_log, id=id , parent=node.id, processed=True, weight=0)
                        id += 1
                    else:
                        # Else add the correlations to the tree to predict them later.
                        for index_log in list_best_log:
                            log = self.dataset.list_logs[index_log["log"]]
                            log.weigth = index_log["weigth"]
                            log_to_add =  self.dataset.get_slice(log.index_line)
                            # Invalid log
                            if log_to_add == -1:
                                local_tree.add_node(log=Log("-1"), id=id, parent=node.id, processed=True, weight=log.weight)
                            else:
                                local_tree.add_node(log=log_to_add, id=id, parent=node.id, processed=False, weight=log.weight)
                            id += 1
                local_tree.update_node(index) 
            local_tree.merge_tree()
            # No new nodes added, we can stop the exploration.
            if nb_node_merged == local_tree.get_number_nodes_merged(): 
                break
            else:
                nb_node_merged = local_tree.get_number_nodes_merged()
            depth += 1
            # Avoiding while true loop
            if depth > 6:
                logger.warning("Exploration is stopped due to depth exceeded")
                break
        local_tree.merge_tree()
        #logger.debug(str("Timing workflow: ") + str((time.time() - begin) / nb_logs_analysed))
        return self.write_workflow_merged(local_tree=local_tree)

    def write_workflow_merged(self, local_tree : Tree) -> str:
        """Write the tree following the graphviz syntax

        Args:
            local_tree (Tree): tree to be written.

        Returns:
            str: representation of the tree.
        """
        local_tree.merge_link()
        string_tree = "digraph prof {ratio = fill; node [style=filled]; \n"
        for node in local_tree.list_node_merge:
            string_tree += str(node.id) + " [labelfontsize=20, label=\"" + str(node.message) + " / " + str(node.cardinality) + "\"]; \n"
        for start in local_tree.dict_link:
            for end in local_tree.dict_link[start]:
                string_tree += str(start) + " -> " + str(end) + "[labelfontsize=20, headlabel=\"" + str(np.mean(local_tree.dict_link[start][end]))[:4] + "/" + str(len(local_tree.dict_link[start][end])) + "\"]; \n" # str(self.dict_link[start][end])[:4]
        string_tree += "}"
        if len(local_tree.list_node_merge) > 6 : 
            print(" Tree is:", string_tree)
        return string_tree