from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ScriptLintOptions(BaseModel):
    """script Zhi Jian Xuan Xiang(can Yong Yu Jiao Ben lint/Ping Fen Ren Wu)."""

    max_dialogue_chars: int = Field(
        15, ge=1, le=100, description="Dan Ju line maximum Zi Fu Shu(not Han Kong Ge/Biao Dian)"
    )
    pass_threshold: float = Field(9.0, ge=0.0, le=10.0, description="He Ge Yu Zhi(0-10)")
    target_word_min: int | None = Field(
        None, ge=1, description="target word count Xia Xian(Gu Suan; Zhong Wen An Zi Ji)"
    )
    target_word_max: int | None = Field(
        None, ge=1, description="target word count Shang Xian(Gu Suan; Zhong Wen An Zi Ji)"
    )


class ScriptLintIssue(BaseModel):
    severity: Literal["error", "warn", "info"] = Field(..., description="Wen Ti Yan Zhong Ji Bie")
    rule_id: str = Field(..., description="Gui Ze ID")
    message: str = Field(..., description="Wen Ti description")
    line: int | None = Field(None, description="Hang Hao(Cong 1 Kai Shi)")
    excerpt: str | None = Field(None, description="Chu Fa Pian Duan(can Xuan)")
    suggestion: str | None = Field(None, description="Xiu Fu suggestion(can Xuan)")


class ScriptLintRuleResult(BaseModel):
    rule_id: str = Field(..., description="Gui Ze ID")
    title: str = Field(..., description="Gui Ze name")
    weight: float = Field(..., ge=0.0, description="Quan Zhong")
    score: float = Field(..., ge=0.0, le=1.0, description="Gui Ze De Fen(0-1)")
    passed: bool = Field(..., description="Gui Ze Shi Fou through")
    details: dict[str, Any] | None = Field(None, description="Gui Ze Xi Jie(can Xuan)")


class ScriptLintMetrics(BaseModel):
    non_empty_lines: int = Field(..., ge=0, description="Fei Kong Xing Shu")
    dialogue_lines: int = Field(..., ge=0, description="dialogue Xing Shu")
    stage_lines: int = Field(..., ge=0, description="Wu Tai Zhi Shi/sound effect Xing Shu")
    estimated_words: int = Field(..., ge=0, description="Gu Suan word count(Zhong Wen An Zi Ji)")
    estimated_dialogue_chars: int = Field(
        ..., ge=0, description="dialogue Gu Suan word count(Zhong Wen An Zi Ji)"
    )


class ScriptLintResult(BaseModel):
    options: ScriptLintOptions = Field(..., description="Ben Ci Zhi Jian Shi Yong Xuan Xiang")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Zong He Ping Fen(0-10)")
    passed: bool = Field(..., description="Shi Fou through(overall_score >= pass_threshold)")
    rules: list[ScriptLintRuleResult] = Field(
        ..., description="Gui Ze Ming Xi(can Biao Ge Hua Zhan Shi)"
    )
    issues: list[ScriptLintIssue] = Field(..., description="Wen Ti list(Han Ding Wei and suggestion)")
    metrics: ScriptLintMetrics = Field(..., description="Tong Ji Zhi Biao")
    unimplemented_checks: list[str] = Field(
        default_factory=list, description="Shang Wei Zi Dong Jian Ce Gui Ze(need Ren Gong or LLM Shen He)"
    )
