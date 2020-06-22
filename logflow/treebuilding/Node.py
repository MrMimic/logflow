
from logflow.treebuilding.Log import Log
class Node:
    """Node of the tree

    Args:
        log (Log): Log associated to the node
        id (int): id of the node
        parent (int): id of the node's parents
        processed (bool): node has been merged or not
        weight (float): weigth associated to the node according to the attention layer.
    """

    def __init__(self, log : Log, id : int, parent : int, processed : bool, weight : float):
        self.log = log
        self.id = id
        self.parent = parent
        self.processed = processed
        self.weight = weight
        self.merged = False
        self.list_parent = [parent]
        self.list_weight = [weight]
        # try:
        #     print("ok")
        self.cardinality = log.cardinality
        self.message = self.log.message
        # except:
        #     self.cardinality = -1
        #     print("error", self.log.line)
        if self.log.line == "-1": # To be tested
            self.message = ["Wrong", "prediction"]