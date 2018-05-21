import torch
from abc import abstractmethod
from .base import BaseMeter
from .aggregators.batch import Average

class BatchMeter(BaseMeter):
    INVALID_INPUT_TYPE_MESSAGE = 'Expected types (Tensor, LongTensor) as inputs'

    def __init__(self, aggregator=None):
        """ Constructor

        Arguments:
            size_average (bool): Average of batch size
        """
        self.aggregator = aggregator

        if self.aggregator is None:
            self.aggregator = Average()

        self.reset()

    def reset(self):
        self.result = self.aggregator.init()

    @abstractmethod
    def _get_result(self, *xs):
        pass

    def check_tensors(self, *xs):
        pass

    def measure(self, *xs):
        self.check_tensors(*xs)
        self.result = self.aggregator.combine(self.result,
                                              self._get_result(*xs))

    def value(self):
        return self.aggregator.final_value(self.result)