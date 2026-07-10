from __future__ import annotations

import pytest
from app.services.story_quality_gate import evaluate_story_quality_gate


def _strong_story() -> dict:
    return {
        "premise": "Lin Xue in company press conference Tu Ran discover Fu Qin Jiu An Zheng Ju be public，Bi Xu Dang Chang counterattack。",
        "synopsis": (
            "Tu Ran，Lin Xue in press conference Xian Chang discover Jiu An Zheng Ju be public，crisis and conflict Li Ke Bao Fa。"
            "Ta Ding Zhu Ya Li Fan Cha Zheng Ju，tense Dui Kang Bu Duan escalate，Zhong Duan reveal Chen Mo Cai is real Cao Pan Zhe。"
            "Zui Zhong climax Dui Jue in truth Bao Guang，Lin Xue complete counterattack and Shou Shu Jie Duan target。"
        ),
        "main_conflict": "Lin Xue Bi Xu in public Xiu Ru and Jiu An Xian Hai in Zhao Chu truth。",
        "resolution": "Lin Xue Duo Hui key Zheng Ju，Bi Chen Mo Bao Lu Xia Yi Ceng mastermind。",
        "plot_structure": {
            "act1": "Tu Ran public Jiu An Zheng Ju，Lin Xue Bei Po Dang Chang counterattack。",
            "act2": "crisis escalate，Lin Xue and Chen Mo Wei Rao ledger tense Dui Kang。",
            "act3": "climax reveal truth，Lin Xue Jie Jue crisis and complete Ni Xi。",
        },
        "hook_plan": {
            "opening_hook": "Tu Ran，press conference Da Ping Bo Fang Lin Xue Fu Qin Jiu An video。",
            "escalation_plan": "Mei San Ji Tui Jin Yi Ge Zheng Ju target。",
            "payoff_plan": "Lin Xue Yong recording counterattack Chen Mo。",
        },
        "cliffhanger_plan": ["ledger final Yi Ye Lu Chu Fu Qin signature"],
        "ad_snippets": [
            {
                "duration_seconds": 15,
                "hook": "Jiu An Zheng Ju public",
                "visual_summary": "Da Ping video and Lin Xue Wo Jin phone Shou",
                "call_to_action": "Kan Ta Ru He counterattack",
            }
        ],
    }


def _ap_regression_story() -> dict:
    story = {
        "premise": (
            "Shang Ye Zi Xun company project Fu Ze RenAPreturn，in key Bing Gou Jin Diao Hui Yi on discover data be Cuan Gai，"
            "Ta Bi Xu in client、team and Dui Shou Jia Ji Xia，Yong phone recording and Tou Ping Zheng Ju Dang Chang counterattack，"
            "Duo Hui Xin Ren and Jie Lu betrayal。"
        ),
        "synopsis": (
            "APreturn in conference room Zhu Chi Bing Gou Jin Diao Hui Bao，client Tu Ran Zhi Yi data exception，Ta Fa Xian Zi Ji Bao Gao be Ren Cuan Gai。"
            "team Nei Bu someone betrayal，Jing Zheng Dui Shou An Zhong Shi Ya。APcalm Ying Dui，Yong phone recording and Yuan Shi Shu Ju Tou Ping Jie Lu Cuan Gai Zhe，"
            "Dan Dai Jia is project suspend and Nei Bu Diao Cha。Ta Bi Xu in24Xiao Shi INT Zhao Dao real Mu Hou mastermind，Fou Ze Zhi Ye Sheng Ya Zhong Jie。"
        ),
        "main_conflict": "APreturn Zao Yu data Cuan Gai、client Zhi Yi and team betrayal，Bi Xu Yong professional Zheng Ju Zheng Ming Qing Bai。",
        "resolution": "APreturn pass Hui Yi recording、You Jian record and Tou Ping Dui Bi，Suo Ding Cuan Gai Zhe and Dang Zhong Jie Chuan，project Hui Fu，Ta Ying De client and company Xin Ren，Bei Pan Zhe be Jie Zhi。",
        "plot_structure": {
            "act1": "opening10seconds：APreturn Da Kai Tou Ping，client Tu Ran Pai Zhuo Zhi Yi data Zao Jia，Ta discover Bao Gao be Cuan Gai，conflict Bao Fa。",
            "act2": "APreturn Yong phone recording and Yuan Shi Shu Ju Tou Ping，Zhu Tiao Dui Bi Jie Lu Cuan Gai Hen Ji，team Nei Bu Chu Xian Fen Lie，Jing Zheng Dui Shou Shi Ya。",
            "act3": "APreturn in24Xiao Shi INT Zhao Dao Mu Hou mastermind，Yong Hui Yi Ji Yao and time Chuo Zheng Ju Dang Zhong Jie Chuan，project Hui Fu，Ta Ying De client Dao Qian and company Jia Jiang。",
        },
        "hook_plan": {
            "opening_hook": "APreturn Da Kai Tou Ping，client Tu Ran Pai Zhuo：this data is Jia！Ta discover Bao Gao be Cuan Gai，Quan Chang Hua Ran。",
            "escalation_plan": "Mei20seconds Cha Ru Fan Zhuan：Tong Shi Fan Yao、recording Zheng Ju、Xin data Chu Xian、Dui Shou Shi Ya、Dong Shi Hui Jie Ru。",
            "payoff_plan": "Wei ShengAPreturn Yong Hui Yi Ji Yao time Chuo Jie Chuan Dui Shou，Dui Fang Ren Zui，Dan camera Ding Ge in Ta phone on Xin Shou Dao Wei Xie Duan Xin。",
        },
        "cliffhanger_plan": ["phone Xin Shou Dao Wei Xie Duan Xin display INT Gui Hai You Tong Huo"],
        "ad_snippets": [
            {
                "duration_seconds": 15,
                "hook": "client Pai Zhuo Zhi Yi data Zao Jia",
                "visual_summary": "conference room Tou Ping、phone recording、APreturn Yan Shen close-up",
                "call_to_action": "Kan Ta Ru He Dang Chang counterattack",
            }
        ],
        "structured_story_contract": {
            "target_audience": "urban workplace short drama user",
            "core_emotional_pain": "professional Neng Li be public Zhi Yi，Xin Ren be team betrayal",
            "big_expectation": "APreturn Cha Qing data Cuan Gai truth and Duo Hui project Zhu Dao Quan",
            "small_expectation_ladder": ["before San Ji Na Dao Hui Yi recording", "Di Shi Ji Bi Chu Cuan Gai Zhe"],
            "protagonist_goal": "24Xiao Shi INT Zhao Chu Cuan Gai data Ren",
            "structural_conflict": "APreturn Bi Xu Jie Zhi Yi Ta team Zi Yuan Fan Cha team Nei Bu mastermind",
            "information_gap": "audience Zhi Dao recording exists，Dui Shou not Zhi Dao key camera already be Pai Xia",
            "first_three_episode_spine": "data Zao Jia、phone recording、INT Gui Wei Xie before San Ji Li Zhu",
            "stage_highs": ["conference room counterattack", "Tou Ping Dui Bi", "Dong Shi Hui Fan Pan"],
            "shootability": "conference room、Zou Lang、Gong Wei、Ye Jing office Di Cheng Ben Ke Pai",
            "compliance_risks": [],
            "traffic_hooks": ["client Pai Zhuo", "phone recording", "Tou Ping counterattack"],
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
        "target_audience": "urban Fu Choufemaleuser",
        "core_emotional_pain": "Fu Qin Meng Yuan、Zun Yan be public Nian Ya",
        "big_expectation": "Lin Xue Cha Qing Jiu An and Duo Hui Jia Zu company",
        "small_expectation_ladder": [
            "before San Ji Na Dao press conference recording",
            "Di Shi Ji Bi Chen Mo Jiao Chu ledger",
        ],
        "protagonist_goal": "San Tian INT Na Dao ledger",
        "structural_conflict": "Lin Xue Bi Xu Jie Chen Mo Zi Yuan Cha Chen Mo Zui Zheng",
        "information_gap": "audience Zhi Dao ledger in Bao Xian Xiang，Lin Xue only Zhi Dao Chen Mo Sa Huang",
        "first_three_episode_spine": "identity、Jiu An、He Xin conflict in before San Ji Quan Bu Li Zhu",
        "stage_highs": ["press conference counterattack", "ledger Zheng Duo", "Dong Shi Hui Fan Pan"],
        "shootability": "office、press conference Ting、Zou Lang San Lei Di Cheng Ben scene",
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
