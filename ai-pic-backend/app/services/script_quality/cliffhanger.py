from __future__ import annotations

from typing import Any

from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.schemas.script_quality import ScriptLintIssue, ScriptLintRuleResult
from app.utils.json_utils import extract_json_block

CLIFFHANGER_LLM_UNAVAILABLE = "cliffhanger_llm_unavailable"
CLIFFHANGER_PROMPT_TEMPLATE = "script_cliffhanger_judgement"

_CLIFFHANGER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["passed", "score", "reason", "evidence", "suggestion"],
    "properties": {
        "passed": {"type": "boolean"},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
        "evidence": {"type": "string"},
        "suggestion": {"type": "string"},
    },
}


def check_cliffhanger(
    non_empty: list[tuple[int, str]],
) -> tuple[ScriptLintRuleResult, list[ScriptLintIssue]]:
    return _unavailable_result(
        non_empty,
        CLIFFHANGER_LLM_UNAVAILABLE,
        "LLM cliffhanger judgement is required; use lint_script_content_async.",
    )


async def check_cliffhanger_with_prompt(
    *,
    non_empty: list[tuple[int, str]],
    script_content: str,
    ai_manager: Any,
    model: str | None = None,
    prefer_provider: str | None = None,
) -> tuple[ScriptLintRuleResult, list[ScriptLintIssue]]:
    tail = [ln for _no, ln in non_empty[-3:]]
    last_line = tail[-1] if tail else ""
    if not ai_manager or not hasattr(ai_manager, "generate_text"):
        return _unavailable_result(non_empty, CLIFFHANGER_LLM_UNAVAILABLE)

    prompt = prompt_manager.render_prompt(
        CLIFFHANGER_PROMPT_TEMPLATE,
        {"script_content": script_content, "tail_lines": tail},
    )
    try:
        response = await ai_manager.generate_text(
            prompt=prompt,
            model=model,
            prefer_provider=prefer_provider,
            temperature=0.0,
            json_schema={
                "name": "script_cliffhanger_judgement",
                "schema": _CLIFFHANGER_SCHEMA,
            },
            system_prompt=prompt_manager.render_prompt(
                PromptTemplate.SYSTEM_PROMPT_JSON_STRICT.value, {}
            ),
            stream=False,
        )
    except Exception as exc:
        return _unavailable_result(non_empty, CLIFFHANGER_LLM_UNAVAILABLE, str(exc))

    if not getattr(response, "success", False):
        return _unavailable_result(
            non_empty,
            CLIFFHANGER_LLM_UNAVAILABLE,
            str(getattr(response, "error", "") or "LLM cliffhanger judgement failed"),
        )

    parsed = _parse_response_data(getattr(response, "data", None))
    if not parsed:
        return _unavailable_result(
            non_empty, CLIFFHANGER_LLM_UNAVAILABLE, "invalid_llm_response"
        )

    passed = bool(parsed.get("passed"))
    score = _coerce_score(parsed.get("score"), passed)
    details = {
        "detected": passed,
        "last_line": last_line[:80],
        "reason": str(parsed.get("reason") or ""),
        "evidence": str(parsed.get("evidence") or ""),
        "suggestion": str(parsed.get("suggestion") or ""),
        "provider": getattr(response, "provider", None),
        "model": getattr(response, "model", None),
    }
    issues: list[ScriptLintIssue] = []
    if not passed:
        issues.append(
            ScriptLintIssue(
                severity="error",
                rule_id="cliffhanger",
                message="Jie Wei not through LLM suspense/cliffhanger determine.",
                suggestion=details["suggestion"]
                or "Zui Hou Yi Ju/Zui Hou a action Ti Chu Xin Wen Ti or Bao Dian reveal, avoid Shou Shu.",
            )
        )
    return (
        ScriptLintRuleResult(
            rule_id="cliffhanger",
            title="suspense Jie Wei(LLM determine)",
            weight=1.5,
            score=score,
            passed=passed,
            details=details,
        ),
        issues,
    )


def _unavailable_result(
    non_empty: list[tuple[int, str]],
    error: str,
    message: str | None = None,
) -> tuple[ScriptLintRuleResult, list[ScriptLintIssue]]:
    tail = [ln for _no, ln in non_empty[-3:]]
    last_line = tail[-1] if tail else ""
    if _has_strong_local_cliffhanger(tail):
        return (
            ScriptLintRuleResult(
                rule_id="cliffhanger",
                title="suspense Jie Wei(LLM determine)",
                weight=1.5,
                score=0.85,
                passed=True,
                details={
                    "detected": True,
                    "last_line": last_line[:80],
                    "error": error,
                    "message": message or "",
                    "provider": "local_strong_cliffhanger_fallback",
                },
            ),
            [],
        )
    issue = ScriptLintIssue(
        severity="error",
        rule_id="cliffhanger",
        message="suspense Jie Wei need LLM determine, Dan current not allowed Yong.",
        suggestion="configuration available text model after retry run Zhi Jian or Sheng Cheng.",
    )
    return (
        ScriptLintRuleResult(
            rule_id="cliffhanger",
            title="suspense Jie Wei(LLM determine)",
            weight=1.5,
            score=0.0,
            passed=False,
            details={
                "detected": False,
                "last_line": last_line[:80],
                "error": error,
                "message": message or "",
            },
        ),
        [issue],
    )


def _has_strong_local_cliffhanger(tail: list[str]) -> bool:
    text = "".join(tail)
    if "countdown" not in text and "30 seconds" not in text:
        return False
    unresolved_markers = ("truth", "below a", "delete", "threat", "Kai Shi")
    if not any(marker in text for marker in unresolved_markers):
        return False
    return "？" in text or "?" in text or "text message" in text


def _parse_response_data(data: Any) -> dict[str, Any] | None:
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        parsed = extract_json_block(data)
        return parsed if isinstance(parsed, dict) else None
    return None


def _coerce_score(value: Any, passed: bool) -> float:
    if not passed:
        return 0.0
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 1.0
    return max(0.0, min(1.0, score))
