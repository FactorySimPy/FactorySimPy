# @title Sink
from factorysimpy.nodes.node import Node
import simpy

from factorysimpy.utils.utils import get_index_selector
class Sink(Node):
    """
    

    A Sink is a terminal node that collects flow items at the end. Once an item enters the
    Sink, it is considered to have exited the system and cannot be
    retrieved or processed further
    This sink can have multiple input edges and no output edges.
   


    

    Raises :
        AssertionError: If the sink does not have at least 1 input edge or has an output edge.  
    """

    def __init__(self, env, id,in_edges=None,  node_setup_time=0, in_edge_selection="FIRST_AVAILABLE"):
        
          super().__init__( env, id, in_edges, None,   node_setup_time)
          self.state = "None"
       
          self.in_edge_events=[]
          self.in_edge_selection = in_edge_selection
          
          self.stats={"num_item_received": 0, "total_time_spent_in_state":{"COLLECTING_STATE":0.0}, "total_cycle_time":0.0}
          self.item_in_process = None

          # Start behavior process
          self.env.process(self.behaviour())

          # Start store level check process


          # Logging the creation and initial state of the source
          #logger.info(f"At time: {self.env.now:.2f}: Sink created: {self.id}")
          #logger.info(f"At time: {self.env.now:.2f}: Initial State: {self.state}")
    def reset(self):
            

            # Initialize in_edge_selection
            if isinstance(self.in_edge_selection, int):
               assert self.in_edge_selection >= 0, "in_edge_selection must be a non-negative integer."
               assert self.in_edge_selection < len(self.in_edges), f"in_edge_selection must be less than the number of in_edges ({len(self.in_edges)})"
               self.in_edge_selection = self.in_edge_selection
            
            elif self.in_edge_selection == "FIRST_AVAILABLE":
                # If in_edge_selection is "FIRST_AVAILABLE", we process it inside class
                self.in_edge_selection = self.in_edge_selection

            elif isinstance(self.in_edge_selection, str):  
                self.in_edge_selection = get_index_selector(self.in_edge_selection, self, self.env, "IN")
                

            elif callable(self.in_edge_selection):
                # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
                self.in_edge_selection = self.in_edge_selection
            elif hasattr(self.in_edge_selection, '__next__'):
                # It's a generator
                self.in_edge_selection = self.in_edge_selection
            
            else:
                raise ValueError("in_edge_selection must be a None, string or a callable (function/generator)")
            
           
            
            

            
            if self.in_edge_selection is None:
                raise ValueError("in_edge_selection should not be None")
         

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
        
    def _get_in_edge_index(self):
        
      
        
        
        #self.out_edge_selection = get_index_selector(self.out_edge_selection, self, self.env, edge_type="OUT")
        if isinstance(self.in_edge_selection, int):
            return self.in_edge_selection
        
        elif hasattr(self.in_edge_selection, '__next__'):
            # It's a generator
            val = next(self.in_edge_selection)
            
            return val
        elif callable(self.in_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.in_edge_selection(self, self.env)
            
            return val
       
        else:
            raise ValueError("in_edge_selection must be a generator or a callable.")  

    
    def _pull_item(self, in_edge):
        """
        It pulls an item from the specified in_edge and assigns it to the worker for processing.
        Args:
            i (int): Index of the worker that will process the item.
            in_edge (Edge Object): The edge from which the item will be pulled.

        """
        if in_edge.__class__.__name__ == "ConveyorBelt":
                get_token = in_edge.reserve_get()
                gtoken = yield get_token
                self.item_in_process=yield in_edge.get(gtoken)
                self.item_in_process.update_node_event(self.id, self.env, "entry")
              
                if self.item_in_process:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process.id} from {in_edge.id}  ")
                
        elif in_edge.__class__.__name__ == "Buffer":
                outstore = in_edge.inbuiltstore
                get_token = outstore.reserve_get()
                yield get_token
                self.item_in_process =outstore.get(get_token)
                self.item_in_process.update_node_event(self.id, self.env, "entry")
                if self.item_in_process:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process.id} from {in_edge.id} ")
        else:
                raise ValueError(f"Unsupported edge type: {in_edge.__class__.__name__}")



    def behaviour(self):

      #assert self.in_edges is not None and len(self.in_edges) >= 1, f"Sink '{self.id}' must have atleast 1 in_edge."
      assert self.out_edges is None , f"Sink '{self.id}' must not have an out_edge."
      self.reset()
      while True:
        #yield self.env.timeout(1)
        #print("sink")

        #self.update_state("COLLECTING_STATE",self.env.now)
        
        if self.in_edge_selection == "FIRST_AVAILABLE":
            
            self.in_edge_events = [edge.reserve_get() if edge.__class__.__name__ == "ConveyorBelt" else edge.inbuiltstore.reserve_get() for edge in self.in_edges]
            triggered_in_edge_events = self.env.any_of(self.in_edge_events)
            yield triggered_in_edge_events  # Wait for any in_edge to be available



            self.chosen_event = next((event for event in self.in_edge_events if event.triggered), None)
            if self.chosen_event is None:
                raise ValueError(f"{self.id} - No in_edge available for processing!")
            
            self.in_edge_events.remove(self.chosen_event)  # Remove the chosen event from the list
            #cancelling already triggered out_edge events
            for event in self.in_edge_events:
                if event.triggered:
                    event.resourcename.reserve_get_cancel(event)
            
            
            item = self.chosen_event.resourcename.get(self.chosen_event)  # Get the item from the chosen in_edge
            if isinstance(item, simpy.events.Process):
                self.item_in_process = item
                yield self.item_in_process # Wait for the item to be available
            else:
                self.item_in_process = item

        else:
            in_edge_index = self._get_in_edge_index()
            if in_edge_index is None:
                raise ValueError(f"{self.id} - No in_edge available for processing!")
            if in_edge_index < 0 or in_edge_index >= len(self.in_edges):
                raise IndexError(f"{self.id} - Invalid edge index {in_edge_index} for in_edges.")
            in_edge_to_get = self.in_edges[in_edge_index]
            
            yield self.env.process(self._pull_item( in_edge_to_get))
            
        
        if self.item_in_process is None:
            raise ValueError(f"{self.id} - No item pulled from in_edge {in_edge_to_get.id}!")
        
       
        
        
                
        self.stats["num_item_received"] += 1
        self.stats["total_cycle_time"] += self.env.now - self.item_in_process.timestamp_creation
        self.item_in_process=None
        #print("fromsink", self.env.now - item.timestamp_creation)
        #print(f"T={self.env.now:.2f}: {self.id } is got an {item} ")
       
        
