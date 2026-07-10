import re
from typing import Any, Dict, List


def extract_script_structure(content: str) -> Dict[str, Any]:
    """
 Cong Chun text script in Jin Li Chou Qu Jie Gou Hua Xin Xi(scene, Dui Hua, Wu Tai Zhi Shi).
 Zhe Shi Qi Fa Shi extract, not Yi LaiAI, Shi He Zuo WeiJSONfailed when fallback.
    """
    scenes: List[Dict[str, Any]] = []
    dialogues: List[Dict[str, Any]] = []
    stage_directions: List[Dict[str, Any]] = []

    lines = [ln.strip() for ln in content.splitlines()]

    # scene Shi Bie Gui Ze
    scene_patterns = [
        re.compile(
            r"^(scene|Scene)\s*([0-9０-９Yi Er San Si Wu Liu Qi Ba Jiu Shi]+)[::,.]?(.*)$", re.I
        ),
        re.compile(r"^(INT\.|EXT\.|INT/EXT\.)\s*(.+)$", re.I),
        re.compile(r"^(Nei Jing|Wai Jing)[::.,,]?\s*(.+)$"),
    ]

    # Dui Hua Shi Bie: for example "Xiaoya: ……", or "LI MING: …"
    dialogue_pattern = re.compile(
        r"^([\u4e00-\u9fa5A-Z][\u4e00-\u9fa5A-Z\s]{0,20})[：:]\s*(.+)$"
    )

    # Wu Tai Zhi Shi: Kuo Hao/Fang Kuo Hao/Yi"action:/narration:/sound effect:/Yin Yue: "Kai Tou
    stage_patterns = [
        re.compile(r"^[（(\[](.+)[)）\]]$"),
        re.compile(r"^(action|narration|sound effect|Yin Yue|environment|shot|Xiao Guo)[::]\s*(.+)$"),
    ]

    current_scene_idx = 0

    for ln in lines:
        if not ln:
            continue

        # 1) scene
        matched_scene = None
        for pat in scene_patterns:
            m = pat.match(ln)
            if m:
                matched_scene = m
                break
        if matched_scene:
            current_scene_idx += 1
            # extractlocation/timeJin Li Er Wei
            location = ""
            time_hint = ""
            if len(matched_scene.groups()) >= 1:
                tail = matched_scene.group(len(matched_scene.groups())) or ""
                # extract Chang Jian time Biao Ji
                if any(
                    t in tail
                    for t in [
                        "day",
                        "Daytime",
                        "Zao Shang",
                        "morning",
                        "Zhong Wu",
                        "afternoon",
                        "night",
                        "evening",
                        "dusk",
                        "twilight",
                    ]
                ):
                    time_hint = "night" if ("night" in tail or "evening" in tail) else "day"
                location = tail.strip()

            scenes.append(
                {
                    "scene_number": current_scene_idx,
                    "location": location,
                    "time": time_hint or None,
                    "description": ln,
                    "characters": [],
                    "props": [],
                    "notes": "",
                }
            )
            continue

        # 2) Dui Hua
        dm = dialogue_pattern.match(ln)
        if dm:
            character = dm.group(1).strip()
            text = dm.group(2).strip()
            dialogues.append(
                {
                    "scene_number": current_scene_idx or None,
                    "character": character,
                    "content": text,
                    "emotion": None,
                    "action": None,
                    "notes": None,
                }
            )
            continue

        # 3) Wu Tai Zhi Shi
        matched_stage = None
        stage_text = None
        for sp in stage_patterns:
            sm = sp.match(ln)
            if sm:
                matched_stage = sm
                stage_text = sm.group(len(sm.groups())) if sm.groups() else ln
                break
        if matched_stage:
            stage_directions.append(
                {
                    "scene_number": current_scene_idx or None,
                    "timing": None,
                    "content": stage_text.strip() if stage_text else ln,
                    "type": None,
                }
            )
            continue

    metadata = {
        "total_scenes": len(scenes),
        "total_dialogues": len(dialogues),
    }

    return {
        "content": content,
        "scenes": scenes,
        "dialogues": dialogues,
        "stage_directions": stage_directions,
        "metadata": metadata,
    }
