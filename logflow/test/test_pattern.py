import unittest
# import sys
# sys.path.append('./code/logsparser/')
from logflow.logsparser.Pattern import Pattern

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.default_pattern_empty = Pattern(0, [], [])
        self.default_pattern_empty_cmp = Pattern(0, [], [])
        self.default_pattern_cmp = Pattern(4, ["a", "b", "c", "d"], [0,1,2,3])
        self.default_pattern = Pattern(4, ["a", "b", "c", "d"], [0,1,2,3])
        self.new_pattern_1 = Pattern(4, ["a", "b", "c", "e"], [0,1,2,3])
        self.new_pattern_2 = Pattern(4, ["a", "b", "c"], [0,1,2])
        self.new_pattern_3 = Pattern(5, ["a", "b", "c"], [0,1,3])

    def test_eq(self):
        self.assertEqual(self.default_pattern_empty == self.default_pattern_empty_cmp, True)
        self.assertEqual(self.default_pattern_cmp == self.default_pattern, True)
        self.assertEqual(self.new_pattern_1 == self.default_pattern, False)
        self.assertEqual(self.new_pattern_2 == self.default_pattern, False)
        self.assertEqual(self.new_pattern_3 == self.default_pattern, False)
        self.assertEqual(self.new_pattern_3 == 2, False)

    def test_hash(self):
        dict_fake = {self.new_pattern_1: -1}
        pass

    def test_str(self):
        self.assertEqual(str(self.new_pattern_1), "Id: -1[0, 1, 2, 3]['a', 'b', 'c', 'e']")