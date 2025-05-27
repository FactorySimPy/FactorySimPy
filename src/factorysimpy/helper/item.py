class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, id):
        self.id = id
        

    def __repr__(self):
        return f"Item({self.id})"