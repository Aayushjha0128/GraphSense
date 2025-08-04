# Overview

This is a Planar Triangulated Graph Visualizer built with Tkinter that allows users to interactively create and manipulate planar graphs while maintaining geometric constraints. The application focuses on computational geometry principles, ensuring that all vertices remain on the periphery, edges don't cross, and the graph maintains planarity throughout operations. Users can add vertices dynamically, apply geometric transformations, and visualize the graph with different rendering modes. The Tkinter version provides better mouse interaction, keyboard shortcuts, and eliminates UI conflicts.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses **Tkinter** as the desktop GUI framework with a clean widget-based architecture:
- **Main Application (`tkinter_app.py`)**: Contains the MainWindow class managing the overall application and GraphCanvas for visualization
- **Custom Canvas Widget (`GraphCanvas`)**: Handles all graph rendering, mouse interactions, and keyboard shortcuts
- **Native Event Handling**: Direct mouse and keyboard event processing for responsive interactions

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

# Recent Changes (August 2025)

**Migration to Tkinter (August 4, 2025)**
- Completely rewrote the application using Tkinter instead of Streamlit
- Resolved duplicate button ID issues and UI conflicts
- Implemented native mouse interactions with proper click detection, dragging, and scrolling
- Added comprehensive keyboard shortcuts (S, R, A, C, T, ESC)
- Full screen canvas with better zoom and pan controls
- Direct vertex selection for manual addition mode
- Improved performance with native drawing operations

# External Dependencies

## Core Frameworks
- **Tkinter**: Native Python GUI framework for desktop application interface
- **TTK**: Themed Tkinter widgets for modern appearance

## Mathematical and Scientific Libraries
- **NumPy**: Mathematical operations, vector calculations, and geometric computations
- **JSON**: Data serialization for graph import/export functionality
- **Math**: Standard mathematical functions for geometric calculations

## Rendering and Visualization
- **Tkinter Canvas**: Native canvas widget for graph visualization with direct drawing operations
- **Custom Mouse/Keyboard Handling**: Native event processing for responsive user interactions

## Development Dependencies
The application is designed to be lightweight using only Python standard library components (Tkinter) plus NumPy for mathematical operations. This eliminates web framework dependencies and provides better performance for desktop use.