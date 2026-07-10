from __future__ import annotations

import pytest
from app.services.story_quality_gate import evaluate_story_quality_gate


def _strong_story() -> dict:
 return {
 "premise": "Lin Xue Zai company press conference suddenly discover Fu Qin Jiu An evidence Bei public, Bi Xu Dang Chang counterattack.",
 "synopsis": (
 "suddenly, Lin Xue Zai press conference Xian Chang discover Jiu An evidence Bei public, crisis He conflict Li Ke Bao Fa."
 "Ta Ding Zhu Ya Li Fan Cha evidence, tense Dui Kang Bu Duan escalate, Zhong Duan reveal Chen Mo Cai Shi real Cao Pan Zhe."
 "final climax Dui Jue Zhong truth Bao Guang, Lin Xue complete counterattack Bing Shou Shu Jie Duan target."
),
 "main_conflict": "Lin Xue Bi Xu Zai public Xiu Ru He Jiu An Xian Hai Zhong Zhao Chu truth.",
 "resolution": "Lin Xue Duo Hui key evidence, Bi Chen Mo Bao Lu Xia Yi Ceng mastermind.",
 "plot_structure": {
 "act1": "suddenly public Jiu An evidence, Lin Xue Bei Po Dang Chang counterattack.",
 "act2": "Wei Ji Sheng Ji, Lin Xue He Chen Mo Wei Rao ledger tense Dui Kang.",
 "act3": "climax reveal truth, Lin Xue Jie Jue crisis Bing complete Ni Xi.",
 },
 "hook_plan": {
 "opening_hook": "suddenly, press conference Da Ping Bo Fang Lin Xue Fu Qin Jiu An video.",
 "escalation_plan": "Mei San Ji Tui Jin Yi Ge evidence target.",
 "payoff_plan": "Lin Xue Yong recording counterattack Chen Mo.",
 },
 "cliffhanger_plan": ["ledger final Yi Ye Lu Chu Fu Qin signature"],
 "ad_snippets": [
 {
 "duration_seconds": 15,
 "hook": "Jiu An evidence public",
 "visual_summary": "Da Ping video He Lin Xue Wo Jin phone De Shou",
 "call_to_action": "Kan Ta Ru He counterattack",
 }
 ],
 }


def _ap_regression_story() -> dict:
 story = {
 "premise": (
 "Shang Ye Zi Xun company project Fu Ze RenAPreturn, Zai key Bing Gou Jin Diao Hui Yi Shang discover data Bei Cuan Gai, "
 "Ta Bi Xu Zai customer, team He Dui Shou De Jia Ji Xia, Yong phone recording He Tou Ping evidence Dang Chang counterattack, "
 "Duo Hui Xin Ren Bing Jie Lu betrayal."
),
 "synopsis": (
 "APreturn Zai conference room Zhu Chi Bing Gou Jin Diao Hui Bao, customer suddenly Zhi Yi data exception, Ta Fa Xian Zi Ji De Bao Gao Bei Ren Cuan Gai."
 "team Nei Bu someone betrayal, Jing Zheng Dui Shou An Zhong Shi Ya.APLeng Jing Ying Dui, Yong phone recording He Yuan Shi Shu Ju Tou Ping Jie Lu Cuan Gai Zhe, "
 "Dan Dai Jia Shi project suspend He Nei Bu Diao Cha.Ta Bi Xu Zai24Xiao Shi INT Zhao Dao real Mu Hou mastermind, Fou Ze Zhi Ye Sheng Ya Zhong Jie."
),
 "main_conflict": "APreturn Zao Yu data Cuan Gai, customer Zhi Yi He team betrayal, Bi Xu Yong professional evidence Zheng Ming Qing Bai.",
 "resolution": "APreturn pass Hui Yi recording, You Jian record He Tou Ping Dui Bi, Suo Ding Cuan Gai Zhe Bing Dang Zhong Jie Chuan, Xiang Mu Hui Fu, Ta Ying De customer He company Xin Ren, Bei Pan Zhe Bei Jie Zhi.",
 "plot_structure": {
 "act1": "opening10seconds: APreturn Da Kai Tou Ping, customer suddenly Pai Zhuo Zhi Yi data Zao Jia, Ta discover Bao Gao Bei Cuan Gai, Chong Tu Bao Fa.",
 "act2": "APreturn Yong phone recording He Yuan Shi Shu Ju Tou Ping, Zhu Tiao Dui Bi Jie Lu Cuan Gai Hen Ji, team Nei Bu Chu Xian Fen Lie, Jing Zheng Dui Shou Shi Ya.",
 "act3": "APHui Gui Zai24Xiao Shi INT Zhao Dao Mu Hou mastermind, Yong Hui Yi Ji Yao He time Chuo evidence Dang Zhong Jie Chuan, Xiang Mu Hui Fu, Ta Ying De customer Dao Qian He company Jia Jiang.",
 },
 "hook_plan": {
 "opening_hook": "APreturn Da Kai Tou Ping, customer suddenly Pai Zhuo: Zhe data Shi Jia De!Ta discover Bao Gao Bei Cuan Gai, Quan Chang Hua Ran.",
 "escalation_plan": "Mei20seconds Cha Ru Fan Zhuan: Tong Shi Fan Yao, Lu Yin Zheng Ju, new data Chu Xian, Dui Shou Shi Ya, Dong Shi Hui Jie Ru.",
 "payoff_plan": "Wei ShengAPreturn Yong Hui Yi Ji Yao time Chuo Jie Chuan Dui Shou, Dui Fang Ren Zui, Dan camera Ding Ge Zai Ta phone Shang new Shou Dao De Wei Xie Duan Xin.",
 },
 "cliffhanger_plan": ["phone new Shou Dao De Wei Xie Duan Xin display INT Gui Hai You Tong Huo"],
 "ad_snippets": [
 {
 "duration_seconds": 15,
 "hook": "customer Pai Zhuo Zhi Yi data Zao Jia",
 "visual_summary": "conference room Tou Ping, Shou Ji Lu Yin, APreturn Yan Shen close-up",
 "call_to_action": "Kan Ta Ru He Dang Chang counterattack",
 }
 ],
 "structured_story_contract": {
 "target_audience": "urban Zhi Chang short drama user",
 "core_emotional_pain": "professional Neng Li Bei public Zhi Yi, Xin Ren Bei team betrayal",
 "big_expectation": "APreturn Cha Qing data Cuan Gai truth Bing Duo Hui project Zhu Dao Quan",
 "small_expectation_ladder": ["Qian San Ji Na Dao Hui Yi recording", "Di Shi Ji Bi Chu Cuan Gai Zhe"],
 "protagonist_goal": "24Xiao Shi INT Zhao Chu Cuan Gai data De Ren",
 "structural_conflict": "APreturn Bi Xu Jie Zhi Yi Ta De team Zi Yuan Fan Cha team Nei Bu mastermind",
 "information_gap": "audience Zhi Dao recording exists, Dui Shou Bu Zhi Dao key camera Yi Bei Pai Xia",
 "first_three_episode_spine": "Shu Ju Zao Jia, Shou Ji Lu Yin, INT Gui Wei Xie Qian San Ji Li Zhu",
 "stage_highs": ["conference room counterattack", "Tou Ping Dui Bi", "Dong Shi Hui Fan Pan"],
 "shootability": "conference room, Zou Lang, Gong Wei, Ye Jing office Di Cheng Ben Ke Pai",
 "compliance_risks": [],
 "traffic_hooks": ["Ke Hu Pai Zhuo", "Shou Ji Lu Yin", "Tou Ping Fan Ji"],
 },
 }
 return story


@pytest.mark.unit
def test_story_gate_requires_structured_contract_in_production() -> None:
 gate = evaluate_story_quality_gate(
 story=_strong_story(),
 require_story_contract=True,
)

 assert gate["passed"] is False
 assert any(
 issue["id"] == "structured_story_contract_required"
 for issue in gate["blocking_issues"]
)


@pytest.mark.unit
def test_story_gate_accepts_structured_contract_when_required() -> None:
 story = _strong_story()
 story["structured_story_contract"] = {
 "target_audience": "Du Shi Fu Choufemaleuser",
 "core_emotional_pain": "Fu Qin Meng Yuan, Zun Yan Bei public Nian Ya",
 "big_expectation": "Lin Xue Cha Qing Jiu An Bing Duo Hui Jia Zu company",
 "small_expectation_ladder": [
 "Qian San Ji Na Dao press conference recording",
 "Di Shi Ji Bi Chen Mo Jiao Chu ledger",
 ],
 "protagonist_goal": "San Tian INT Na Dao ledger",
 "structural_conflict": "Lin Xue Bi Xu Jie Chen Mo De Zi Yuan Cha Chen Mo De Zui Zheng",
 "information_gap": "audience Zhi Dao ledger Zai Bao Xian Xiang, Lin Xue only Zhi Dao Chen Mo Sa Huang",
 "first_three_episode_spine": "identity, Jiu An, He Xin conflict Zai Qian San Ji Quan Bu Li Zhu",
 "stage_highs": ["press conference counterattack", "Zhang Ben Zheng Duo", "Dong Shi Hui Fan Pan"],
 "shootability": "office, Fa Bu Hui Ting, Zou Lang San Lei Di Cheng Ben scene",
 "compliance_risks": [],
 "traffic_hooks": ["Da Ping Jiu An video", "phone recording counterattack"],
 }

 gate = evaluate_story_quality_gate(
 story=story,
 require_story_contract=True,
)

 blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
 assert "structured_story_contract_required" not in blocking_ids


@pytest.mark.unit
def test_story_gate_accepts_ap_regression_commercial_outline() -> None:
 gate = evaluate_story_quality_gate(
 story=_ap_regression_story(),
 require_story_contract=True,
)

 assert gate["passed"] is True
