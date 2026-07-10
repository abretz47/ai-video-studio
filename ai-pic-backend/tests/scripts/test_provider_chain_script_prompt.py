import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "ai-pic-backend"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(BACKEND_ROOT))

from tests.scripts.provider_chain_fixtures import provider_payload # noqa: E402

from scripts.harness.production_quality_script import (# noqa: E402
 provider_chain_script_text,
)
from scripts.harness.provider_chain_payloads import build_script_prompt # noqa: E402


def test_build_script_prompt_accepts_optional_premise() -> None:
 prompt = build_script_prompt("full-30s", "Jiang Jin Qing Ling, robot Bi Xu Zhao Chu truth")

 assert "Jiang Jin Qing Ling" in prompt
 assert "Create exactly 2 scene" in prompt
 assert "<= 15 visible" in prompt
 assert "one stable protagonist" in prompt
 assert "visible action" in prompt
 assert "specific story turn" in prompt
 assert "Do not use generic speaker names" in prompt
 assert "Scene-level dialogue must not copy any beat dialogue" in prompt
 assert "data already lost" in prompt


def test_build_script_prompt_aligns_with_script_score_pass_rubric() -> None:
 prompt = build_script_prompt("full-30s", "Jian Ji Shi discover customer Yan Shou file Bei Gai")

 assert "ScriptScore pass" in prompt
 assert "character_recognizability" in prompt
 assert "logic_coherence" in prompt
 assert "clip_ability" in prompt
 assert "Jue Se Biao Qian" in prompt
 assert "because/therefore" in prompt
 assert "seed every hidden code, password, account, or backdoor" in prompt
 assert "visual shock + subtitle-friendly dialogue" in prompt
 assert "opposition must literally include" in prompt
 assert "causal_seed" in prompt
 assert "owner, access rule, limitation, and motive" in prompt


def test_build_script_prompt_includes_repair_notes_for_retry() -> None:
 prompt = build_script_prompt(
 "full-30s",
 "Jian Ji Shi discover customer Yan Shou file Bei Gai",
 repair_notes=[
 "character Bian Shi Du Bu Zu: Protagonist Que Shao fixed Kou Tou Chan",
 "logic Yi Zhi Xing You Lou Dong: Yin Cang Mi Ma Que Shao Qian Zhi Pu Dian",
 ],
)

 assert "Rewrite the previous failed script" in prompt
 assert "character Bian Shi Du Bu Zu" in prompt
 assert "Yin Cang Mi Ma Que Shao Qian Zhi Pu Dian" in prompt
 assert "Do not repeat the same plot structure" in prompt


def test_build_script_prompt_blocks_unseeded_backdoor_solutions() -> None:
 prompt = build_script_prompt("full-30s", "Jian Ji Shi discover customer Yan Shou file Bei Gai")

 assert "different color/material/silhouette" in prompt
 assert "their motive must be visible" in prompt
 assert (
 "Do not use hidden code, password, account, or backdoor as the solution"
 in prompt
)
 assert "who created it, why it exists, and what limitation it has" in prompt
 assert "secondary character cannot simply reveal the answer" in prompt
 assert "non-screen physical action" in prompt
 assert "opposition motive must be planted before confrontation" in prompt
 assert "do not make an antagonist confess" in prompt
 assert "do not put Shan Chu Wan Cheng" in prompt
 assert "unknown operator must be seeded in scene 1" in prompt
 assert "permission or account action must name the access rule" in prompt


def test_provider_chain_script_text_preserves_scene_conflict_metadata() -> None:
 text = provider_chain_script_text(provider_payload())

 assert "【conflict】issue: Shui Ba Xiao Lan De bonus countdown reset to zero?" in text
 assert "Dai Jia: 15seconds INT Zhao Bu Dao Bian Hao, bonus Yong Jiu reset to zero." in text
 assert "Zu Li: Shi Jian Zhou system Ju Jue Xiaolan permission." in text
 assert "Zhuan Zhe: permission Ju Jue Hou, Ri Zhi Fan Xiang Tiao Chu Cao Zuo Zhe Bian Hao." in text


def test_provider_chain_script_text_preserves_all_character_roles() -> None:
 payload = provider_payload()
 script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
 script["characters"].append(
 {
 "name": "Hong Dun",
 "role": "calm Shen He Yuan Yao Wei Hu permission Gui Ze",
 "appearance_prompt": "red Fang Xing robot, Lv Se Sao Miao Yan",
 "consistency_anchor": "red square robot, green scanner eye",
 }
)
 payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
 script, ensure_ascii=False
)

 text = provider_chain_script_text(payload)

 assert "▲Jue Se Biao Qian: Xiaolan｜Protagonist｜Lan Se Ka Tong robot, Cheng Se Wei Jin" in text
 assert "▲Jue Se Biao Qian: Hong Dun｜calm Shen He Yuan Yao Wei Hu permission Gui Ze" in text
 assert "red square robot, green scanner eye" in text


def test_provider_chain_script_text_preserves_causal_seed_metadata() -> None:
 payload = provider_payload()
 script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
 script["scenes"][0]["causal_seed"] = "Shen Ji Ling Pai Lai Zi Hong Dun, Zhi Du permission Xian Zhi Xie Ru."
 payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
 script, ensure_ascii=False
)

 text = provider_chain_script_text(payload)

 assert "Yin Guo Zhong Zi: Shen Ji Ling Pai Lai Zi Hong Dun, Zhi Du permission Xian Zhi Xie Ru." in text
