"""
Authors: Ali Mokhtari
Created on Dec. 22, 2020.

Description:


"""
import numpy as np


class RandomSample:

    def __init__(self, start_time, end_time, no_of_tasks, seed=100):
        self.start_time = start_time
        self.end_time = end_time
        self.no_of_tasks = no_of_tasks
        self.seed = seed

    def generate(self, pattern):

        self.pattern = pattern
        np.random.seed(self.seed)
        if self.pattern == 'uniform':
            distribution = self.uniform()

        elif self.pattern == 'normal':
            distribution = self.normal()

        elif self.pattern == 'exponential':
            distribution = self.exponential()

        elif self.pattern == 'spiky':
            distribution = self.spiky()

        return distribution

    def uniform(self):
        distribution = np.random.uniform(self.start_time, self.end_time,
                                         self.no_of_tasks)
        distribution = [round(x, 3) for x in distribution]

        return distribution

    def normal(self):
        mu = (self.start_time + self.end_time) / 2.0
        sigma = (self.end_time - self.start_time) / 6.0

        distribution = np.random.normal(mu, sigma, self.no_of_tasks)
        distribution[distribution > self.end_time] = self.end_time
        distribution[distribution < self.start_time] = self.start_time
        distribution = [round(x, 3) for x in distribution]

        return distribution

    def exponential(self):

        beta = (self.end_time - self.start_time) / self.no_of_tasks
        interarrival = np.random.exponential(
            beta, self.no_of_tasks)
        distribution = self.start_time + np.cumsum(interarrival)
        distribution = [round(x, 3) for x in distribution]

        return distribution
