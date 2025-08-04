import numpy as np
import math
from typing import List, Tuple, Dict, Optional
from graph_model import PlanarGraph, Vertex

class GeometryEngine:
    """
    Handles all geometric calculations for the planar graph
    """
    
    def __init__(self):
        self.min_angle = math.radians(60)  # Minimum angle constraint
        self.edge_length_tolerance = 0.2  # ±20% edge length variation
        self.vertex_separation = 20  # Minimum distance between vertices
    
    def calculate_vertex_position(self, graph: PlanarGraph, periphery_start: int, 
                                periphery_end: int) -> Tuple[float, float]:
        """
        Calculate optimal position for a new vertex connecting to periphery segment
        """
        # Get periphery segment vertices
        segment = graph.get_periphery_segment(periphery_start, periphery_end)
        
        if len(segment) < 2:
            raise ValueError("Invalid periphery segment")
        
        # Calculate centroid of the segment
        segment_vertices = [graph.vertices[vid] for vid in segment]
        centroid_x = sum(v.x for v in segment_vertices) / len(segment_vertices)
        centroid_y = sum(v.y for v in segment_vertices) / len(segment_vertices)
        
        # Calculate desired distance from centroid
        avg_edge_length = self._calculate_average_edge_length(graph)
        if avg_edge_length == 0:
            avg_edge_length = 80  # Default edge length
        
        # Find direction perpendicular to the segment
        start_vertex = graph.vertices[periphery_start]
        end_vertex = graph.vertices[periphery_end]
        
        # Vector from start to end
        segment_vector = np.array([end_vertex.x - start_vertex.x, 
                                 end_vertex.y - start_vertex.y])
        
        # Perpendicular vector (outward from graph)
        if np.linalg.norm(segment_vector) > 0:
            segment_vector = segment_vector / np.linalg.norm(segment_vector)
            perpendicular = np.array([-segment_vector[1], segment_vector[0]])
        else:
            perpendicular = np.array([0, 1])
        
        # Determine which direction is outward
        graph_center = self._calculate_graph_center(graph)
        to_center = np.array([graph_center[0] - centroid_x, graph_center[1] - centroid_y])
        
        # Choose perpendicular direction away from center
        if np.dot(perpendicular, to_center) > 0:
            perpendicular = -perpendicular
        
        # Calculate position
        distance = avg_edge_length * 1.1  # Slightly longer for convexity
        new_x = centroid_x + perpendicular[0] * distance
        new_y = centroid_y + perpendicular[1] * distance
        
        # Ensure minimum separation from existing vertices
        new_x, new_y = self._ensure_vertex_separation(graph, new_x, new_y)
        
        return new_x, new_y
    
    def calculate_random_vertex_position(self, graph: PlanarGraph) -> Tuple[int, int, float, float]:
        """
        Calculate position for a random vertex on the periphery
        """
        if len(graph.periphery) < 2:
            raise ValueError("Need at least 2 periphery vertices")
        
        # Choose random adjacent pair on periphery
        import random
        start_idx = random.randint(0, len(graph.periphery) - 1)
        end_idx = (start_idx + 1) % len(graph.periphery)
        
        periphery_start = graph.periphery[start_idx]
        periphery_end = graph.periphery[end_idx]
        
        x, y = self.calculate_vertex_position(graph, periphery_start, periphery_end)
        
        return periphery_start, periphery_end, x, y
    
    def apply_redraw_logic(self, graph: PlanarGraph):
        """
        Apply redraw logic to maintain convexity and uniform edge lengths
        """
        if len(graph.vertices) < 3:
            return
        
        # Update periphery first
        graph.update_periphery()
        
        # Rebalance angular spacing
        self._rebalance_angular_spacing(graph)
        
        # Adjust edge lengths
        self._adjust_edge_lengths(graph)
        
        # Maintain convex contour
        self._maintain_convex_contour(graph)
        
        # Update vertex diameters if needed
        self._update_vertex_diameters(graph)
    
    def _rebalance_angular_spacing(self, graph: PlanarGraph):
        """Rebalance angular spacing between connected vertices"""
        for vertex_id, vertex in graph.vertices.items():
            neighbors = list(graph.get_neighbors(vertex_id))
            
            if len(neighbors) < 2:
                continue
            
            # Calculate current angles to neighbors
            angles = []
            for neighbor_id in neighbors:
                neighbor = graph.vertices[neighbor_id]
                angle = math.atan2(neighbor.y - vertex.y, neighbor.x - vertex.x)
                angles.append((angle, neighbor_id))
            
            # Sort by angle
            angles.sort()
            
            # Check for sharp angles and adjust if needed
            for i in range(len(angles)):
                curr_angle = angles[i][0]
                next_angle = angles[(i + 1) % len(angles)][0]
                
                angle_diff = next_angle - curr_angle
                if angle_diff < 0:
                    angle_diff += 2 * math.pi
                
                if angle_diff < self.min_angle:
                    # Adjust positions to meet minimum angle requirement
                    self._adjust_for_minimum_angle(graph, vertex_id, angles[i][1], angles[(i + 1) % len(angles)][1])
    
    def _adjust_edge_lengths(self, graph: PlanarGraph):
        """Adjust vertex positions to maintain uniform edge lengths"""
        target_length = self._calculate_average_edge_length(graph)
        
        if target_length == 0:
            return
        
        # Iterative adjustment
        for iteration in range(3):  # Limit iterations to prevent excessive computation
            for edge in graph.edges:
                v1 = graph.vertices[edge.v1_id]
                v2 = graph.vertices[edge.v2_id]
                
                current_length = v1.distance_to(v2)
                length_ratio = current_length / target_length
                
                # Only adjust if outside tolerance
                if abs(length_ratio - 1.0) > self.edge_length_tolerance:
                    # Move vertices closer to target length
                    center_x = (v1.x + v2.x) / 2
                    center_y = (v1.y + v2.y) / 2
                    
                    direction = np.array([v2.x - v1.x, v2.y - v1.y])
                    if np.linalg.norm(direction) > 0:
                        direction = direction / np.linalg.norm(direction)
                        
                        half_target = target_length / 2
                        
                        v1.update_position(center_x - direction[0] * half_target,
                                         center_y - direction[1] * half_target)
                        v2.update_position(center_x + direction[0] * half_target,
                                         center_y + direction[1] * half_target)
    
    def _maintain_convex_contour(self, graph: PlanarGraph):
        """Ensure the periphery maintains a convex contour"""
        if len(graph.periphery) < 3:
            return
        
        # Check each triplet of consecutive periphery vertices
        for i in range(len(graph.periphery)):
            prev_id = graph.periphery[i - 1]
            curr_id = graph.periphery[i]
            next_id = graph.periphery[(i + 1) % len(graph.periphery)]
            
            prev_vertex = graph.vertices[prev_id]
            curr_vertex = graph.vertices[curr_id]
            next_vertex = graph.vertices[next_id]
            
            # Calculate cross product to check convexity
            cross = self._cross_product_2d(
                (curr_vertex.x - prev_vertex.x, curr_vertex.y - prev_vertex.y),
                (next_vertex.x - curr_vertex.x, next_vertex.y - curr_vertex.y)
            )
            
            # If cross product is negative, we have a concave angle
            if cross < 0:
                # Adjust current vertex position to maintain convexity
                self._adjust_for_convexity(graph, prev_id, curr_id, next_id)
    
    def _calculate_average_edge_length(self, graph: PlanarGraph) -> float:
        """Calculate the average edge length in the graph"""
        if not graph.edges:
            return 0
        
        total_length = 0
        for edge in graph.edges:
            v1 = graph.vertices[edge.v1_id]
            v2 = graph.vertices[edge.v2_id]
            total_length += v1.distance_to(v2)
        
        return total_length / len(graph.edges)
    
    def _calculate_graph_center(self, graph: PlanarGraph) -> Tuple[float, float]:
        """Calculate the center point of the graph"""
        if not graph.vertices:
            return 0, 0
        
        total_x = sum(v.x for v in graph.vertices.values())
        total_y = sum(v.y for v in graph.vertices.values())
        
        return total_x / len(graph.vertices), total_y / len(graph.vertices)
    
    def _ensure_vertex_separation(self, graph: PlanarGraph, x: float, y: float) -> Tuple[float, float]:
        """Ensure new vertex position maintains minimum separation from existing vertices"""
        for vertex in graph.vertices.values():
            distance = math.sqrt((x - vertex.x)**2 + (y - vertex.y)**2)
            if distance < self.vertex_separation:
                # Move away from the conflicting vertex
                direction = np.array([x - vertex.x, y - vertex.y])
                if np.linalg.norm(direction) > 0:
                    direction = direction / np.linalg.norm(direction)
                    x = vertex.x + direction[0] * self.vertex_separation
                    y = vertex.y + direction[1] * self.vertex_separation
        
        return x, y
    
    def _cross_product_2d(self, v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """Calculate 2D cross product of two vectors"""
        return v1[0] * v2[1] - v1[1] * v2[0]
    
    def _adjust_for_minimum_angle(self, graph: PlanarGraph, center_id: int, 
                                neighbor1_id: int, neighbor2_id: int):
        """Adjust vertex positions to meet minimum angle requirements"""
        # Simplified adjustment - move neighbors slightly to increase angle
        center = graph.vertices[center_id]
        n1 = graph.vertices[neighbor1_id]
        n2 = graph.vertices[neighbor2_id]
        
        # Calculate bisector direction
        v1 = np.array([n1.x - center.x, n1.y - center.y])
        v2 = np.array([n2.x - center.x, n2.y - center.y])
        
        if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
            v1 = v1 / np.linalg.norm(v1)
            v2 = v2 / np.linalg.norm(v2)
            
            # Rotate vectors slightly away from each other
            rotation_angle = self.min_angle / 4
            
            # Rotate v1 clockwise
            cos_a, sin_a = math.cos(-rotation_angle), math.sin(-rotation_angle)
            v1_rot = np.array([v1[0] * cos_a - v1[1] * sin_a,
                              v1[0] * sin_a + v1[1] * cos_a])
            
            # Rotate v2 counter-clockwise
            cos_a, sin_a = math.cos(rotation_angle), math.sin(rotation_angle)
            v2_rot = np.array([v2[0] * cos_a - v2[1] * sin_a,
                              v2[0] * sin_a + v2[1] * cos_a])
            
            # Update positions
            avg_dist = (np.linalg.norm([n1.x - center.x, n1.y - center.y]) + 
                       np.linalg.norm([n2.x - center.x, n2.y - center.y])) / 2
            
            n1.update_position(center.x + v1_rot[0] * avg_dist,
                              center.y + v1_rot[1] * avg_dist)
            n2.update_position(center.x + v2_rot[0] * avg_dist,
                              center.y + v2_rot[1] * avg_dist)
    
    def _adjust_for_convexity(self, graph: PlanarGraph, prev_id: int, 
                             curr_id: int, next_id: int):
        """Adjust vertex position to maintain convexity"""
        prev_vertex = graph.vertices[prev_id]
        curr_vertex = graph.vertices[curr_id]
        next_vertex = graph.vertices[next_id]
        
        # Calculate the position that would make the angle convex
        # Move current vertex slightly outward
        center = self._calculate_graph_center(graph)
        
        # Direction from center to current vertex
        to_curr = np.array([curr_vertex.x - center[0], curr_vertex.y - center[1]])
        
        if np.linalg.norm(to_curr) > 0:
            to_curr = to_curr / np.linalg.norm(to_curr)
            
            # Move vertex outward by a small amount
            adjustment = 10  # pixels
            new_x = curr_vertex.x + to_curr[0] * adjustment
            new_y = curr_vertex.y + to_curr[1] * adjustment
            
            curr_vertex.update_position(new_x, new_y)
    
    def _update_vertex_diameters(self, graph: PlanarGraph):
        """Update vertex diameters based on current indices"""
        for vertex in graph.vertices.values():
            vertex.diameter = vertex._calculate_diameter()
    
    def scale_graph(self, graph: PlanarGraph, scale_factor: float, center: Tuple[float, float]):
        """Scale the entire graph around a center point"""
        for vertex in graph.vertices.values():
            # Translate to origin relative to center
            rel_x = vertex.x - center[0]
            rel_y = vertex.y - center[1]
            
            # Scale
            rel_x *= scale_factor
            rel_y *= scale_factor
            
            # Translate back
            vertex.update_position(center[0] + rel_x, center[1] + rel_y)
    
    def translate_graph(self, graph: PlanarGraph, dx: float, dy: float):
        """Translate the entire graph by the given offset"""
        for vertex in graph.vertices.values():
            vertex.update_position(vertex.x + dx, vertex.y + dy)
    
    def center_graph_in_bounds(self, graph: PlanarGraph, bounds: Tuple[float, float, float, float]):
        """Center the graph within the given bounds (x_min, y_min, x_max, y_max)"""
        if not graph.vertices:
            return
        
        # Calculate current bounding box
        min_x = min(v.x for v in graph.vertices.values())
        max_x = max(v.x for v in graph.vertices.values())
        min_y = min(v.y for v in graph.vertices.values())
        max_y = max(v.y for v in graph.vertices.values())
        
        # Calculate current center
        curr_center_x = (min_x + max_x) / 2
        curr_center_y = (min_y + max_y) / 2
        
        # Calculate target center
        target_center_x = (bounds[0] + bounds[2]) / 2
        target_center_y = (bounds[1] + bounds[3]) / 2
        
        # Calculate graph dimensions
        graph_width = max_x - min_x
        graph_height = max_y - min_y
        bounds_width = bounds[2] - bounds[0]
        bounds_height = bounds[3] - bounds[1]
        
        # Scale to fit with padding
        padding_factor = 0.8  # Use more conservative padding
        scale_factor = 1.0
        
        if graph_width > 0 and graph_height > 0:
            scale_x = (bounds_width * padding_factor) / graph_width
            scale_y = (bounds_height * padding_factor) / graph_height
            scale_factor = min(scale_x, scale_y)
            
            # Apply scaling first (around current center)
            self.scale_graph(graph, scale_factor, (curr_center_x, curr_center_y))
        
        # Recalculate center after scaling
        min_x = min(v.x for v in graph.vertices.values())
        max_x = max(v.x for v in graph.vertices.values())
        min_y = min(v.y for v in graph.vertices.values())
        max_y = max(v.y for v in graph.vertices.values())
        
        curr_center_x = (min_x + max_x) / 2
        curr_center_y = (min_y + max_y) / 2
        
        # Translate to center
        dx = target_center_x - curr_center_x
        dy = target_center_y - curr_center_y
        
        self.translate_graph(graph, dx, dy)
