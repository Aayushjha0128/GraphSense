#!/usr/bin/env python3
"""
Planar Triangulated Graph Visualizer - Tkinter Version
Interactive graph visualization with computational geometry constraints
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import json
import random
from typing import Dict, List, Tuple, Optional, Set
from graph_model import PlanarGraph, Vertex, Edge
from geometry import GeometryEngine
from commands import CommandProcessor
from settings import COLORS, SETTINGS

class GraphCanvas(tk.Canvas):
    """Custom canvas for graph visualization with mouse interactions"""
    
    def __init__(self, parent, width=1400, height=800, **kwargs):
        super().__init__(parent, width=width, height=height, bg='white', **kwargs)
        
        self.graph = PlanarGraph()
        self.geometry_engine = GeometryEngine()
        self.command_processor = CommandProcessor(self.graph, self.geometry_engine)
        
        # View state
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        self.view_mode = 'color'  # 'color' or 'index'
        self.hidden_threshold = None
        
        # Mouse interaction state
        self.last_click_pos = None
        self.is_panning = False
        self.selected_vertices = []
        self.manual_add_mode = False
        
        # Bind mouse events
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<MouseWheel>", self.on_scroll)
        self.bind("<Button-4>", self.on_scroll)  # Linux scroll up
        self.bind("<Button-5>", self.on_scroll)  # Linux scroll down
        
        # Make canvas focusable for keyboard events
        self.focus_set()
        self.bind("<Key>", self.on_key_press)
        
        # Initial triangle
        self.command_processor.start_triangle()
        self.update_display()
    
    def transform_coords(self, x: float, y: float) -> Tuple[float, float]:
        """Transform graph coordinates to canvas coordinates"""
        # Apply zoom
        tx = x * self.zoom_level
        ty = y * self.zoom_level
        
        # Apply pan offset
        tx += self.pan_offset[0]
        ty += self.pan_offset[1]
        
        # Center in canvas
        tx += self.winfo_width() / 2
        ty += self.winfo_height() / 2
        
        return tx, ty
    
    def inverse_transform_coords(self, canvas_x: float, canvas_y: float) -> Tuple[float, float]:
        """Transform canvas coordinates to graph coordinates"""
        # Reverse centering
        x = canvas_x - self.winfo_width() / 2
        y = canvas_y - self.winfo_height() / 2
        
        # Reverse pan offset
        x -= self.pan_offset[0]
        y -= self.pan_offset[1]
        
        # Reverse zoom
        x /= self.zoom_level
        y /= self.zoom_level
        
        return x, y
    
    def update_display(self):
        """Update the canvas display"""
        self.delete("all")
        
        # Draw edges first (so they appear behind vertices)
        for edge in self.graph.edges:
            v1 = self.graph.vertices[edge.v1_id]
            v2 = self.graph.vertices[edge.v2_id]
            
            # Check if vertices should be hidden
            if self.hidden_threshold is not None:
                if v1.id > self.hidden_threshold or v2.id > self.hidden_threshold:
                    continue
            
            x1, y1 = self.transform_coords(v1.x, v1.y)
            x2, y2 = self.transform_coords(v2.x, v2.y)
            
            self.create_line(x1, y1, x2, y2, 
                           fill=COLORS['edge_color'], 
                           width=2, 
                           tags="edge")
        
        # Draw vertices
        for vertex_id, vertex in self.graph.vertices.items():
            # Check if vertex should be hidden
            if self.hidden_threshold is not None and vertex_id > self.hidden_threshold:
                continue
            
            x, y = self.transform_coords(vertex.x, vertex.y)
            radius = vertex.diameter / 2 * self.zoom_level
            
            # Get vertex color based on view mode
            if self.view_mode == 'color':
                fill_color = COLORS['vertex_colors'].get(vertex.color_index, COLORS['vertex_colors'][1])
            else:
                fill_color = COLORS['vertex_colors'][1]
            
            # Highlight selected vertices
            outline_color = COLORS['vertex_colors'][1]
            outline_width = 2
            if vertex_id in self.selected_vertices:
                outline_color = COLORS['selected_vertex']
                outline_width = 3
            
            # Highlight periphery vertices
            if vertex_id in self.graph.periphery:
                outline_color = COLORS['periphery_highlight']
                outline_width = 3
            
            # Draw vertex circle
            self.create_oval(x - radius, y - radius, x + radius, y + radius,
                           fill=fill_color, 
                           outline=outline_color,
                           width=outline_width,
                           tags=f"vertex_{vertex_id}")
            
            # Draw vertex label
            label_text = str(vertex_id) if self.view_mode == 'index' else str(vertex.color_index)
            font_size = max(8, min(16, int(radius / 2)))
            
            self.create_text(x, y, 
                           text=label_text, 
                           font=("Arial", font_size, "bold"),
                           fill="black",
                           tags=f"label_{vertex_id}")
    
    def on_left_click(self, event):
        """Handle left mouse click"""
        self.last_click_pos = (event.x, event.y)
        
        # Check if clicking on a vertex
        clicked_vertex = self.get_vertex_at_position(event.x, event.y)
        
        if self.manual_add_mode and clicked_vertex is not None:
            # Manual vertex addition mode
            if clicked_vertex in self.graph.periphery:
                if len(self.selected_vertices) < 2:
                    if clicked_vertex not in self.selected_vertices:
                        self.selected_vertices.append(clicked_vertex)
                        
                        if len(self.selected_vertices) == 2:
                            # Add vertex between selected periphery vertices
                            v1, v2 = self.selected_vertices
                            try:
                                self.command_processor.add_manual_vertex(v1, v2)
                                self.update_display()
                                self.parent.update_status(f"Added vertex between {v1} and {v2}")
                            except Exception as e:
                                messagebox.showerror("Error", f"Error adding vertex: {e}")
                            finally:
                                self.manual_add_mode = False
                                self.selected_vertices = []
                                self.parent.update_manual_mode_status()
                        
                        self.update_display()
                else:
                    messagebox.showwarning("Warning", "Click on a periphery vertex")
        else:
            # Start panning
            self.is_panning = True
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.is_panning and self.last_click_pos:
            # Pan the graph
            dx = event.x - self.last_click_pos[0]
            dy = event.y - self.last_click_pos[1]
            
            self.pan_offset[0] += dx
            self.pan_offset[1] += dy
            
            self.last_click_pos = (event.x, event.y)
            self.update_display()
    
    def on_release(self, event):
        """Handle mouse button release"""
        self.is_panning = False
        self.last_click_pos = None
    
    def on_scroll(self, event):
        """Handle mouse scroll for zooming"""
        # Determine scroll direction
        if event.delta > 0 or event.num == 4:
            # Zoom in
            zoom_factor = 1.1
        else:
            # Zoom out
            zoom_factor = 0.9
        
        # Apply zoom
        old_zoom = self.zoom_level
        self.zoom_level = max(0.1, min(5.0, self.zoom_level * zoom_factor))
        
        # Adjust pan offset to zoom towards mouse position
        mouse_x, mouse_y = event.x, event.y
        canvas_center_x = self.winfo_width() / 2
        canvas_center_y = self.winfo_height() / 2
        
        # Calculate offset from center
        offset_x = mouse_x - canvas_center_x
        offset_y = mouse_y - canvas_center_y
        
        # Adjust pan to keep mouse position stable
        zoom_change = self.zoom_level / old_zoom - 1
        self.pan_offset[0] -= offset_x * zoom_change
        self.pan_offset[1] -= offset_y * zoom_change
        
        self.update_display()
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        key = event.keysym.upper()
        
        if key == 'S':
            self.command_processor.start_triangle()
            self.update_display()
            self.parent.update_status("Started new triangle")
        elif key == 'R':
            try:
                self.command_processor.add_random_vertex()
                self.update_display()
                self.parent.update_status("Added random vertex")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        elif key == 'A':
            self.manual_add_mode = True
            self.selected_vertices = []
            self.parent.update_manual_mode_status()
            self.parent.update_status("Manual add mode - Click two periphery vertices")
        elif key == 'C':
            self.center_graph()
        elif key == 'T':
            self.toggle_display_mode()
        elif key == 'ESCAPE':
            self.manual_add_mode = False
            self.selected_vertices = []
            self.parent.update_manual_mode_status()
            self.update_display()
    
    def get_vertex_at_position(self, canvas_x: float, canvas_y: float) -> Optional[int]:
        """Get vertex at canvas position"""
        for vertex_id, vertex in self.graph.vertices.items():
            if self.hidden_threshold is not None and vertex_id > self.hidden_threshold:
                continue
            
            vx, vy = self.transform_coords(vertex.x, vertex.y)
            radius = vertex.diameter / 2 * self.zoom_level
            
            distance = math.sqrt((canvas_x - vx)**2 + (canvas_y - vy)**2)
            if distance <= radius:
                return vertex_id
        
        return None
    
    def center_graph(self):
        """Center and fit graph to canvas"""
        try:
            canvas_size = (self.winfo_width(), self.winfo_height())
            self.command_processor.center_graph(canvas_size)
            
            # Reset zoom and pan
            self.zoom_level = 1.0
            self.pan_offset = [0, 0]
            
            self.update_display()
            self.parent.update_status("Graph centered and fitted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def toggle_display_mode(self):
        """Toggle between color and index display"""
        self.view_mode = 'index' if self.view_mode == 'color' else 'color'
        self.update_display()
        self.parent.update_status(f"Display mode: {self.view_mode}")
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.update_display()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.update_display()
    
    def add_random_vertex(self):
        """Add random vertex"""
        try:
            self.command_processor.add_random_vertex()
            self.update_display()
            self.parent.update_status("Added random vertex")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def export_graph(self):
        """Export graph to JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                graph_data = self.graph.to_dict()
                with open(filename, 'w') as f:
                    json.dump(graph_data, f, indent=2)
                self.parent.update_status(f"Graph exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def import_graph(self):
        """Import graph from JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    graph_data = json.load(f)
                self.graph.from_dict(graph_data)
                self.update_display()
                self.parent.update_status(f"Graph imported from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")

class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Planar Triangulated Graph Visualizer")
        self.root.geometry("1500x900")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create control frame
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Initialize variables first
        self.manual_mode_var = tk.StringVar()
        self.manual_mode_label = None
        self.info_var = tk.StringVar()
        self.hide_var = tk.StringVar()
        self.status_var = tk.StringVar()
        
        # Create canvas
        self.canvas = GraphCanvas(self.main_frame, width=1480, height=820)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.parent = self  # Set parent reference
        
        # Create controls
        self.create_controls()
        
        # Create status bar
        self.status_var.set("Ready - Press 'S' to start triangle, 'R' for random vertex, 'A' for manual add")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind window events
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Make canvas focusable
        self.canvas.focus_set()
    
    def create_controls(self):
        """Create control buttons"""
        # Row 1: Main operations
        row1 = ttk.Frame(self.control_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Button(row1, text="Start Triangle (S)", 
                  command=self.start_triangle).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Add Random (R)", 
                  command=self.add_random_vertex).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Add Manual (A)", 
                  command=self.start_manual_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Center Graph (C)", 
                  command=self.center_graph).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(row1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # View controls
        ttk.Button(row1, text="Toggle Display (T)", 
                  command=self.toggle_display).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Zoom In", 
                  command=self.canvas.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Zoom Out", 
                  command=self.canvas.zoom_out).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(row1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # File operations
        ttk.Button(row1, text="Export Graph", 
                  command=self.canvas.export_graph).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Import Graph", 
                  command=self.canvas.import_graph).pack(side=tk.LEFT, padx=2)
        
        # Hide vertices control
        hide_frame = ttk.Frame(row1)
        hide_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(hide_frame, text="Hide vertices >").pack(side=tk.LEFT)
        hide_entry = ttk.Entry(hide_frame, textvariable=self.hide_var, width=5)
        hide_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(hide_frame, text="Apply", 
                  command=self.apply_hide).pack(side=tk.LEFT, padx=2)
        ttk.Button(hide_frame, text="Show All", 
                  command=self.show_all).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Info and manual mode status
        row2 = ttk.Frame(self.control_frame)
        row2.pack(fill=tk.X, pady=2)
        
        # Graph info
        info_frame = ttk.Frame(row2)
        info_frame.pack(side=tk.LEFT)
        
        self.info_var.set("Vertices: 3, Edges: 3, Periphery: 3")
        ttk.Label(info_frame, textvariable=self.info_var).pack(side=tk.LEFT)
        
        # Manual mode status (packed but not visible initially)
        self.manual_mode_label = ttk.Label(row2, textvariable=self.manual_mode_var, 
                                         foreground="red", font=("Arial", 10, "bold"))
        # Initially hidden
    
    def start_triangle(self):
        """Start new triangle"""
        self.canvas.command_processor.start_triangle()
        self.canvas.update_display()
        self.update_status("Started new triangle")
        self.update_info()
    
    def add_random_vertex(self):
        """Add random vertex"""
        self.canvas.add_random_vertex()
        self.update_info()
    
    def start_manual_add(self):
        """Start manual vertex addition"""
        self.canvas.manual_add_mode = True
        self.canvas.selected_vertices = []
        self.update_manual_mode_status()
        self.update_status("Manual add mode - Click two periphery vertices in clockwise order")
        self.canvas.update_display()
    
    def center_graph(self):
        """Center graph"""
        self.canvas.center_graph()
        self.update_info()
    
    def toggle_display(self):
        """Toggle display mode"""
        self.canvas.toggle_display_mode()
        self.update_info()
    
    def apply_hide(self):
        """Apply hide threshold"""
        try:
            threshold = int(self.hide_var.get()) if self.hide_var.get() else None
            self.canvas.hidden_threshold = threshold
            self.canvas.update_display()
            self.update_status(f"Hide threshold set to {threshold}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def show_all(self):
        """Show all vertices"""
        self.canvas.hidden_threshold = None
        self.canvas.update_display()
        self.update_status("Showing all vertices")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_var.set(message)
    
    def update_info(self):
        """Update graph information"""
        vertices = len(self.canvas.graph.vertices)
        edges = len(self.canvas.graph.edges)
        periphery = len(self.canvas.graph.periphery)
        zoom = self.canvas.zoom_level
        mode = self.canvas.view_mode.title()
        
        info_text = f"Vertices: {vertices}, Edges: {edges}, Periphery: {periphery}, Zoom: {zoom:.1f}x, Mode: {mode}"
        self.info_var.set(info_text)
    
    def update_manual_mode_status(self):
        """Update manual mode status"""
        if self.canvas.manual_add_mode:
            selected = len(self.canvas.selected_vertices)
            text = f"Manual Add Mode - Selected: {selected}/2 vertices"
            if selected > 0:
                text += f" ({', '.join(map(str, self.canvas.selected_vertices))})"
            text += " - Press ESC to cancel"
            self.manual_mode_var.set(text)
            if self.manual_mode_label:
                self.manual_mode_label.pack(side=tk.RIGHT, padx=10)
        else:
            if self.manual_mode_label:
                self.manual_mode_label.pack_forget()
    
    def on_window_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            # Update canvas size and redraw
            self.canvas.update_display()
    
    def run(self):
        """Run the application"""
        self.update_info()
        self.root.mainloop()

def main():
    """Main function"""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()