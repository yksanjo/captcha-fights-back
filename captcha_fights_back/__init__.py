"""
CAPTCHA That Fights Back
"""

__version__ = "0.1.0"
__author__ = "yksanjo"

from .challenge_generator import ChallengeGenerator
from .behavior_analyzer import BehaviorAnalyzer
from .bot_scorer import BotScorer

__all__ = ["ChallengeGenerator", "BehaviorAnalyzer", "BotScorer"]

