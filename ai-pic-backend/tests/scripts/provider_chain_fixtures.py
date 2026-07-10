import json
from types import SimpleNamespace


def provider_payload() -> dict:
    script = {
        "title": "bonus reset to zero",
        "logline": "robot discover bonus countdown reset to zero，final Yi Miao Fan Zhuan truth。",
        "characters": [
            {
                "name": "Xiaolan",
                "role": "protagonist",
                "appearance_prompt": "Lan Se Ka Tong robot，Cheng Se Wei Jin",
                "consistency_anchor": "blue cartoon robot, orange scarf, LED eyes",
            }
        ],
        "scenes": [
            _scene_one(),
            _scene_two(),
        ],
    }
    return {
        "ok": True,
        "request_chain": [
            {"label": "deepseek-script", "duration_seconds": 1.0},
            {"label": "timeline-create", "duration_seconds": 0.1},
            {"label": "timeline-shot-plan", "duration_seconds": 1.0},
            {"label": "openai-character-image", "duration_seconds": 2.0},
            {"label": "seedance-video-1", "duration_seconds": 10.0},
            {"label": "seedance-video-2", "duration_seconds": 10.0},
            {"label": "timeline-assets-update", "duration_seconds": 0.1},
            {"label": "timeline-render-queue", "duration_seconds": 0.1},
        ],
        "key_artifacts": {
            "script": {"raw_content": json.dumps(script, ensure_ascii=False)},
            "image": {"oss_url": "https://example.com/robot.png"},
            "timeline_seed": {"id": 23, "version": 1},
            "timeline_shot_plan": {"id": 23, "seed_version": 1, "version": 2},
            "timeline": {"id": 23, "version": 3},
            "render_job": {
                "output_url": "https://example.com/render.mp4",
                "status": "succeeded",
            },
            "render_media_probe": {
                "ok": True,
                "expected_duration_seconds": 30,
                "format_duration_seconds": 30.1,
                "video_duration_seconds": 30.1,
                "audio_duration_seconds": 30.0,
                "checks": {
                    "has_video_stream": True,
                    "has_audio_stream": True,
                    "format_duration_matches_timeline": True,
                    "video_duration_matches_timeline": True,
                    "audio_duration_matches_timeline": True,
                    "scene_frames_extracted": True,
                },
            },
            "videos": [
                _video("video_s1_provider_chain_1_001", 1),
                _video("video_s2_provider_chain_2_002", 2),
            ],
        },
    }


def passing_script_score() -> dict:
    return {
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "verdict": "pass",
        "overall_score": 4.2,
        "dimension_scores": {
            "conflict_intensity": 4.0,
            "character_recognizability": 4.2,
            "cultural_fit": 4.1,
            "clip_ability": 4.0,
            "logic_coherence": 4.3,
        },
    }


class CliffhangerManager:
    async def generate_text(self, **kwargs):
        return SimpleNamespace(
            success=True,
            provider="deepseek",
            model=kwargs.get("model") or "deepseek-v4-flash",
            data={
                "passed": True,
                "score": 1.0,
                "reason": "Jie Wei continue Pao issue",
                "evidence": "final Yi Ju Liu Xia Zheng Ju Yi Wen",
                "suggestion": "",
            },
        )


def sample(
    sample_id: str,
    attempt: int,
    *,
    passed: bool,
    hard_failures: list[str] | None = None,
    failure_categories: list[str] | None = None,
) -> dict:
    return {
        "sample_id": sample_id,
        "attempt": attempt,
        "passed": passed,
        "hard_failures": hard_failures or [],
        "failure_categories": failure_categories or [],
        "script_lint": {"overall_score": 9.2},
        "structured_script_score": {"average": 3.8},
    }


def _scene_one() -> dict:
    return {
        "scene_id": "s1",
        "duration_seconds": 15,
        "question": "who Xiao Lan bonus countdown reset to zero？",
        "stakes": "15seconds INT Zhao Bu Dao Bian Hao，bonus Yong Jiu reset to zero。",
        "opposition": "Shi Jian Zhou system Ju Jue Xiaolan permission。",
        "turn": "permission Ju Jue after，Ri Zhi Fan Xiang Tiao Chu Cao Zuo Zhe Bian Hao。",
        "plot": "Xiaolan discover bonus be reset to zero，Jing Bao Xiang Qi。",
        "dialogue": [{"speaker": "Xiaolan", "line": "who Qing Kong bonus"}],
        "beats": [
            _beat(
                1,
                "hook",
                "Pao Chu exception",
                "bonus reset to zero Jing Bao Liang Qi",
                "Shi Jian Zhou who Gai",
                "Xiaolan Chong Xiang Kong Zhi Tai",
                duration_seconds=3,
            ),
            _beat(
                2,
                "conflict",
                "Zeng Jia Zu Li",
                "permission be system Ju Jue",
                "permission Mei",
                "Kong Zhi Tai Dan Chu Ju Jue prompt",
                duration_seconds=6,
            ),
            _beat(
                3,
                "reveal",
                "Fang Da Mi Tuan",
                "Ri Zhi Chu Xian Dao Tui Yi Miao",
                "time in Dao Tui",
                "countdown Fan Xiang Shan Shuo",
                duration_seconds=6,
            ),
        ],
        "image_prompt": "cartoon robot in studio",
        "video_prompt": "blue robot sees countdown alarm",
    }


def _scene_two() -> dict:
    return {
        "scene_id": "s2",
        "duration_seconds": 15,
        "question": "Xiao Lan Neng Bu Neng in Ri Zhi delete before Na Dao Zheng Ju？",
        "stakes": "Ri Zhi delete before Na Bu Dao Zheng Ju，client Yan Shou Hui failed。",
        "opposition": "Hei Ying in Hou Tai delete final Ri Zhi。",
        "turn": "bonus record Hui Fu Yi Ban after，Hei Ying delete final Ri Zhi。",
        "plot": "Xiaolan discover truth，final Yi Miao Fan Zhuan。",
        "dialogue": [{"speaker": "Xiaolan", "line": "Zheng Ju Zhi Xiang Hei Ying"}],
        "beats": [
            _beat(
                1,
                "conflict",
                "continue Zhui Cha truth",
                "Yin Cang Wen Jian Jia Zi Dong Da Kai",
                "Zheng Ju in Zhe Li",
                "Xiaolan Zhua Zhu Shan Shuo file",
            ),
            {
                **_beat(
                    2,
                    "payoff",
                    "Zheng Ming protagonist Zhao Dao key Zheng Ju",
                    "bonus record Hui Fu Yi Ban",
                    "Zhao Dao",
                    "screen Hui Fu bonus record",
                ),
                "payoff_tag": "proof_found",
            },
            {
                **_beat(
                    3,
                    "cliffhanger",
                    "Liu Xia Xin Cao Zuo Zhe Wei Xie",
                    "Hei Ying delete final Ri Zhi",
                    "who Hai Zai Xian",
                    "Ri Zhi Mo Xing Xiao Shi",
                ),
                "cliffhanger_tag": "hidden_operator",
            },
        ],
        "image_prompt": "cartoon robot finds proof",
        "video_prompt": "blue robot reveals proof",
    }


def _beat(
    order: int,
    beat_type: str,
    purpose: str,
    event: str,
    line: str,
    action: str,
    *,
    duration_seconds: int = 5,
) -> dict:
    return {
        "order_index": order,
        "beat_type": beat_type,
        "dramatic_purpose": purpose,
        "visible_event": event,
        "dialogue": [{"speaker": "Xiaolan", "line": line}],
        "action": [action],
        "duration_seconds": duration_seconds,
    }


def _video(clip_id: str, ordinal: int) -> dict:
    return {
        "ordinal": ordinal,
        "clip_id": clip_id,
        "duration_seconds": 15,
        "video_url": f"https://example.com/video-{ordinal}.mp4",
        "image_url": "https://example.com/robot.png",
        "provider": "volcengine",
        "model": "doubao-seedance-2-0-260128",
        "task_id": f"task-{ordinal}",
        "timeline_shot_plan": {
            "character_anchor": "blue cartoon robot, orange scarf, LED eyes",
            "dialogue_source": "Xiaolan: Zheng Ju in Zhe Li",
            "video_prompt": "blue robot acts with clear story beat",
        },
    }
