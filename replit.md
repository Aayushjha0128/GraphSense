# Overview

This is a Planar Triangulated Graph Visualizer built with Streamlit that allows users to interactively create and manipulate planar graphs while maintaining geometric constraints. The application focuses on computational geometry principles, ensuring that all vertices remain on the periphery, edges don't cross, and the graph maintains planarity throughout operations. Users can add vertices dynamically, apply geometric transformations, and visualize the graph with different rendering modes.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses **Streamlit** as the web framework with a component-based architecture:
- **Main Application (`app.py`)**: Orchestrates the UI layout and handles session state management
- **GUI Components (`gui_components.py`)**: Manages graph rendering using `streamlit_drawable_canvas` for interactive visualization
- **Session State Management**: Maintains graph state, view settings, and user interactions across page refreshes

## Core Engine Components
The system follows a modular design with specialized engines:

### Graph Model (`graph_model.py`)
- **Vertex Class**: Encapsulates vertex properties (position, color, diameter, ID)
- **Edge Class**: Manages edge relationships and metadata
- **PlanarGraph Class**: Maintains graph structure with adjacency lists and periphery tracking
- **Serialization Support**: JSON-based import/export capabilities

### Geometry Engine (`geometry.py`)
- **Constraint Enforcement**: Maintains minimum angles (60°), edge length uniformity (±20% tolerance)
- **Position Calculation**: Computes optimal vertex placement for planarity preservation
- **Convexity Maintenance**: Ensures the graph periphery remains convex
- **Redraw Logic**: Rebalances angular spacing and edge lengths after modifications

### Command Processing (`commands.py`)
- **Command Pattern Implementation**: Handles user operations (S, R, A, G, Z, C, T commands)
- **Validation Logic**: Ensures all operations maintain graph planarity and geometric constraints
- **Error Handling**: Provides user feedback for invalid operations

## Data Flow Architecture
1. **User Input** → Streamlit UI components
2. **Command Processing** → Validates and executes graph operations
3. **Geometry Calculations** → Maintains mathematical constraints
4. **Graph Model Updates** → Modifies internal data structures
5. **Rendering** → Updates visual representation via canvas

## Configuration Management
The system uses a centralized configuration approach:
- **Settings Module (`settings.py`)**: Defines color palettes, geometry constraints, canvas settings, and performance parameters
- **Utilities (`utils.py`)**: Provides geometric calculation helpers (distance, angle, rotation functions)

## Design Patterns
- **Engine Pattern**: Separate engines for geometry, rendering, and command processing
- **State Management**: Streamlit session state for persistence
- **Component Architecture**: Modular UI components for different visualization aspects

# External Dependencies

## Core Frameworks
- **Streamlit**: Web application framework for the user interface and session management
- **streamlit-drawable-canvas**: Interactive canvas component for graph visualization and user interactions

## Mathematical and Scientific Libraries
- **NumPy**: Mathematical operations, vector calculations, and geometric computations
- **JSON**: Data serialization for graph import/export functionality

## Rendering and Visualization
- **streamlit-drawable-canvas**: Provides the interactive drawing surface with mouse interaction capabilities
- **Custom Canvas Rendering**: SVG-based drawing commands for vertices, edges, and labels

## Development Dependencies
The application is designed to be lightweight with minimal external dependencies, relying primarily on Streamlit's built-in capabilities and NumPy for mathematical operations. The modular architecture allows for easy integration of additional visualization libraries or geometric constraint solvers if needed.