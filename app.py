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
    st.session_state.canvas_size = [1400, 800]  # Larger default size for full screen

def main():
    st.set_page_config(
        page_title="Planar Graph Visualizer",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Top control bar for full screen layout
    st.markdown("### 🔗 Planar Triangulated Graph Visualizer")
    
    # Compact control buttons in columns
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
    
    with col1:
        if st.button("Start Triangle (S)", help="Create initial triangle with 3 vertices", use_container_width=True):
            st.session_state.commands.start_triangle()
            st.rerun()
    
    with col2:
        if st.button("Add Random (R)", help="Add random vertex to periphery", use_container_width=True):
            st.session_state.commands.add_random_vertex()
            st.rerun()
    
    with col3:
        if st.button("Add Manual (A)", help="Add vertex manually", use_container_width=True):
            st.session_state.add_manual_mode = True
            st.rerun()
    
    with col4:
        if st.button("Center Graph (C)", help="Center and fit graph to screen", use_container_width=True):
            st.session_state.commands.center_graph(st.session_state.canvas_size)
            st.rerun()
    
    with col5:
        if st.button("Toggle Display (T)", help="Switch between color and index display", use_container_width=True):
            st.session_state.view_mode = 'index' if st.session_state.view_mode == 'color' else 'color'
            st.rerun()
    
    with col6:
        if st.button("Zoom In (Z+)", use_container_width=True):
            st.session_state.zoom_level = min(st.session_state.zoom_level * 1.2, 5.0)
            st.rerun()
    
    with col7:
        if st.button("Zoom Out (Z-)", use_container_width=True):
            st.session_state.zoom_level = max(st.session_state.zoom_level / 1.2, 0.1)
            st.rerun()
    
    with col8:
        # Hide vertices control
        hide_threshold = st.number_input(
            "Hide > index", 
            min_value=0, 
            max_value=max(len(st.session_state.graph.vertices), 1),
            value=len(st.session_state.graph.vertices) if st.session_state.hidden_threshold is None else st.session_state.hidden_threshold,
            help="Hide vertices with index greater than this value",
            label_visibility="collapsed"
        )
        if st.button("Apply", use_container_width=True):
            st.session_state.hidden_threshold = hide_threshold
            st.rerun()
    
    with col9:
        # Graph stats and export
        with st.popover("📊 Info & Export"):
            st.metric("Vertices", len(st.session_state.graph.vertices))
            st.metric("Edges", len(st.session_state.graph.edges))
            st.metric("Periphery", len(st.session_state.graph.periphery))
            
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
    
    # Status line
    status_col1, status_col2, status_col3 = st.columns([2, 2, 4])
    with status_col1:
        st.write(f"View: {st.session_state.view_mode.title()}")
    with status_col2:
        st.write(f"Zoom: {st.session_state.zoom_level:.1f}x")
    with status_col3:
        if hasattr(st.session_state, 'add_manual_mode') and st.session_state.add_manual_mode:
            st.warning("Manual add mode: Click two periphery vertices in clockwise order")
            if st.button("Cancel Manual Add", type="secondary"):
                st.session_state.add_manual_mode = False
                st.session_state.selected_vertices = []
                st.rerun()
    
    # Optional sidebar (collapsed by default) for advanced controls
    with st.sidebar:
        st.header("Advanced Controls")
        st.write("Detailed controls and graph information")
        
        # Graph validation status
        st.subheader("Graph Status")
        st.metric("Vertices", len(st.session_state.graph.vertices))
        st.metric("Edges", len(st.session_state.graph.edges))
        st.metric("Periphery Size", len(st.session_state.graph.periphery))
        
        # Edge statistics
        if st.session_state.graph.edges:
            edge_stats = st.session_state.graph.get_edge_length_stats()
            st.metric("Avg Edge Length", f"{edge_stats['mean']:.1f}")
        
        # Advanced operations
        st.subheader("Advanced Operations")
        if st.button("Show All Vertices"):
            st.session_state.hidden_threshold = None
            st.rerun()
        
        if st.button("Reset Zoom & Pan"):
            st.session_state.zoom_level = 1.0
            st.session_state.pan_offset = [0, 0]
            st.rerun()
    
    # Full screen canvas
    # Get viewport dimensions for full screen canvas
    import streamlit.components.v1 as components
    
    # JavaScript to get viewport dimensions
    viewport_js = """
    <script>
    function sendViewportSize() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        window.parent.postMessage({
            type: 'viewport_size',
            width: width - 50,  // Account for padding
            height: height - 150  // Account for header and controls
        }, '*');
    }
    sendViewportSize();
    window.addEventListener('resize', sendViewportSize);
    </script>
    """
    components.html(viewport_js, height=0)
    
    # Update canvas size to be full screen
    if 'viewport_width' not in st.session_state:
        st.session_state.viewport_width = 1400
    if 'viewport_height' not in st.session_state:
        st.session_state.viewport_height = 800
    
    # Use larger canvas size for full screen
    st.session_state.canvas_size = [st.session_state.viewport_width, st.session_state.viewport_height]
    
    # Canvas for graph visualization (full width)
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
    
    # Instructions in an expander to save space
    with st.expander("📖 Instructions & Controls", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Commands:**
            - **S**: Start with triangle
            - **R**: Add random vertex
            - **A**: Add vertex manually
            - **C**: Center graph
            - **T**: Toggle display mode
            - **G**: Hide vertices
            - **Z+/-**: Zoom in/out
            """)
        with col2:
            st.markdown("""
            **Mouse:**
            - **Left drag**: Pan graph
            - **Click**: Select vertices (manual mode)
            
            **Status:**
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
