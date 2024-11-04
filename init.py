"""
Feedback Analyzer
================

A package for analyzing open-ended feedback using Large Language Models.
"""

from .analyzer import FeedbackAnalyzer
from .thematic import ThematicAnalyzer

__version__ = "0.1.0"
__all__ = ['FeedbackAnalyzer', 'ThematicAnalyzer']