"""
script Ping Fen service

Shi Xian HookScore/ScriptScore agent, Ping Gu short drama script Tou Liu Xiao Guo and Zhi Zuo Ke Xing Xing.
Ping Fen Wei Du: conflict Qiang Du, character Bian Shi Du, Wen Hua Shi Pei, Su Cai can Jian Xing, Luo Ji Yi Zhi Xing(Ge 0-5 Fen)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.core.logging import get_logger
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.schemas.generation import ScriptScoreDimensions, ScriptScoreResult
from app.services.scoring.script_score_calibration import (
    calibrate_commercial_anchor_score,
)
from app.services.scoring.script_score_schema import (
    script_score_json_schema,
    script_score_json_schema as _script_score_json_schema,
)
from app.services.script_score_thresholds import (
    PASS_DIMENSION_THRESHOLD,
    PASS_OVERALL_THRESHOLD,
    REVIEW_DIMENSION_MIN,
    REVIEW_OVERALL_MIN,
)
from app.utils.json_utils import extract_json_block

if TYPE_CHECKING:
    from app.services.ai_service import AIService

logger = get_logger()


class ScriptScoreService:
    """script Ping Fen service"""

    def __init__(self, ai_service: "AIService") -> None:
        self.ai_service = ai_service

    async def score_script(
        self,
        script_content: str,
        story: Optional[Dict[str, Any]] = None,
        episode: Optional[Dict[str, Any]] = None,
        scenes: Optional[List[Dict[str, Any]]] = None,
        dialogues: Optional[List[Dict[str, Any]]] = None,
        prefer_provider: Optional[str] = None,
        prefer_model: Optional[str] = None,
    ) -> ScriptScoreResult:
        """
 Ping Gu script Zhi Liang and return Ping Fen Jie Guo.

        Args:
 script_content: script body text content
 story: story context(title, type, market, Wei type)
 episode: episode context(Ji Shu, title, outline)
 scenes: scene list
 dialogues: dialogue list
 prefer_provider: priority Shi Yong AI provider
 prefer_model: priority Shi Yong model

        Returns:
 ScriptScoreResult: Ping Fen Jie Guo
        """
        # build prompt Bian Liang
        variables = {
            "script_content": script_content,
            "story": story or {},
            "episode": episode or {},
            "scenes": scenes or [],
            "dialogues": dialogues or [],
        }

        # Xuan Ran prompt
        prompt = prompt_manager.render_prompt(
            PromptTemplate.SCRIPT_SCORE.value,
            variables,
        )

        logger.info(
            "Scoring script",
            extra={
                "story_title": story.get("title") if story else None,
                "episode_number": episode.get("episode_number") if episode else None,
                "script_length": len(script_content),
            },
        )

        # call AI service
        ai_manager = getattr(self.ai_service, "ai_manager", None)
        if not ai_manager:
            logger.warning("AI manager unavailable, returning default score result")
            return self._default_score_result()

        resp = await ai_manager.generate_text(
            prompt=prompt,
            prefer_provider=prefer_provider,
            model=prefer_model,
            max_tokens=2000,
            temperature=0.3,  # Di Wen Du Yi keep Ping Fen Yi Zhi Xing
            json_schema={"name": "script_score", "schema": script_score_json_schema()},
            stream=False,
        )

        response_text = resp.data
        if isinstance(response_text, dict):
            response_text = json.dumps(response_text, ensure_ascii=False)
        if not isinstance(response_text, str):
            response_text = ""

        # parse response
        result = self._parse_score_response(response_text)
        result = calibrate_commercial_anchor_score(result, script_content)

        logger.info(
            "Script scored",
            extra={
                "overall_score": result.overall_score,
                "verdict": result.verdict,
                "strengths_count": len(result.strengths),
                "risks_count": len(result.risks),
                "provider_used": getattr(resp, "provider", None),
                "model_used": getattr(resp, "model", None),
            },
        )

        return result

    def _parse_score_response(self, response: str) -> ScriptScoreResult:
        """parse AI response as Ping Fen Jie Guo"""
        try:
            data = extract_json_block(response)
            if not data:
                raise ValueError("No JSON found in response")

            # parse Wei Du Ping Fen
            dim_data = data.get("dimension_scores", {})
            dimensions = ScriptScoreDimensions(
                conflict_intensity=float(dim_data.get("conflict_intensity", 3.0)),
                character_recognizability=float(
                    dim_data.get("character_recognizability", 3.0)
                ),
                cultural_fit=float(dim_data.get("cultural_fit", 3.0)),
                clip_ability=float(dim_data.get("clip_ability", 3.0)),
                logic_coherence=float(dim_data.get("logic_coherence", 3.0)),
            )

            # Ji Suan Zong Fen(Ru Guo AI not Ti Gong)
            overall = data.get("overall_score")
            if overall is None:
                overall = (
                    dimensions.conflict_intensity
                    + dimensions.character_recognizability
                    + dimensions.cultural_fit
                    + dimensions.clip_ability
                    + dimensions.logic_coherence
                ) / 5.0

            # Pan Ding Jie Guo(Ru Guo AI not Ti Gong or not Zhun Que)
            verdict = self._compute_verdict(float(overall), dimensions)

            return ScriptScoreResult(
                overall_score=float(overall),
                dimension_scores=dimensions,
                verdict=verdict,
                strengths=data.get("strengths", []),
                risks=data.get("risks", []),
                rewrite_guidance=data.get("rewrite_guidance", []),
                suggested_ad_hooks=data.get("suggested_ad_hooks", []),
            )

        except Exception as e:
            logger.warning(f"Failed to parse score response: {e}, using defaults")
            return self._default_score_result()

    def _compute_verdict(
        self, overall: float, dimensions: ScriptScoreDimensions
    ) -> str:
        """Gen Ju Yu Zhi Ji Suan Pan Ding Jie Guo"""
        min_dim = min(
            dimensions.conflict_intensity,
            dimensions.character_recognizability,
            dimensions.cultural_fit,
            dimensions.clip_ability,
            dimensions.logic_coherence,
        )

        # Pass: Zong Fen >= 4.0 Qie none any Wei Du < 3.5
        if overall >= PASS_OVERALL_THRESHOLD and min_dim >= PASS_DIMENSION_THRESHOLD:
            return "pass"

        # Rewrite: Zong Fen < 3.5 or Ren Yi Wei Du < 3.0
        if overall < REVIEW_OVERALL_MIN or min_dim < REVIEW_DIMENSION_MIN:
            return "rewrite"

        # Review: Qi Ta Qing Kuang
        return "review"

    def _default_score_result(self) -> ScriptScoreResult:
        """return default Ping Fen Jie Guo(parse failed when Shi Yong)"""
        default_dims = ScriptScoreDimensions(
            conflict_intensity=3.0,
            character_recognizability=3.0,
            cultural_fit=3.0,
            clip_ability=3.0,
            logic_coherence=3.0,
        )
        return ScriptScoreResult(
            overall_score=3.0,
            dimension_scores=default_dims,
            verdict="review",
            strengths=[],
            risks=["Ping Fen parse failed, suggestion Ren Gong Shen He"],
            rewrite_guidance=["Qing retry submit Ping Fen or Ren Gong Shen He"],
            suggested_ad_hooks=[],
        )
