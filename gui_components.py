import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas
from typing import Dict, List, Tuple, Optional
from graph_model import PlanarGraph
from settings import COLORS

class GraphRenderer:
    """
    Handles rendering of the planar graph using Streamlit components
    """
    
    def __init__(self):
        self.default_canvas_size = [800, 600]
        self.vertex_colors = COLORS['vertex_colors']
        self.edge_color = COLORS['edge_color']
        self.background_color = COLORS['background_color']
        
    def render_interactive_canvas(self, graph: PlanarGraph, canvas_size: List[int], 
                                zoom_level: float, pan_offset: List[float], 
                                view_mode: str, hidden_threshold: Optional[int]):
        """
        Render the graph on an interactive canvas
        """
        # Prepare drawing commands for the canvas
        drawing_data = self._prepare_drawing_data(
            graph, canvas_size, zoom_level, pan_offset, view_mode, hidden_threshold
        )
        
        # Create the canvas
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
            stroke_width=2,
            stroke_color="#000000",
            background_color=self.background_color,
            background_image=None,
            update_streamlit=True,
            height=canvas_size[1],
            width=canvas_size[0],
            drawing_mode="transform",  # Allow interactions but not drawing
            point_display_radius=0,
            display_toolbar=False,
            key="graph_canvas",
            initial_drawing=drawing_data
        )
        
        return canvas_result
    
    def _prepare_drawing_data(self, graph: PlanarGraph, canvas_size: List[int],
                            zoom_level: float, pan_offset: List[float],
                            view_mode: str, hidden_threshold: Optional[int]) -> Dict:
        """
        Prepare the drawing data structure for the canvas
        """
        objects = []
        
        # Transform coordinates based on zoom and pan
        def transform_coords(x, y):
            # Apply zoom
            tx = x * zoom_level
            ty = y * zoom_level
            
            # Apply pan offset
            tx += pan_offset[0]
            ty += pan_offset[1]
            
            # Center in canvas
            tx += canvas_size[0] / 2
            ty += canvas_size[1] / 2
            
            return tx, ty
        
        # Draw edges first (so they appear behind vertices)
        for edge in graph.edges:
            v1 = graph.vertices[edge.v1_id]
            v2 = graph.vertices[edge.v2_id]
            
            # Check if vertices should be hidden
            if hidden_threshold is not None:
                if v1.id > hidden_threshold or v2.id > hidden_threshold:
                    continue
            
            x1, y1 = transform_coords(v1.x, v1.y)
            x2, y2 = transform_coords(v2.x, v2.y)
            
            # Create edge object
            edge_obj = {
                "type": "line",
                "version": "4.4.0",
                "originX": "left",
                "originY": "top",
                "left": min(x1, x2),
                "top": min(y1, y2),
                "width": abs(x2 - x1),
                "height": abs(y2 - y1),
                "fill": "",
                "stroke": self.edge_color,
                "strokeWidth": 2,
                "strokeDashArray": None,
                "strokeLineCap": "butt",
                "strokeDashOffset": 0,
                "strokeLineJoin": "miter",
                "strokeUniform": False,
                "strokeMiterLimit": 4,
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "flipX": False,
                "flipY": False,
                "opacity": 1,
                "shadow": None,
                "visible": True,
                "backgroundColor": "",
                "x1": 0 if x1 <= x2 else abs(x2 - x1),
                "y1": 0 if y1 <= y2 else abs(y2 - y1),
                "x2": abs(x2 - x1) if x1 <= x2 else 0,
                "y2": abs(y2 - y1) if y1 <= y2 else 0
            }
            objects.append(edge_obj)
        
        # Draw vertices
        for vertex_id, vertex in graph.vertices.items():
            # Check if vertex should be hidden
            if hidden_threshold is not None and vertex_id > hidden_threshold:
                continue
            
            x, y = transform_coords(vertex.x, vertex.y)
            radius = vertex.diameter / 2 * zoom_level
            
            # Get vertex color based on view mode
            if view_mode == 'color':
                fill_color = self.vertex_colors.get(vertex.color_index, self.vertex_colors[1])
            else:
                # Use a default color for index mode
                fill_color = self.vertex_colors[1]
            
            # Create vertex circle object
            vertex_obj = {
                "type": "circle",
                "version": "4.4.0",
                "originX": "center",
                "originY": "center",
                "left": x,
                "top": y,
                "width": radius * 2,
                "height": radius * 2,
                "fill": fill_color,
                "stroke": self.vertex_colors[1],  # Outline color
                "strokeWidth": 2,
                "strokeDashArray": None,
                "strokeLineCap": "butt",
                "strokeDashOffset": 0,
                "strokeLineJoin": "miter",
                "strokeUniform": False,
                "strokeMiterLimit": 4,
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "flipX": False,
                "flipY": False,
                "opacity": 1,
                "shadow": None,
                "visible": True,
                "backgroundColor": "",
                "radius": radius,
                "startAngle": 0,
                "endAngle": 6.283185307179586,
                "vertex_id": vertex_id  # Custom property for identification
            }
            objects.append(vertex_obj)
            
            # Add vertex label
            label_text = str(vertex_id) if view_mode == 'index' else str(vertex.color_index)
            
            label_obj = {
                "type": "text",
                "version": "4.4.0",
                "originX": "center",
                "originY": "center",
                "left": x,
                "top": y,
                "width": 100,
                "height": 50,
                "fill": "#000000",
                "stroke": None,
                "strokeWidth": 1,
                "strokeDashArray": None,
                "strokeLineCap": "butt",
                "strokeDashOffset": 0,
                "strokeLineJoin": "miter",
                "strokeUniform": False,
                "strokeMiterLimit": 4,
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "flipX": False,
                "flipY": False,
                "opacity": 1,
                "shadow": None,
                "visible": True,
                "backgroundColor": "",
                "text": label_text,
                "fontSize": max(12, min(20, int(radius / 2))),
                "fontWeight": "bold",
                "fontFamily": "Arial",
                "fontStyle": "normal",
                "lineHeight": 1.16,
                "underline": False,
                "overline": False,
                "linethrough": False,
                "textAlign": "center",
                "textBackgroundColor": "",
                "charSpacing": 0,
                "styles": {}
            }
            objects.append(label_obj)
        
        return {
            "version": "4.4.0",
            "objects": objects
        }
    
    def render_graph_info_panel(self, graph: PlanarGraph):
        """
        Render an information panel about the current graph
        """
        st.subheader("Graph Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vertices", len(graph.vertices))
        
        with col2:
            st.metric("Edges", len(graph.edges))
        
        with col3:
            st.metric("Periphery", len(graph.periphery))
        
        # Edge length statistics
        if graph.edges:
            edge_stats = graph.get_edge_length_stats()
            st.subheader("Edge Length Statistics")
            
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.metric("Average Length", f"{edge_stats['mean']:.1f}")
                st.metric("Minimum Length", f"{edge_stats['min']:.1f}")
            
            with stat_col2:
                st.metric("Standard Deviation", f"{edge_stats['std']:.1f}")
                st.metric("Maximum Length", f"{edge_stats['max']:.1f}")
        
        # Periphery vertices
        if graph.periphery:
            st.subheader("Periphery Vertices")
            periphery_str = " → ".join(map(str, graph.periphery))
            st.text(periphery_str)
    
    def render_vertex_details(self, graph: PlanarGraph, vertex_id: int):
        """
        Render detailed information about a specific vertex
        """
        if vertex_id not in graph.vertices:
            st.error(f"Vertex {vertex_id} not found")
            return
        
        vertex = graph.vertices[vertex_id]
        neighbors = graph.get_neighbors(vertex_id)
        
        st.subheader(f"Vertex {vertex_id} Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Position X", f"{vertex.x:.1f}")
            st.metric("Position Y", f"{vertex.y:.1f}")
        
        with col2:
            st.metric("Color Index", vertex.color_index)
            st.metric("Degree", len(neighbors))
        
        if neighbors:
            st.subheader("Neighbors")
            neighbors_str = ", ".join(map(str, sorted(neighbors)))
            st.text(neighbors_str)
        
        # Show if vertex is on periphery
        if vertex_id in graph.periphery:
            st.success("This vertex is on the periphery")
            periphery_index = graph.periphery.index(vertex_id)
            st.text(f"Periphery position: {periphery_index}")
        else:
            st.info("This vertex is not on the periphery")
    
    def render_error_message(self, message: str):
        """
        Render an error message
        """
        st.error(f"❌ {message}")
    
    def render_success_message(self, message: str):
        """
        Render a success message
        """
        st.success(f"✅ {message}")
    
    def render_info_message(self, message: str):
        """
        Render an info message
        """
        st.info(f"ℹ️ {message}")
    
    def render_command_help(self):
        """
        Render help information for available commands
        """
        st.subheader("Command Reference")
        
        commands = [
            ("S", "Start Triangle", "Create initial triangle with 3 vertices"),
            ("R", "Add Random", "Add a random vertex to the periphery"),
            ("A", "Add Manual", "Manually add a vertex by selecting two periphery vertices"),
            ("C", "Center Graph", "Center and fit the graph to the screen"),
            ("T", "Toggle Display", "Switch between color and index display modes"),
            ("G", "Hide Vertices", "Hide all vertices with index greater than specified"),
            ("Z+", "Zoom In", "Increase zoom level"),
            ("Z-", "Zoom Out", "Decrease zoom level")
        ]
        
        for key, name, description in commands:
            with st.expander(f"{key} - {name}"):
                st.write(description)
    
    def render_graph_validation_status(self, graph: PlanarGraph):
        """
        Render the current validation status of the graph
        """
        st.subheader("Graph Validation")
        
        # Check basic properties
        is_connected = len(graph.vertices) <= 1 or self._is_graph_connected(graph)
        is_planar = graph.validate_planarity()
        has_valid_periphery = len(graph.periphery) >= 3 if len(graph.vertices) >= 3 else True
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if is_connected:
                st.success("Connected ✓")
            else:
                st.error("Not Connected ✗")
        
        with col2:
            if is_planar:
                st.success("Planar ✓")
            else:
                st.error("Not Planar ✗")
        
        with col3:
            if has_valid_periphery:
                st.success("Valid Periphery ✓")
            else:
                st.error("Invalid Periphery ✗")
    
    def _is_graph_connected(self, graph: PlanarGraph) -> bool:
        """
        Check if the graph is connected using DFS
        """
        if not graph.vertices:
            return True
        
        visited = set()
        start_vertex = next(iter(graph.vertices.keys()))
        stack = [start_vertex]
        
        while stack:
            vertex_id = stack.pop()
            if vertex_id not in visited:
                visited.add(vertex_id)
                neighbors = graph.get_neighbors(vertex_id)
                stack.extend(n for n in neighbors if n not in visited)
        
        return len(visited) == len(graph.vertices)
