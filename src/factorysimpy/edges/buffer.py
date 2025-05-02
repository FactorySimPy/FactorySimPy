# @title buffer
import simpy
from Edge import Edge
from ReservablePriorityReqStore import ReservablePriorityReqStore  # Import your class
class Buffer(Edge):
  def __init__(self, env, name, store_capacity=10, delay=0):
        super().__init__( env, name,)
        self.env = env
        self.store_capacity =  store_capacity
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=self.store_capacity)
        self.state = "Idle"
        #self.behavior =  self.env.process(self.behaviour())

  def behaviour(self):
    while True:
      if self.inbuiltstore.items :
        state = "idle"
      else:
        state = "notempty"


