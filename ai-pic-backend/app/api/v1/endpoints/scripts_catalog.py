"""Static script catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/formats")
async def get_script_formats():
    """Get script format list"""
    return [
        {"value": "screenplay", "label": "Screenplay"},
        {"value": "stage_play", "label": "Stage play"},
        {"value": "radio_drama", "label": "Radio drama"},
        {"value": "short_video", "label": "Short video script"},
        {"value": "live_stream", "label": "Live stream script"},
        {"value": "animation", "label": "Animation script"},
    ]


@router.get("/languages")
async def get_script_languages():
    """Get script language list"""
    return [
        {"value": "zh-CN", "label": "Simplified Chinese"},
        {"value": "zh-TW", "label": "Traditional Chinese"},
        {"value": "en-US", "label": "English"},
        {"value": "ja-JP", "label": "Japanese"},
        {"value": "ko-KR", "label": "Korean"},
    ]
