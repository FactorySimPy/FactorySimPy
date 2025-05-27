# src/ReservablePriorityReqStore.py



import simpy
from simpy.resources.store import Store

class ReservablePriorityReqStore(Store):
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

    def __init__(self, env, capacity=float('inf')):
        """
        Initializes a reservable store with priority-based reservations.

        Args:
         
            capacity (int, optional): The maximum number of items the store can hold.
                                      Defaults to infinity.
        """
        super().__init__(env, capacity)
        self.env = env
        self.reserve_put_queue = []  # Queue for managing reserve_put reservations
        self.reservations_put = []   # List of successful put reservations
        self.reserve_get_queue = []  # Queue for managing reserve_get reservations
        self.reservations_get = []   # List of successful get reservations
        self.reserved_events = []     # Maintains events corresponding to reserved items to preserve item order


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
            - Logs the reservation status to the console. (currently commented out)

        """
        # Check if there's enough space to reserve
        if len(self.reservations_put) + len(self.items) < self.capacity:
            self.reservations_put.append(event)  # Add reservation
            event.succeed()
            # Log the success of the reservation
            #print(f"At time={self.env.now:.2f}, Process {self.env.active_process} "
                 # f"reserved space. Total reservations: {len(self.reservations_put)}")

            # Mark the event as successful

        #else:
            #print(f"At {self.env.now:.2f}, Reservation failed for {self.env.active_process} "
             #     f"on {self}. Store is full.")


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
        self.items.insert(delta_position, item_to_shift)
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
        if len(self.reservations_get) < len(self.items):
            # Successful reservation; add to reservations list
            self.reservations_get.append(event)
            event.succeed()  # Immediately succeed the event

            #reserving the item to preserved item order by adding the reserve_get event to a list(the index position of event= index position of reserved item)
            self.reserved_events.append(event)




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
        item_index = self.reserved_events.index(reserved_event)
        self.reservations_get.remove(reserved_event)

        # Retrieve the assigned item and remove it from storage
        assigned_item = self.items.pop(item_index)
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
          
        #if the put operation is not successful, then raise an erro

        if not proceed:

          raise RuntimeError(f"No matching put_event found in the reservations and put failed for{item}")
        else:
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
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True  # Successfully added item
        



        