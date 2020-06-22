# Copyright 2020 BULL SAS All rights reserved #
from loguru import logger
from logflow.treebuilding.Log import Log
from logflow.treebuilding.Node import Node
from typing import Dict, List

class Tree:
    """Manages the tree building according to the relation found by the Inference with the weigths of the attention value.
    """

    def __init__(self):
        self.list_nodes = []

    def add_node(self, log : Log, id=0, parent=-1, processed=False,  weight=0):
        """Add a node to the tree

        Args:
            log (Log): log to add. 
            id (int, optional): id of the node. Defaults to 0.
            parent (int, optional): id of the node's parent. Defaults to -1.
            processed (bool, optional): node has been merged or not. Defaults to False.
            weight (int, optional): weigth associated to the node according to the attention layer. Defaults to 0.
        """
        if len(self.list_nodes) == 0:
            self.list_nodes = [Node(log=log, id=id, parent=parent, processed=processed,  weight=weight)]
        else:
            self.list_nodes.append(Node(log=log, id=id, parent=parent, processed=processed,  weight=weight))
    
    def __len__(self) -> int:
        """Get the length of the tree (the number of nodes)

        Returns:
            int: length of the tree
        """
        return len(self.list_nodes)

    def get_node(self, index : int) -> Node:
        """Get a node at the index

        Args:
            index (int): index of the node

        Returns:
            Node: node at the index "index"
        """
        return self.list_nodes[index]

    def update_node(self, index : int):
        """Update the processed statut of a node at the index "index"

        Args:
            index (int): index of the node
        """
        self.list_nodes[index].processed = True

    def merge_tree(self):
        """Merge the tree to keep only the relevant relations.
        """
        #logger.info("Merging tree")
        self.list_node_merge = []
        self.dict_new_id = {}
        # No nodes have been merged.
        for index in range(len(self.list_nodes)):
            self.list_nodes[index].merged = False
        # Let's start
        for index in range(len(self.list_nodes)):
            node = self.list_nodes[index]
            # If the node is not already merged
            if not node.merged:
                # Check the following nodes to check if we can merge them with the current node.
                for index_cmp in range(index+1, len(self.list_nodes)):
                    node_cmp = self.list_nodes[index_cmp]
                    # If the node is not already merged
                    if not node_cmp.merged:
                        self.dict_new_id[node_cmp.id] = node.id
                        self.dict_new_id[node.id] = node.id
                        #try:
                        # If the two nodes have the same pattern, we can merge them. Add the parents of the following node to the parents of the current node. Same for its weight.
                        if node_cmp.log.pattern == node.log.pattern:
                            node.list_parent.append(node_cmp.parent)
                            node.list_weight.append(node_cmp.weight)
                            self.list_nodes[index_cmp].merged = True
                        # except: # No needed anymore, default pattern
                        #     # Only for the -1 pattern, ie error pattern.
                        #     if node_cmp.log == node.log:
                        #         node.list_parent.append(node_cmp.parent)
                        #         node.list_weight.append(node_cmp.weight)
                        #         self.list_nodes[index_cmp].merged = True
                # Current node is merged.
                self.list_nodes[index].merged = True
                # Add it to the tree.
                self.list_node_merge.append(self.list_nodes[index])

    def merge_link(self):
        """Merge the links
        """
        #logger.info("Merging links")
        self.dict_link : Dict[int, Dict[int, List[int, ...]]] = {}
        # Use the merged nodes
        for node in self.list_node_merge:
            try:
                # Add a link between the parents of the current node and itself.
                for index in range(len(node.list_parent)):
                    self.dict_link.setdefault(self.dict_new_id[node.list_parent[index]], {})
                    self.dict_link[self.dict_new_id[node.list_parent[index]]].setdefault(node.id, [])
                    # Dict[parent][child] = [weigth]
                    self.dict_link[self.dict_new_id[node.list_parent[index]]][node.id].append(node.list_weight[index])
            except Exception as e:
                print(e)

    def get_number_nodes_merged(self) -> int:
        """Return the number of merged nodes

        Returns:
            int: number of merged nodes.
        """
        return len(self.list_node_merge)

