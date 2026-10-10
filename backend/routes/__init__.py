"""Backend Routes Package"""
from .meta_routes import meta_bp
from .analyze_routes import analyze_bp
from .feedback_routes import feedback_bp

__all__ = ["meta_bp", "analyze_bp", "feedback_bp"]
