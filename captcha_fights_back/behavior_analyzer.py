"""
Behavior Analyzer
Analyzes user interaction patterns using topological methods.
"""

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
import networkx as nx


@dataclass
class InteractionPoint:
    """Represents a point in user interaction."""
    x: float
    y: float
    timestamp: float
    event_type: str  # click, move, keypress


class BehaviorAnalyzer:
    """Analyzes user behavior patterns for bot detection."""
    
    def __init__(self):
        """Initialize behavior analyzer."""
        pass
    
    def analyze_interaction_path(self, interactions: List[InteractionPoint]) -> Dict:
        """Analyze interaction path using topological methods."""
        if len(interactions) < 3:
            return {"complexity": 0.0, "is_human": False}
        
        # Convert to point cloud
        points = np.array([[p.x, p.y, p.timestamp] for p in interactions])
        
        # Compute path complexity
        complexity = self._compute_path_complexity(points)
        
        # Check for bot-like patterns
        is_human = self._check_human_patterns(interactions)
        
        return {
            "complexity": complexity,
            "is_human": is_human,
            "num_interactions": len(interactions),
            "duration": interactions[-1].timestamp - interactions[0].timestamp
        }
    
    def _compute_path_complexity(self, points: np.ndarray) -> float:
        """Compute topological complexity of interaction path."""
        if len(points) < 3:
            return 0.0
        
        # Compute total path length
        distances = np.diff(points[:, :2], axis=0)
        path_length = np.sum(np.linalg.norm(distances, axis=1))
        
        # Compute straight-line distance
        start = points[0, :2]
        end = points[-1, :2]
        straight_distance = np.linalg.norm(end - start)
        
        # Complexity = path_length / straight_distance (higher = more complex)
        if straight_distance > 0:
            complexity = path_length / straight_distance
        else:
            complexity = 1.0
        
        return float(complexity)
    
    def _check_human_patterns(self, interactions: List[InteractionPoint]) -> bool:
        """Check if interaction patterns look human."""
        if len(interactions) < 5:
            return False
        
        # Check timing variance (humans have irregular timing)
        timestamps = [p.timestamp for p in interactions]
        time_diffs = np.diff(timestamps)
        
        if len(time_diffs) == 0:
            return False
        
        # High variance = human-like
        variance = np.var(time_diffs)
        if variance < 0.01:  # Too regular = bot
            return False
        
        # Check movement patterns (humans don't move in perfect lines)
        movements = []
        for i in range(1, len(interactions)):
            dx = interactions[i].x - interactions[i-1].x
            dy = interactions[i].y - interactions[i-1].y
            movements.append((dx, dy))
        
        if len(movements) < 2:
            return True
        
        # Check for too-perfect patterns
        angles = []
        for i in range(1, len(movements)):
            v1 = movements[i-1]
            v2 = movements[i]
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
        
        if len(angles) > 0:
            angle_variance = np.var(angles)
            if angle_variance < 0.01:  # Too regular = bot
                return False
        
        return True




