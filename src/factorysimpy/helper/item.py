class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, name):
        self.name = name
        

    def __repr__(self):
        return f"Item({self.name})"