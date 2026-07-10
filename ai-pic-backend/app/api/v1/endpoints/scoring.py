"""
Script scoring and traffic-sheet API endpoints

Provides HookScore/ScriptScore scoring endpoints and Traffic Sheet generation endpoints.
"""

from typing import Optional

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.generation import ScriptScoreResult, TrafficSheet
from app.services.scoring import ScriptScoreService, TrafficSheetService
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

logger = get_logger()
router = APIRouter()


# ========== Request/Response Schemas ==========


class ScoreScriptRequest(BaseModel):
    """Script scoring request"""

    script_id: Optional[int] = Field(None, description="Script ID (loaded from the database)")
    script_content: Optional[str] = Field(None, description="Script content (passed directly)")
    story_title: Optional[str] = Field(None, description="Story title")
    story_genre: Optional[str] = Field(None, description="Story genre")
    market_region: Optional[str] = Field(None, description="Target market")
    micro_genre: Optional[str] = Field(None, description="Micro-genre")
    episode_number: Optional[int] = Field(None, description="Episode number")
    episode_title: Optional[str] = Field(None, description="Episode title")
    prefer_provider: Optional[str] = Field(None, description="Preferred AI provider")
    prefer_model: Optional[str] = Field(None, description="Preferred model")


class GenerateTrafficSheetRequest(BaseModel):
    """Traffic-sheet generation request"""

    script_id: Optional[int] = Field(None, description="Script ID (loaded from the database)")
    script_content: Optional[str] = Field(None, description="Script content (passed directly)")
    episode_number: int = Field(..., description="Episode number")
    episode_id: Optional[int] = Field(None, description="Episode ID")
    episode_title: Optional[str] = Field(None, description="Episode title")
    episode_summary: Optional[str] = Field(None, description="Episode summary")
    story_title: Optional[str] = Field(None, description="Story title")
    story_genre: Optional[str] = Field(None, description="Story genre")
    market_region: Optional[str] = Field(None, description="Target market")
    micro_genre: Optional[str] = Field(None, description="Micro-genre")
    prefer_provider: Optional[str] = Field(None, description="Preferred AI provider")
    prefer_model: Optional[str] = Field(None, description="Preferred model")


# ========== Endpoints ==========


@router.post("/score", response_model=ScriptScoreResult)
async def score_script(
    request: ScoreScriptRequest,
    db: Session = Depends(get_db),
) -> ScriptScoreResult:
    """
    Evaluate script quality.

    Scoring dimensions:
    - Conflict intensity (0-5)
    - Character distinctiveness (0-5)
    - Cultural fit (0-5)
    - Editability of source material (0-5)
    - Logical consistency (0-5)

    Decision thresholds:
    - Pass: total score >= 4.0 and no dimension < 3.5
    - Review: total score 3.5-3.9 or any dimension 3.0-3.4
    - Rewrite: total score < 3.5 or any dimension < 3.0
    """
    # Either script_id or script_content must be provided
    if not request.script_id and not request.script_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either script_id or script_content must be provided",
        )

    from app.services.ai_service import ai_service

    score_service = ScriptScoreService(ai_service)

    # If script_id is provided, load from the database
    if request.script_id:
        from app.services.scoring import score_script_from_db

        try:
            result = await score_script_from_db(
                ai_service=ai_service,
                script_id=request.script_id,
                db_session=db,
                prefer_provider=request.prefer_provider,
                prefer_model=request.prefer_model,
            )
            return result
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    # Use directly provided content
    story_ctx = None
    if request.story_title or request.story_genre or request.market_region:
        story_ctx = {
            "title": request.story_title,
            "genre": request.story_genre,
            "market_region": request.market_region,
            "micro_genre": request.micro_genre,
        }

    episode_ctx = None
    if request.episode_number or request.episode_title:
        episode_ctx = {
            "episode_number": request.episode_number,
            "title": request.episode_title,
        }

    result = await score_service.score_script(
        script_content=request.script_content,
        story=story_ctx,
        episode=episode_ctx,
        prefer_provider=request.prefer_provider,
        prefer_model=request.prefer_model,
    )

    return result


@router.post("/traffic-sheet", response_model=TrafficSheet)
async def generate_traffic_sheet(
    request: GenerateTrafficSheetRequest,
    db: Session = Depends(get_db),
) -> TrafficSheet:
    """
    Generate a traffic sheet from a script (Traffic Sheet).

    Generate 15/30/60-second traffic assets, including:
    - asset_id: Unique asset identifier
    - duration_seconds: Duration
    - hook_type: Hook type
    - key_line: Subtitle anchor
    - visual_hook: Visual hook
    - shot_list: List of key shots
    - cliff_or_cta: Beat/CTA copy

    Target: for every 10 episodes, produce 12-20 15s assets, 6-10 30s assets, and 2-4 60s assets
    """
    # Either script_id or script_content must be provided
    if not request.script_id and not request.script_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either script_id or script_content must be provided",
        )

    from app.services.ai_service import ai_service

    traffic_service = TrafficSheetService(ai_service)

    # If script_id is provided, load from the database
    if request.script_id:
        from app.services.scoring import generate_traffic_sheet_from_db

        try:
            result = await generate_traffic_sheet_from_db(
                ai_service=ai_service,
                script_id=request.script_id,
                db_session=db,
                prefer_provider=request.prefer_provider,
                prefer_model=request.prefer_model,
            )
            return result
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    # Use directly provided content
    story_ctx = None
    if request.story_title or request.story_genre or request.market_region:
        story_ctx = {
            "title": request.story_title,
            "genre": request.story_genre,
            "market_region": request.market_region,
            "micro_genre": request.micro_genre,
        }

    result = await traffic_service.generate_traffic_sheet(
        script_content=request.script_content,
        episode_number=request.episode_number,
        story=story_ctx,
        episode_id=request.episode_id,
        episode_title=request.episode_title,
        episode_summary=request.episode_summary,
        prefer_provider=request.prefer_provider,
        prefer_model=request.prefer_model,
    )

    return result


@router.get("/score/{script_id}", response_model=ScriptScoreResult)
async def get_script_score(
    script_id: int,
    prefer_provider: Optional[str] = None,
    prefer_model: Optional[str] = None,
    db: Session = Depends(get_db),
) -> ScriptScoreResult:
    """
    Get the score by script ID (convenience endpoint).
    """
    from app.services.ai_service import ai_service
    from app.services.scoring import score_script_from_db

    try:
        result = await score_script_from_db(
            ai_service=ai_service,
            script_id=script_id,
            db_session=db,
            prefer_provider=prefer_provider,
            prefer_model=prefer_model,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/traffic-sheet/{script_id}", response_model=TrafficSheet)
async def get_traffic_sheet(
    script_id: int,
    prefer_provider: Optional[str] = None,
    prefer_model: Optional[str] = None,
    db: Session = Depends(get_db),
) -> TrafficSheet:
    """
    Generate the traffic sheet by script ID (convenience endpoint).
    """
    from app.services.ai_service import ai_service
    from app.services.scoring import generate_traffic_sheet_from_db

    try:
        result = await generate_traffic_sheet_from_db(
            ai_service=ai_service,
            script_id=script_id,
            db_session=db,
            prefer_provider=prefer_provider,
            prefer_model=prefer_model,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
