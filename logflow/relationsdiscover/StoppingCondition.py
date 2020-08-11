# Copyright 2020 BULL SAS All rights reserved #
import datetime

class StoppingCondition:
    """Condition to stop the learning. Three conditions can be selected:
        1) Increase of the F1 value needs to be less than 0.005 during more than 3 steps to stop the learning process.
        2) A timer. If the duration of the training is longer than the timer, the training step is stopped
        3) Number of epochs. Do the learning step during a fixed number of epochs.
    Please note that the timer excludes the duration of the testing step.
    Args:
        method (str, optional): 3 options: "earlystopping", "timer", "epoch". Earlystopping uses the increase of the macro f1 value accros multiples steps, timer uses a timer, and epoch uses a nb of epoch. Defaults to "earlystopping".
        condition_value (float, optional): value of the increase. Defaults to 0.005.
        condition_step (int, optional): number of steps. Defaults to 3.
        duration (int, optional): duration of the learning step in seconde. Defaults to 60.
        condition_epoch (int, optional): number of epochs to be done. Defaults to 3.
    """
    def __init__(self, method="earlystopping", condition_value=0.005, condition_step=3, duration=60, condition_epoch=3):
        self.method = method
        self.metric_value = 0
        if self.method == "earlystopping":
            self.condition_value = condition_value
            self.condition_step = condition_step
            self.nb_step = 0
        elif self.method == "timer":
            self.start = datetime.datetime.now()
            self.end = self.start + datetime.timedelta(seconds=duration)
        elif self.method == "epoch":
            self.nb_epoch = 0
            self.condition_epoch = condition_epoch
        self.stopped = False
        self.last_increased = -1

    def stop(self) -> bool:
        """Compute the condition

        Returns:
            bool: If the stopping condition is reached return True, else return False
        """
        if self.stopped:
            return True
        if self.method == "earlystopping":
            if self.nb_step == self.condition_step:
                self.stopped = True
                return True
            else:
                return False
        elif self.method == "timer":
            if datetime.datetime.now() > self.end:
                self.stopped = True
                return True
            else:
                return False
        elif self.method == "epoch":
            if self.nb_epoch == self.condition_epoch:
                self.stopped = True
                return True
            else:
                return False

    def update(self, metric=0.1):
        """Update the new value of the metric and compute the number of increase steps.

        Args:
            metric (optional, float): value of the metric. Should only be used with the earlystopping method.
        """
        if self.method == "earlystopping":
            if metric - self.metric_value < self.condition_value:
                self.nb_step += 1
            else:
                self.nb_step = 0 

            self.last_increased = metric - self.metric_value
            self.metric_value = metric
        elif self.method == "epoch":
            self.nb_epoch += 1

    def __str__(self) -> str:
        """Return the string representation of the condition

        Returns:
            str: string representation
        """
        if self.method == "earlystopping":
            if self.stopped:
                return "Condition is reached, last increase is: " + str(self.last_increased)
            else:
                return "Condition is not reached, last increase is: " + str(self.last_increased) + " number of steps: " + str(self.nb_step)
        elif self.method == "timer":
            if self.stopped:
                return "Condition is reached, expected end: " + str(self.end) + " now: " + str(datetime.datetime.now())
            else:
                return "Condition is not reached, expected end: " + str(self.end) + " remaining: " + str(self.end - datetime.datetime.now()) + " now: " + str(datetime.datetime.now())
        elif self.method == "epoch":
            if self.stopped:
                return "Condition is reached, epoch is : " + str(self.nb_epoch) + " end at: " + str(self.condition_epoch)
            else:
                return "Condition is not reached, epoch is : " + str(self.nb_epoch) + " end at: " + str(self.condition_epoch)