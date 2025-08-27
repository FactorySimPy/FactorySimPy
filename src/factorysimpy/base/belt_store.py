# src/ReservablePriorityReqStore.py



import simpy
from simpy.resources.store import Store

class BeltStore(Store):
    """
        This is a class that is derived from SimPy's Store class and has extra capabilities
        that makes it a priority-based reservable store for processes to reserve space
        for storing and retrieving items with priority-based access.

        Processes can use reserve_put() and reserve_get() methods to get notified when a space becomes
        available in the store or when an item gets available in the ReservablePriorityReqStore.
        These methods returns a unique event (SimPy.Event) to the process for every reserve requests it makes.
        Processes can also pass a priority as argument in the request. Lower values indicate higher priority.

        get and put are two methods that can be used for item storing and retrieval from ReservablePriorityReqStore.
        Process has to make a prior reservation and pass the associated reservation event as argument in the get and
        put requests. ReservablePriorityReqStore maintains separate queues for `reserve_put` and `reserve_get` operations
        to ensures that only processes with valid reservations can store or retrieve items.

        ReservablePriorityReqStore preserves item order by associating an unreserved item in the store with a reservation event
        by index when a reserve_get() request is made. As a result, it maintains a list of reserved events to preserve item order.

        It also allows users to cancel an already placed reserve_get or reserve_put request even if it is yielded.
        It also handles the dissociation of the event and item done at the time of reservation when an already yielded
        event is canceled.

        Attributes:
           reserved_events (list):  Maintains events corresponding to reserved items to preserve item order by index
           reserve_put_queue (list): Queue for managing reserve_put reservations
           reservations_put (list): List of successful put reservations
           reserve_get_queue (list): Queue for managing reserve_get reservations
           reservations_get (list):List of successful get reservations
        """

    def __init__(self, env, capacity=float('inf'),mode='FIFO', speed=1):
        """
        Initializes a reservable store with priority-based reservations.

        Args:
         
            capacity (int, optional): The maximum number of items the store can hold.
                                      Defaults to infinity.
        """
        super().__init__(env, capacity)
        self.env = env
        self.mode=mode
        self.speed = speed  # Speed of the conveyor belt (units per time)
        self.reserve_put_queue = []  # Queue for managing reserve_put reservations
        self.reservations_put = []   # List of successful put reservations
        self.reserve_get_queue = []  # Queue for managing reserve_get reservations
        self.reservations_get = []   # List of successful get reservations
        self.reserved_events = []     # Maintains events corresponding to reserved items to preserve item order
        self.ready_items=[]  #Maintains the items ready to be taken out
        self.reserved_items   = []   # parallel list of the exact items reserved
        self._last_level_change_time = self.env.now
        self._last_num_items = 0
        self._weighted_sum = 0.0
        self.time_averaged_num_of_items_in_store = 0.0  # Time-averaged number of items in the store
        # Process tracking for interrupt functionality
        self.active_move_processes = {}  # Dictionary to track active move_to_ready_items processes
        self.resume_event = self.env.event()  # Event to signal when to resume processes
        self.noaccumulation_mode_on = False # to control if the belt is in noaccumulation mode
        self.one_item_inserted = False # to control insertion of only one item in noaccumulation mode
        self.ready_item_event= self.env.event()

    def _update_time_averaged_level(self):
        now = self.env.now
        interval = now - self._last_level_change_time
        self._weighted_sum += self._last_num_items * interval
        self._last_level_change_time = now
        self._last_num_items = len(self.items)+len(self.ready_items)
        
        total_time = now
        self.time_averaged_num_of_items_in_store = (
            self._weighted_sum / total_time if total_time > 0 else 0.0
        )

    def reserve_put(self, priority=0):
        """
        Create a reservation request to put an item into the store.

        This function generates a SimPy event representing a reservation request. The event is
        assigned attributes such as priority, resource name, and the process making the request.
        The event is then added to `reserve_put_queue`, which is maintained in priority order.

        After adding the event to the queue, `_trigger_reserve_put` is called to process
        any pending reservations.

        Args:
            priority (int, optional): The priority level of the reservation request.
                                      Lower values indicate higher priority. Defaults to 0.

        Returns:
            event (simpy.Event): A reservation event that will succeed when space is available.

        """
        event = self.env.event()
        event.resourcename = self  # Store reference
        event.requesting_process = self.env.active_process  # Process making the reservation
        event.priority_to_put = priority  # Priority for sorting reservations

        # Add the event to the reservation queue and sort by priority
        self.reserve_put_queue.append(event)
        self.reserve_put_queue.sort(key=lambda e: e.priority_to_put)

        # Attempt to process reservations
        self._trigger_reserve_put(event)

        return event



    def _trigger_reserve_put(self, event):
        """
        Process pending reservation requests for putting items into the store.

        This method iterates through the `reserve_put_queue` and attempts to fulfill
        pending `reserve_put` requests by calling `do_reserve_put`.

        Args:
            event (simpy.Event): The event associated with the reservation request.

        Raises:
            RuntimeError: If an event expected to be in `reserve_put_queue` is not found
                          when attempting to remove it after successful processing.
        """
        idx=0

        while idx < len(self.reserve_put_queue):

          reserve_put_event = self.reserve_put_queue[idx]
          proceed = self._do_reserve_put(reserve_put_event)
          if not reserve_put_event.triggered:
            idx += 1
          elif self.reserve_put_queue.pop(idx) != reserve_put_event:
            raise RuntimeError('Reserve put queue invariant violated')

          if not proceed:
            break




    def _do_reserve_put(self,event):
        """
        Attempts to reserve space in the store for an incoming item.
        This method processes a `reserve_put` request by checking if the store has
        available capacity for the reservation. If space is available, the request
        is granted, and the reservation is recorded. Otherwise, the request remains as is.

        Args:
            event (simpy.Event): The event associated with the reservation request.


        Side Effects:
            - Modifies `self.reservations_put` by appending the successful reservation.
            - Calls `event.succeed()` to indicate a successful reservation.
      

        """
        # Check if there's enough space to reserve
        if self.items:
            if len(self.reservations_put) + len(self.items) +len(self.ready_items) < self.capacity:
                if not self.noaccumulation_mode_on or (self.noaccumulation_mode_on and self.one_item_inserted==False):
                    if self.env.now>= self.items[-1][0].conveyor_entry_time + self.items[-1][0].length/self.speed:
                        #print(f"At time={self.env.now:.2f}, Process {self.env.active_process} "
                        # f"reserved space. Total reservations: {len(self.reservations_put)}")
                        self.reservations_put.append(event)
                        event.succeed()
                        if self.noaccumulation_mode_on:
                           self.one_item_inserted=True
        else:
           
            if len(self.reservations_put) + len(self.items) +len(self.ready_items) < self.capacity:
                self.reservations_put.append(event)  # Add reservation
                event.succeed()
                # Log the success of the reservation
                #print(f"At time={self.env.now:.2f}, Process {self.env.active_process} "
                    # f"reserved space. Total reservations: {len(self.reservations_put)}")

                # Mark the event as successful

            #else:
                #print(f"At {self.env.now:.2f}, Reservation failed for {self.env.active_process} "
                #     f"on {self}. Store is full.")
    def _add_trigger_event(self, item):
        """Trigger get events after a delay time after put event."""
        event=self.env.event()
        self.delay=item[0].length/self.speed
        #print(f"created Added event suceeded{self.delay}")
        event.callbacks.append(self._trigger_reserve_put)# after putting an item, an event is created and will be triggered ater delay amount of time to allow waiting get calls to succeed in a stalled belt
        #event.callbacks.append(self._trigger_put)# this may not be needed
        yield self.env.timeout(self.delay)
        #print(f"{self.env.now}Added event suceed        ed")
        event.succeed()

    def reserve_put_cancel(self, put_event_to_cancel):
      """
        Cancel a previously made `reserve_put` request.

        This method allows a process to cancel its reservation for putting an item
        into the store. If the reservation exists in the `reserve_put_queue`, it is
        removed before triggering `_trigger_reserve_put` to process any pending reservations.
        If the reservation is already in `reservations_put`, it is also removed and
        `_trigger_reserve_put` is triggered.

        Args:
            put_event_to_cancel (simpy.Event): The reservation event that needs to be canceled.

        Returns:
           proceed (bool): True if the reservation was successfully canceled.

        Raises:
            RuntimeError: If the specified event does not exist in `reserve_put_queue`
                          or `reservations_put`.
        """

      #checking and removing the event if it is not yielded and is present in the reserve_put_queue
      proceed = False
      if put_event_to_cancel in self.reserve_put_queue:
        self.reserve_put_queue.remove(put_event_to_cancel)
        self._trigger_reserve_put(None)#if t is removed, then a waiting event can be succeeded, if any
        proceed = True
      #checking and removing the event if it is already yielded and is present in the reservations_put
      elif put_event_to_cancel in self.reservations_put:
        self.reservations_put.remove(put_event_to_cancel)
        self._trigger_reserve_put(None)#if t is removed, then a waiting event can be succeeded, if any
        proceed = True

      else:
        raise RuntimeError("No matching event in reserve_put_queue or reservations_put for this process")
      return proceed
    
    def reserve_get_cancel(self, get_event_to_cancel):
        """
        Cancel a previously made `reserve_get` request.
        """
        # Case 1: still waiting
        if get_event_to_cancel in self.reserve_get_queue:
            self.reserve_get_queue.remove(get_event_to_cancel)
            self._trigger_reserve_get(None)
            return True

        # Case 2: already yielded reservation
        if get_event_to_cancel in self.reservations_get:
            # 1) Remove from active reservations
            self.reservations_get.remove(get_event_to_cancel)

            # 2) Find its index in the parallel lists
            ev_idx = self.reserved_events.index(get_event_to_cancel)

            # 3) Pop out the exact item reference
            item = self.reserved_items.pop(ev_idx)
            # 4) Drop the event token
            self.reserved_events.pop(ev_idx)

            # 5) Remove it from ready_items wherever it currently is
            try:
                self.ready_items.remove(item)
            except ValueError:
                raise RuntimeError(f"Item {item!r} not found in ready_items during cancel.")

            # 6) Compute new insertion index
            if self.mode == "FIFO":
                # one slot before the remaining reserved block
                insert_idx = len(self.ready_items) - len(self.reserved_events) - 1
            else:  # LIFO
                # top of stack
                insert_idx = len(self.ready_items)

            # 7) Re‑insert it
            self.ready_items.insert(insert_idx, item)

            # 8) Trigger any other pending reservations
            self._trigger_reserve_get(None)
            return True

        # No such reservation
        raise RuntimeError(
            "No matching event in reserve_get_queue or reservations_get"
        )

    def reserve_get_cancel1(self, get_event_to_cancel):

      """
        Cancel a previously made `reserve_get` request.

        This method allows a process to cancel its reservation for retrieving an item
        from the store. If the reservation exists in the `reserve_get_queue`, it is removed,
        and `_trigger_reserve_get()` is called to process any remaining reservations.

        If the reservation is already in `reservations_get`, it is removed, and the corresponding
        item is repositioned in the store to maintain order. `_trigger_reserve_get()` is then
        triggered to handle pending reservations.

        Args:
            get_event_to_cancel (simpy.Event): The reservation event that needs to be canceled.

        Returns:
            proceed (bool): True if the reservation was successfully canceled.

        Raises:
            RuntimeError: If the specified event does not exist in `reserve_get_queue`
                          or `reservations_get`.
        """
      
      proceed = False
      #checking and removing the event if it is not yielded and is present in the reserve_get_queue
      if get_event_to_cancel in self.reserve_get_queue:
        self.reserve_get_queue.remove(get_event_to_cancel)
        self._trigger_reserve_get(None)#if t is removed, then a waiting event can be succeeded, if any
        proceed = True

      #checking and removing the event if it is already yielded and is present in the reservations_queue.
      # 1-to-1 association with items done to preserve item order should also be removed.
      elif get_event_to_cancel in self.reservations_get:
        self.reservations_get.remove(get_event_to_cancel)

        #deleting the associated event in the reserved_events list to preserve the order of the items
        #finding index of the item
        event_in_index = self.reserved_events.index(get_event_to_cancel)
        delta_position = len(self.reserved_events)
        #shifting the item
        item_to_shift = self.items.pop(event_in_index)
        self.items.insert(delta_position-1, item_to_shift)
        #deleting the event
        self.reserved_events.pop(event_in_index)#if t is removed, then a waiting event can be succeeded, if any

        self._trigger_reserve_get(None)
        proceed = True

      else:
        raise RuntimeError("No matching event in reserve_get_queue or reservations_get for this process")
      
      return proceed

    def reserve_get(self,priority=0):
        """
        Create a reservation request to retrieve an item from the store.

        This method generates a SimPy event representing a request to reserve an item
        for retrieval (`get`). The event is assigned attributes such as priority,
        the resource it belongs to, and the process making the request.

        The event is then added to `reserve_get_queue`, which is maintained in
        priority order, and `_trigger_reserve_get()` is called to process pending
        reservations if items are available.

        Args:
            priority (int, optional): The priority level of the reservation request.
                                      Lower values indicate higher priority. Defaults to 0.

        Returns:
           event (simpy.Event): A reservation event that will succeed when an item becomes available.
        """
        #adding attributes to the newly created event for reserve_get
        event = self.env.event()
        event.resourcename=self
        event.requesting_process = self.env.active_process  # Associate event with the current process
       
        #event.priority_to_get = (priority, self._env.now)
        event.priority_to_get = priority

        #sorting the list based on priority after appending the new event
        self.reserve_get_queue.append(event)
        self.reserve_get_queue.sort(key=lambda e: e.priority_to_get)

        self._trigger_reserve_get(event)
        return event


    def _trigger_reserve_get(self, event):
        """
        Process pending `reserve_get` requests to fulfill reservations.

        This method iterates through the `reserve_get_queue` and attempts
        to fulfill pending `reserve_get` requests by calling `do_reserve_get`.


        Args:
            event (simpy.Event): The event associated with the reservation request.

        Raises:
            RuntimeError: If an event expected to be in `reserve_get_queue` is not
                          found when attempting to remove it after successful processing.
        """
        idx=0
        while idx < len(self.reserve_get_queue):
          reserve_get_event = self.reserve_get_queue[idx]
          proceed = self._do_reserve_get(reserve_get_event)
          if not reserve_get_event.triggered:
            idx += 1
          elif self.reserve_get_queue.pop(idx) != reserve_get_event:
            raise RuntimeError('Reserve get queue invariant violated')

          if not proceed:
            break

    def _do_reserve_get(self,event):
        """
        Process a `reserve_get` request and reserve an item if available.

        This method checks if there are available items in the store. If so,
        it grants the reservation request by adding the event to `reservations_get`
        and marking the reservation as successful. The event is also added
        to `reserved_events` to maintain item order. If a request is
        successfully processed, it is removed from the queue.

        Args:
            event (simpy.Event): The event associated with the reservation request.


        """
        #if there are items that are unreserved, the create a reservation by adding that event to the reservations_get list
        if len(self.reservations_get) < len(self.ready_items):
            # Successful reservation; add to reservations list
            self.reservations_get.append(event)
            event.succeed()  # Immediately succeed the event
            if self.noaccumulation_mode_on==True:
                self.one_item_inserted=False
                self._trigger_reserve_get(event)

            #reserving the item to preserved item order by adding the reserve_get event to a list(the index position of event= index position of reserved item)
            

            """
            Called when a process reserves an item.
            We pick the j-th from top (for LIFO) or bottom (for FIFO)
            but do NOT remove it yet—we just record the exact item.
            """
            j = len(self.reserved_events)
            if self.mode == "FIFO":
                item = self.ready_items[j]
            else:  # LIFO
                item = self.ready_items[-1 - j]

            # record the reservation
            self.reserved_events.append(event)
            self.reserved_items .append(item)




    def get(self,get_event):
        """
        Retrieve an item from the store after a successful reservation.

        This method attempts to retrieve an item associated with a `reserve_get`
        event. If the reservation exists, it triggers `_trigger_get` to retrieve
        the item. If successful, `_trigger_reserve_put` is called to process any
        pending `reserve_put` requests. If the item retrieval fails, an error
        message is raised.

        Args:
            get_event (simpy.Event): The reservation event associated with the request.

        Returns:
            item (Object): The retrieved item if successful, otherwise raises an error

        Raises:
            RuntimeError: If no reservations are available in the reservations_get
            RuntimeError: If item returned is None
        """

        item = None
        #if there are reservations, then call _trigger_get
        if self.reservations_get:
          item= self._trigger_get(get_event)
        #else raise an error
        else:
          raise RuntimeError("No matching reservation found for process: reservations_get is empty")
        #if an item is returned then call _trigger_reserve_put to process pending requests
        if item is not None:
          self._trigger_reserve_put(None)

        if item is None:
          raise RuntimeError(f"No item found in the store for {get_event.requesting_process} and get request failed")
        else:
          #self._update_time_averaged_level()
          return item

    def _trigger_get(self, get_event):
        """
        Attempt to retrieve an item associated with a `reserve_get` request.

        This method is responsible for processing a `get_event` by calling `_do_get`
        if there are pending reservations.
        Args:
            get_event (simpy.Event): The event corresponding to the reservation.

        Returns:
            item (Object): The retrieved item if successful, otherwise `None`.
        """
        item = None
        idx=0
        if idx < len(self.reservations_get):
          item = self._do_get(get_event)
        return item


    def _do_get(self, get_event):
        """
        Execute the actual `get` (process has called yield on the Event).
        Removes the reservation and takes out that exact item from ready_items.
        """
        # 1) validate reservation exists for this process
        reserved_event = next(
            (ev for ev in self.reservations_get
             if ev == get_event and ev.requesting_process == self.env.active_process),
            None
        )
        if reserved_event is None:
            raise RuntimeError(
                f"Time {self.env.now:.2f}, no matching reservation for process {self.env.active_process}."
            )

        # 2) find its index in the reservation lists
        ev_idx = self.reserved_events.index(reserved_event)

        # 3) remove from reservations
        self.reservations_get.remove(reserved_event)
        self.reserved_events.remove(reserved_event)

        # 4) pop out the exact item reference
        try:
            assigned_item = self.reserved_items.pop(ev_idx)
        except IndexError:
            raise ValueError(f"Reserved item for {get_event} not found in store.")

        # 5) remove that object from ready_items by value
        try:
            self.ready_items.remove(assigned_item)
        except ValueError:
            raise ValueError(f"Item {assigned_item} not in ready_items.")
        self._update_time_averaged_level()
        return assigned_item

    def _do_get1(self, get_event):
        """
        Execute a `get` operation from the store while ensuring valid reservations.

        This method processes a `reserve_get` request by validating that the calling
        process has a matching reservation. It retrieves the corresponding item from
        the store while maintaining the correct order of reservations.

        Args:
            get_event (simpy.Event): The event associated with the reservation request.

        Returns:
            item (object): The retrieved item if successful.

        Raises:
            RuntimeError: If the process does not have a valid reservation ie, if the get_event is not in the reservations_gett list
            ValueError: If the reserved item is not found in the store.
        """

        # Locate the reservation event for the current process
        reserved_event = next(
            (event for event in self.reservations_get
            if event == get_event and event.requesting_process == self.env.active_process),
            None
        )

        if reserved_event is None:
            raise RuntimeError(
                f"Time {self.env.now:.2f}, No matching reservation found for process {self.env.active_process}."
            )

        # Identify the corresponding item in the reserved events list
        if self.mode == 'FIFO':
            item_index = self.reserved_events.index(reserved_event)
            self.reservations_get.remove(reserved_event)

            # Retrieve the assigned item and remove it from storage
            assigned_item = self.ready_items.pop(item_index)
            self.reserved_events.pop(item_index)

        if assigned_item is None:
            raise ValueError(f"Reserved item for {get_event} not found in store.")

        return assigned_item  # Successfully retrieved item




    def put(self,put_event,item):
        """
        Perform a `put` operation on the store and trigger any pending `reserve_get` requests.

        Ensures that only processes with a valid reservation can put items into the store.
        If the put operation succeeds, it triggers `_trigger_reserve_get` to process pending get requests.

        Args:
            put_event (simpy.Event): The event corresponding to the reservation.
            item (object): The item to be added to the store.

        Returns:
            proceed (bool): True if the put operation succeeded, False otherwise.

        Raises:
            RuntimeError: If no reservations are available in the reservations_put
            RuntimeError: If proceed is False after put operation
        """
        proceed = False

        if self.reservations_put:
          proceed = self._trigger_put(put_event,item)
        else:
          raise RuntimeError("No matching reservation found for process: reservations_put is empty")

        if proceed:
          #print(f"{self.env.now} proceed")
          #self._trigger_get(None)
          self._trigger_reserve_get(None)
          
        

        if not proceed:

          raise RuntimeError(f"No matching put_event found in the reservations and put failed for{item}")
        else:
          #self._update_time_averaged_level()
          return proceed

    def _trigger_put(self,put_event, item):
        """
        Trigger the `put` operation by checking if there are any active reservations.

        This method ensures that the process attempting to put an item has a valid reservation.
        It delegates the actual put operation to `_do_put`.

        Args:
            put_event (simpy.Event): The event associated with the reservation request.
            item (object): The item to be added to the store.

        Returns:
            bool: True if the item was successfully added, False otherwise.
        """
        proceed= False

        if len(self.reservations_put)>0:
           proceed = self._do_put(put_event,item)
           #print(f"{self.env.now} {self.env.active_process}{proceed}")
        return proceed




    def _do_put(self, put_event, item):
        """
        Execute the actual `put` operation while ensuring only processes with a valid reservation can proceed.

        This method checks whether the active process has a corresponding reservation and then
        attempts to add the item to the store. If the store is full, an exception is raised.

        Args:
            put_event (simpy.Event): The reservation event associated with the put request.
            item (object): The item to be stored.

        Returns:
            proceed (bool): True if the item was successfully added, else raises an error

        Raises:
            RuntimeError: If the process does not have a valid reservation ie, if the put_event is not in the reservations_put list

        """

        # Locate and remove the reservation event efficiently
    
        reserved_event = next(
            (event for event in self.reservations_put if event == put_event and event.requesting_process == self.env.active_process),
            None
        )

        if reserved_event is None:
            raise RuntimeError(
                f"Time {self.env.now:.2f}, No matching reservation found "
                f"for process {self.env.active_process} in reservations_put."
            )

        self.reservations_put.remove(reserved_event)

        # Add the item if space is available
        if len(self.items)+len(self.ready_items) < self.capacity:
            self.items.append(item)
            self._update_time_averaged_level()
            #self.env.process(self.move_to_ready_items(item))
            #self.env.process(self._add_trigger_event(item))
            # Start the move process and track it
            move_process = self.env.process(self.move_to_ready_items(item))
            item_id = item[0].id if hasattr(item[0], 'id') else str(id(item))
            self.active_move_processes[item_id] = {
                'process': move_process,
                'item': item,
                'start_time': self.env.now
            }
            
            # Handle selective interruption for new items during no accumulation mode
            if self.noaccumulation_mode_on:
                self.handle_new_item_during_interruption(item)
            
            return True  # Successfully added item
        
        
    def move_to_ready_items(self, item):
        """
        Move items from the store to the ready_items list after a put operation.
        This method is called as a process to ensure that items are moved asynchronously.
        Handles interrupts when state changes to stalled and resumes when state changes back.
        Movement is split into two phases:
        1. First phase: item[0].length/self.speed time (time for item to fully enter belt)
        2. Second phase: remaining time (time for item to reach exit)
        """
        item_id = item[0].id if hasattr(item[0], 'id') else str(id(item))
        event=self.env.event()
        #self.delay=item[0].length/self.speed
        #print(f"created Added event suceeded{self.delay}")
        event.callbacks.append(self._trigger_reserve_put)# after putting an item, an event is created and will be triggered ater delay amount of time to allow waiting get calls to succeed in a stalled belt
        #event.callbacks.append(self._trigger_put)# this may not be needed
       
        #print(f"{self.env.now}Added event suceed        ed")
        
        # Calculate the two phases of movement
        phase1_time = item[0].length / self.speed  # Time for item to fully enter belt
        phase2_time = item[1] - phase1_time        # Remaining time to reach exit
        
        try:
            # Move items to the ready_items list
            if self.items:
                print(f"T={self.env.now:.2f} beltstore received an item {item[0].id, item[1]} . Item started moving in belt")
                
                # Phase 1: Item entering the belt (length/speed time)
                remaining_phase1_time = phase1_time
                print(f"T={self.env.now:.2f} Item {item_id} starting Phase 1 (entering belt): {phase1_time:.2f} time")
                
                while remaining_phase1_time > 0:
                    try:
                        start_time = self.env.now
                        yield self.env.timeout(remaining_phase1_time)
                        # If we reach here, phase 1 completed without interruption
                        event.succeed()
                        remaining_phase1_time = 0
                        break
                    except simpy.Interrupt as interrupt:
                        # Calculate how much time has passed
                        elapsed_time = self.env.now - start_time
                        remaining_phase1_time -= elapsed_time
                        
                        print(f"T={self.env.now:.2f} Move process Phase 1 for item {item_id} interrupted: {interrupt.cause}")
                        print(f"T={self.env.now:.2f} Remaining Phase 1 time for item {item_id}: {remaining_phase1_time:.2f}")
                        
                        # Wait for resume signal
                        print(f"T={self.env.now:.2f} Item {item_id} waiting for resume signal (Phase 1)...")
                        yield self.resume_event
                        print(f"T={self.env.now:.2f} Item {item_id} resuming Phase 1 movement with {remaining_phase1_time:.2f} time remaining")
                
                print(f"T={self.env.now:.2f} Item {item_id} completed Phase 1 (fully entered belt)")
                
                # Phase 2: Item moving through the belt to exit
                remaining_phase2_time = phase2_time
                print(f"T={self.env.now:.2f} Item {item_id} starting Phase 2 (moving to exit): {phase2_time:.2f} time")
                
                while remaining_phase2_time > 0:
                    try:
                        start_time = self.env.now
                        yield self.env.timeout(remaining_phase2_time)
                        # If we reach here, phase 2 completed without interruption
                        remaining_phase2_time = 0
                        break
                    except simpy.Interrupt as interrupt:
                        # Calculate how much time has passed
                        elapsed_time = self.env.now - start_time
                        remaining_phase2_time -= elapsed_time
                        
                        print(f"T={self.env.now:.2f} Move process Phase 2 for item {item_id} interrupted: {interrupt.cause}")
                        print(f"T={self.env.now:.2f} Remaining Phase 2 time for item {item_id}: {remaining_phase2_time:.2f}")
                        
                        # Wait for resume signal
                        print(f"T={self.env.now:.2f} Item {item_id} waiting for resume signal (Phase 2)...")
                        yield self.resume_event
                        print(f"T={self.env.now:.2f} Item {item_id} resuming Phase 2 movement with {remaining_phase2_time:.2f} time remaining")
                
                print(f"T={self.env.now:.2f} Item {item_id} completed Phase 2 (reached exit)")
                print(f"T={self.env.now:.2f} bufferstore finished moving item {item[0].id, item[1]} going to ready_items")
                
                item_index = self.items.index(item)
                item_to_put = self.items.pop(item_index)  # Remove the item
                
                if len(self.ready_items) + len(self.items) < self.capacity:
                    self.ready_items.append(item_to_put[0])
                    self.ready_item_event.succeed()  # Notify that a new item is ready
                    print(f"T={self.env.now:.2f} bufferstore finished moving item {item[0].id, item[1]} moved to ready_items")
                    self._trigger_reserve_get(None)
                    self._trigger_reserve_put(None)
                else:
                    raise RuntimeError("Total number of items in the store exceeds capacity. Cannot move item to ready_items.")
            
            
            
        
        finally:
            # Clean up the process tracking when done
            if item_id in self.active_move_processes:
                del self.active_move_processes[item_id]
                print(f"T={self.env.now:.2f} Removed tracking for completed move process of item {item_id}")

    def interrupt_all_move_processes(self, reason="External interrupt"):
        """
        Interrupt all active move_to_ready_items processes.
        
        Args:
            reason (str): Reason for the interrupt
        """
        print(f"T={self.env.now:.2f} BufferStore interrupting {len(self.active_move_processes)} move processes - {reason}")
        
        for item_id, process_info in self.active_move_processes.items():
            process = process_info['process']
            if process and not process.processed:
                try:
                    process.interrupt(reason)
                    print(f"T={self.env.now:.2f} Interrupted move process for item {item_id}")
                except RuntimeError:
                    # Process might already be finished
                    pass
    
    def resume_all_move_processes(self):
        """
        Resume all interrupted move_to_ready_items processes.
        """
        print(f"T={self.env.now:.2f} BufferStore resuming move processes")
        
        # Create a new resume event and trigger it
        old_resume_event = self.resume_event
        self.resume_event = self.env.event()
        old_resume_event.succeed()
    
    def _get_belt_pattern(self):
        """
        Generate a pattern string representing the current belt occupancy.
        Returns a string where '*' represents an item and '_' represents empty space.
        """
        # Create a representation of the belt with capacity positions
        belt_positions = ['_'] * self.capacity
        
        # Mark positions with items
        # Items in self.items are still moving, items in ready_items are at the end
        num_moving_items = len(self.items)
        num_ready_items = len(self.ready_items)
        
        # Place moving items based on their current position on the belt
        for i, item in enumerate(self.items):
            if i < self.capacity:
                # Calculate position based on time since entry and belt speed
                if hasattr(item[0], 'conveyor_entry_time'):
                    time_on_belt = self.env.now - item[0].conveyor_entry_time
                    # Assuming each position takes 1 time unit to traverse
                    position = int(time_on_belt * self.speed)
                    if 0 <= position < self.capacity:
                        belt_positions[position] = '*'
                else:
                    raise AttributeError("Item does not have 'conveyor_entry_time' attribute.")
        
        # Place ready items at the end of the belt
        for i in range(num_ready_items):
            pos = self.capacity - 1 - i
            if pos >= 0:
                belt_positions[pos] = '*'
        
        return ''.join(belt_positions)
    
    def selective_interrupt(self, reason="Selective interrupt"):
        """
        Perform selective interruption based on belt occupancy patterns and mode.
        
        When noaccumulation_mode_on=True (STALLED_NONACCUMULATING_STATE):
        - Interrupt all items immediately
        
        When noaccumulation_mode_on=False (STALLED_ACCUMULATING_STATE):
        - Use pattern-based interruption with delays based on item positions
        
        Pattern-based rules for accumulating mode:
        - For patterns like '_****', interrupt all items.
        - For patterns like '_*_*_', interrupt item in second last position after 1 delay,
          and second item after 2 delays.
        - For patterns like '*___*', interrupt first item and second item after 3 delays.
        - For patterns like '**__*', interrupt first item, second after 2 delays,
          and third after 2 delays.
        
        Args:
            reason (str): Reason for the interrupt
        """
        if not self.items:
            print(f"T={self.env.now:.2f} No items on belt to interrupt")
            return
        
        # If noaccumulation_mode_on is True (STALLED_NONACCUMULATING_STATE), interrupt all items immediately
        if self.noaccumulation_mode_on:
            print(f"T={self.env.now:.2f} No accumulation mode: interrupting all items immediately")
            for i, item in enumerate(self.items):
                item_id = item[0].id if hasattr(item[0], 'id') else str(id(item))
                self._interrupt_specific_item(item_id, f"{reason} - immediate (no accumulation)")
            return
        
        # For accumulating mode (STALLED_ACCUMULATING_STATE), use pattern-based interruption
        print(f"T={self.env.now:.2f} Accumulating mode: using pattern-based interruption")
        
        # Get current belt pattern
        pattern = self._get_belt_pattern()
        print(f"T={self.env.now:.2f} Current belt pattern: {pattern}")
        
        # Analyze pattern and determine interruption strategy
        interruption_plan = self._analyze_pattern_for_interruption(pattern)
        
        if not interruption_plan:
            print(f"T={self.env.now:.2f} No interruption needed for current pattern")
            return
        
        print(f"T={self.env.now:.2f} Executing selective interruption plan: {interruption_plan}")
        
        # Execute the interruption plan
        self._execute_interruption_plan(interruption_plan, reason)

    def _analyze_pattern_for_interruption(self, pattern):
        """
        Analyze the belt pattern and determine which items to interrupt and when.
        
        Args:
            pattern (str): Belt pattern string with '*' for items and '_' for empty spaces
            
        Returns:
            list: List of dictionaries with interruption instructions
                  [{'item_index': int, 'delay': float}, ...]
        """
        interruption_plan = []
        
        # Find all item positions
        item_positions = [i for i, char in enumerate(pattern) if char == '*']
        
        if not item_positions:
            return interruption_plan
        
        # Check for consecutive items pattern (like '_****' or '**__*')
        if self._has_consecutive_items(pattern):
            # Rule: Interrupt all items in consecutive blocks
            for i, pos in enumerate(item_positions):
                interruption_plan.append({'item_index': i, 'delay': 0})
        else:
            # Rule: Interrupt items with delays based on gaps
            interruption_plan = self._calculate_gap_based_interruptions(pattern, item_positions)
        
        return interruption_plan

    def _has_consecutive_items(self, pattern):
        """
        Check if the pattern has consecutive items (no gaps between items).
        """
        item_positions = [i for i, char in enumerate(pattern) if char == '*']
        
        if len(item_positions) <= 1:
            return True
        
        # Check if positions are consecutive
        for i in range(1, len(item_positions)):
            if item_positions[i] - item_positions[i-1] > 1:
                return False
        
        return True

    def _calculate_gap_based_interruptions(self, pattern, item_positions):
        """
        Calculate interruption delays based on gaps between items.
        
        For patterns with gaps:
        - First item: interrupt immediately
        - Subsequent items: delay = number of empty spaces before this item from the previous item
        """
        interruption_plan = []
        
        if not item_positions:
            return interruption_plan
        
        # First item always interrupted immediately
        interruption_plan.append({'item_index': 0, 'delay': 0})
        
        # Calculate delays for subsequent items
        for i in range(1, len(item_positions)):
            prev_pos = item_positions[i-1]
            curr_pos = item_positions[i]
            gap_size = curr_pos - prev_pos - 1  # Number of empty spaces between items
            
            # Delay is based on gap size
            delay = max(gap_size, 1)  # Minimum delay of 1
            interruption_plan.append({'item_index': i, 'delay': delay})
        
        return interruption_plan

    def _execute_interruption_plan(self, interruption_plan, reason):
        """
        Execute the interruption plan by interrupting items with specified delays.
        
        Args:
            interruption_plan (list): List of interruption instructions
            reason (str): Reason for interruption
        """
        for instruction in interruption_plan:
            item_index = instruction['item_index']
            delay = instruction['delay']
            
            if item_index < len(self.items):
                item = self.items[item_index]
                item_id = item[0].id if hasattr(item[0], 'id') else str(id(item))
                
                if delay > 0:
                    # Schedule delayed interruption
                    self.env.process(self._delayed_interrupt(item_id, delay, reason))
                else:
                    # Immediate interruption
                    self._interrupt_specific_item(item_id, reason)

    def _delayed_interrupt(self, item_id, delay, reason):
        """
        Process to handle delayed interruption of a specific item.
        
        Args:
            item_id: ID of the item to interrupt
            delay (float): Delay before interruption
            reason (str): Reason for interruption
        """
        try:
            yield self.env.timeout(delay)
            self._interrupt_specific_item(item_id, f"{reason} (delayed by {delay})")
        except simpy.Interrupt:
            print(f"T={self.env.now:.2f} Delayed interrupt process for item {item_id} was itself interrupted")

    def _interrupt_specific_item(self, item_id, reason):
        """
        Interrupt a specific item's move process.
        
        Args:
            item_id: ID of the item to interrupt
            reason (str): Reason for interruption
        """
        if item_id in self.active_move_processes:
            process_info = self.active_move_processes[item_id]
            process = process_info['process']
            
            if process and not process.processed:
                try:
                    process.interrupt(reason)
                    print(f"T={self.env.now:.2f} Selectively interrupted item {item_id}: {reason}")
                except RuntimeError:
                    print(f"T={self.env.now:.2f} Could not interrupt item {item_id} - process may be finished")
            else:
                print(f"T={self.env.now:.2f} Item {item_id} process already finished")
        else:
            print(f"T={self.env.now:.2f} Item {item_id} not found in active processes")

    def handle_new_item_during_interruption(self, item):
        """
        Handle new items arriving during selective interruption.
        
        For new items, the delay before interruption is: capacity - num_items
        
        Args:
            item: The new item being added
        """
        if self.noaccumulation_mode_on:
            num_items = len(self.items) + len(self.ready_items)
            delay_before_interrupt = max(self.capacity - num_items, 0)
            
            item_id = item[0].id if hasattr(item[0], 'id') else str(id(item))
            
            if delay_before_interrupt > 0:
                print(f"T={self.env.now:.2f} New item {item_id} will be interrupted after {delay_before_interrupt} time units")
                self.env.process(self._delayed_interrupt(item_id, delay_before_interrupt, "New item during interruption"))
            else:
                print(f"T={self.env.now:.2f} New item {item_id} interrupted immediately")
                self._interrupt_specific_item(item_id, "New item during interruption")