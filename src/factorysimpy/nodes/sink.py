# @title Sink
from Node import Node
from Buffer import Buffer
class Sink(Node):
  def __init__(self, env, name,in_edges, work_capacity=0, store_capacity=10, delay=(1, 3)):
        super().__init__( env, name,  work_capacity, store_capacity, delay)
        self.state = "Idle"
        self.store_level_low = self.env.event()  # Event triggered when store is empty

        # Start behavior process
        self.env.process(self.behaviour())
        # Start store level check process


        # Logging the creation and initial state of the source
        #logger.info(f"At time: {self.env.now:.2f}: Sink created: {self.name}")
        #logger.info(f"At time: {self.env.now:.2f}: Initial State: {self.state}")






  def behaviour(self):
    while True:
      #yield self.env.timeout(1)
      print("sink")
      item_token =  self.in_edges[0].inbuiltstore.reserve_get()
      print(f"Time = {self.env.now:.2f}{self.name } is going to yield an from {self.in_edges[0].name}")
      yield item_token
      item = self.in_edges[0].inbuiltstore.get(item_token)
      print(f"Time = {self.env.now:.2f}{self.name } is getting an {item} from {self.in_edges[0].name}")
      #logger.info(f"At time:{self.env.now : .2f}: {self.name} received item: {item.name}")
      #self.store.put(item)
