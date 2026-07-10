"""
AI workflow node prompt management module

This module provides unified prompt management for templates used by various AI tasks.
Includes: 
- virtual IP generation
- character profile generation
- story outline generation
- episode generation
- script generation
- image generation
and more
"""

from.manager import PromptManager
from.templates import (
 DEFAULT_GENERATION_PARAMS,
 NEGATIVE_PROMPTS,
 QUALITY_ENHANCERS,
 TEMPLATE_EXAMPLES,
 DialogueStyle,
 ImageCategory,
 ImageStyle,
 Pacing,
 PlotComplexity,
 PromptCategory,
 PromptTemplate,
 ScriptFormat,
 get_category_by_template,
 get_template_by_category,
)

__all__ = [
 "DEFAULT_GENERATION_PARAMS",
 "NEGATIVE_PROMPTS",
 "QUALITY_ENHANCERS",
 "TEMPLATE_EXAMPLES",
 "DialogueStyle",
 "ImageCategory",
 "ImageStyle",
 "Pacing",
 "PlotComplexity",
 "PromptCategory",
 "PromptManager",
 "PromptTemplate",
 "ScriptFormat",
 "get_category_by_template",
 "get_template_by_category",
]
