"""
Utility functions for the planar graph visualizer
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import json
import time

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_angle(p1: Tuple[float, float], center: Tuple[float, float], 
                   p2: Tuple[float, float]) -> float:
    """
    Calculate angle between three points (in radians)
    """
    v1 = (p1[0] - center[0], p1[1] - center[1])
    v2 = (p2[0] - center[0], p2[1] - center[1])
    
    # Calculate dot product and magnitudes
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
    magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    # Calculate angle
    cos_angle = dot_product / (magnitude1 * magnitude2)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to avoid numerical errors
    
    return math.acos(cos_angle)

def rotate_point(point: Tuple[float, float], center: Tuple[float, float], 
                angle: float) -> Tuple[float, float]:
    """
    Rotate a point around a center by the given angle (in radians)
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate to origin
    x = point[0] - center[0]
    y = point[1] - center[1]
    
    # Rotate
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # Translate back
    return (new_x + center[0], new_y + center[1])

def normalize_angle(angle: float) -> float:
    """
    Normalize angle to [0, 2π] range
    """
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle

def point_to_line_distance(point: Tuple[float, float], line_start: Tuple[float, float], 
                          line_end: Tuple[float, float]) -> float:
    """
    Calculate the shortest distance from a point to a line segment
    """
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Calculate line length
    line_length = calculate_distance(line_start, line_end)
    
    if line_length == 0:
        return calculate_distance(point, line_start)
    
    # Calculate parameter t for the closest point on the line
    t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / (line_length ** 2)
    
    # Clamp t to [0, 1] to stay within the line segment
    t = max(0, min(1, t))
    
    # Find the closest point on the line segment
    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)
    
    return calculate_distance(point, (closest_x, closest_y))

def lines_intersect(line1_start: Tuple[float, float], line1_end: Tuple[float, float],
                   line2_start: Tuple[float, float], line2_end: Tuple[float, float]) -> bool:
    """
    Check if two line segments intersect
    """
    x1, y1 = line1_start
    x2, y2 = line1_end
    x3, y3 = line2_start
    x4, y4 = line2_end
    
    # Calculate the denominator
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:  # Lines are parallel
        return False
    
    # Calculate parameters
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Check if intersection occurs within both line segments
    return 0 <= t <= 1 and 0 <= u <= 1

def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Calculate the convex hull of a set of points using Graham scan
    """
    if len(points) < 3:
        return points
    
    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    # Sort points lexicographically
    points = sorted(set(points))
    
    if len(points) <= 1:
        return points
    
    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    
    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    
    # Remove last point of each half because it's repeated
    return lower[:-1] + upper[:-1]

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def calculate_polygon_area(points: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula
    """
    if len(points) < 3:
        return 0
    
    area = 0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    
    return abs(area) / 2

def calculate_polygon_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a polygon
    """
    if not points:
        return (0, 0)
    
    if len(points) == 1:
        return points[0]
    
    if len(points) == 2:
        return ((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2)
    
    area = calculate_polygon_area(points)
    if area == 0:
        # Degenerate case - return simple average
        return (sum(p[0] for p in points) / len(points), 
                sum(p[1] for p in points) / len(points))
    
    cx = cy = 0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        factor = points[i][0] * points[j][1] - points[j][0] * points[i][1]
        cx += (points[i][0] + points[j][0]) * factor
        cy += (points[i][1] + points[j][1]) * factor
    
    cx /= (6 * area)
    cy /= (6 * area)
    
    return (cx, cy)

def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values
    """
    return a + t * (b - a)

def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max
    """
    return max(min_value, min(max_value, value))

def format_number(value: float, precision: int = 2) -> str:
    """
    Format a number with specified precision
    """
    return f"{value:.{precision}f}"

def safe_divide(a: float, b: float, default: float = 0) -> float:
    """
    Safe division that returns default value if divisor is zero
    """
    return a / b if abs(b) > 1e-10 else default

def create_timestamp() -> str:
    """
    Create a timestamp string for logging
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def validate_json(data: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate JSON string and return parsed data if valid
    """
    try:
        parsed = json.loads(data)
        return True, parsed
    except json.JSONDecodeError as e:
        return False, None

def deep_copy_dict(original: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a deep copy of a dictionary
    """
    return json.loads(json.dumps(original))

def calculate_bounding_box(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box (min_x, min_y, max_x, max_y) for a list of points
    """
    if not points:
        return (0, 0, 0, 0)
    
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    return (min_x, min_y, max_x, max_y)

def expand_bounding_box(bbox: Tuple[float, float, float, float], 
                       padding: float) -> Tuple[float, float, float, float]:
    """
    Expand a bounding box by adding padding
    """
    min_x, min_y, max_x, max_y = bbox
    return (min_x - padding, min_y - padding, max_x + padding, max_y + padding)

def points_are_collinear(p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float], tolerance: float = 1e-10) -> bool:
    """
    Check if three points are collinear within a tolerance
    """
    # Calculate the cross product of vectors (p2-p1) and (p3-p1)
    cross = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
    return abs(cross) < tolerance

def generate_random_color() -> str:
    """
    Generate a random hex color
    """
    import random
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def color_distance(color1: str, color2: str) -> float:
    """
    Calculate perceptual distance between two hex colors
    """
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    # Simple Euclidean distance in RGB space
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

def performance_timer(func):
    """
    Decorator to measure function execution time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

class CircularBuffer:
    """
    Simple circular buffer for storing recent values
    """
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = [None] * size
        self.index = 0
        self.count = 0
    
    def append(self, item):
        self.buffer[self.index] = item
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
    
    def get_all(self):
        if self.count < self.size:
            return self.buffer[:self.count]
        else:
            return self.buffer[self.index:] + self.buffer[:self.index]
    
    def get_last(self, n: int):
        all_items = self.get_all()
        return all_items[-n:] if n <= len(all_items) else all_items

def smooth_values(values: List[float], window_size: int = 3) -> List[float]:
    """
    Apply moving average smoothing to a list of values
    """
    if window_size <= 1 or len(values) <= window_size:
        return values[:]
    
    smoothed = []
    half_window = window_size // 2
    
    for i in range(len(values)):
        start = max(0, i - half_window)
        end = min(len(values), i + half_window + 1)
        smoothed.append(sum(values[start:end]) / (end - start))
    
    return smoothed
