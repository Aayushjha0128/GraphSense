import random
from typing import Tuple, Optional
from graph_model import PlanarGraph
from geometry import GeometryEngine
import streamlit as st

class CommandProcessor:
    """
    Handles all user commands and graph operations
    """
    
    def __init__(self, graph: PlanarGraph, geometry_engine: GeometryEngine):
        self.graph = graph
        self.geometry = geometry_engine
    
    def start_triangle(self) -> bool:
        """
        Execute the 'S' command: Start with base triangle
        """
        try:
            self.graph.create_initial_triangle()
            return True
        except Exception as e:
            st.error(f"Error creating initial triangle: {e}")
            return False
    
    def add_random_vertex(self) -> bool:
        """
        Execute the 'R' command: Add random vertex to periphery
        """
        try:
            if len(self.graph.periphery) < 2:
                st.error("Need at least 2 periphery vertices to add a random vertex")
                return False
            
            # Get random position
            periphery_start, periphery_end, x, y = self.geometry.calculate_random_vertex_position(self.graph)
            
            # Add vertex
            vertex_id = self.graph.add_vertex(x, y, self._get_random_color_index())
            
            # Connect to periphery segment
            segment = self.graph.get_periphery_segment(periphery_start, periphery_end)
            for seg_vertex_id in segment:
                self.graph.add_edge(vertex_id, seg_vertex_id)
            
            # Apply redraw logic
            self.geometry.apply_redraw_logic(self.graph)
            
            st.success(f"Added random vertex {vertex_id} between periphery vertices {periphery_start} and {periphery_end}")
            return True
            
        except Exception as e:
            st.error(f"Error adding random vertex: {e}")
            return False
    
    def add_manual_vertex(self, periphery_start: int, periphery_end: int) -> bool:
        """
        Execute the 'A' command: Add vertex manually between two periphery vertices
        """
        try:
            # Validate periphery vertices
            if periphery_start not in self.graph.periphery:
                st.error(f"Vertex {periphery_start} is not on the periphery")
                return False
            
            if periphery_end not in self.graph.periphery:
                st.error(f"Vertex {periphery_end} is not on the periphery")
                return False
            
            # Check if vertices are adjacent on periphery
            if not self._are_periphery_adjacent(periphery_start, periphery_end):
                st.error(f"Vertices {periphery_start} and {periphery_end} are not adjacent on the periphery")
                return False
            
            # Calculate position
            x, y = self.geometry.calculate_vertex_position(self.graph, periphery_start, periphery_end)
            
            # Add vertex
            vertex_id = self.graph.add_vertex(x, y, self._get_random_color_index())
            
            # Connect to periphery segment
            segment = self.graph.get_periphery_segment(periphery_start, periphery_end)
            for seg_vertex_id in segment:
                self.graph.add_edge(vertex_id, seg_vertex_id)
            
            # Apply redraw logic
            self.geometry.apply_redraw_logic(self.graph)
            
            st.success(f"Added manual vertex {vertex_id} between periphery vertices {periphery_start} and {periphery_end}")
            return True
            
        except Exception as e:
            st.error(f"Error adding manual vertex: {e}")
            return False
    
    def hide_vertices_above_index(self, max_index: int) -> bool:
        """
        Execute the 'G' command: Hide vertices with index > max_index
        """
        try:
            # This is handled in the rendering logic, not by actually removing vertices
            st.success(f"Hiding all vertices with index > {max_index}")
            return True
            
        except Exception as e:
            st.error(f"Error hiding vertices: {e}")
            return False
    
    def center_graph(self, canvas_size: Tuple[int, int]) -> bool:
        """
        Execute the 'C' command: Center and fit graph to screen
        """
        try:
            if not self.graph.vertices:
                st.warning("No vertices to center")
                return False
            
            # Define bounds based on canvas size with generous padding
            padding = 100
            bounds = (padding, padding, canvas_size[0] - padding, canvas_size[1] - padding)
            
            # First reset zoom and pan to get true positions
            st.session_state.zoom_level = 1.0
            st.session_state.pan_offset = [0, 0]
            
            # Center graph in bounds
            self.geometry.center_graph_in_bounds(self.graph, bounds)
            
            st.success("Graph centered and fitted to screen")
            return True
            
        except Exception as e:
            st.error(f"Error centering graph: {e}")
            return False
    
    def toggle_display_mode(self) -> bool:
        """
        Execute the 'T' command: Toggle between color and index display
        """
        try:
            current_mode = st.session_state.get('view_mode', 'color')
            new_mode = 'index' if current_mode == 'color' else 'color'
            st.session_state.view_mode = new_mode
            
            st.success(f"Display mode changed to: {new_mode}")
            return True
            
        except Exception as e:
            st.error(f"Error toggling display mode: {e}")
            return False
    
    def zoom_in(self, factor: float = 1.2) -> bool:
        """
        Execute the 'Z+' command: Zoom in
        """
        try:
            current_zoom = st.session_state.get('zoom_level', 1.0)
            new_zoom = min(current_zoom * factor, 5.0)  # Maximum zoom level
            st.session_state.zoom_level = new_zoom
            
            st.success(f"Zoomed in to {new_zoom:.1f}x")
            return True
            
        except Exception as e:
            st.error(f"Error zooming in: {e}")
            return False
    
    def zoom_out(self, factor: float = 1.2) -> bool:
        """
        Execute the 'Z-' command: Zoom out
        """
        try:
            current_zoom = st.session_state.get('zoom_level', 1.0)
            new_zoom = max(current_zoom / factor, 0.1)  # Minimum zoom level
            st.session_state.zoom_level = new_zoom
            
            st.success(f"Zoomed out to {new_zoom:.1f}x")
            return True
            
        except Exception as e:
            st.error(f"Error zooming out: {e}")
            return False
    
    def pan_graph(self, dx: float, dy: float) -> bool:
        """
        Pan the graph by the given offset
        """
        try:
            current_offset = st.session_state.get('pan_offset', [0, 0])
            new_offset = [current_offset[0] + dx, current_offset[1] + dy]
            st.session_state.pan_offset = new_offset
            
            return True
            
        except Exception as e:
            st.error(f"Error panning graph: {e}")
            return False
    
    def validate_graph_integrity(self) -> bool:
        """
        Validate the integrity of the current graph
        """
        try:
            # Check basic graph properties
            if not self.graph.validate_planarity():
                st.error("Graph planarity violated")
                return False
            
            # Check periphery consistency
            if len(self.graph.vertices) >= 3 and len(self.graph.periphery) < 3:
                st.error("Invalid periphery configuration")
                return False
            
            # Check for isolated vertices
            for vertex_id in self.graph.vertices:
                if len(self.graph.get_neighbors(vertex_id)) == 0 and len(self.graph.vertices) > 1:
                    st.error(f"Isolated vertex found: {vertex_id}")
                    return False
            
            # Check edge consistency
            for edge in self.graph.edges:
                if edge.v1_id not in self.graph.vertices or edge.v2_id not in self.graph.vertices:
                    st.error(f"Edge references non-existent vertex: {edge.id}")
                    return False
            
            st.success("Graph integrity validated")
            return True
            
        except Exception as e:
            st.error(f"Error validating graph: {e}")
            return False
    
    def get_command_history(self) -> list:
        """
        Get the history of executed commands
        """
        # Initialize command history if not exists
        if 'command_history' not in st.session_state:
            st.session_state.command_history = []
        
        return st.session_state.command_history
    
    def add_to_command_history(self, command: str, success: bool, details: str = ""):
        """
        Add a command to the history
        """
        if 'command_history' not in st.session_state:
            st.session_state.command_history = []
        
        entry = {
            'command': command,
            'success': success,
            'details': details,
            'timestamp': st.session_state.get('current_time', 'unknown'),
            'graph_state': {
                'vertices': len(self.graph.vertices),
                'edges': len(self.graph.edges),
                'periphery': len(self.graph.periphery)
            }
        }
        
        st.session_state.command_history.append(entry)
        
        # Keep only last 50 commands
        if len(st.session_state.command_history) > 50:
            st.session_state.command_history = st.session_state.command_history[-50:]
    
    def _get_random_color_index(self) -> int:
        """
        Get a random color index (1-4)
        """
        return random.randint(1, 4)
    
    def _are_periphery_adjacent(self, v1_id: int, v2_id: int) -> bool:
        """
        Check if two vertices are adjacent on the periphery
        """
        if v1_id not in self.graph.periphery or v2_id not in self.graph.periphery:
            return False
        
        idx1 = self.graph.periphery.index(v1_id)
        idx2 = self.graph.periphery.index(v2_id)
        
        # Check if they are consecutive (considering wrap-around)
        return (abs(idx1 - idx2) == 1 or 
                abs(idx1 - idx2) == len(self.graph.periphery) - 1)
    
    def execute_keyboard_command(self, key: str) -> bool:
        """
        Execute a command based on keyboard input
        """
        key = key.upper()
        
        try:
            if key == 'S':
                success = self.start_triangle()
                self.add_to_command_history('S - Start Triangle', success)
                return success
                
            elif key == 'R':
                success = self.add_random_vertex()
                self.add_to_command_history('R - Add Random Vertex', success)
                return success
                
            elif key == 'C':
                success = self.center_graph(st.session_state.get('canvas_size', [800, 600]))
                self.add_to_command_history('C - Center Graph', success)
                return success
                
            elif key == 'T':
                success = self.toggle_display_mode()
                self.add_to_command_history('T - Toggle Display', success)
                return success
                
            elif key == 'Z+':
                success = self.zoom_in()
                self.add_to_command_history('Z+ - Zoom In', success)
                return success
                
            elif key == 'Z-':
                success = self.zoom_out()
                self.add_to_command_history('Z- - Zoom Out', success)
                return success
                
            else:
                st.warning(f"Unknown command: {key}")
                return False
                
        except Exception as e:
            st.error(f"Error executing command {key}: {e}")
            self.add_to_command_history(f'{key} - Command', False, str(e))
            return False
