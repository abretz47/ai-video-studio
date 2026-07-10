from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImageGenProfileDefaultsResponse(BaseModel):
    steps: int | None = Field(None, description="sampling Bu Shu(can Xuan)")
    cfg_scale: float | None = Field(None, description="CFG scale(can Xuan)")
    negative_prompt: str | None = Field(None, description="Fan Xiang prompt Ci(can Xuan)")
    strength: float | None = Field(None, description="Tu Sheng Tu Qiang Du(can Xuan)")
    image_reference: str | None = Field(None, description="Tu Sheng Tu image reference type(can Xuan)")
    image_fidelity: float | None = Field(
        None, description="Tu Sheng Tu reference Qiang Du(can Xuan, 0~1)"
    )
    human_fidelity: float | None = Field(
        None, description="Tu Sheng Tu Mian Bu reference Qiang Du(can Xuan, 0~1)"
    )


class ImageGenProfileResponse(BaseModel):
    id: str = Field(..., description="profile Biao Shi(Yong Yu generation_profile)")
    label: str = Field(..., description="Xian Shi name")
    description: str | None = Field(None, description="note")
    defaults: ImageGenProfileDefaultsResponse = Field(..., description="default parameters")


class ImageGenProfilesResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    provider: str | None = Field(None, description="Tui Duan Chu provider(if available)")
    model_id: str | None = Field(
        None, description="Qu Diao provider Qian Zhui after model_id(if available)"
    )
    mode: Literal["text_to_image", "image_to_image"] = Field(
        ..., description="Sheng Cheng mode"
    )
    default_profile_id: str | None = Field(
        None, description="default profile id(profiles as Kong Shi as null)"
    )
    profiles: list[ImageGenProfileResponse] = Field(default_factory=list)
