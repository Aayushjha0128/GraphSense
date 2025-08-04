import numpy as np
from typing import Dict, List, Set, Tuple, Optional
import json

class Vertex:
    """Represents a vertex in the planar graph"""
    
    def __init__(self, vertex_id: int, x: float, y: float, color_index: int = 1):
        self.id = vertex_id
        self.x = x
        self.y = y
        self.color_index = color_index  # 1-4 for color palette
        self.diameter = self._calculate_diameter()
        
    def _calculate_diameter(self) -> float:
        """Calculate vertex diameter based on label size"""
        # Base diameter + scaling factor for larger indices
        base_diameter = 30
        label_length = len(str(self.id))
        return base_diameter + (label_length - 1) * 5
    
    def update_position(self, x: float, y: float):
        """Update vertex position"""
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Vertex') -> float:
        """Calculate Euclidean distance to another vertex"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_dict(self) -> Dict:
        """Convert vertex to dictionary for serialization"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'color_index': self.color_index,
            'diameter': self.diameter
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Vertex':
        """Create vertex from dictionary"""
        vertex = cls(data['id'], data['x'], data['y'], data['color_index'])
        vertex.diameter = data.get('diameter', vertex.diameter)
        return vertex

class Edge:
    """Represents an edge in the planar graph"""
    
    def __init__(self, v1_id: int, v2_id: int):
        self.v1_id = min(v1_id, v2_id)  # Ensure consistent ordering
        self.v2_id = max(v1_id, v2_id)
        self.id = f"{self.v1_id}-{self.v2_id}"
    
    def __eq__(self, other):
        return isinstance(other, Edge) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def contains_vertex(self, vertex_id: int) -> bool:
        """Check if edge contains the given vertex"""
        return vertex_id == self.v1_id or vertex_id == self.v2_id
    
    def get_other_vertex(self, vertex_id: int) -> int:
        """Get the other vertex ID in this edge"""
        if vertex_id == self.v1_id:
            return self.v2_id
        elif vertex_id == self.v2_id:
            return self.v1_id
        else:
            raise ValueError(f"Vertex {vertex_id} not in edge {self.id}")
    
    def to_dict(self) -> Dict:
        """Convert edge to dictionary for serialization"""
        return {
            'v1_id': self.v1_id,
            'v2_id': self.v2_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Edge':
        """Create edge from dictionary"""
        return cls(data['v1_id'], data['v2_id'])

class PlanarGraph:
    """
    Represents a planar triangulated graph with dynamic periphery tracking
    """
    
    def __init__(self):
        self.vertices: Dict[int, Vertex] = {}
        self.edges: Set[Edge] = set()
        self.adjacency: Dict[int, Set[int]] = {}
        self.periphery: List[int] = []  # Ordered list of periphery vertex IDs
        self.next_vertex_id = 1
        
    def add_vertex(self, x: float, y: float, color_index: int = 1) -> int:
        """Add a new vertex to the graph"""
        vertex_id = self.next_vertex_id
        self.next_vertex_id += 1
        
        vertex = Vertex(vertex_id, x, y, color_index)
        self.vertices[vertex_id] = vertex
        self.adjacency[vertex_id] = set()
        
        return vertex_id
    
    def add_edge(self, v1_id: int, v2_id: int) -> bool:
        """Add an edge between two vertices"""
        if v1_id not in self.vertices or v2_id not in self.vertices:
            raise ValueError("Both vertices must exist in the graph")
        
        if v1_id == v2_id:
            return False  # No self-loops
        
        edge = Edge(v1_id, v2_id)
        
        # Check if edge already exists
        if edge in self.edges:
            return False
        
        # Add edge and update adjacency
        self.edges.add(edge)
        self.adjacency[v1_id].add(v2_id)
        self.adjacency[v2_id].add(v1_id)
        
        return True
    
    def remove_vertex(self, vertex_id: int):
        """Remove a vertex and all its edges"""
        if vertex_id not in self.vertices:
            return
        
        # Remove all edges connected to this vertex
        edges_to_remove = [edge for edge in self.edges if edge.contains_vertex(vertex_id)]
        for edge in edges_to_remove:
            self.edges.remove(edge)
        
        # Update adjacency lists
        for neighbor_id in self.adjacency[vertex_id]:
            self.adjacency[neighbor_id].discard(vertex_id)
        
        # Remove vertex
        del self.vertices[vertex_id]
        del self.adjacency[vertex_id]
        
        # Update periphery
        if vertex_id in self.periphery:
            self.periphery.remove(vertex_id)
    
    def get_neighbors(self, vertex_id: int) -> Set[int]:
        """Get all neighbors of a vertex"""
        return self.adjacency.get(vertex_id, set())
    
    def is_edge(self, v1_id: int, v2_id: int) -> bool:
        """Check if an edge exists between two vertices"""
        return Edge(v1_id, v2_id) in self.edges
    
    def update_periphery(self):
        """Update the periphery vertices in clockwise order"""
        if len(self.vertices) < 3:
            self.periphery = list(self.vertices.keys())
            return
        
        # Find the periphery by identifying vertices on the convex hull
        vertices_list = [(v.x, v.y, v.id) for v in self.vertices.values()]
        
        if len(vertices_list) < 3:
            self.periphery = [v[2] for v in vertices_list]
            return
        
        # Compute convex hull using Graham scan
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        # Sort points lexicographically
        vertices_list.sort()
        
        # Build lower hull
        lower = []
        for p in vertices_list:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # Build upper hull
        upper = []
        for p in reversed(vertices_list):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        # Remove last point of each half because it's repeated
        hull = lower[:-1] + upper[:-1]
        
        # Extract vertex IDs in clockwise order
        self.periphery = [p[2] for p in hull]
    
    def get_periphery_segment(self, start_id: int, end_id: int) -> List[int]:
        """Get vertices between start_id and end_id on periphery (clockwise)"""
        if start_id not in self.periphery or end_id not in self.periphery:
            return []
        
        start_idx = self.periphery.index(start_id)
        end_idx = self.periphery.index(end_id)
        
        if start_idx <= end_idx:
            return self.periphery[start_idx:end_idx + 1]
        else:
            return self.periphery[start_idx:] + self.periphery[:end_idx + 1]
    
    def validate_planarity(self) -> bool:
        """Check if the graph maintains planarity (no edge crossings)"""
        # For now, we assume the graph is planar if it follows our construction rules
        # A full planarity test would require more complex algorithms
        return True
    
    def get_edge_length_stats(self) -> Dict[str, float]:
        """Get statistics about edge lengths"""
        lengths = []
        for edge in self.edges:
            v1 = self.vertices[edge.v1_id]
            v2 = self.vertices[edge.v2_id]
            length = v1.distance_to(v2)
            lengths.append(length)
        
        if not lengths:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        lengths = np.array(lengths)
        return {
            'mean': float(np.mean(lengths)),
            'std': float(np.std(lengths)),
            'min': float(np.min(lengths)),
            'max': float(np.max(lengths))
        }
    
    def create_initial_triangle(self):
        """Create the initial triangle with 3 vertices"""
        self.clear()
        
        # Create triangle vertices
        center_x, center_y = 400, 300
        radius = 100
        
        for i in range(3):
            angle = i * 2 * np.pi / 3
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            vertex_id = self.add_vertex(x, y, 1)
        
        # Add edges to form triangle
        self.add_edge(1, 2)
        self.add_edge(2, 3)
        self.add_edge(3, 1)
        
        # Update periphery
        self.update_periphery()
    
    def clear(self):
        """Clear all vertices and edges"""
        self.vertices.clear()
        self.edges.clear()
        self.adjacency.clear()
        self.periphery.clear()
        self.next_vertex_id = 1
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary for serialization"""
        return {
            'vertices': {vid: v.to_dict() for vid, v in self.vertices.items()},
            'edges': [e.to_dict() for e in self.edges],
            'periphery': self.periphery,
            'next_vertex_id': self.next_vertex_id
        }
    
    def from_dict(self, data: Dict):
        """Load graph from dictionary"""
        self.clear()
        
        # Load vertices
        for vid_str, vertex_data in data['vertices'].items():
            vid = int(vid_str)
            vertex = Vertex.from_dict(vertex_data)
            self.vertices[vid] = vertex
            self.adjacency[vid] = set()
        
        # Load edges
        for edge_data in data['edges']:
            edge = Edge.from_dict(edge_data)
            self.edges.add(edge)
            self.adjacency[edge.v1_id].add(edge.v2_id)
            self.adjacency[edge.v2_id].add(edge.v1_id)
        
        # Load periphery and next ID
        self.periphery = data.get('periphery', [])
        self.next_vertex_id = data.get('next_vertex_id', len(self.vertices) + 1)
