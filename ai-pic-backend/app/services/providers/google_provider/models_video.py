"""
Google Veo video model definitions.
"""

from __future__ import annotations

from typing import List

from ..base import AIModelType, ModelInfo


def get_video_models() -> List[ModelInfo]:
    """Return static fallback video models for Google Veo."""
    return [
        ModelInfo(
            model_id="veo-3.1-generate-preview",
            name="Veo 3.1 Generate (preview)",
            description="Google Veo 3.1 Yu Lan Ban video Sheng Cheng model, support Wen/Tu Sheng video and reference Tu",
            model_type=AIModelType.TEXT_TO_VIDEO,
            capabilities=[
                "text_to_video",
                "image_to_video",
                "reference_images",
                "first_last_frame",
                "720p",
                "1080p",
                "4s",
                "6s",
                "8s",
            ],
            metadata={
                "ui": {
                    "ratio_options": ["16:9", "9:16"],
                    "resolution_options": ["720P", "1080P"],
                    "duration_options": [4, 6, 8],
                    "duration_options_by_resolution": {
                        "720P": [4, 6, 8],
                        "1080P": [8],
                    },
                    "supports_end_frame": True,
                    "default_ratio": "16:9",
                    "default_resolution": "720P",
                }
            },
        ),
        ModelInfo(
            model_id="veo-3.1-fast-generate-preview",
            name="Veo 3.1 Fast (preview)",
            description="Google Veo 3.1 Yu Lan Ban quick model, support Wen/Tu Sheng video and reference Tu",
            model_type=AIModelType.TEXT_TO_VIDEO,
            capabilities=[
                "text_to_video",
                "image_to_video",
                "reference_images",
                "first_last_frame",
                "720p",
                "1080p",
                "4s",
                "6s",
                "8s",
            ],
            metadata={
                "ui": {
                    "ratio_options": ["16:9", "9:16"],
                    "resolution_options": ["720P", "1080P"],
                    "duration_options": [4, 6, 8],
                    "duration_options_by_resolution": {
                        "720P": [4, 6, 8],
                        "1080P": [8],
                    },
                    "supports_end_frame": True,
                    "default_ratio": "16:9",
                    "default_resolution": "720P",
                }
            },
        ),
        ModelInfo(
            model_id="veo-3.0-generate-001",
            name="Veo 3.0 Generate",
            description="Google Veo 3.0 Wen Ding Ban video Sheng Cheng model(8s)",
            model_type=AIModelType.TEXT_TO_VIDEO,
            capabilities=[
                "text_to_video",
                "image_to_video",
                "first_last_frame",
                "720p",
                "1080p",
                "8s",
            ],
            metadata={
                "ui": {
                    "ratio_options": ["16:9"],
                    "resolution_options": ["720P", "1080P"],
                    "duration_options": [8],
                    "supports_end_frame": True,
                    "default_ratio": "16:9",
                    "default_resolution": "720P",
                }
            },
        ),
        ModelInfo(
            model_id="veo-3.0-fast-generate-001",
            name="Veo 3.0 Fast",
            description="Google Veo 3.0 quick model(8s)",
            model_type=AIModelType.TEXT_TO_VIDEO,
            capabilities=[
                "text_to_video",
                "image_to_video",
                "first_last_frame",
                "720p",
                "1080p",
                "8s",
            ],
            metadata={
                "ui": {
                    "ratio_options": ["16:9"],
                    "resolution_options": ["720P", "1080P"],
                    "duration_options": [8],
                    "supports_end_frame": True,
                    "default_ratio": "16:9",
                    "default_resolution": "720P",
                }
            },
        ),
        ModelInfo(
            model_id="veo-2.0-generate-001",
            name="Veo 2.0 Generate",
            description="Google Veo 2.0 video Sheng Cheng model(720p)",
            model_type=AIModelType.TEXT_TO_VIDEO,
            capabilities=[
                "text_to_video",
                "image_to_video",
                "first_last_frame",
                "720p",
                "5s",
                "6s",
                "8s",
            ],
            metadata={
                "ui": {
                    "ratio_options": ["16:9"],
                    "resolution_options": ["720P"],
                    "duration_options": [5, 6, 8],
                    "supports_end_frame": True,
                    "default_ratio": "16:9",
                    "default_resolution": "720P",
                }
            },
        ),
    ]
