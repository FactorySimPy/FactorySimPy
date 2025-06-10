from factorysimpy.helper.baseflowitem import BaseFlowItem

class Item(BaseFlowItem):
    """A class representing a pallet, which can hold multiple items."""
    def __init__(self, id):
        super().__init__(id)
        self.flow_item_type = "item"
     

