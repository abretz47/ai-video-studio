"""Schemas for LLM-generated dynamic storyboard image prompts."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class FramePromptItem(BaseModel):
    """One frame's dynamically generated prompt bundle."""

    frame_index: int = Field(..., description="Zhen in storyboard list in index")
    image_prompt: str = Field(..., description="Dan Zhen storyboard Tu Sheng Tu prompt Ci")
    start_keyframe_prompt: str = Field(..., description="first frame Guan Jian Zhen prompt Ci")
    end_keyframe_prompt: str = Field(..., description="Wei Zhen Guan Jian Zhen prompt Ci")


class DynamicPromptBatch(BaseModel):
    """LLM batch output: prompts for all frames of one scene chunk."""

    frames: List[FramePromptItem]
