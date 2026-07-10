"""
Keling provider model definitions.

Contains ModelInfo instances for video and image generation models.
"""

from __future__ import annotations

from typing import List

from ..base import AIModelType, ModelInfo


def get_available_models() -> List[ModelInfo]:
    """Return the list of available Keling models."""
    return [
        # V2 Series Models - Latest generation
        ModelInfo(
            model_id="kling-v2-6",
            name="Kling V2.6",
            description="Zui XinV2.6version, support Sheng Yin Kong Zhi, 1080pGao Qing output",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=[
                "image_to_video",
                "sound_control",
                "1080p",
                "30fps",
                "professional_mode",
            ],
            metadata={
                "ui": {
                    "resolution_options": ["1080P", "720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "1080P",
                    "default_ratio": "16:9",
                    "supports_camera_control": True,
                    "supports_watermark": False,
                    "camera_control_hint": "An Ke Ling image2video camera_control JSON Chuan Can, for example Gui Ji/Su Du.",
                }
            },
        ),
        ModelInfo(
            model_id="kling-v2-5-turbo",
            name="Kling V2.5 Turbo",
            description="V2.5quick version, Sheng Cheng Su Du Geng Kuai",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=["image_to_video", "fast_generation", "1080p", "30fps"],
            metadata={
                "ui": {
                    "resolution_options": ["1080P", "720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "1080P",
                    "default_ratio": "16:9",
                    "supports_camera_control": True,
                    "supports_watermark": False,
                    "camera_control_hint": "An Ke Ling image2video camera_control JSON Chuan Can, for example Gui Ji/Su Du.",
                }
            },
        ),
        ModelInfo(
            model_id="kling-v2-1-master",
            name="Kling V2.1 Master",
            description="V2.1Zhuan Ye Ban, support Geng multiple Gao Ji Te Xing",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=[
                "image_to_video",
                "master_quality",
                "1080p",
                "30fps",
                "advanced_controls",
            ],
            metadata={
                "ui": {
                    "resolution_options": ["1080P", "720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "1080P",
                    "default_ratio": "16:9",
                    "supports_camera_control": True,
                    "supports_watermark": False,
                    "camera_control_hint": "An Ke Ling image2video camera_control JSON Chuan Can, for example Gui Ji/Su Du.",
                }
            },
        ),
        ModelInfo(
            model_id="kling-v2-1",
            name="Kling V2.1",
            description="V2.1Biao Zhun Ban, Ping Heng Zhi Liang and Su Du",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=["image_to_video", "1080p", "30fps"],
            metadata={
                "ui": {
                    "resolution_options": ["1080P", "720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "1080P",
                    "default_ratio": "16:9",
                    "supports_camera_control": True,
                    "supports_watermark": False,
                    "camera_control_hint": "An Ke Ling image2video camera_control JSON Chuan Can, for example Gui Ji/Su Du.",
                }
            },
        ),
        # V1 Series Models - Legacy but still supported
        ModelInfo(
            model_id="kling-v1-6",
            name="Kling V1.6",
            description="V1.6version, support Duo Tu Sheng Cheng video",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=["image_to_video", "multi_image", "720p", "24fps"],
            metadata={
                "ui": {
                    "resolution_options": ["720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "720P",
                    "default_ratio": "16:9",
                    "supports_camera_control": False,
                    "supports_watermark": False,
                }
            },
        ),
        ModelInfo(
            model_id="kling-v1-5",
            name="Kling V1.5",
            description="V1.5version, Wen Ding Ke Kao",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=["image_to_video", "720p", "24fps"],
            metadata={
                "ui": {
                    "resolution_options": ["720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "720P",
                    "default_ratio": "16:9",
                    "supports_camera_control": False,
                    "supports_watermark": False,
                }
            },
        ),
        ModelInfo(
            model_id="kling-v1",
            name="Kling V1",
            description="V1basic version",
            model_type=AIModelType.IMAGE_TO_VIDEO,
            supported_formats=["mp4"],
            capabilities=["image_to_video", "720p", "24fps"],
            metadata={
                "ui": {
                    "resolution_options": ["720P"],
                    "duration_options": [5, 10],
                    "supports_end_frame": True,
                    "supports_camera_fixed": False,
                    "ratio_options": ["16:9", "9:16", "1:1", "4:3"],
                    "default_resolution": "720P",
                    "default_ratio": "16:9",
                    "supports_camera_control": False,
                    "supports_watermark": False,
                }
            },
        ),
        # Image Generation Models
        ModelInfo(
            model_id="kling-v2",
            name="Kling image Sheng Cheng V2",
            description="Kling image Sheng Cheng model(kling-v2), support Wen Sheng Tu and Tu Sheng Tu reference",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=["text_to_image", "image_to_image", "2k_resolution"],
            metadata={
                "ui": {
                    "size_options": ["2k", "1k"],
                    "aspect_ratio_options": [
                        "1:1",
                        "16:9",
                        "9:16",
                        "4:3",
                        "3:4",
                        "3:2",
                        "2:3",
                        "21:9",
                    ],
                    "supports_aspect_ratio": True,
                    "supports_reference_image": True,
                }
            },
        ),
        ModelInfo(
            model_id="kling-v2-1",
            name="Kling image Sheng Cheng V2.1",
            description="Kling image Sheng Cheng model(kling-v2-1), support 2K High qualityWen Sheng Tu output",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=["text_to_image", "2k_resolution"],
            metadata={
                "ui": {
                    "size_options": ["2k", "1k"],
                    "aspect_ratio_options": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "supports_aspect_ratio": True,
                    "supports_reference_image": False,
                }
            },
        ),
        ModelInfo(
            model_id="kling-v1",
            name="Kling image Sheng Cheng V1",
            description="Kling image Sheng Cheng model(kling-v1), support 1K output and Tu Sheng Tu reference",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=["text_to_image", "image_to_image", "1k_resolution"],
            metadata={
                "ui": {
                    "size_options": ["1k"],
                    "aspect_ratio_options": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "supports_aspect_ratio": True,
                    "supports_reference_image": True,
                }
            },
        ),
    ]
