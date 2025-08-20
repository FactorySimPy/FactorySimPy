class BaseFlowItem:
    """A class representing an item ."""
    def __init__(self, id):
        self.id = id
        self.timestamp_creation = None
        self.timestamp_destruction = None
        self.timestamp_node_entry = None
        self.timestamp_node_exit = None
        self.current_node_id = None
        self.source_id = None      # Track the source node
        self.payload = None
        self.destructed_in_node = None  # Node where item was destructed
        self.stats = {}  # Dictionary to store time spent at each node

    def set_creation(self, source_id, env):
        """Set creation time and source node ID."""
        self.timestamp_creation = env.now
        self.source_id = source_id
    
    def set_destruction(self, node_id,  env):
        """set the destruction time and node of the item."""
        self.timestamp_destruction = env.now
        self.destructed_in_node = node_id

    def update_node_event(self, node_id, env, event_type="entry"):
        """
        Update item details and stats when entering or exiting a node.

        Args:
            node_id (str): The ID of the node.
            env (simpy.Environment): The simulation environment (for current time).
            event_type (str): "entry" or "exit" to specify the event.
        """
        if event_type == "entry":
            self.timestamp_node_entry = env.now
            #print(f"T={self.timestamp_node_entry:.2f}: {self.id} entered node {node_id}")
            self.current_node_id = node_id
        elif event_type == "exit":
            self.timestamp_node_exit = env.now
            # Calculate time spent at the node and update stats
            if self.current_node_id is not None and self.timestamp_node_entry is not None:
                time_spent = self.timestamp_node_exit - self.timestamp_node_entry
                if self.current_node_id in self.stats:
                    self.stats[self.current_node_id] += time_spent
                else:
                    self.stats[self.current_node_id] = time_spent
            #self.current_node_id = None
            #self.timestamp_node_entry = None
            

    def __repr__(self):
        return f"Item({self.id})"