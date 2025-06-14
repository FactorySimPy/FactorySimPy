# Machine m input and 1 output without using cancel
import simpy
from factorysimpy.nodes.node import Node
from factorysimpy.utils.utils import get_edge_selector



class Machine(Node):
    """
        Machine represents a processing node in a factory simulation.
        This Machine can have multiple input edges and  output edges.

        Parameters:
            state (str): Current state of the machine node. One of :
                   
                - SETUP_STATE: Initial setup phase before machine starts to operate.
                - IDLE_STATE: Worker threads waiting to receive items.
                - PROCESSING_STATE: Actively processing items.
                - BLOCKED_STATE: When all the worker threads are waiting to push the processed item but the out going edge is full.
           
            blocking (bool): If True, the source waits until it can put an item into the out edge. If False, it discards the item if the out edge is full and cannot accept the item that is being pushed by the machine.
            work_capacity (int): Maximum no. of processing that can be performed simultaneously.1  worker thread can process one item.
            processing_delay (None, int, float, Generator, Callable): Delay for processing items. Can be:
                
                - None: Used when the processing time depends on parameters of the node object (like current state of the object) or environment. 
                - int or float: Used as a constant delay.
                - Generator: A generator function yielding delay values over time.
                - Callable: A function that returns a delay (int or float).
            in_edge_selection (None or str or callable): Criterion or function for selecting the edge.
                                              Options include "RANDOM", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when edge selction depends on parameters of the node object (like current state of the object) or environment. 
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random edge.
                    - "ROUND_ROBIN": Selects edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can give an item.
                - callable: A function that returns an edge index.
            out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when out edge selction depends on parameters of the node object (like current state of the object) or environment.   
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random out edge in the out_edges list.
                    - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
                - callable: A function that returns an edge index.
            

        Behavior:
            The machine node represents components that process or modify the items that flow in the simulation model. It can have multiple incoming edges
            and multiple outgoing edge. Edge from which the item comes in and the edge to which processed item is pushed is decided using the method specified
            in the parameter `in_edge_selection` and `out_edge_selection`. Machine will transition through the states- `SETUP_STATE`, `PROCESSING_STATE`, `IDLE_STATE` and 
            `BLOCKED_STATE`. The machine has a blocking behavior if `blocking`=`True` and gets blocked when all its worker threads have processed items and the out edge is full and 
            cannot accept the item that is being pushed by the machine and waits until the out edge can accept the item. If `blocking`=`False`, the machine will 
            discard the item if the out edge is full and cannot accept the item that is being pushed by the machine.


        Raises:
            AssertionError: If the Machine has no input or output edges.
        Output performance metrics:
        The key performance metrics of the Machine node is captured in `stats` attribute (dict) during a simulation run. 
            
            last_state_change_time    : Time when the state was last changed.
            num_item_processed        : Total number of items generated.
            num_item_discarded        : Total number of items discarded.
            total_time_spent_in_states: Dictionary with total time spent in each state.
                
    """

    def __init__(self, env, id, in_edges=None, out_edges=None,node_setup_time=0, work_capacity=1,processing_delay=0,blocking=False,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE"):
        super().__init__(env, id,in_edges, out_edges, node_setup_time)
        
        self.state = "SETUP_STATE"  # Initial state of the machine
        self.work_capacity = work_capacity
        self.in_edge_selection = in_edge_selection
        self.out_edge_selection = out_edge_selection
        self.blocking = blocking
        self.per_thread_total_time_in_blocked_state = 0.0
        self.per_thread_total_time_in_processing_state = 0.0
        self.worker_process_map = {}
        
        self.item_in_process= None
        self.num_workers = 0  # Number of worker threads currently processing
        self.time_last_occupancy_change = 0  # Time when the occupancy was last changed
        self.worker_thread = simpy.Resource(env, capacity=self.work_capacity)  # Resource for worker threads
        self.time_per_work_occupancy = [0.0 for _ in range(work_capacity+1)]  # Time spent by each worker thread
        self.stats={"total_time_spent_in_states": {"SETUP_STATE": 0.0, "IDLE_STATE":0.0, "PROCESSING_STATE": 0.0,"BLOCKED_STATE":0.0 },
                    "last_state_change_time": None, "num_item_processed": 0, "num_item_discarded": 0,}
       
     
        

        

        # Initialize processing delay 
        # If processing_delay is a generator, callable, int, float or None, it is accepted.
        
        if callable(processing_delay) or hasattr(processing_delay, '__next__') or isinstance(processing_delay, (int, float)) or processing_delay is None:
            self.processing_delay = processing_delay
    
        else:
            raise ValueError(
                "processing_delay must be None, int, float, generator, or callable."
            )
        
        self.env.process(self.behaviour())  # Start the machine behavior process
        

        
        
      
    def reset(self):
            
            self.state = "SETUP_STATE"  # Reset state to SETUP_STATE
            
            # Initialize in_edge_selection
            if isinstance(self.in_edge_selection, int):
                assert 0 <= self.in_edge_selection < len(self.in_edges), f"in_edge_selection must be in range 0 to {len(self.in_edges)-1}"
            # Already an int, use as is
            elif self.in_edge_selection == "FIRST_AVAILABLE":
                # Special handling in class logic, use as is
                pass
            elif isinstance(self.in_edge_selection, str):
                self.in_edge_selection = get_edge_selector(self.in_edge_selection, self, self.env, "IN")
            elif callable(self.in_edge_selection) or hasattr(self.in_edge_selection, '__next__'):
                # Use as is (function or generator)
                pass
            else:
                raise ValueError("in_edge_selection must be None, string, int, or a callable (function/generator)")
            
            # Initialize out_edge_selection
            if isinstance(self.out_edge_selection, int):
                assert 0 <= self.out_edge_selection < len(self.out_edges), f"out_edge_selection must be in range 0 to {len(self.out_edges)-1}"
                # Already an int, use as is
            elif self.out_edge_selection == "FIRST_AVAILABLE":
                # Special handling in class logic, use as is
                pass
            elif isinstance(self.out_edge_selection, str):
                self.out_edge_selection = get_edge_selector(self.out_edge_selection, self, self.env, "OUT")
            elif callable(self.out_edge_selection) or hasattr(self.out_edge_selection, '__next__'):
                # Use as is (function or generator)
                pass
            else:
                raise ValueError("out_edge_selection must be None, string, int, or a callable (function/generator)")
 

            

            if self.processing_delay is None:
                raise ValueError("Processing delay cannot be None.")
            if self.in_edge_selection is None:
                raise ValueError("in_edge_selection should not be None")
            if self.out_edge_selection is None:
                raise ValueError("out_edge_selection should not be None.")
        

    
        
 
    def update_state(self, new_state: str, current_time: float):
        """
        Update node state and track the time spent in the previous state.
        
        Args:
            i (int): The index of the worker thread to update the state for.
            new_state (str): The new state to transition to. Must be one of "SETUP_STATE", "GENERATING_STATE", "BLOCKED_STATE".
            current_time (float): The current simulation time.

        """
        
        if self.state is not None and self.stats["last_state_change_time"] is not None:
            elapsed = current_time - self.stats["last_state_change_time"]

            self.stats["total_time_spent_in_states"][self.state] = (
                self.stats["total_time_spent_in_states"].get(self.state, 0.0) + elapsed
            )
        self.state = new_state
        self.stats["last_state_change_time"] = current_time

        
    


    def add_in_edges(self, edge):
        """
        Adds an in_edge to the node. Raises an error if the edge already exists in the in_edges list.
        
        Args:
            edge (Edge Object) : The edge to be added as an in_edge.
            """
        if self.in_edges is None:
            self.in_edges = []
        
        # if len(self.in_edges) >= self.num_in_edges:
        #     raise ValueError(f"Machine'{self.id}' already has {self.num_in_edges} in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' in_edges.")

    def add_out_edges(self, edge):
        """
        Adds an out_edge to the node. Raises an error if the edge already exists in the out_edges list.
        
        Args:
            edge (Edge Object) : The edge to be added as an out_edge.
        """
        if self.out_edges is None:
            self.out_edges = []

        # if len(self.out_edges) >= 1:
        #     raise ValueError(f"Machine '{self.id}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' out_edges.")
        
    def _get_out_edge_index(self):
        
         
   
        if isinstance(self.out_edge_selection, int):
            val = self.out_edge_selection
        elif hasattr(self.out_edge_selection, '__next__'):
            # It's a generator
            val = next(self.out_edge_selection)          
        elif callable(self.out_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.out_edge_selection(self, self.env)       
        else:
            raise ValueError("out_edge_selection must be a generator or a callable.")   
        assert 0<= val < len(self.in_edges), f"{self.id} - Invalid edge index. {val} is not in range. Range must be between {0} and  {len(self.out_edges)-1} for out_edges." 
        return val   
 

    def _get_in_edge_index(self):
         
        if isinstance(self.in_edge_selection, int):
            val = self.in_edge_selection
        elif hasattr(self.in_edge_selection, '__next__'):
            # It's a generator
            val = next(self.in_edge_selection)    
        elif callable(self.in_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.in_edge_selection(self, self.env)   
        else:
            raise ValueError("in_edge_selection must be a generator or a callable.")    
        assert 0<=val < len(self.in_edges), f"{self.id} - Invalid edge index. {val} is not in range. Range must be between {0} and  {len(self.in_edges)-1} for in_edges."
        return val
                  
   

    def _push_item(self, item_to_push, out_edge):
        """
        It picks a processed item from the store and pushes it to the specified out_edge.
        The out_edge can be a ConveyorBelt or Buffer.
        Args:
            item_to_push (BaseFlowItem Object): Item to be pushed.
            out_edge (Edge Object): The edge to which the item will be pushed.


        """
       
        if out_edge.__class__.__name__ == "ConveyorBelt":                 
                put_token = out_edge.reserve_put()
                pe = yield put_token
                item_to_push.update_node_event(self.id, self.env, "exit")
                
                y=out_edge.put(pe, item_to_push)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {item_to_push.id} item into {out_edge.id}  ")
        elif out_edge.__class__.__name__ == "Buffer":
                outstore = out_edge.inbuiltstore
                put_token = outstore.reserve_put()
                yield put_token
                item_to_push.update_node_event(self.id, self.env, "exit")
                y=outstore.put(put_token, item_to_push)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {out_edge.id}")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")
        
    def _pull_item(self, in_edge):
        """
        It pulls an item from the specified in_edge and assigns it to the worker for processing.
        Args:
           
            in_edge (Edge Object): The edge from which the item will be pulled.

        """

        if in_edge.__class__.__name__ == "ConveyorBelt":
               
                get_token = in_edge.reserve_get()
                
                gtoken = yield get_token
                
                pulled_item = yield in_edge.get(gtoken)
                pulled_item.update_node_event(self.id, self.env, "entry")
                              
                if pulled_item is not None:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {pulled_item.id} from {in_edge.id} ")
                    self.item_in_process= pulled_item  # Assign the pulled item to the item_in_process attribute
                    
                else:
                    raise ValueError(f"{self.id} - No item pulled from in_edge {in_edge.id}!")
                
        elif in_edge.__class__.__name__ == "Buffer":
                outstore = in_edge.inbuiltstore
                get_token = outstore.reserve_get()
                yield get_token
                pulled_item =outstore.get(get_token)
                pulled_item.update_node_event(self.id, self.env, "entry")
                if pulled_item is not None:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {pulled_item.id} from {in_edge.id} ")
                    self.item_in_process= pulled_item  # Assign the pulled item to the item_in_process attribute
                else:
                    raise ValueError(f"T={self.env.now:.2f}: {self.id} - No item pulled from in_edge {in_edge.id}!")
        else:
                raise ValueError(f"Unsupported edge type: {in_edge.__class__.__name__}")
              
            
    

    def _update_avg_time_spent_in_processing(self, processing_delay):
        """
        Update the average time spent in processing based on the processing delay and work capacity.
        
        Args:
            processing_delay (int or float): The delay for processing items.
        """
        if not isinstance(processing_delay, (int, float)):
            raise ValueError("processing_delay must be an int or float.")
        
        if self.work_capacity <= 0:
            raise ValueError("work_capacity must be greater than 0.")
        time_spent_in_processing = self.per_thread_total_time_in_processing_state*self.work_capacity 
        avg_time_spent_in_processing = (time_spent_in_processing + processing_delay) / self.work_capacity #to calculate the average time spent in processing per worker
        self.per_thread_total_time_in_processing_state = avg_time_spent_in_processing
        
       
    def _update_avg_time_spent_in_blocked(self, blocked_delay):
        """
        Update the average time spent in blocked state based on the blocked delay and work capacity.
        
        Args:
            blocked_delay (int or float): The delay for being blocked.
        """
        if not isinstance(blocked_delay, (int, float)):
            raise ValueError("blocked_delay must be an int or float.")
        
        if self.work_capacity <= 0:
            raise ValueError("work_capacity must be greater than 0.")
        
        time_spent_in_blocked = self.per_thread_total_time_in_blocked_state*self.work_capacity 
        avg_time_spent_in_blocked = (time_spent_in_blocked + blocked_delay) / self.work_capacity
        self.per_thread_total_time_in_blocked_state = avg_time_spent_in_blocked

    def _update_worker_occupancy(self, action=None):
        #print(self.num_workers)
        if self.num_workers is not None and self.time_last_occupancy_change is not None:
            if action == "ADD":
                elapsed = self.env.now - self.time_last_occupancy_change
                self.time_per_work_occupancy[self.num_workers] += elapsed
                self.num_workers += 1
                self.time_last_occupancy_change = self.env.now
            elif action == "REMOVE":
                elapsed = self.env.now - self.time_last_occupancy_change
                self.time_per_work_occupancy[self.num_workers] += elapsed
                self.num_workers -= 1
                self.time_last_occupancy_change = self.env.now
            elif action =="UPDATE":
                elapsed = self.env.now - self.time_last_occupancy_change
                if self.num_workers==len(self.worker_thread.users):
                    self.time_per_work_occupancy[self.num_workers] += elapsed
                    self.time_last_occupancy_change = self.env.now
                else:
                    raise ValueError("Cannot update worker occupancy when the number of workers is not equal to the number of users in the worker thread.") 

            else:
                raise ValueError("Invalid action. Use 'ADD' or 'REMOVE'.")

            
    
    def _count_worker_state(self):
        """
        Counts and returns the number of threads in "PROCESSING_STATE" and "BLOCKED_STATE"
        using self.worker_process_map.
    
        Returns:
            num_threads_PROCESSING (int): Number of threads in "PROCESSING_STATE"
            num_threads_BLOCKED (int): Number of threads in "BLOCKED_STATE"
        """
        if not self.worker_process_map:
            num_threads_PROCESSING = 0
            num_threads_BLOCKED = 0
        else:
            num_threads_PROCESSING = sum(
                proc["state"] == "PROCESSING_STATE" for proc in self.worker_process_map.values()
            )
            num_threads_BLOCKED = sum(
                proc["state"] == "BLOCKED_STATE" for proc in self.worker_process_map.values()
            )
    
        assert 0 <= num_threads_BLOCKED <= self.work_capacity \
            and 0 <= num_threads_PROCESSING <= self.work_capacity \
            and 0 <= num_threads_BLOCKED + num_threads_PROCESSING <= self.work_capacity, \
            f"T={self.env.now:.2f} {self.id} has more threads than work_capacity is created. num_threads_PROCESSING={num_threads_PROCESSING}, num_threads_BLOCKED={num_threads_BLOCKED}, work_capacity={self.work_capacity}"
        return num_threads_PROCESSING, num_threads_BLOCKED
          
                


    def worker(self,item,processing_delay,req_token,):
        #Worker process that processes items with resource and reserve handling."""
        
            
            #wait for processing_delay amount of time
            yield self.env.timeout(processing_delay)
            self.stats["num_item_processed"] += 1
            self._update_avg_time_spent_in_processing(processing_delay)
          
               #out_edge_selection is "FIRST_AVAILABLE"---> 
            if self.out_edge_selection == "FIRST_AVAILABLE":
                # if blocking yield reserve_put on all out_edges and take the one with min index and cancel others and push item
                if self.blocking:

                    blocking_start_time = self.env.now
                
                    self.out_edge_events = [edge.reserve_put() if edge.__class__.__name__ == "ConveyorBelt" else edge.inbuiltstore.reserve_put() for edge in self.out_edges]
                    triggered_out_edge_events = self.env.any_of(self.out_edge_events)
                    ev = yield triggered_out_edge_events  # Wait for any in_edge to be available
                    
                    for i in ev:
                        if i.triggered:
                            ev_to_process = i

                    # Find the first triggered event
                    chosen_put_event = next((event for event in self.out_edge_events if event.triggered), None)
                    edge_index = self.out_edge_events.index(chosen_put_event)
                    #self.out_edge_events.remove(chosen_put_event)  # Remove the chosen event from the list
                    if chosen_put_event is None:
                        raise ValueError(f"{self.id} - No in_edge available for processing!")
                    
                    #cancelling already triggered out_edge events
                    for event in self.out_edge_events:
                        if event.triggered:
                            event.resourcename.reserve_put_cancel(event)

                    #putting the item in the chosen out_edge
                    item.update_node_event(self.id, self.env, "exit")
                    if self.out_edges[edge_index].__class__.__name__ == "ConveyorBelt":
                        itemput = chosen_put_event.resourcename.put(ev[i], item)  # Get the item from the chosen in_edge
                    elif self.out_edges[edge_index].__class__.__name__ == "Buffer":
                        itemput = chosen_put_event.resourcename.put(chosen_put_event, item)  # Get the item from the chosen in_edge
                    else:
                        raise ValueError(f"Unsupported edge type: {self.out_edges[edge_index].__class__.__name__}")
                        #print(f"T={self.env.now:.2f}: {self.id} puts item {item.id} into {self.out_edges[edge_index].id} ")
                    if isinstance(itemput, simpy.events.Process):
                        self.item_in_process = itemput
                        yield self.item_in_process # Wait for the item to be available
                    else:
                        self.item_in_process = item

                    self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                #inot blocking, check can_put on all, if all fails, then the item is discarded
                else:
                    out_edge_index_to_put = None
                    for edge in self.out_edges:
                        if edge.can_put():
                            out_edge_to_put = edge
                            break
                    
                    if out_edge_to_put is not None:
                         blocking_start_time = self.env.now
                         yield self.env.process(self._push_item(item, out_edge_to_put))  
                         print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {out_edge_to_put.id} ")
                         self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)

                        
                    else:               
                        print(f"T={ self.env.now:.2f}: {self.id} worker is discarding item {item.id} because out_edge {edge.id} is full.")
                        self.stats["num_item_discarded"] += 1  # Decrement processed count if item is discarded


                    
                    
                

            #out_edge_selection is not "FIRST_AVAILABLE" ---> get index value and push the item if not blocking
            else:
                print(f"T={self.env.now:.2f}: {self.id} worker processed item: {item.id}")
                out_edge_index_to_put = self._get_out_edge_index()
                assert 0<=out_edge_index_to_put < len(self.out_edges), f"{self.id} - Invalid edge index. {out_edge_index_to_put} is not in range. Range must be between {0} and  {len(self.out_edges)-1} for in_edges."
                outedge_to_put = self.out_edges[out_edge_index_to_put]
                #push the item if not blocking
                if self.blocking:
                    blocking_start_time = self.env.now
                    print(f"T={self.env.now:.2f}: {self.id} worker is in BLOCKED_STATE")
                    yield self.env.process(self._push_item(item, outedge_to_put))
                    print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {out_edge_to_put.id} ")
                    self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                #check can_put and only if it succeeds push the item if not blocking
                else:
                    # Check if the out_edge can accept the item
                    if outedge_to_put.can_put():
                        blocking_start_time = self.env.now
                        yield self.env.process(self._push_item(item, outedge_to_put))
                        print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {outedge_to_put.id} ")
                        self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                    else:
                        print(f"T={self.env.now:.2f}: {self.id} worker is discarding item {item.id} because out_edge {outedge_to_put.id} is full.")
                        self.stats["num_item_discarded"] += 1
            # Release the worker thread after processing
        
            yield self.worker_thread.release(req_token)  # Release the worker thread
            #print(self.env.active_process, self.worker_process_map)
            if self.worker_process_map[self.env.active_process]:
                #print("deleting")
                del self.worker_process_map[self.env.active_process]
            self._update_worker_occupancy(action="REMOVE")  # Update worker occupancy after processing
                

 
                

    def behaviour(self):
        #Machine behavior that creates workers based on the effective capacity."""
        i=0
        self.reset()
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."

        #get edge
        #do reserve_get
        #get item from edge
        #get processing time
        #resource request
        #worker thread process

        while True:
            #print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            if self.state == "SETUP_STATE":
                
                print(f"T={self.env.now:.2f}: {self.id} is in SETUP_STATE")
                yield self.env.timeout(self.node_setup_time)# always an int or float
                self.update_state("IDLE_STATE", self.env.now)

            else:
                
                self._update_worker_occupancy(action="UPDATE")
                numthreads_PROCESSING, numthreads_BLOCKED = self._count_worker_state()
                if numthreads_PROCESSING >0:
                    self.update_state("PROCESSING_STATE", self.env.now)
                if numthreads_BLOCKED == self.work_capacity:
                    self.update_state("BLOCKED_STATE", self.env.now)
                            
                
                print(f"T={self.env.now:.2f}: {self.id} is in {self.state}, creating workers")
                # Create workers based on work_capacity
                
                #in_edge_selection is "FIRST_AVAILABLE"--->     yield in a list, select one with min. index value and cancel other and pull item
                if self.in_edge_selection == "FIRST_AVAILABLE":
                    
                    self.in_edge_events = [edge.reserve_get() if edge.__class__.__name__ == "ConveyorBelt" else edge.inbuiltstore.reserve_get() for edge in self.in_edges]
                    triggered_in_edge_events = self.env.any_of(self.in_edge_events)
                    ev= yield triggered_in_edge_events  # Wait for any in_edge to be available
                    #print(triggered_in_edge_events,)
                    
                    for i in ev:
                        if i.triggered:
                            ev_to_process = i
                    
                   



                    self.chosen_event = next((event for event in self.in_edge_events if event.triggered), None)
                    edge_index = self.in_edge_events.index(self.chosen_event)  # Get the index of the chosen event
                    print(f"T={self.env.now:.2f}: {self.id} yielded from {self.in_edges[edge_index].id} ")
                    if self.chosen_event is None:
                        raise ValueError(f"{self.id} - No in_edge available for processing!")
                    
                    self.in_edge_events.remove(self.chosen_event)  # Remove the chosen event from the list
                    #cancelling already triggered out_edge events
                    for event in self.in_edge_events:
                        if event.triggered:
                            event.resourcename.reserve_get_cancel(event)

                    #if self.edge_index[]
                    
                    if self.in_edges[edge_index].__class__.__name__ == "ConveyorBelt":
                        item = self.chosen_event.resourcename.get(ev[i])  # Get the item from the chosen in_edge
                    elif self.in_edges[edge_index].__class__.__name__ == "Buffer":
                        item = self.chosen_event.resourcename.get(self.chosen_event)  # Get the item from the chosen in_edge
                    else:
                        raise ValueError(f"Unsupported edge type: {self.in_edges[edge_index].__class__.__name__}")
                    #print(f"T={self.env.now:.2f}: {self.id} received item {item.id} from {self.in_edges[edge_index].id} ")
                    
                    if isinstance(item, simpy.events.Process):
                        
                        self.item_in_process = yield item# Wait for the item to be available
                    else:
                        self.item_in_process = item
                    self.item_in_process.update_node_event(self.id, self.env, "entry")
                #in_edge_selection is not "FIRST_AVAILABLE"---> use get_in_edge_index and pull item
                else:
                    in_edge_index = self._get_in_edge_index()
                    
                    assert 0<=in_edge_index < len(self.in_edges), f"{self.id} - Invalid edge index. {in_edge_index} is not in range. Range must be between {0} and  {len(self.in_edges)-1} for in_edges."
                    in_edge_to_get = self.in_edges[in_edge_index]
                    
                    yield self.env.process(self._pull_item( in_edge_to_get))
                    
                    print(f"T={self.env.now:.2f}: {self.id} received item {self.item_in_process.id} from {in_edge_to_get.id} ")
              
                if self.item_in_process is None:
                    raise ValueError(f"{self.id} - No item pulled from in_edge {in_edge_to_get.id}!")
                #get a worker thread
                worker_thread_req = self.worker_thread.request()  # Request a worker thread
                yield worker_thread_req
                
                #print(f"{self.env.now:.2f}--yielded {i}, {len(self.worker_thread.users)}")
                
                #update occupancy
                self._update_worker_occupancy(action="ADD")
                #get processing_time
                next_processing_time = self.get_delay(self.processing_delay)
                print(f"T={self.env.now:.2f}: {self.id} worker started processing item {self.item_in_process.id} ")
                #spawn a worker process
                proc = self.env.process(self.worker(self.item_in_process, next_processing_time, worker_thread_req))  # Start the worker process
                self.worker_process_map[proc] = {
                    "item":self.item_in_process,# Map the process to the item being processed. to be utilised by out_edge_selection from node as 
                    "state":"PROCESSING_STATE", #state of the process
                }
                #initialise item into none
                self.item_in_process=None
                #node.worker_process_map[node.env.active_process] will return the item being processed by the active process.
                

                

       
