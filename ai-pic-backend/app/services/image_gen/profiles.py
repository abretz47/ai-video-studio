from __future__ import annotations

from dataclasses import dataclass, field

from .types import ImageGenMode


@dataclass(frozen=True, slots=True)
class ImageGenProfileDefaults:
    steps: int | None = None
    cfg_scale: float | None = None
    negative_prompt: str | None = None
    strength: float | None = None
    image_reference: str | None = None
    image_fidelity: float | None = None
    human_fidelity: float | None = None


@dataclass(frozen=True, slots=True)
class ImageGenProfile:
    id: str
    label: str
    description: str | None = None
    defaults: ImageGenProfileDefaults = field(default_factory=ImageGenProfileDefaults)


@dataclass(frozen=True, slots=True)
class ImageGenProfileSet:
    default_profile_id: str
    profiles: tuple[ImageGenProfile, ...]

    def resolve(self, profile_id: str | None) -> ImageGenProfile:
        wanted = (profile_id or "").strip()
        if wanted:
            for profile in self.profiles:
                if profile.id == wanted:
                    return profile
        for profile in self.profiles:
            if profile.id == self.default_profile_id:
                return profile
        return self.profiles[0]


DEFAULT_NEGATIVE_PROMPT = (
    "text, watermark, logo, subtitles, UI, collage, split-screen, multi-panel, blurry, lowres, "
    "low quality, jpeg artifacts, bad anatomy, deformed, extra limbs, extra fingers, mutated hands"
)


def _normalize_model_id(value: str) -> str:
    return (value or "").strip().lower().replace(".", "-")


def list_image_gen_profiles(
    *,
    provider: str | None,
    model_id: str | None,
    mode: ImageGenMode,
) -> ImageGenProfileSet | None:
    """Return available profiles for a provider+model (if supported)."""
    if not provider or not model_id:
        return None
    provider_key = provider.lower()
    normalized_model_id = _normalize_model_id(model_id)

    if provider_key == "jimeng":
        if mode == ImageGenMode.IMAGE_TO_IMAGE:
            return ImageGenProfileSet(
                default_profile_id="balanced",
                profiles=(
                    ImageGenProfile(
                        id="balanced",
                        label="Jun Heng",
                        description="Shi He Da Duo Shu scene default Zhi Liang Dang Wei",
                        defaults=ImageGenProfileDefaults(
                            strength=0.75,
                            steps=25,
                            cfg_scale=7.0,
                        ),
                    ),
                    ImageGenProfile(
                        id="quality",
                        label="Zhi Liang priority",
                        description="Geng Gao Bu Shu Yi Huo De Geng Wen Ding Xi Jie(Geng Man)",
                        defaults=ImageGenProfileDefaults(
                            strength=0.7,
                            steps=35,
                            cfg_scale=7.5,
                        ),
                    ),
                    ImageGenProfile(
                        id="fast",
                        label="Su Du priority",
                        description="Geng Di Bu Shu Yi Jia Kuai Sheng Cheng(Xi Jie Ke Neng Xia Jiang)",
                        defaults=ImageGenProfileDefaults(
                            strength=0.8,
                            steps=18,
                            cfg_scale=6.5,
                        ),
                    ),
                ),
            )

        return ImageGenProfileSet(
            default_profile_id="balanced",
            profiles=(
                ImageGenProfile(
                    id="balanced",
                    label="Jun Heng",
                    description="Shi He Da Duo Shu scene default Zhi Liang Dang Wei",
                    defaults=ImageGenProfileDefaults(
                        steps=30,
                        cfg_scale=7.0,
                        negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                    ),
                ),
                ImageGenProfile(
                    id="quality",
                    label="Zhi Liang priority",
                    description="Geng Gao Bu Shu Yi Huo De Geng Wen Ding Xi Jie(Geng Man)",
                    defaults=ImageGenProfileDefaults(
                        steps=40,
                        cfg_scale=7.5,
                        negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                    ),
                ),
                ImageGenProfile(
                    id="fast",
                    label="Su Du priority",
                    description="Geng Di Bu Shu Yi Jia Kuai Sheng Cheng(Xi Jie Ke Neng Xia Jiang)",
                    defaults=ImageGenProfileDefaults(
                        steps=20,
                        cfg_scale=6.5,
                        negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                    ),
                ),
            ),
        )

    if provider_key == "keling":
        if mode == ImageGenMode.IMAGE_TO_IMAGE:
            return ImageGenProfileSet(
                default_profile_id="balanced",
                profiles=(
                    ImageGenProfile(
                        id="balanced",
                        label="Jun Heng",
                        description="Shi Yong Kling default reference Qiang Du(Geng Shi He Da Duo Shu scene)",
                        defaults=ImageGenProfileDefaults(
                            image_fidelity=0.5,
                            human_fidelity=0.45,
                        ),
                    ),
                    ImageGenProfile(
                        id="identity",
                        label="Shen Fen priority",
                        description="Geng Qiang reference Qiang Du, Shi He Xu Ni IP Duo Ci Sheng Cheng Bao Chi Yi Zhi(Geng Bao Shou)",
                        defaults=ImageGenProfileDefaults(
                            image_fidelity=0.7,
                            human_fidelity=0.6,
                        ),
                    ),
                    ImageGenProfile(
                        id="creative",
                        label="Geng Zi You",
                        description="Geng Ruo reference Qiang Du, Yun Xu Geng multiple change(Geng Fa San)",
                        defaults=ImageGenProfileDefaults(
                            image_fidelity=0.35,
                            human_fidelity=0.35,
                        ),
                    ),
                ),
            )
        return ImageGenProfileSet(
            default_profile_id="balanced",
            profiles=(
                ImageGenProfile(
                    id="balanced",
                    label="Jun Heng",
                    description="default Fan Xiang prompt Ci(Qu Shui Yin/Wen Zi/Di Qing Xi Du Deng)",
                    defaults=ImageGenProfileDefaults(
                        negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                    ),
                ),
            ),
        )

    if provider_key == "volcengine":
        # Volcengine guidance_scale is supported by specific legacy Seedream/Seededit models.
        if (
            mode == ImageGenMode.TEXT_TO_IMAGE
            and "seedream-3-0" in normalized_model_id
            and "t2i" in normalized_model_id
        ):
            return ImageGenProfileSet(
                default_profile_id="balanced",
                profiles=(
                    ImageGenProfile(
                        id="balanced",
                        label="default",
                        description="Shi Yong Guan Fang default guidance_scale(Ying She to cfg_scale)",
                        defaults=ImageGenProfileDefaults(cfg_scale=2.5),
                    ),
                ),
            )
        if (
            mode == ImageGenMode.IMAGE_TO_IMAGE
            and "seededit-3-0" in normalized_model_id
            and "i2i" in normalized_model_id
        ):
            return ImageGenProfileSet(
                default_profile_id="balanced",
                profiles=(
                    ImageGenProfile(
                        id="balanced",
                        label="default",
                        description="Shi Yong Guan Fang default guidance_scale(Ying She to cfg_scale)",
                        defaults=ImageGenProfileDefaults(cfg_scale=5.5),
                    ),
                ),
            )
        return None

    return None


def resolve_image_gen_profile(
    *,
    provider: str | None,
    model_id: str | None,
    mode: ImageGenMode,
    requested_profile: str | None,
) -> ImageGenProfile | None:
    profiles = list_image_gen_profiles(provider=provider, model_id=model_id, mode=mode)
    if profiles is None:
        return None
    return profiles.resolve(requested_profile)
