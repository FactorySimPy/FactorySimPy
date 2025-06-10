import simpy
from factorysimpy.nodes.node import Node
from factorysimpy.utils.utils import get_index_selector

class Joint(Node):
    """
    Joint class representing a processing node in a factory simulation.
    Inherits from the Node class.
    This joint can have multiple input edges and a multiple output edges.
    It gets items from the input edges and packs them into a pallet or box and pushes it to the output edge.

       

    Parameters:
        state (str): Current state of the node. One of :
                
            - SETUP_STATE: Initial setup phase before Joint starts to operate.
            - IDLE_STATE: Worker threads waiting to receive items.
            - PROCESSING_STATE: Actively processing items.
            - BLOCKED_STATE: When all the worker threads are waiting to push the processed item but the out going edge is full.
        
        
        work_capacity (int): Maximum number of items that can be processed simultaneously.
        blocking (bool): If True, the source waits until it can put an item into the out edge.
        processing_delay (None, int, float, Generator, Callable): Delay for processing items. Can be:
            
            - None: Used when the processing time depends on parameters of the node object (like current state of the object) or environment. 
            - int or float: Used as a constant delay.
            - Generator: A generator function yielding delay values over time.
            - Callable: A function that returns a delay (int or float).
        target_quantity_of_each_item (list): List with target quantity of each item to be combined where index correspond to the input edge.
                                            The first index corresponds to the edge that supplies pallet/box and it is always 1
        out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                            Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

            - None: None: Used when out edge selction depends on parameters of the node object (like current state of the object) or environment.   
            - str: A string that specifies the selection method.
                - "RANDOM": Selects a random out edge in the out_edges list.
                - "FIRST": Selects the first out edge in the out_edges list.
                - "LAST": Selects the last out edge in the out_edges list.
                - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
            - callable: A function that returns an edge index.
                

        Behavior:
            The joint node represents components that joints together or packs items from multiple in_edges. It can have multiple incoming edges
            and multiple outgoing edge. User can specify a list in_edges and the number of quantity that has to be packed from each of the in_edges
            as a list. The first item corresponds to the pallet used to put these packed items and the corresponding entry in the 
            `target_quantity_of_each_item` list is 1. Edge to which packed item is pushed is decided using the method specified
            in the parameter `out_edge_selection`. Joint will transition through the states- `SETUP_STATE`, `PROCESSING_STATE`, `IDLE_STATE` AND 
            `BLOCKED_STATE`. The joint has a blocking behavior if `blocking`=`True` and gets blocked when all its worker threads have processed items and the out edge is full and 
            cannot accept the item that is being pushed by the joint. It waits until the out edge becomes available to push the item. If `blocking`=`False`, 
            it will discard the item if the out edge is full and cannot accept the item that is being pushed by the joint.

        Raises:
            AssertionError: If the Joint has no input or atleast 1 output edge.
        Output performance metrics:
        The key performance metrics of the joint node is captured in `stats` attribute (dict) during a simulation run. 
            
            last_state_change_time    : Time when the state was last changed.
            num_item_processed        : Total number of items generated.
            total_time_spent_in_states: Dictionary with total time spent in each state.
                
    
    """ 
    def __init__(self, env, id,in_edges=None , out_edges=None,node_setup_time=0,target_quantity_of_each_item=[1], work_capacity=1, processing_delay=1, blocking= "False", out_edge_selction="FIRST"):
        super().__init__(env, id,in_edges=in_edges , out_edges=out_edges, node_setup_time=node_setup_time)  
        
        
        
        self.state={}
        self.work_capacity = work_capacity
        self.processing_delay = processing_delay
        self.blocking = blocking
        # list with target quantity of each item to be combined where index correspond to the input edge
        # the first index correponds to the edge that supplies pallet/box.
        self.target_quantity_of_each_item=  target_quantity_of_each_item 
        
        self.out_edge_selection = out_edge_selction

        self.in_edge_events={}

       

    
        self.in_edges = in_edges
        self.out_edges = out_edges
        
        


      
    


        # Initialize processing delay 
        if callable(processing_delay):
            self.processing_delay = processing_delay 
        elif hasattr(processing_delay, '__next__'):
            # It's a generator
            self.processing_delay = processing_delay    
        elif isinstance(processing_delay, (int, float)):
            self.processing_delay = processing_delay
        elif processing_delay is None:
            self.processing_delay = None
        else:
            raise ValueError(
                "processing_delay must be a None, int, float, generator, or callable."
            )
        
        self.env.process(self.behaviour())  # Start the machine behavior process
        

        
        
      
    def reset(self):
            

            
            
            if isinstance(self.out_edge_selection, str):  
                self.out_edge_selection = get_index_selector(self.out_edge_selection, self, self.env, "OUT")
            elif callable(self.out_edge_selection):
                # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
                self.out_edge_selection = self.out_edge_selection
            elif self.out_edge_selection is None:
                # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
                self.out_edge_selection = self.out_edge_selection
            else:
                raise ValueError("out_edge_selection must be a None, string or a callable (function/generator)")  
            
            

            if self.processing_delay is None:
                raise ValueError("Processing delay cannot be None.")
            if self.in_edge_selection is None:
                raise ValueError("in_edge_selection should not be None")
            if self.out_edge_selection is None:
                raise ValueError("out_edge_selection should not be None.")
        

    
    def _get_out_edge_index(self):
        
        #Returns the next edge index from out_edge_selection, whether it's a generator or a callable.
        event = self.env.event()
        
        #self.out_edge_selection = get_index_selector(self.out_edge_selection, self, self.env, edge_type="OUT")
        if hasattr(self.out_edge_selection, '__next__'):
            # It's a generator
            val = next(self.out_edge_selection)
            event.succeed(val)
            return event
        elif callable(self.out_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.out_edge_selection(self, self.env)
            event.succeed(val)
            return event
        elif isinstance(self.out_edge_selection, (simpy.events.Event)):
            #print("out_edge_selection is an event")
            self.env.process(self.call_out_process(self.out_edge_selection,event))
            return event
        else:
            raise ValueError("out_edge_selection must be a generator or a callable.")    
                
    def  call_out_process(self, out_edge_selection,event):
        val = yield out_edge_selection
        event.succeed(val) 

    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []
        
        if len(self.in_edges) >= 2:
            raise ValueError(f"Joint '{self.name}' already has 2 in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Joint '{self.name}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Joint '{self.name}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Joint '{self.name}' out_edges.")
        
    def _push_item(self, i, out_edge):
        """
        It picks a processed item from the store and pushes it to the specified out_edge.
        The out_edge can be a ConveyorBelt or Buffer.
        Args:
            i (int): Index of the worker processing the item.
            out_edge (Edge Object): The edge to which the item will be pushed.


        """
       
        if out_edge.__class__.__name__ == "ConveyorBelt":                 
                put_token = out_edge.reserve_put()
                pe = yield put_token
                self.item_in_process[i].update_node_event(self.id, self.env, "exit")
                
                y=out_edge.put(pe, self.item_in_process[i])
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {self.item_in_process[i].id} item into {out_edge.id}  ")
        elif out_edge.__class__.__name__ == "Buffer":
                outstore = out_edge.inbuiltstore
                put_token = outstore.reserve_put()
                yield put_token
                self.item_in_process[i].update_node_event(self.id, self.env, "exit")
                y=outstore.put(put_token, self.item_in_process[i])
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {out_edge.id}")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")
        
    def _pull_item(self,i, in_edge):
        """
        It pulls an item from the specified in_edge and assigns it to the worker for processing.
        Args:
            i (int): Index of the worker that will process the item.
            in_edge (Edge Object): The edge from which the item will be pulled.

        """
        if in_edge.__class__.__name__ == "ConveyorBelt":
                get_token = in_edge.reserve_get()
                gtoken = yield get_token
                self.item_in_process[i]=yield in_edge.get(gtoken)
                self.item_in_process[i].update_node_event(self.id, self.env, "entry")
              
                if self.item_in_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process[i].id} from {in_edge.id}  ")
                
        elif in_edge.__class__.__name__ == "Buffer":
                outstore = in_edge.inbuiltstore
                get_token = outstore.reserve_get()
                yield get_token
                self.item_in_process[i] =outstore.get(get_token)
                self.item_in_process[i].update_node_event(self.id, self.env, "entry")
                if self.item_in_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process[i].id} from {in_edge.id} ")
        else:
                raise ValueError(f"Unsupported edge type: {in_edge.__class__.__name__}")


    
    def worker(self, i):
        """Worker process that processes items by combining two items."""
        while True:
            #print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            if self.state[i] == "SETUP_STATE":
                
                print(f"T={self.env.now:.2f}: {self.id} worker{i} is in SETUP_STATE")
                yield self.env.timeout(self.node_setup_time)# always an int or float
                self.update_state(i,"IDLE_STATE", self.env.now)
            
            elif self.state[i] == "IDLE_STATE":
                 #get all items from the in_edges
                 # 1. Pull the pallet from in_edges[0]
                yield self.env.process(self._pull_item(i, self.in_edges[0]))
                if self.item_in_process[i].flow_item_type != "Pallet":
                    raise RuntimeError(f"{self.id} worker{i} - Expected a Pallet item, but got {self.item_in_process[i].type}!")
                
                pallet = self.item_in_process[i]  # Assume the pulled item is a Pallet instance

                # 2. Pull required items from other in_edges and add to pallet
                for edge_idx in range(1, len(self.in_edges)):
                    qty = self.target_quantity_of_each_item[edge_idx]
                    for _ in range(qty):
                        yield self.env.process(self._pull_item(i, self.in_edges[edge_idx]))
                        item = self.item_in_process[i]
                        pallet.add_item(item)  # Add the item to the pallet

                # 3. Assign the filled pallet to item_in_process for processing
                self.item_in_process[i] = pallet
                self.update_state(i, "PROCESSING_STATE", self.env.now)
                        
                
            elif self.state[i] == "PROCESSING_STATE":
                if self.item_in_process[i] is None:
                    raise RuntimeError(f"{self.id} worker{i} - No item to process!")
                next_processing_time = self.get_delay(self.processing_delay)
                if not isinstance(next_processing_time, (int, float)):
                    raise AssertionError("processing_delay returns an valid value. It should be int or float")
                yield self.env.timeout(next_processing_time)
                self.stats["num_item_processed"] += 1
                print(f"T={self.env.now:.2f}: {self.id} worker{i} processed item: {self.item_in_process[i].id}")
                out_edge_index_to_put_event = self._get_out_edge_index()
                out_edge_index_to_put = yield out_edge_index_to_put_event
                outedge_to_put = self.out_edges[out_edge_index_to_put]
                self.update_state(i,"BLOCKED_STATE", self.env.now)
                # Push the combined item to the output edge
                if self.blocking :
                    yield self.env.process(self._push_item(self.item_in_process[i], outedge_to_put))
                else:
                    # Check if the out_edge can accept the item
                    if outedge_to_put.can_put():
                        yield self.env.process(self._push_item(i, outedge_to_put))
                    else:
                        print(f"T={self.env.now:.2f}: {self.id} worker{i} is discarding item {self.item_in_process[i].id} because out_edge {outedge_to_put.id} is full.")
                        self.stats[i]["num_item_discarded"] += 1  # Decrement processed count if item is discarded
                        self.item_in_process[i].set_destruction(self.id, self.env)
                       
                self.update_state(i,"IDLE_STATE", self.env.now)
                self.item_in_process[i] = None  # Clear the processed item
                 # process items and put in inbuiltstore. 
                 # Pull_items will take the items and push it to next component.
    def behaviour(self):
        """Combiner behavior that creates workers based on the effective capacity."""
        self.reset()  # Reset the joint to ensure proper initialization


        assert self.in_edges is not None and len(self.in_edges) == 2, f"Joint '{self.name}' must have exactly 2 in_edges."
        assert self.out_edges is not None and len(self.out_edges) == 1, f"Joint '{self.name}' must have exactly 1 out_edge."
        assert len(self.target_quantity_of_each_item) == len(self.in_edges), \
            f"Joint '{self.name}' target_quantity_of_each_item must match the number of in_edges."
        self.state[i+1] = "SETUP_STATE" # Initialize state for each worker
        self.item_in_process[i+1] = None  # Initialize item to process for each worker
        
        # Initialize stats for each worker
        self.stats[i+1] = {
                    "last_state_change_time": None,
                    "num_item_processed": 0,
                    "num_item_discarded": 0,
                    "total_time_spent_in_states":{"SETUP_STATE": 0.0,"IDLE_STATE": 0.0, "PROCESSING_STATE": 0.0, "BLOCKED_STATE": 0.0}
                }
        
        for i in range(self.work_capacity):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay
