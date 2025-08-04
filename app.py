import streamlit as st
import numpy as np
import json
from graph_model import PlanarGraph
from geometry import GeometryEngine
from gui_components import GraphRenderer
from commands import CommandProcessor
from settings import COLORS, SETTINGS
import utils

# Initialize session state
if 'graph' not in st.session_state:
    st.session_state.graph = PlanarGraph()
    st.session_state.geometry = GeometryEngine()
    st.session_state.renderer = GraphRenderer()
    st.session_state.commands = CommandProcessor(st.session_state.graph, st.session_state.geometry)
    st.session_state.view_mode = 'color'  # 'color' or 'index'
    st.session_state.hidden_threshold = None
    st.session_state.zoom_level = 1.0
    st.session_state.pan_offset = [0, 0]
    st.session_state.canvas_size = [800, 600]

def main():
    st.set_page_config(
        page_title="Planar Graph Visualizer",
        page_icon="🔗",
        layout="wide"
    )
    
    st.title("🔗 Planar Triangulated Graph Visualizer")
    st.markdown("Interactive graph visualization with computational geometry constraints")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        # Graph operations
        st.subheader("Graph Operations")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Triangle (S)", help="Create initial triangle with 3 vertices"):
                st.session_state.commands.start_triangle()
                st.rerun()
                
            if st.button("Add Random (R)", help="Add random vertex to periphery"):
                st.session_state.commands.add_random_vertex()
                st.rerun()
        
        with col2:
            if st.button("Add Manual (A)", help="Add vertex manually (select two periphery vertices)"):
                st.session_state.add_manual_mode = True
                st.rerun()
                
            if st.button("Center Graph (C)", help="Center and fit graph to screen"):
                st.session_state.commands.center_graph(st.session_state.canvas_size)
                st.rerun()
        
        # View controls
        st.subheader("View Controls")
        
        # Toggle display mode
        if st.button("Toggle Display (T)", help="Switch between color and index display"):
            st.session_state.view_mode = 'index' if st.session_state.view_mode == 'color' else 'color'
            st.rerun()
        
        # Hide vertices
        hide_threshold = st.number_input(
            "Hide vertices > index (G)", 
            min_value=0, 
            max_value=len(st.session_state.graph.vertices),
            value=len(st.session_state.graph.vertices) if st.session_state.hidden_threshold is None else st.session_state.hidden_threshold,
            help="Hide all vertices with index greater than this value"
        )
        
        if st.button("Apply Hide"):
            st.session_state.hidden_threshold = hide_threshold
            st.rerun()
        
        if st.button("Show All"):
            st.session_state.hidden_threshold = None
            st.rerun()
        
        # Zoom controls
        st.subheader("Zoom Controls")
        zoom_col1, zoom_col2 = st.columns(2)
        
        with zoom_col1:
            if st.button("Zoom In (Z+)"):
                st.session_state.zoom_level = min(st.session_state.zoom_level * 1.2, 5.0)
                st.rerun()
        
        with zoom_col2:
            if st.button("Zoom Out (Z-)"):
                st.session_state.zoom_level = max(st.session_state.zoom_level / 1.2, 0.1)
                st.rerun()
        
        # Graph info
        st.subheader("Graph Information")
        st.metric("Vertices", len(st.session_state.graph.vertices))
        st.metric("Edges", len(st.session_state.graph.edges))
        st.metric("Periphery Size", len(st.session_state.graph.periphery))
        
        # Export/Import
        st.subheader("Data Operations")
        if st.button("Export Graph"):
            graph_data = st.session_state.graph.to_dict()
            st.download_button(
                "Download JSON",
                json.dumps(graph_data, indent=2),
                "graph.json",
                "application/json"
            )
        
        uploaded_file = st.file_uploader("Import Graph", type="json")
        if uploaded_file is not None:
            try:
                graph_data = json.load(uploaded_file)
                st.session_state.graph.from_dict(graph_data)
                st.success("Graph imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing graph: {e}")
    
    # Main canvas area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Canvas for graph visualization
        canvas_result = st.session_state.renderer.render_interactive_canvas(
            st.session_state.graph,
            st.session_state.canvas_size,
            st.session_state.zoom_level,
            st.session_state.pan_offset,
            st.session_state.view_mode,
            st.session_state.hidden_threshold
        )
        
        # Handle canvas interactions
        if canvas_result.json_data is not None:
            # Process mouse interactions
            handle_canvas_interaction(canvas_result.json_data)
    
    with col2:
        st.subheader("Instructions")
        st.markdown("""
        **Commands:**
        - **S**: Start with triangle
        - **R**: Add random vertex
        - **A**: Add vertex manually
        - **C**: Center graph
        - **T**: Toggle display mode
        - **G**: Hide vertices
        - **Z+/-**: Zoom in/out
        
        **Mouse:**
        - **Left drag**: Pan graph
        - **Click**: Select vertices (manual mode)
        """)
        
        if hasattr(st.session_state, 'add_manual_mode') and st.session_state.add_manual_mode:
            st.info("Manual add mode: Click two periphery vertices in clockwise order")
            if st.button("Cancel Manual Add"):
                st.session_state.add_manual_mode = False
                st.session_state.selected_vertices = []
                st.rerun()

def handle_canvas_interaction(interaction_data):
    """Handle mouse and keyboard interactions from the canvas"""
    if not interaction_data:
        return
    
    # Handle vertex selection for manual addition
    if hasattr(st.session_state, 'add_manual_mode') and st.session_state.add_manual_mode:
        if 'objects' in interaction_data:
            for obj in interaction_data['objects']:
                if obj.get('type') == 'circle':  # Vertex clicked
                    vertex_id = obj.get('vertex_id')
                    if vertex_id and vertex_id in st.session_state.graph.periphery:
                        if not hasattr(st.session_state, 'selected_vertices'):
                            st.session_state.selected_vertices = []
                        
                        if len(st.session_state.selected_vertices) < 2:
                            st.session_state.selected_vertices.append(vertex_id)
                            
                            if len(st.session_state.selected_vertices) == 2:
                                # Add vertex between selected periphery vertices
                                v1, v2 = st.session_state.selected_vertices
                                try:
                                    st.session_state.commands.add_manual_vertex(v1, v2)
                                    st.success(f"Added vertex between {v1} and {v2}")
                                except Exception as e:
                                    st.error(f"Error adding vertex: {e}")
                                finally:
                                    st.session_state.add_manual_mode = False
                                    st.session_state.selected_vertices = []
                                    st.rerun()
    
    # Handle pan operations
    if 'pan' in interaction_data:
        pan_data = interaction_data['pan']
        st.session_state.pan_offset[0] += pan_data.get('dx', 0)
        st.session_state.pan_offset[1] += pan_data.get('dy', 0)
        st.rerun()

if __name__ == "__main__":
    main()
