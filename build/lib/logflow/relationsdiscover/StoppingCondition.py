# Copyright 2020 BULL SAS All rights reserved #
class StoppingCondition:
    """Condition to stop the learning. Increase of the F1 value needs to be less than 0.005 during more than 3 steps to stop the learning process.

    Args:
        method (str, optional): Not implemented yet. Defaults to "earlystopping".
        condition_value (float, optional): value of the increase. Defaults to 0.005.
        condition_step (int, optional): number of steps. Defaults to 3.
    """
    def __init__(self, method="earlystopping", condition_value = 0.005, condition_step=3):
        self.method = method
        self.metric_value = 0
        if method == "earlystopping":
            self.condition_value = condition_value
            self.condition_step = condition_step
            self.nb_step = 0
        self.stopped = False
        self.last_increased = -1

    def stop(self) -> bool:
        """Compute the condition

        Returns:
            bool: If the stopping condition is reached return True, else return False
        """
        if self.stopped:
            return True
        if self.nb_step == self.condition_step:
            self.stopped = True
            return True
        else:
            return False

    def update(self, metric : float):
        """Update the new value of the metric and compute the number of increase steps.

        Args:
            metric (float): value of the metric
        """
        if metric - self.metric_value < self.condition_value:
            self.nb_step += 1
        else:
            self.nb_step = 0 

        self.last_increased = metric - self.metric_value
        self.metric_value = metric

    def __str__(self) -> str:
        """Return the string representation of the condition

        Returns:
            str: string representation
        """
        if self.stopped:
            return "Condition is reached, last increase is: " + str(self.last_increased)
        else:
            return "Condition is not reached, last increase is: " + str(self.last_increased) + " number of steps: " + str(self.nb_step)
