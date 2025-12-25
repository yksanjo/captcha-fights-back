"""
Challenge Generator
Uses LLM to generate dynamic CAPTCHA challenges.
"""

import ollama
import json
import random
from typing import Dict, Optional
from loguru import logger


class ChallengeGenerator:
    """Generates adaptive CAPTCHA challenges using LLM."""
    
    def __init__(self, model: str = "phi3:mini"):
        """Initialize challenge generator."""
        self.model = model
        self.challenge_templates = [
            "logic_puzzle",
            "math_problem",
            "pattern_recognition",
            "contextual_question",
            "sequence_completion"
        ]
    
    def generate_challenge(self, difficulty: str = "medium") -> Dict:
        """Generate a new challenge."""
        challenge_type = random.choice(self.challenge_templates)
        
        prompt = f"""Generate a {difficulty} difficulty {challenge_type} CAPTCHA challenge.

Requirements:
- Should be solvable by humans in 10-30 seconds
- Should be difficult for bots/AI to solve
- Provide a clear question
- Provide the correct answer
- Make it engaging

Format as JSON:
{{
    "question": "the challenge question",
    "answer": "the correct answer",
    "type": "{challenge_type}",
    "difficulty": "{difficulty}",
    "hints": ["optional hint 1", "optional hint 2"]
}}

Challenge:"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.7}
            )
            
            text = response["response"]
            
            # Parse JSON from response
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                challenge_data = json.loads(text[json_start:json_end])
            else:
                # Fallback challenge
                challenge_data = self._generate_fallback(difficulty)
            
            challenge_data["challenge_id"] = f"ch_{random.randint(100000, 999999)}"
            return challenge_data
            
        except Exception as e:
            logger.error(f"Error generating challenge: {e}")
            return self._generate_fallback(difficulty)
    
    def _generate_fallback(self, difficulty: str) -> Dict:
        """Generate a fallback challenge if LLM fails."""
        questions = [
            {
                "question": "What is 7 + 5?",
                "answer": "12",
                "type": "math_problem",
                "difficulty": difficulty
            },
            {
                "question": "What day comes after Monday?",
                "answer": "Tuesday",
                "type": "contextual_question",
                "difficulty": difficulty
            },
            {
                "question": "If all cats are animals, and Fluffy is a cat, what is Fluffy?",
                "answer": "animal",
                "type": "logic_puzzle",
                "difficulty": difficulty
            }
        ]
        challenge = random.choice(questions)
        challenge["challenge_id"] = f"ch_{random.randint(100000, 999999)}"
        return challenge




