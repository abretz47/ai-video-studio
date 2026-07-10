from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StoryNovelExportSummary(BaseModel):
    """Lightweight novel export record used for history listing."""

    id: int
    business_id: str
    task_id: Optional[int] = None

    style: str = Field(..., description="output style, for example zhihu")
    target_words: int = Field(..., description="target word count")
    chapter_count: Optional[int] = Field(None, description="Zhang Jie Shu")
    total_words: Optional[int] = Field(None, description="Shi Ji word count")
    model: Optional[str] = Field(None, description="Sheng Cheng model(Yuan Yang)")
    temperature: Optional[float] = Field(None, description="Sheng Cheng Wen Du")

    file_relative_path: Optional[str] = Field(None, description="Dao Chu file Xiang Dui Lu Jing")
    created_at: datetime

    class Config:
        from_attributes = True


class StoryNovelExportListResponse(BaseModel):
    items: List[StoryNovelExportSummary]
