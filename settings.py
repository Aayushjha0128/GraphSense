"""
Configuration and settings for the planar graph visualizer
"""

# Color palette for vertices and edges
COLORS = {
    'vertex_colors': {
        1: '#FF6B6B',  # Red
        2: '#4ECDC4',  # Teal
        3: '#45B7D1',  # Blue
        4: '#FFA07A'   # Light Salmon
    },
    'edge_color': '#2C3E50',      # Dark blue-gray
    'background_color': '#FFFFFF', # White
    'periphery_highlight': '#FFD93D', # Yellow for highlighting periphery
    'selected_vertex': '#FF1744'   # Bright red for selected vertices
}

# Graph layout and geometry settings
GEOMETRY_SETTINGS = {
    'min_angle_degrees': 60,        # Minimum angle between edges
    'edge_length_tolerance': 0.2,   # ±20% variation allowed
    'vertex_separation': 20,        # Minimum distance between vertices
    'default_edge_length': 80,      # Default edge length for new graphs
    'convexity_adjustment': 10,     # Pixels to move for convexity
    'angular_adjustment': 0.1       # Radians for angle adjustments
}

# Canvas and rendering settings
CANVAS_SETTINGS = {
    'default_width': 800,
    'default_height': 600,
    'max_zoom': 5.0,
    'min_zoom': 0.1,
    'zoom_factor': 1.2,
    'pan_sensitivity': 1.0,
    'vertex_label_min_size': 8,
    'vertex_label_max_size': 24,
    'edge_stroke_width': 2,
    'vertex_stroke_width': 2
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'max_vertices': 10000,          # Maximum number of vertices
    'redraw_iterations': 3,         # Number of redraw iterations
    'enable_antialiasing': True,    # Enable anti-aliasing for rendering
    'lazy_periphery_update': True,  # Only update periphery when needed
    'edge_bundling': False          # Enable edge bundling for large graphs
}

# User interface settings
UI_SETTINGS = {
    'sidebar_width': 300,
    'info_panel_height': 200,
    'command_history_length': 50,
    'auto_center_new_vertex': True,
    'show_coordinates': False,
    'show_vertex_degrees': False,
    'enable_tooltips': True
}

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    'S': 'start_triangle',
    'R': 'add_random_vertex',
    'A': 'add_manual_vertex',
    'C': 'center_graph',
    'T': 'toggle_display',
    'G': 'hide_vertices',
    'Z+': 'zoom_in',
    'Z-': 'zoom_out',
    'ESC': 'cancel_operation',
    'DEL': 'delete_selected',
    'SPACE': 'pause_animation'
}

# Validation settings
VALIDATION_SETTINGS = {
    'check_planarity': True,
    'check_connectivity': True,
    'check_periphery_validity': True,
    'allow_self_loops': False,
    'allow_multiple_edges': False,
    'enforce_triangulation': True
}

# Export/Import settings
IO_SETTINGS = {
    'default_format': 'json',
    'include_layout': True,
    'include_colors': True,
    'include_metadata': True,
    'compress_export': False,
    'auto_backup': True,
    'backup_interval': 300  # seconds
}

# Animation settings
ANIMATION_SETTINGS = {
    'enable_animations': True,
    'vertex_addition_duration': 500,  # milliseconds
    'redraw_animation_duration': 1000,
    'zoom_animation_duration': 300,
    'pan_animation_duration': 200,
    'easing_function': 'ease-in-out'
}

# Debug and development settings
DEBUG_SETTINGS = {
    'show_periphery_order': False,
    'show_edge_labels': False,
    'show_angle_measurements': False,
    'show_distance_measurements': False,
    'highlight_new_elements': True,
    'verbose_logging': False,
    'performance_monitoring': False
}

# Complete settings dictionary
SETTINGS = {
    'colors': COLORS,
    'geometry': GEOMETRY_SETTINGS,
    'canvas': CANVAS_SETTINGS,
    'performance': PERFORMANCE_SETTINGS,
    'ui': UI_SETTINGS,
    'keyboard': KEYBOARD_SHORTCUTS,
    'validation': VALIDATION_SETTINGS,
    'io': IO_SETTINGS,
    'animation': ANIMATION_SETTINGS,
    'debug': DEBUG_SETTINGS
}

# Theme variants
THEMES = {
    'light': {
        'background': '#FFFFFF',
        'primary': '#2C3E50',
        'secondary': '#3498DB',
        'accent': '#E74C3C',
        'text': '#2C3E50'
    },
    'dark': {
        'background': '#2C3E50',
        'primary': '#FFFFFF',
        'secondary': '#3498DB',
        'accent': '#E74C3C',
        'text': '#FFFFFF'
    },
    'high_contrast': {
        'background': '#000000',
        'primary': '#FFFFFF',
        'secondary': '#FFFF00',
        'accent': '#FF0000',
        'text': '#FFFFFF'
    }
}

def get_theme_colors(theme_name: str = 'light') -> dict:
    """
    Get color scheme for a specific theme
    """
    return THEMES.get(theme_name, THEMES['light'])

def update_colors_for_theme(theme_name: str):
    """
    Update the global COLORS dictionary for a specific theme
    """
    theme = get_theme_colors(theme_name)
    
    COLORS['background_color'] = theme['background']
    COLORS['edge_color'] = theme['primary']
    
    # Keep vertex colors as they are designed to be distinct
    # but could be modified for accessibility if needed

def get_setting(category: str, key: str, default=None):
    """
    Get a specific setting value
    """
    return SETTINGS.get(category, {}).get(key, default)

def update_setting(category: str, key: str, value):
    """
    Update a specific setting value
    """
    if category not in SETTINGS:
        SETTINGS[category] = {}
    SETTINGS[category][key] = value

def reset_settings():
    """
    Reset all settings to their default values
    """
    global SETTINGS
    SETTINGS = {
        'colors': COLORS.copy(),
        'geometry': GEOMETRY_SETTINGS.copy(),
        'canvas': CANVAS_SETTINGS.copy(),
        'performance': PERFORMANCE_SETTINGS.copy(),
        'ui': UI_SETTINGS.copy(),
        'keyboard': KEYBOARD_SHORTCUTS.copy(),
        'validation': VALIDATION_SETTINGS.copy(),
        'io': IO_SETTINGS.copy(),
        'animation': ANIMATION_SETTINGS.copy(),
        'debug': DEBUG_SETTINGS.copy()
    }
