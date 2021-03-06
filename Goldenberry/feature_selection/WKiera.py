from Goldenberry.optimization.base.GbCostFunction import GbCostFunction
from Orange.evaluation.testing import cross_validation
from Orange.evaluation.scoring import CA
from Orange.data.continuization import DomainContinuizer
import numpy as np
import time
from copy import deepcopy
import Orange
import threading as th
from orngSVM import SVMLearner

class GbWrapperCostFunction(GbCostFunction):
    """WKiera cost function."""

    def __init__(self, data, test_data, factory, solution_weight = 0.1, folds = 10, test_folds = 10, normalization = True):
        self.retest_last = True
        self.reset_statistics()
        self.factory = factory
        self.data = self._normalize(data) if normalization else data
        self.test_data = self._normalize(test_data) if normalization else test_data
        self.folds = folds
        self.test_folds = test_folds
        self.solution_weight = solution_weight
        self.var_size = len(data.domain.attributes)
        
    def execute(self, solutions, is_last = False):
        if not is_last:
           data = self.data
           folds = self.folds
        else :
            data = self.test_data
            folds = self.test_folds
            
        results = np.empty(len(solutions), dtype = float)
        threads = [None] * len(solutions)
        for idx, weight in enumerate(solutions):                    
            thread = th.Thread(target = test_solution, args = [self.factory, weight, data, results, idx, folds])
            thread.start()
            threads[idx] = thread
                    
        #sync all threads
        for thread in threads:
            thread.join()

        self._update_statistics(results)
        return results*(1 - self.solution_weight) + (1 - np.average(solutions, axis = 1)) * self.solution_weight

    def _update_statistics(self, results):
        for result in results:
            super(GbWrapperCostFunction, self)._update_statistics(result)

    def _normalize(self, data):
        dc = DomainContinuizer()
        dc.class_treatment = DomainContinuizer.Ignore
        dc.continuous_treatment = DomainContinuizer.NormalizeBySpan
        dc.multinomial_treatment = DomainContinuizer.AsNormalizedOrdinal
        newdomain = dc(data)
        return data.translate(newdomain)

def test_solution(factory, weight, data, results, idx, folds):  
    weighted_data = data.to_numpy("ac")[0] * np.concatenate((np.sqrt(weight), [1]))
    new_data = Orange.data.Table(data.domain, weighted_data)
    learner = factory()
    results[idx] = CA(cross_validation([learner], new_data, folds = folds))[0]
   