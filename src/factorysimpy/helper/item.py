class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, id):
        self.id = id
        self.timestamp_creatiom_ = None
        self.timestamp_destruction = None
        self.timestamp_node_entry = None
        self.timestamp_node_exit = None
        self.payload = None
        

    def __repr__(self):
        return f"Item({self.id})"