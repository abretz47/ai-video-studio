"""
Tou Liu Biao Sheng Cheng service

Cong script in Ti Lian 15/30/60 seconds Tou Liu Su Cai, Sheng Cheng Traffic Sheet.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.core.logging import get_logger
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.schemas.generation import TrafficSheet
from app.services.scoring.traffic_sheet_parser import parse_traffic_sheet_response

if TYPE_CHECKING:
    from app.services.ai_service import AIService

logger = get_logger()


class TrafficSheetService:
    """Tou Liu Biao Sheng Cheng service"""

    def __init__(self, ai_service: "AIService") -> None:
        self.ai_service = ai_service

    async def generate_traffic_sheet(
        self,
        script_content: str,
        episode_number: int,
        story: Optional[Dict[str, Any]] = None,
        episode_id: Optional[int] = None,
        episode_title: Optional[str] = None,
        episode_summary: Optional[str] = None,
        script_id: Optional[int] = None,
        scenes: Optional[List[Dict[str, Any]]] = None,
        dialogues: Optional[List[Dict[str, Any]]] = None,
        hook_plan: Optional[Dict[str, Any]] = None,
        prefer_provider: Optional[str] = None,
        prefer_model: Optional[str] = None,
    ) -> TrafficSheet:
        """
 Cong script Sheng Cheng Tou Liu Biao.

        Args:
 script_content: script body text content
 episode_number: episode ID
 story: story context(title, type, market, Wei type)
 episode_id: episode ID
 episode_title: episode title
 episode_summary: episode outline
 script_id: script ID
 scenes: scene list
 dialogues: dialogue list
 hook_plan: Shuang Dian/Gou Zi Gui Hua
 prefer_provider: priority Shi Yong AI provider
 prefer_model: priority Shi Yong model

        Returns:
 TrafficSheet: Tou Liu Biao
        """
        # build prompt Bian Liang
        variables = {
            "script_content": script_content,
            "episode_number": episode_number,
            "story": story or {},
            "episode_id": episode_id,
            "episode_title": episode_title or "",
            "episode_summary": episode_summary or "",
            "script_id": script_id,
            "scenes": scenes or [],
            "dialogues": dialogues or [],
            "hook_plan": hook_plan or {},
            "current_time": datetime.utcnow().isoformat(),
        }

        # Xuan Ran prompt
        prompt = prompt_manager.render_prompt(
            PromptTemplate.TRAFFIC_SHEET_GENERATION.value,
            variables,
        )

        logger.info(
            "Generating traffic sheet",
            extra={
                "episode_number": episode_number,
                "story_title": story.get("title") if story else None,
                "script_length": len(script_content),
            },
        )

        # call AI service
        ai_manager = getattr(self.ai_service, "ai_manager", None)
        if not ai_manager:
            logger.warning("AI manager unavailable, returning empty traffic sheet")
            return TrafficSheet(
                episode_id=episode_id,
                script_id=script_id,
                market_region=story.get("market_region") if story else None,
                micro_genre=story.get("micro_genre") if story else None,
                assets=[],
                generated_at=datetime.utcnow(),
            )

        schema = TrafficSheet.model_json_schema()
        resp = await ai_manager.generate_text(
            prompt=prompt,
            prefer_provider=prefer_provider,
            model=prefer_model,
            max_tokens=3000,
            temperature=0.5,
            json_schema={"name": "traffic_sheet_generation", "schema": schema},
            stream=False,
        )

        response_text = resp.data
        if isinstance(response_text, dict):
            response_text = json.dumps(response_text, ensure_ascii=False)
        if not isinstance(response_text, str):
            response_text = ""

        # parse response
        result = self._parse_traffic_sheet_response(
            response_text,
            episode_id=episode_id,
            script_id=script_id,
            story=story,
        )

        logger.info(
            "Traffic sheet generated",
            extra={
                "episode_number": episode_number,
                "asset_count": len(result.assets),
                "asset_15s": sum(1 for a in result.assets if a.duration_seconds == 15),
                "asset_30s": sum(1 for a in result.assets if a.duration_seconds == 30),
                "asset_60s": sum(1 for a in result.assets if a.duration_seconds == 60),
            },
        )

        return result

    def _parse_traffic_sheet_response(
        self,
        response: str,
        episode_id: Optional[int] = None,
        script_id: Optional[int] = None,
        story: Optional[Dict[str, Any]] = None,
    ) -> TrafficSheet:
        """parse AI response as Tou Liu Biao"""
        return parse_traffic_sheet_response(
            response,
            episode_id=episode_id,
            script_id=script_id,
            story=story,
        )


async def generate_traffic_sheet_from_db(
    ai_service: "AIService",
    script_id: int,
    db_session: Any,
    prefer_provider: Optional[str] = None,
    prefer_model: Optional[str] = None,
) -> TrafficSheet:
    """
 Cong database Jia Zai script and Sheng Cheng Tou Liu Biao(Bian Jie function).

    Args:
 ai_service: AI service instance
 script_id: script ID
 db_session: database Hui Hua
 prefer_provider: priority Shi Yong AI provider
 prefer_model: priority Shi Yong model

    Returns:
 TrafficSheet: Tou Liu Biao
    """
    from app.models.script import Script
    from app.utils.marketing_meta import merge_marketing_meta

    script = db_session.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise ValueError(f"Script {script_id} not found")

    # Jia Zai Guan Lian episode and story
    episode = getattr(script, "episode", None)
    story = getattr(episode, "story", None) if episode else None

    # build context
    story_ctx = None
    if story:
        marketing_meta = merge_marketing_meta(
            story.extra_metadata if isinstance(story.extra_metadata, dict) else {},
            script.extra_metadata if isinstance(script.extra_metadata, dict) else {},
            (
                script.generation_params
                if isinstance(script.generation_params, dict)
                else {}
            ),
        )
        story_ctx = {
            "title": story.title,
            "genre": story.genre,
            "market_region": marketing_meta.get("market_region"),
            "micro_genre": marketing_meta.get("micro_genre"),
        }

    marketing_meta = merge_marketing_meta(
        (
            story.extra_metadata
            if story and isinstance(story.extra_metadata, dict)
            else {}
        ),
        (
            episode.extra_metadata
            if episode and isinstance(episode.extra_metadata, dict)
            else {}
        ),
        script.extra_metadata if isinstance(script.extra_metadata, dict) else {},
        script.generation_params if isinstance(script.generation_params, dict) else {},
    )
    hook_plan = marketing_meta.get("hook_plan")

    # Sheng Cheng Tou Liu Biao
    service = TrafficSheetService(ai_service)
    return await service.generate_traffic_sheet(
        script_content=script.content or "",
        episode_number=episode.episode_number if episode else 1,
        story=story_ctx,
        episode_id=episode.id if episode else None,
        episode_title=episode.title if episode else None,
        episode_summary=episode.summary if episode else None,
        script_id=script_id,
        scenes=script.scenes or [],
        dialogues=script.dialogues or [],
        hook_plan=hook_plan,
        prefer_provider=prefer_provider,
        prefer_model=prefer_model,
    )
