import pytest

from app.services.story.story_outline_quality import validate_story_outline_quality


@pytest.mark.unit
def test_validate_story_outline_quality_uses_outline_fields() -> None:
 story = {
 "premise": "Nv Zhu Tui Men discover betrayal video Zheng Zai company Da Ping Bo Fang.",
 "synopsis": (
 "suddenly, heroine Zai Nian Hui Xian Chang discover Tou Pai video Bei public, crisis He conflict Li Ke Bao Fa."
 "Ta Ding Zhu Ya Li Fan Cha evidence, tense Dui Kang Bu Duan escalate, Zhong Duan reveal Jing Zheng Dui Shou Cai Shi real mastermind."
 "final climax Dui Jue Zhong truth Bao Guang, heroine complete counterattack Bing Shou Shu Jie Ju."
),
 "plot_structure": {
 "act1": "suddenly Bao Chu Xiu Ru video, heroine Bei Po Dang Chang counterattack.",
 "act2": "Wei Ji Sheng Ji, Shuang Fang Wei Rao evidence He Zhi Wei Zhan Kai tense Dui Kang.",
 "act3": "climax reveal truth, heroine Jie Jue crisis complete Ni Xi Jie Ju.",
 },
 "hook_plan": {
 "opening_hook": "suddenly, Nv Zhu Tui Men discover betrayal video Zheng Zai Bo Fang.",
 "escalation_plan": "conflict Mei Yi Chang Dou escalate.",
 "payoff_plan": "final truth reveal Bing complete counterattack.",
 "key_reversals": [
 {
 "beat_type": "hook",
 "description": "Tou Pai video public",
 "timing": "opening",
 "intensity": "high",
 }
 ],
 },
 "cliffhanger_plan": ["Dan Shi Ta discover Mu Hou mastermind Ling You Qi Ren"],
 }

 result = validate_story_outline_quality(story)

 assert result["story_quality_passed"] is True
 quality = result["story_quality_result"]
 assert quality["pacing_analysis"]["overall_score"] >= 0.6
 assert quality["hook_score"] >= 0.5


@pytest.mark.unit
def test_validate_story_outline_quality_fails_weak_story() -> None:
 story = {
 "premise": "Yi Ge general De Ri Chang Sheng Huo story.",
 "synopsis": "Da Jia calm Di Shang Ban, general Di Liao Tian, final Shi Qing Jie Shu.",
 "plot_structure": {
 "act1": "Pu Tong Kai Shi.",
 "act2": "Pu Tong Fa Zhan.",
 "act3": "Ping Jing Jie Shu.",
 },
 "hook_plan": {
 "opening_hook": "general De Yi Tian start Le.",
 "key_reversals": [],
 },
 }

 result = validate_story_outline_quality(story)

 assert result["story_quality_passed"] is False
 issue_types = {
 issue["issue_type"] for issue in result["story_quality_result"]["issues"]
 }
 assert "pacing_issue" in issue_types
 assert "weak_hook" in issue_types
