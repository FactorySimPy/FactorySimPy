class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, name, ready=True):
        self.name = name
        self.ready = ready  # Flag indicating if the item is ready for processing

    def __repr__(self):
        return f"Item({self.name}, ready={self.ready})"