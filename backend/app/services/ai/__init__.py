"""
AI Services for Colonie-IA.

This package provides artificial intelligence capabilities for the game,
including game state analysis, decision making, and difficulty scaling.
"""
from app.services.ai.ai_difficulty import AIDifficultyLevel, DifficultyModifiers
from app.services.ai.game_analysis import GameAnalysis, GamePhase
from app.services.ai.ai_service import AIService
from app.services.ai.ai_expansion import AIExpansionService, ColonizationTarget

__all__ = [
    "AIDifficultyLevel",
    "DifficultyModifiers",
    "GameAnalysis",
    "GamePhase",
    "AIService",
    "AIExpansionService",
    "ColonizationTarget",
]
