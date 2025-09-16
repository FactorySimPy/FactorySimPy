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

    def __init__(self, env, id, in_edges=None, out_edges=None,node_setup_time=0, work_capacity=1,processing_delay=0,blocking=True,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE"):
        super().__init__(env, id,in_edges, out_edges, node_setup_time)
        
        self.state = "SETUP_STATE"  # Initial state of the machine
        self.work_capacity = work_capacity
        self.in_edge_selection = in_edge_selection
        self.out_edge_selection = out_edge_selection
        self.blocking = blocking
        self.per_thread_total_time_in_blocked_state = 0.0
        self.per_thread_total_time_in_processing_state = 0.0
        
        self.worker_thread_list = []  # List to keep track of worker threads
        
        self.item_in_process= None
        self.num_workers = 0  # Number of worker threads currently processing
        self.time_last_occupancy_change = 0  # Time when the occupancy was last changed
        self.worker_thread = simpy.Resource(env, capacity=self.work_capacity)  # Resource for worker threads
        self.time_per_work_occupancy = [0.0 for _ in range(work_capacity+1)]  # Time spent by each worker thread
        self.stats={"total_time_spent_in_states": {"SETUP_STATE": 0.0, "IDLE_STATE":0.0, "PROCESSING_STATE": 0.0,"BLOCKED_STATE":0.0 },
                    "last_state_change_time": None, "num_item_processed": 0, "num_item_discarded": 0,"processing_delay":[], "in_edge_selection":[],"out_edge_selection":[]}
        
        #self.stats={"total_time_spent_in_states": {"SETUP_STATE": 0.0, "IDLE_STATE":0.0, "ATLEASE_ONE_PROCESSING_STATE": 0.0,"ATLEAST_ONE_BLOCKED_STATE":0.0, "ATLEAST_ONE_BLOCKED_STATE":0.0 },
                   # "last_state_change_time": None, "num_item_processed": 0, "num_item_discarded": 0,"processing_delay":[], "in_edge_selection":[],"out_edge_selection":[]}
       
     
        

        

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
            
            # setting the edge_selection and processing_delay parameters
            # Initialize in_edges and out_edges. This can be initialized only in the reset method, as the edges can be added later.
            
            #checking if parameter is int and if so it should belong to a valid range
            if isinstance(self.in_edge_selection, int):
                assert 0 <= self.in_edge_selection < len(self.in_edges), f"in_edge_selection must be in range 0 to {len(self.in_edges)-1}"
            
            #checking if parameter is "FIRST_AVAILABLE". If so it is handled in the class logic.
            elif self.in_edge_selection == "FIRST_AVAILABLE":
                # Special handling in class logic, use as is
                pass
            #checking if in_edge_selection is a string, then it is converted to a generator using get_edge_selector function. 
            # Names of the methods are passed as strings. These methods are inbuilt and available.
            elif isinstance(self.in_edge_selection, str):
                self.in_edge_selection = get_edge_selector(self.in_edge_selection, self, self.env, "IN")

            #checking if in_edge_selection is a callable or a generator. If so, it is used as is.
            # it is treated in get_in_edge_index method
            elif callable(self.in_edge_selection) or hasattr(self.in_edge_selection, '__next__'):
                # Use as is (function or generator)
                self.in_edge_selection = self.in_edge_selection
            # If in_edge_selection is not one of the above types, raise an error.
            else:
                raise ValueError("in_edge_selection must be None, string, int, or a callable (function/generator)")
            

            # Initialize out_edge_selection
            #checking if parameter is int and if so it should belong to a valid range
            if isinstance(self.out_edge_selection, int):
                assert 0 <= self.out_edge_selection < len(self.out_edges), f"out_edge_selection must be in range 0 to {len(self.out_edges)-1}"
            #checking if parameter is "FIRST_AVAILABLE". If so it is handled in the class logic.
            elif self.out_edge_selection == "FIRST_AVAILABLE":
                # Special handling in class logic, use as is
                pass
            #checking if out_edge_selection is a string, then it is converted to a generator using get_edge_selector function.
            # Names of the methods are passed as strings. These methods are inbuilt and available.
            elif isinstance(self.out_edge_selection, str):
                self.out_edge_selection = get_edge_selector(self.out_edge_selection, self, self.env, "OUT")
            
            #checking if out_edge_selection is a callable or a generator. If so, it is used as is.
            # it is treated in get_out_edge_index method
            elif callable(self.out_edge_selection) or hasattr(self.out_edge_selection, '__next__'):
                # Use as is (function or generator)
                pass
            else:
                raise ValueError("out_edge_selection must be None, string, int, or a callable (function/generator)")
 

            
            # If it is initialise as None and missed to initialise it to a valid function before simulation
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
        
    def update_final_state_time(self, simulation_end_time):
        duration = simulation_end_time- self.stats["last_state_change_time"]
        # updating the time of per thread states
        for procs in self.worker_thread_list:
            if procs.thread_state == "PROCESSING_STATE":
                self._update_avg_time_spent_in_processing(duration)
            elif procs.thread_state == "BLOCKED_STATE":
                self._update_avg_time_spent_in_blocked(duration)
        #checking threadstates and updating the machine state
        if self.state is not None and self.stats["last_state_change_time"] is not None:
            duration = simulation_end_time- self.stats["last_state_change_time"]
            self.stats["total_time_spent_in_states"][self.state] = (
                self.stats["total_time_spent_in_states"].get(self.state, 0.0) + duration
            )
        #updating the time vs no. of worker thread list
        #num worker thread is the index of the list and time spent by that many worker threads is the value)
        self._update_worker_occupancy("UPDATE")
                

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
        
         
        # if it is a constant integer, use the value as is
        if isinstance(self.out_edge_selection, int):
            val = self.out_edge_selection
        # if it is a generator, get the next value from the generator
        elif hasattr(self.out_edge_selection, '__next__'):
            # It's a generator
            val = next(self.out_edge_selection)     
        # if it is a function return the value returned by the function     
        elif callable(self.out_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.out_edge_selection()       
        else:
            raise ValueError("out_edge_selection must be a generator or a callable.")   
        # Check if the value is within the valid range of out_edges
        #print(f"OUT: {val} {len(self.out_edges)}")
        assert 0<= val < len(self.out_edges), f"{self.id} - Invalid edge index. {val} is not in range. Range must be between {0} and  {len(self.out_edges)-1} for out_edges." 
        self.stats["out_edge_selection"].append(val)
        return val   
 

    def _get_in_edge_index(self):

        # if it is a constant integer, use the value as is 
        if isinstance(self.in_edge_selection, int):
            val = self.in_edge_selection
        # if it is a generator, get the next value from the generator
        elif hasattr(self.in_edge_selection, '__next__'):
            # It's a generator
            val = next(self.in_edge_selection)    
        # if it is a function return the value returned by the function
        elif callable(self.in_edge_selection):
          
            val = self.in_edge_selection()   
        else:
            raise ValueError("in_edge_selection must be a generator or a callable.")    
        # Check if the value is within the valid range of in_edges
        #print( val )
        assert 0<=val < len(self.in_edges), f"{self.id} - Invalid edge index. {val} is not in range. Range must be between {0} and  {len(self.in_edges)-1} for in_edges."
        self.stats["in_edge_selection"].append(val)
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
                outstore = out_edge
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
                outstore = in_edge
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
        using self.worker_thread_list.
    
        Returns:
            num_threads_PROCESSING (int): Number of threads in "PROCESSING_STATE"
            num_threads_BLOCKED (int): Number of threads in "BLOCKED_STATE"
        """
        if not self.worker_thread_list:
            num_threads_PROCESSING = 0
            num_threads_BLOCKED = 0
        else:
            num_threads_PROCESSING = sum(
                proc.thread_state == "PROCESSING_STATE" for proc in self.worker_thread_list
            )
            num_threads_BLOCKED = sum(
                proc.thread_state == "BLOCKED_STATE" for proc in self.worker_thread_list
            )
    
        assert 0 <= num_threads_BLOCKED <= self.work_capacity \
            and 0 <= num_threads_PROCESSING <= self.work_capacity \
            and 0 <= num_threads_BLOCKED + num_threads_PROCESSING <= self.work_capacity, \
            f"T={self.env.now:.2f} {self.id} has more threads than work_capacity is created. num_threads_PROCESSING={num_threads_PROCESSING}, num_threads_BLOCKED={num_threads_BLOCKED}, work_capacity={self.work_capacity}"
        return num_threads_PROCESSING, num_threads_BLOCKED
    
    

    def check_thread_state_and_update_machine_state_flexsim(self):
        n_proc, n_blocked = self._count_worker_state()
        print(f"T={self.env.now:.2f} {self.id} - Invalid worker thread state. n_proc={n_proc}, n_blocked={n_blocked}, work_capacity={self.work_capacity}")
        if n_proc == 0 and n_blocked == 0:
            new_state = "IDLE_STATE"
            self.update_state("IDLE_STATE", self.env.now)
        #elif n_blocked>=self.work_capacity-1 :  # all slots blocked
        elif n_blocked >0 and n_proc== self.work_capacity - n_blocked:  # all slots blocked   
        #elif n_blocked>0 and n_blocked + n_proc == self.work_capacity:  # all slots blocked
            new_state = "BLOCKED_STATE"
            self.update_state("BLOCKED_STATE", self.env.now)
        elif n_proc>0 and n_blocked==0:                       # ≥1 slot still processing
            new_state = "PROCESSING_STATE"
            self.update_state("PROCESSING_STATE", self.env.now)
        else:
            raise ValueError(f"{self.id} - Invalid worker thread state. n_proc={n_proc}, n_blocked={n_blocked}, work_capacity={self.work_capacity}")

        # # <<< TRACE every change >>> ------------------------------------------
        # if new_state != getattr(self, "current_state", None):
        #     self._dbg( f"→ {new_state}   (proc={n_proc}, blk={n_blocked}, "
        #             f"active={len(self.worker_thread_list)})")
        # # ---------------------------------------------------------------------

        # if new_state != getattr(self, "current_state", None):
        #     self.update_state(new_state, self.env.now)
        #     self.current_state = new_state

          
    def check_thread_state_and_update_machine_state(self):
        numthreads_PROCESSING, numthreads_BLOCKED = self._count_worker_state()
        #print(f"T={self.env.now:.2f}: {self.id} - numthreads_PROCESSING={numthreads_PROCESSING}, numthreads_BLOCKED={numthreads_BLOCKED}, work_capacity={self.work_capacity}")

        # if numthreads_PROCESSING == 0 and numthreads_BLOCKED == 0, then the state is IDLE_STATE
        #No active threads
        if numthreads_PROCESSING == 0 and numthreads_BLOCKED == 0 :
            #print(f"T={self.env.now:.2f}: idle")
            self.update_state("IDLE_STATE", self.env.now)
        # if there is atleast one thread that is PROCESSING, then the state is PROCESSING_STATE, then the state is updated to PROCESSING_STATE
        
        #all active threads are in blocked state
        elif numthreads_BLOCKED ==len(self.worker_thread_list):
        #elif numthreads_BLOCKED >=1:
            #print(self.env.now, numthreads_BLOCKED,len(self.worker_thread.users))
            print(f"T={self.env.now:.2f}: {self.id} is in BLOCKED_STATE")
            self.update_state("BLOCKED_STATE", self.env.now)
        # atleast one active thread is in processing state
        elif numthreads_PROCESSING >0:
            self.update_state("PROCESSING_STATE", self.env.now)
        # if all threads are in blocked state, then the state is BLOCKED_STATE, then the state is updated to BLOCKED_STATE
        #elif numthreads_BLOCKED == self.work_capacity:
        else:
            raise ValueError(f"{self.id} - Invalid worker thread state1. numthreads_PROCESSING={numthreads_PROCESSING}, numthreads_BLOCKED={numthreads_BLOCKED}, work_capacity={self.work_capacity}")
       



    def check_thread_state_and_update_machine_state_2(self):
        numthreads_PROCESSING, numthreads_BLOCKED = self._count_worker_state()
        #print(f"T={self.env.now:.2f}: {self.id} - numthreads_PROCESSING={numthreads_PROCESSING}, numthreads_BLOCKED={numthreads_BLOCKED}, work_capacity={self.work_capacity}")

        # if numthreads_PROCESSING == 0 and numthreads_BLOCKED == 0, then the state is IDLE_STATE
        #No active threads
        if numthreads_PROCESSING == 0 and numthreads_BLOCKED == 0 :
            #print(f"T={self.env.now:.2f}: idle")
            self.update_state("IDLE_STATE", self.env.now)
        # if there is atleast one thread that is PROCESSING, then the state is PROCESSING_STATE, then the state is updated to PROCESSING_STATE        
        elif numthreads_BLOCKED>0:
            #print(self.env.now, numthreads_BLOCKED,len(self.worker_thread.users))
            print(f"T={self.env.now:.2f}: {self.id} is in BLOCKED_STATE")
            self.update_state("BLOCKED_STATE", self.env.now)
        # atleast one active thread is in processing state and no thread is in blocked state
        elif numthreads_PROCESSING>0 and numthreads_BLOCKED==0:
            print(f"T={self.env.now:.2f}: {self.id} is in PROCESSING_STATE")
            self.update_state("PROCESSING_STATE", self.env.now)
        else:
            raise ValueError(f"{self.id} - Invalid worker thread state2. numthreads_PROCESSING={numthreads_PROCESSING}, numthreads_BLOCKED={numthreads_BLOCKED}, work_capacity={self.work_capacity}")
     
        
        
  
        

        

    def worker(self,item,processing_delay,req_token,):
        #Worker process that processes items with resource and reserve handling."""
            self.check_thread_state_and_update_machine_state()  # Check and update the machine state based on worker states
            processing_start_time = self.env.now
            #wait for processing_delay amount of time
            yield self.env.timeout(processing_delay)
            #self.stats["num_item_processed"] += 1
            self._update_avg_time_spent_in_processing(self.env.now - processing_start_time)  # Update the average time spent in processing
          
               #out_edge_selection is "FIRST_AVAILABLE"---> 
            if self.out_edge_selection == "FIRST_AVAILABLE":
                # if blocking yield reserve_put on all out_edges and take the one with min index and cancel others and push item
                if self.blocking:
                    self.check_thread_state_and_update_machine_state()
                    self.env.active_process.thread_state = "BLOCKED_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
                    self.check_thread_state_and_update_machine_state()
                    blocking_start_time = self.env.now
                
                    #self.out_edge_events = [edge.reserve_put() if edge.__class__.__name__ == "ConveyorBelt" else edge.inbuiltstore.reserve_put() for edge in self.out_edges]
                    #out_edge_events = [self.out_edges[i].inbuiltstore.reserve_put() for i in range(len(self.out_edges)-1,-1,-1)]
                    out_edge_events= [edge.reserve_put() for edge in self.out_edges]  # Filter out None events
                    #print(self.env.now,len(self.out_edge_events),self.out_edges)
                    triggered_out_edge_events = self.env.any_of(out_edge_events)
                    yield triggered_out_edge_events  # Wait for any in_edge to be available
                    
                    chosen_put_event = next((event for event in out_edge_events if event.triggered), None)
                    
                    
                    #self.out_edge_events.remove(chosen_put_event)  # Remove the chosen event from the list
                    if chosen_put_event is None:
                        raise ValueError(f"{self.env.now},{self.id} - No out_edge available for processing{[edge.id for edge in self.out_edges]}!")
                    edge_index = out_edge_events.index(chosen_put_event)
                    self.stats["out_edge_selection"].append(edge_index)  # Store the index of the chosen out_edge
                    #out_edge_events.remove(chosen_put_event)  # Remove the chosen event from the list
                    #cancelling already triggered out_edge events
                    for event in out_edge_events:
                        #if event.triggered and event is not chosen_put_event:
                        if event is not chosen_put_event:
                            event.resourcename.reserve_put_cancel(event)
                    #out_edge_events=[]

                    #putting the item in the chosen out_edge
                    
                    item.update_node_event(self.id, self.env, "exit")
                    if self.out_edges[edge_index].__class__.__name__  in [ "Buffer", "ConveyorBelt"]:
                        self.stats["num_item_processed"] += 1
                        itemput=self.out_edges[edge_index].put(chosen_put_event, item)
                        #itemput = chosen_put_event.resourcename.put(chosen_put_event, item)  # Get the item from the chosen in_edge

                    else:
                        raise ValueError(f"Unsupported edge type: {self.out_edges[edge_index].__class__.__name__}")
                    print(f"T={self.env.now:.2f}: {self.id} puts item {item.id} into {self.out_edges[edge_index].id} ")
                    
                    self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                    #self.env.active_process.thread_state = "PROCESSING_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
                    self.check_thread_state_and_update_machine_state()
                    # c=self.worker_thread_list.index(self.env.active_process)
                    # if c>=0:
                    #     assert self.worker_thread_list[c].thread_state == "PROCESSING_STATE", f"{self.id} - Worker thread {c} is not in PROCESSED_STATE after processing item {self.worker_thread_list[c].thread_state}."
                    #self.check_thread_state_and_update_machine_state()
                    
                #not blocking, check can_put on all, if all fails, then the item is discarded
                else:
                    out_edge_index_to_put = None
                    for edge in self.out_edges:
                        if edge.can_put():
                            out_edge_index_to_put = edge
                            break
                    
                    if out_edge_index_to_put is not None:
                         blocking_start_time = self.env.now
                         self.check_thread_state_and_update_machine_state()
                         self.env.active_process.thread_state = "BLOCKED_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
                         self.check_thread_state_and_update_machine_state()
                         yield self.env.process(self._push_item(item, out_edge_index_to_put)) 
                         self.stats["num_item_processed"] += 1 
                         print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {out_edge_index_to_put.id} ")
                         #self.check_thread_state_and_update_machine_state()
                         #self.env.active_process.thread_state = "PROCESSING_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
                         
                         self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                         self.check_thread_state_and_update_machine_state()

                    else:
                        print(f"T={ self.env.now:.2f}: {self.id} worker is discarding item {item.id} because out_edge {edge.id} is full.")
                        self.stats["num_item_discarded"] += 1  # Decrement processed count if item is discarded


                    
                    
                

            #out_edge_selection is not "FIRST_AVAILABLE" ---> get index value and push the item if not blocking
            else:
                print(f"T={self.env.now:.2f}: {self.id} worker processed item: {item.id}")
                out_edge_index_to_put = self._get_out_edge_index()
                #print("OUT",out_edge_index_to_put)
                assert 0<=out_edge_index_to_put < len(self.out_edges), f"{self.id} - Invalid edge index. {out_edge_index_to_put} is not in range. Range must be between {0} and  {len(self.out_edges)-1} for in_edges."
                outedge_to_put = self.out_edges[out_edge_index_to_put]
                #push the item if not blocking
                self.env.active_process.thread_state = "BLOCKED_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
                self.check_thread_state_and_update_machine_state()
                if self.blocking:
                    blocking_start_time = self.env.now
                    print(f"T={self.env.now:.2f}: {self.id} worker is in BLOCKED_STATE and machine is in {self.state}")
                    #yield self.env.process(self._push_item(item, outedge_to_put))
                    put_event=outedge_to_put.reserve_put()
                    yield put_event
                    print(f"T={self.env.now:.2f}: {self.id} yielded and worker is putting item {item.id} into {outedge_to_put.id} " )
                    item.update_node_event(self.id, self.env, "exit")
                    self.stats["num_item_processed"] += 1
                    y=outedge_to_put.put(put_event, item)
                    if y:
                     print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {outedge_to_put.id} ")
                    self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                    #self.check_thread_state_and_update_machine_state()  # Check and update the machine state after blocking
                #check can_put and only if it succeeds push the item if not blocking
                else:
                    # Check if the out_edge can accept the item
                    if outedge_to_put.can_put():
                        blocking_start_time = self.env.now
                        yield self.env.process(self._push_item(item, outedge_to_put))
                        self.stats["num_item_processed"] += 1
                        print(f"T={self.env.now:.2f}: {self.id} worker puts item {item.id} into {outedge_to_put.id} ")
                        self._update_avg_time_spent_in_blocked(self.env.now - blocking_start_time)
                    else:
                        print(f"T={self.env.now:.2f}: {self.id} worker is discarding item {item.id} because out_edge {outedge_to_put.id} is full.")
                        self.stats["num_item_discarded"] += 1
            # Release the worker thread after processing
            #self.env.active_process.thread_state = "PROCESSING_STATE"  # Update the thread state to PROCESSING_STATE BLOCKING
            #self.check_thread_state_and_update_machine_state()
            yield self.worker_thread.release(req_token)  # Release the worker thread
      
            #delete the worker thread from the worker_thread_list
            if self.env.active_process in self.worker_thread_list:
                self.worker_thread_list.remove(self.env.active_process)
            self._update_worker_occupancy(action="REMOVE")  # Update worker occupancy after processing
            self.check_thread_state_and_update_machine_state()    

    
                

    def behaviour(self):
        #Machine behavior that creates workers based on the effective capacity."""
        # Reset the machine state and edge selection parameters and processing delay parameter
        self.reset()

        #checking of the machine has atleast 1 in_edge and 1 out_edge
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."


        while True:
            #print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            if self.state == "SETUP_STATE":
                
                print(f"T={self.env.now:.2f}: {self.id} is in SETUP_STATE")
                yield self.env.timeout(self.node_setup_time)# always an int or float
                self.update_state("IDLE_STATE", self.env.now)

            else:
               
                
                #updating the working occupancy of the machine-- 
                # done to account the time of an iteration incase there is no change is worker occupancy
            
                #self._update_worker_occupancy(action="UPDATE")
                self.check_thread_state_and_update_machine_state()               
                print(f"T={self.env.now:.2f}: {self.id} is in {self.state}!!!")
                worker_thread_req = self.worker_thread.request()  # Request a worker thread
                yield worker_thread_req
                self._update_worker_occupancy(action="ADD")
                
                #in_edge_selection is "FIRST_AVAILABLE"--->     yield in a list, select one with min. index value and cancel other and pull item
                if self.in_edge_selection == "FIRST_AVAILABLE":
                    
                    #if not self.in_edge_events:
                    self.in_edge_events=  [edge.reserve_get() for edge in self.in_edges]

                    # for i in self.in_edges:
                    #     if len(i.inbuiltstore.items):

                    #        print( f"T={self.env.now:.2f}: {self.id} in {i.id} item entry time - {[item.timestamp_node_exit for item in i.inbuiltstore.items] } and no. of reservations {len(i.inbuiltstore.reservations_get)} ") # Update the timestamp of items in the inbuilt store 
                    #        #if len(i.inbuiltstore.reservations_get):
                                                     
                    #     else:
                    #         print(f"T={self.env.now:.2f}: {self.id} in {i.id} is empty")
                    #self.in_edge_events = [self.in_edges[i].inbuiltstore.reserve_get() for i in range(len(self.in_edges)-1,-1,-1)]
                    print(f"T={self.env.now:.2f}: {self.id} waiting for in_edge events to be triggered")
                    #print(f"T={self.env.now:.2f}: {self.id} in_edge_events: {[event.resourcename for event in self.in_edge_events]}")  # Debugging line to check in_edge_events
                    triggered_in_edge_events = self.env.any_of(self.in_edge_events)
                    
                    yield triggered_in_edge_events  # Wait for any in_edge to be available
                    trig_count = [1 if event.triggered else 0 for event in self.in_edge_events]
                    #print(f"T={self.env.now:.2f}: {self.id} no of trigerred events {sum(trig_count)} , {trig_count}, in_edge_events triggered")
                    # Find the first triggered event           
                    self.chosen_event = next((event for event in self.in_edge_events if event.triggered), None)
                    if self.chosen_event is None:
                        raise ValueError(f"{self.id} - No in_edge available for processing!")
                    # Find the index of the chosen event in the in_edge_events list
                    edge_index_to_print = None
                    for i in range(len(self.in_edges)):
                        #print(self.chosen_event.resourcename, self.in_edges[i])
                        if self.in_edges[i].__class__.__name__ == "Buffer" or self.in_edges[i].__class__.__name__ == "Fleet":
                            if self.chosen_event.resourcename == self.in_edges[i].inbuiltstore :
                        
                                edge_index_to_print=i
                        elif self.in_edges[i].__class__.__name__ == "ConveyorBelt":

                            print(self.chosen_event.resourcename, self.in_edges[i].belt)
                            #if self.chosen_event.resourcename == self.in_edges[i].out_buf:
                            if self.chosen_event.resourcename == self.in_edges[i].belt:
                                
                                edge_index_to_print=i
                        else:
                            raise ValueError(f"Unsupported edge type: {self.in_edges[i].__class__.__name__}")

                            
                    edge_index = self.in_edge_events.index(self.chosen_event)  # Get the index of the chosen event
                    assert edge_index == edge_index_to_print, f"{self.id} - Edge index mismatch. {edge_index} != {edge_index_to_print}. Check the in_edge_events and in_edges."
                    
                    #print("!!!!!!",edge_index)
                    self.stats["in_edge_selection"].append(edge_index)
                    
                    print(f"T={self.env.now:.2f}: {self.id} yielded from {self.in_edges[edge_index].id} ")
                    
                    
                    #self.in_edge_events.remove(self.chosen_event)  # Remove the chosen event from the list
                    #cancelling already triggered in_edge events other than chosen events
                    
                    for event in self.in_edge_events:
                        event_cancelled = False
                        #if event.triggered and event is not self.chosen_event:
                        if  event is not self.chosen_event:
                            #print(f"T={self.env.now:.2f}: {self.id} cancelling  in_edge events  ")
                            event_cancelled = event.resourcename.reserve_get_cancel(event)
                            if not event_cancelled:
                                raise ValueError(f"{self.id} - Failed to cancel reserve_get for event {event}.")
                            
                        #self.in_edge_events=[]

                    

                    ####---3/9 Create workers based on work_capacity
                    # worker_thread_req = self.worker_thread.request()  # Request a worker thread
                    # print(f"T={self.env.now:.2f}: {self.id} requested worker thread for processing item from {self.in_edges[edge_index].id} ")
                    # yield worker_thread_req
                    # print(f"T={self.env.now:.2f}: {self.id} got worker thread for processing item from {self.in_edges[edge_index].id} ")
                    ####---3/9
                    
                    #update occupancy
                    #self._update_worker_occupancy(action="ADD")

                    if self.in_edges[edge_index].__class__.__name__ in ["Buffer", "Fleet", "ConveyorBelt"]:
                        self.item_in_process=self.in_edges[edge_index].get(self.chosen_event)  # Get the item from the chosen in_edge
                        #print("getting getting getting getting  item from in_edge", self.chosen_event.resourcename)
                        #self.item_in_process = self.chosen_event.resourcename.get(self.chosen_event)  # Get the item from the chosen in_edge
                        self.item_in_process.update_node_event(self.id, self.env, "entry")
                    else:
                        raise ValueError(f"Unsupported edge type: {self.in_edges[edge_index].__class__.__name__}")
                    #print(f"T={self.env.now:.2f}: {self.id} received item {item.id} from {self.in_edges[edge_index].id} ")
                    
                    
                    
                #in_edge_selection is not "FIRST_AVAILABLE"---> use get_in_edge_index and pull item
                else:
                    #print("not_first_available")
                    in_edge_index = self._get_in_edge_index()
                    #print(self.id, in_edge_index)
                    
                    assert type(in_edge_index)==int and 0<=in_edge_index < len(self.in_edges), f"{self.id} - Invalid edge index. {in_edge_index} is not in range. Range must be between {0} and  {len(self.in_edges)-1} for in_edges."
                    #print("IN", in_edge_index)
                    in_edge_to_get = self.in_edges[in_edge_index]
                    
                    #yield self.env.process(self._pull_item( in_edge_to_get))

                   
                    
                    

                    if in_edge_to_get.__class__.__name__ in ["Buffer", "Fleet", "ConveyorBelt"]:
                        print(f"T={self.env.now:.2f}: {self.id} is pulling item from {in_edge_to_get.id} ")
                        outstore = in_edge_to_get
                        get_token = outstore.reserve_get()
                        yield get_token
                        print(f"T={self.env.now:.2f}: {self.id} yielded from {in_edge_to_get.id} ")
                         # Create workers based on work_capacity
                        #worker_thread_req = self.worker_thread.request()  # Request a worker thread
                        #yield worker_thread_req
                        #update occupancy
                        #self._update_worker_occupancy(action="ADD")
                        
                        
                        self.item_in_process =outstore.get(get_token)
                        
                        if self.item_in_process  is not None:
                            #print(self.item_in_process)
                            self.item_in_process .update_node_event(self.id, self.env, "entry")
                            print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process .id} from {in_edge_to_get.id} ")
                        else:
                            raise ValueError(f"T={self.env.now:.2f}: {self.id} - No item pulled from in_edge {in_edge_to_get.id}!")
                    else:
                        raise ValueError(f"Unsupported edge type: {in_edge_to_get.__class__.__name__}")



                    
                    
              
                if self.item_in_process is None:
                    raise ValueError(f"{self.id} - No item pulled from in_edge {in_edge_to_get.id}!")
                #get a worker thread
                # worker_thread_req = self.worker_thread.request()  # Request a worker thread
                # yield worker_thread_req
                
                # #print(f"{self.env.now:.2f}--yielded {i}, {len(self.worker_thread.users)}")
                
                # #update occupancy
                # self._update_worker_occupancy(action="ADD")
                #get processing_time
                next_processing_time = self.get_delay(self.processing_delay)
                #print("!!!!!!!!!!!!!!!!!!EGKEKHRTUOYO!!!!!!!!!!!!!!!!!!!!!!!!!", next_processing_time)

                self.stats["processing_delay"].append(next_processing_time)  # Update the processing delay in stats
                print(f"T={self.env.now:.2f}: {self.id} worker started processing item {self.item_in_process.id} ")
                #spawn a worker process
                proc = self.env.process(self.worker(self.item_in_process, next_processing_time, worker_thread_req))  # Start the worker process
                proc.thread_state="PROCESSING_STATE" # Set the thread state to PROCESSING_STATE
                proc.item_to_put = self.item_in_process # Set the item to be put by the worker process
                self.worker_thread_list.append(proc)  # Add the worker process to the worker_thread_list
                self.check_thread_state_and_update_machine_state()  # Check and update the machine state based on worker states
                #initialise item into none
                self.item_in_process=None
            
                

                

       
