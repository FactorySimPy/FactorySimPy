# @title Sink
from factorysimpy.nodes.node import Node
import simpy

from factorysimpy.utils.utils import get_edge_selector
class Sink(Node):
    """
    

    A Sink is a terminal node that collects flow items at the end. Once an item enters the
    Sink, it is considered to have exited the system and cannot be
    retrieved or processed further
    This sink can have multiple input edges and no output edges.
   


    

    Raises :
        AssertionError: If the sink does not have at least 1 input edge or has an output edge.  
    """

    def __init__(self, env, id,in_edges=None,  node_setup_time=0):
        
          super().__init__( env, id, in_edges, None,   node_setup_time)
          self.state = "COLLECTING_STATE"
          self.in_edge_events=[]
          self.stats={"num_item_received": 0, "last_state_change_time":0.0, "total_time_spent_in_states":{"COLLECTING_STATE":0.0}, "total_cycle_time":0.0}
          self.item_in_process = None
          self.buffertime=0
          # Start behavior process
          self.env.process(self.behaviour())

    def reset(self):
        self.state = "COLLECTING_STATE"
            
    def update_final_state_time(self, simulation_end_time):
        duration = simulation_end_time- self.stats["last_state_change_time"]
        
        #checking threadstates and updating the machine state
        if self.state is not None and self.stats["last_state_change_time"] is not None:
            duration = simulation_end_time- self.stats["last_state_change_time"]
            self.stats["total_time_spent_in_states"][self.state] = (
                self.stats["total_time_spent_in_states"].get(self.state, 0.0) + duration
            )
           
         

    def add_out_edges(self, edge):
          raise ValueError("Source does not have out_edges. Cannot add any.")

          

      

    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []

        if len(self.in_edges) >= 1:
            raise ValueError(f"Sink '{self.id}' already has 1 in_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Sink '{self.id}' in_edges.")

    


    def behaviour(self):

      assert self.in_edges is not None and len(self.in_edges) >= 1, f"Sink '{self.id}' must have atleast 1 in_edge."
      assert self.out_edges is None , f"Sink '{self.id}' must not have an out_edge."

      self.reset()
      while True:
        #yield self.env.timeout(1)
        #print("sink")

        self.update_state("COLLECTING_STATE",self.env.now)   
        

        

        self.in_edge_events = [edge.inbuiltstore.reserve_get() for edge in self.in_edges]
        
        triggered_in_edge_events = self.env.any_of(self.in_edge_events)
        yield triggered_in_edge_events  # Wait for any in_edge to be available



        self.chosen_event = next((event for event in self.in_edge_events if event.triggered), None)
        if self.chosen_event is None:
            raise ValueError(f"{self.id} - No in_edge available for processing!")
        
        self.in_edge_events.remove(self.chosen_event)  # Remove the chosen event from the list
        #cancelling already triggered out_edge events
        for event in self.in_edge_events:
        #     if event.triggered:
               event.resourcename.reserve_get_cancel(event)
        
        
        
        item = self.chosen_event.resourcename.get(self.chosen_event)  # Get the item from the chosen in_edge
        if isinstance(item, simpy.events.Process):
            self.item_in_process = item
            yield self.item_in_process # Wait for the item to be available
        else:
            self.item_in_process = item

      
        
        if self.item_in_process is None:
            raise RuntimeError (f"{self.id} - No item available for processing!")
        
       
        
        
                
        self.stats["num_item_received"] += 1
        self.stats["total_cycle_time"] += self.env.now - self.item_in_process.timestamp_creation
        
        #print("fromsink", self.env.now - item.timestamp_creation)
        #print(self.item_in_process.timestamp_node_entry)
        #self.buffertime+=(self.item_in_process.timestamp_node_entry- self.item_in_process.timestamp_creation)
        #print(f"buffertime={item.timestamp_node_entry- item.timestamp_creation}")
        print(f"T={self.env.now:.2f}: {self.id } got an {self.item_in_process} ")
        #print(f"item{self.item_in_process.id} conveyortime {self.item_in_process.conveyor_entry_time} and {self.item_in_process.conveyor_exit_time} - time spend in conveyor {self.item_in_process.conveyor_exit_time - self.item_in_process.conveyor_entry_time if self.item_in_process.conveyor_exit_time and self.item_in_process.conveyor_entry_time else 'N/A'}")
        self.item_in_process=None
       
        
