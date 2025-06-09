from item import Item

class Pallet(Item):
    """A class representing a pallet, which can hold multiple items."""
    def __init__(self, id):
        super().__init__(id)
        self.item_type = "Pallet"
        self.items = []  # List to hold contained items

    def add_item(self, item):
        """Add an item to the pallet."""
        self.items.append(item)

    def remove_item(self):
        """Remove an item from the pallet if present."""
        if self.items:
            item = self.items.pop(-1)  # Remove the last item
            return item
        return None

    def __repr__(self):
        return f"Pallet({self.id}, items={len(self.items)})"