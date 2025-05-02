#%%writefile PriorityReqStore.py
# @title  PriorityReqStore
# @title  PriorityReqStore
import simpy,random
from simpy.resources.store import Store, StorePut
from simpy.resources.base import Get, Put
from simpy.core import BoundClass

class SortedQueue(list):
    """Queue for sorting events by their :attr:`~PriorityRequest.key`
    attribute.

    """

    def __init__(self, maxlen = None):
        super().__init__()
        self.maxlen = maxlen
        """Maximum length of the queue."""

    def append(self, item) -> None:
        """Sort *item* into the queue.

        Raise a :exc:`RuntimeError` if the queue is full.

        """
        if self.maxlen is not None and len(self) >= self.maxlen:
            raise RuntimeError('Cannot append event. Queue is full.')

        super().append(item)
        super().sort(key=lambda e: e.key)



class PriorityGet(Get):

     def __init__(self, resource, priority=0, ):
        self.priority = priority
        """The priority of this request. A smaller number means higher
        priority."""


        self.time = resource._env.now
        """The time at which the request was made."""

        self.key = (self.priority, self.time)
        #print("Resource is ", resource)


        super().__init__(resource)

class PriorityPut(Put):

     def __init__(self, resource, item, priority=0, ):
        self.priority = priority
        """The priority of this request. A smaller number means higher
        priority."""


        self.time = resource._env.now
        """The time at which the request was made."""

        self.key = (self.priority, self.time)
        self.item = item
        #print("Resource is ", resource)


        super().__init__(resource)



class PriorityReqStore(Store):
    """
        This is a class derived from SimPy's Store class and has extra capabilities
        that makes it a priority-based store for put and get.

        Processes can pass a priority as argument in the put and get request. Request with lower
        values of priority yields first among all get(or put) requests. If two requests with same 
        priority are placed from two processes then FIFO order is followed to yield the requests.

        """

    GetQueue = SortedQueue

    PutQueue = SortedQueue


    def __init__(self, env, capacity=1):
        super().__init__(env, capacity)

    get = BoundClass(PriorityGet)
    """yields a get request with the given *priority*."""

    put= BoundClass(PriorityPut)
    """yields a put request with the given *priority*"""
