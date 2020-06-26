from logflow.treebuilding.Tree import Tree
from logflow.treebuilding.Node import Node
from logflow.treebuilding.Log import Log
from logflow.logsparser.Pattern import Pattern
import unittest

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.log = Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123")
        default_pattern = Pattern(0, ["home"], [])
        default_pattern.id = 0
        self.log.pattern = default_pattern
        self.log.cardinality = 3
        
        self.log2 = Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 1234")
        default_pattern = Pattern(0, ["house"], [])
        default_pattern.id = 1
        self.log2.pattern = default_pattern
        self.log2.cardinality = 3

        self.log3  = Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 1235")
        default_pattern = Pattern(0, ["HouseCat"], [])
        default_pattern.id = 2
        self.log3.pattern = default_pattern
        self.log3.cardinality = 3

        self.log5  = Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 1235")
        default_pattern = Pattern(0, ["HouseCat"], [])
        default_pattern.id = 2
        self.log5.pattern = default_pattern
        self.log5.cardinality = 3

        self.log4  = Log("1530388399a 2018 Jun 30 21:53:19 m21205 authpriv info")
        default_pattern = Pattern(0, [], [])
        default_pattern.id = 2
        self.log4.pattern = default_pattern

        self.log5 = Log("-1")

    def test_create_node(self):
        root = Node(self.log, id =0, parent=-1, processed=False, weight=0.1)
        child1 = Node(self.log2, id =1, parent=0, processed=False, weight=0.1)
        child2 = Node(self.log3, id =2, parent=0, processed=False, weight=0.1)
        child3 = Node(self.log3, id =3, parent=0, processed=False, weight=0.1) # To merge

        child4 = Node(self.log4, id =4, parent=0, processed=False, weight=0.1)  
        self.assertListEqual(child4.message, [])

        child5 = Node(self.log5, id =5, parent=0, processed=False, weight=0.1)  
        self.assertListEqual(child5.message, ["Wrong", "prediction"])

    def test_create_tree(self):
        tree = Tree()

    def test_add_node(self):
        root = Node(self.log, id =0, parent=-1, processed=False, weight=0.1)
        child1 = Node(self.log2, id =1, parent=0, processed=False, weight=0.1)
        child2 = Node(self.log3, id =2, parent=0, processed=False, weight=0.1)
        child3 = Node(self.log3, id =3, parent=0, processed=False, weight=0.1) # To merge

        child4 = Node(self.log4, id =4, parent=0, processed=False, weight=0.1)  

        tree = Tree()
        tree.add_node(self.log, id =0, parent=-1, processed=False, weight=0.1)
        self.assertEqual(len(tree.list_nodes), 1)

        tree.add_node(self.log2, id =1, parent=0, processed=False, weight=0.1)
        self.assertEqual(len(tree.list_nodes), 2)
        self.assertEqual(len(tree), 2)

        self.assertIsInstance(tree.get_node(0), Node)
        self.assertFalse(tree.get_node(0).processed)
        tree.update_node(0)
        self.assertTrue(tree.get_node(0).processed)

    def test_tree_merge(self):
        tree = Tree()
        tree.add_node(self.log, id =0, parent=-1, processed=False, weight=0.1)
        tree.add_node(self.log2, id =1, parent=0, processed=False, weight=0.2)
        tree.add_node(self.log3, id =2, parent=0, processed=False, weight=0.3)
        tree.add_node(self.log4, id =3, parent=0, processed=False, weight=0.4)
        tree.add_node(self.log5, id =4, parent=0, processed=False, weight=0.5)
        tree.add_node(self.log5, id =5, parent=3, processed=False, weight=0.6)
        self.assertEqual(len(tree.list_nodes), 6)
        tree.merge_tree()
        self.assertEqual(len(tree.list_node_merge), 4) # Merging
        self.assertEqual(tree.get_number_nodes_merged(), 4)

        tree.merge_link()
        self.assertEqual(len(tree.dict_link), 2)
        self.assertEqual(len(tree.dict_link[0]), 3)