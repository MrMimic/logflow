import unittest
from logflow.relationsdiscover.StoppingCondition import StoppingCondition
import time

class UtilTest(unittest.TestCase):
    def test_creation(self):
        self.stop = StoppingCondition()

    def test_update(self):
        self.stop = StoppingCondition(condition_value=0.2)
        self.stop.update(0.05)
        self.assertEqual(self.stop.nb_step, 1)
        self.assertAlmostEqual(self.stop.last_increased, 0.05)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.22)
        self.assertEqual(self.stop.nb_step, 2)
        self.assertAlmostEqual(self.stop.last_increased, 0.17)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.35)
        self.assertEqual(self.stop.nb_step, 3)
        self.assertAlmostEqual(self.stop.last_increased, 0.13)
        self.assertTrue(self.stop.stop())

        self.stop.update(0.6)
        self.assertEqual(self.stop.nb_step, 0)
        self.assertAlmostEqual(self.stop.last_increased, 0.25)
        self.assertTrue(self.stop.stop())

    def test_little_variation_and_print(self):
        self.stop = StoppingCondition(condition_value=0.2)
        self.stop.update(0.05)
        self.assertEqual(self.stop.nb_step, 1)
        self.assertAlmostEqual(self.stop.last_increased, 0.05)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.22)
        self.assertEqual(self.stop.nb_step, 2)
        self.assertAlmostEqual(self.stop.last_increased, 0.17)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.6)
        self.assertEqual(self.stop.nb_step, 0)
        self.assertAlmostEqual(self.stop.last_increased, 0.38)
        self.assertFalse(self.stop.stop())
        self.assertEqual(str(self.stop), "Condition is not reached, last increase is: 0.38 number of steps: 0")

        self.stop.update(0.61)
        self.assertEqual(self.stop.nb_step, 1)
        self.assertAlmostEqual(self.stop.last_increased, 0.01)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.62)
        self.assertEqual(self.stop.nb_step, 2)
        self.assertAlmostEqual(self.stop.last_increased, 0.01)
        self.assertFalse(self.stop.stop())

        self.stop.update(0.63)
        self.assertEqual(self.stop.nb_step, 3)
        self.assertAlmostEqual(self.stop.last_increased, 0.01)
        self.assertTrue(self.stop.stop())
        self.assertEqual(str(self.stop), "Condition is reached, last increase is: 0.010000000000000009")

    def test_epoch(self):
        self.stop = StoppingCondition(method="epoch", condition_epoch=3)
        self.stop.update()
        self.assertEqual(self.stop.nb_epoch, 1)
        self.assertFalse(self.stop.stop())
        self.assertTrue( "Condition is not reached" in str(self.stop))
        self.stop.update()
        self.stop.update()
        self.assertTrue(self.stop.stop())
        self.assertTrue( "Condition is reached" in str(self.stop))

    def test_timer(self):
        self.stop = StoppingCondition(method="timer", duration=3)
        self.assertFalse(self.stop.stop())
        time.sleep(1)
        self.assertTrue( "Condition is not reached" in str(self.stop))
        self.assertFalse(self.stop.stop())
        time.sleep(3)
        self.assertTrue(self.stop.stop())
        self.assertTrue( "Condition is reached" in str(self.stop))



