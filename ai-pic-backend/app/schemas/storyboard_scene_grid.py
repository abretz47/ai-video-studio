"""Schemas for scene-level grid storyboard sheets and continuous videos."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SceneGridCell(BaseModel):
    """One panel's metadata inside the grid sheet."""

    panel_index: int = Field(..., description="Gong Ge Xu Hao, Cong1Kai Shi")
    title: str = Field(..., description="shot name(note Lan title)")
    caption: str = Field("", description="note Lan Wen Zi")


class SceneGridPromptModel(BaseModel):
    """LLM output schema for the grid sheet prompt."""

    sheet_prompt: str = Field(..., description="Gong Ge storyboard Da Tu Sheng Tu prompt Ci")
    cells: List[SceneGridCell]


class SceneGridVideoPromptModel(BaseModel):
    """LLM output schema for the grid-to-video prompt."""

    video_prompt: str = Field(..., description="Gong Ge Tu Zhuan Lian Xu Cheng Pian video prompt Ci")


class SceneGridCharacterRef(BaseModel):
    """User-selected character reference for grid generation."""

    virtual_ip_id: Optional[int] = None
    url: Optional[str] = None
    name: Optional[str] = None


class SceneGridSheetRequest(BaseModel):
    """Request schema for generating a scene grid storyboard sheet."""

    scene_number: int = Field(..., description="scene ID")
    grid_size: int = Field(12, description="Gong Ge Shu Liang(4/6/9/12/16)")
    model: Optional[str] = Field(None, description="Sheng Tu model")
    generation_profile: Optional[str] = None
    style: Optional[str] = Field(None, description="style")
    aspect_ratio: str = Field("16:9", description="Hua Fu ratio")
    character_refs: Optional[List[SceneGridCharacterRef]] = Field(
        None, description="user Xuan Ze character reference Tu"
    )
    environment_refs: Optional[List[str]] = Field(
        None, description="user Xuan Ze environment reference Tu URL list"
    )


class SceneGridVideoRequest(BaseModel):
    """Request schema for generating a continuous video from the grid sheet."""

    scene_number: int = Field(..., description="scene ID")
    model: Optional[str] = Field("seedance-2.0", description="video model")
    duration: Optional[int] = Field(
        None, description="target when Zhang(seconds, 4-15; Bu Chuan then An Zhen duration He Ji and Jie Duan)"
    )
    resolution: Optional[str] = Field("720p", description="Fen Bian Lv")
    ratio: Optional[str] = Field(None, description="Hua Fu ratio")
    generate_audio: Optional[bool] = Field(None, description="Shi Fou Sheng Cheng audio")
    prompt: Optional[str] = Field(None, description="Zi Ding Yi video prompt Ci Fu Gai")


class SceneGridInfo(BaseModel):
    """Persisted scene grid payload returned to clients."""

    scene_number: int
    status: str = "ready"
    sheet_prompt: Optional[str] = None
    prompt_source: Optional[str] = None
    cells: Optional[List[Dict[str, Any]]] = None
    image_url: Optional[str] = None
    refs_used: Optional[List[Dict[str, Any]]] = None
    video_prompt: Optional[str] = None
    video_url: Optional[str] = None
    video_thumbnail_url: Optional[str] = None
    model: Optional[str] = None
    video_model: Optional[str] = None
    generated_at: Optional[str] = None
    video_generated_at: Optional[str] = None
