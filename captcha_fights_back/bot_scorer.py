"""
Bot Scorer
Scores user behavior to detect bots.
"""

from typing import Dict, List
from .behavior_analyzer import BehaviorAnalyzer, InteractionPoint


class BotScorer:
    """Scores user behavior for bot detection."""
    
    def __init__(self):
        """Initialize bot scorer."""
        self.analyzer = BehaviorAnalyzer()
    
    def score(self, 
              interaction_path: List[Dict],
              browser_fingerprint: Dict,
              answer_correct: bool) -> Dict:
        """Score user behavior."""
        # Convert interaction path
        interactions = [
            InteractionPoint(
                x=p["x"],
                y=p["y"],
                timestamp=p["timestamp"],
                event_type=p.get("event_type", "click")
            )
            for p in interaction_path
        ]
        
        # Analyze behavior
        behavior = self.analyzer.analyze_interaction_path(interactions)
        
        # Compute bot score (0 = human, 1 = bot)
        bot_score = 0.0
        
        # Behavior analysis
        if not behavior["is_human"]:
            bot_score += 0.4
        
        if behavior["complexity"] < 0.5:  # Too simple path
            bot_score += 0.2
        
        # Browser fingerprint checks
        if browser_fingerprint.get("canvas_hash") == "suspicious":
            bot_score += 0.2
        
        if browser_fingerprint.get("webgl_hash") == "suspicious":
            bot_score += 0.1
        
        # Answer correctness (bots might answer too quickly)
        if not answer_correct:
            bot_score += 0.1
        
        bot_score = min(1.0, bot_score)
        
        return {
            "bot_score": bot_score,
            "is_bot": bot_score > 0.6,
            "behavior_analysis": behavior,
            "confidence": abs(bot_score - 0.5) * 2  # Higher when closer to 0 or 1
        }

