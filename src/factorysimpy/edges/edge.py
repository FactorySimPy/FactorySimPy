import simpy
import Split
import Joint
import Node

class Edge:
  def __init__(self,env, name):
    self.env=env

    self.name=name
    self.state=None
    self.src_node=None
    self.dest_node=None

  def connect(self,src,dest):
    self.src_node=src
    self.dest_node=dest
    #if self.src_node is not None and self.src_node is not self:
    if not isinstance(self.src_node, Split):
        # Check if out_edges is None or already configured
        assert self.src_node.out_edges is None or self in self.src_node.out_edges, (
            f"{self.src_node} is already connected to another edge"
        )
    else:
        # Allow up to 2 connections for Split, accounting for self already being present
        assert len(self.src_node.out_edges) < 2 or self in self.src_node.out_edges, (
            f"{self.src_node} already has more than 2 edges connected"
        )

    if not isinstance(self.dest_node, Joint):
      assert self.dest_node.in_edges is None or self in self.dest_node.in_edges, (f"{self.dest_node} is already connected")
    else:
      assert self.dest_node.in_edges <2 or self in self.dest_node.in_edges,  (f"{self.dest_node} already has more than 2 edges connected")
    # Add this edge to the source node's out_edges if not already present
    if self.src_node.out_edges is None:
        self.src_node.out_edges = []
    if self not in self.src_node.out_edges:
        self.src_node.out_edges.append(self)

    # Add this edge to the destination node's in_edges if not already present
    if self.dest_node.in_edges is None:
        self.dest_node.in_edges = []
    if self not in self.dest_node.in_edges:
        self.dest_node.in_edges.append(self)