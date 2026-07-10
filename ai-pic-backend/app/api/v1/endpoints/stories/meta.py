from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/genres")
async def get_story_genres():
    """Get story genre list"""
    return [
        {"value": "drama", "label": "Drama"},
        {"value": "comedy", "label": "Comedy"},
        {"value": "romance", "label": "Romance"},
        {"value": "thriller", "label": "Thriller"},
        {"value": "action", "label": "Action"},
        {"value": "fantasy", "label": "Fantasy"},
        {"value": "sci-fi", "label": "Sci-fi"},
        {"value": "horror", "label": "Horror"},
        {"value": "mystery", "label": "Mystery"},
        {"value": "historical", "label": "Historical"},
        {"value": "biographical", "label": "Biographical"},
        {"value": "documentary", "label": "Documentary"},
    ]
