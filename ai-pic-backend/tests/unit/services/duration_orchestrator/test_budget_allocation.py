"""
Yu Suan Fen Pei Dan Yuan Ce Shi

test Duration Orchestrator De Yu Suan Fen Pei logic.
"""

from app.services.duration_orchestrator.constants import (
 BUFFER_RATIO,
 DIALOGUE_DENSITY_FACTOR,
 DURATION_TOLERANCE_SCENE_HIGH,
 DURATION_TOLERANCE_SCENE_LOW,
 MAX_SCENE_DURATION_SECONDS,
 MIN_SCENE_DURATION_SECONDS,
 WORDS_PER_SECOND,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus
from app.services.duration_orchestrator.utils import (
 allocate_scene_budgets,
 calculate_target_word_count,
 compute_adjustment_hint,
 count_dialogue_words,
 estimate_duration_from_words,
 rebalance_remaining_budgets,
)


class TestCalculateTargetWordCount:
 """test word count Ji Suan

 new Gong Shi Kao Lv dialogue Mi Du Yin Zi (DIALOGUE_DENSITY_FACTOR = 0.90):
 Mu Biao Zi Shu = duration(seconds) * Dui Bai Mi Du * speech rate
 """

 def test_normal_duration(self):
 """normal duration De word count Ji Suan"""
 word_count = calculate_target_word_count(60)
 # 60seconds * Dui Bai Mi Du * speech rate
 expected = int(60 * DIALOGUE_DENSITY_FACTOR * WORDS_PER_SECOND)
 assert word_count == expected

 def test_short_duration(self):
 """Duan Shi length De word count Ji Suan"""
 word_count = calculate_target_word_count(10)
 # 10seconds * Dui Bai Mi Du * speech rate
 expected = int(10 * DIALOGUE_DENSITY_FACTOR * WORDS_PER_SECOND)
 assert word_count == expected

 def test_long_duration(self):
 """Zhang Shi Chang De word count Ji Suan"""
 word_count = calculate_target_word_count(180)
 # 180seconds * Dui Bai Mi Du * speech rate
 expected = int(180 * DIALOGUE_DENSITY_FACTOR * WORDS_PER_SECOND)
 assert word_count == expected


class TestAllocateSceneBudgets:
 """test Yu Suan Fen Pei"""

 def test_empty_scenes(self):
 """Kong scene list"""
 budgets, buffer = allocate_scene_budgets(
 total_duration_minutes=3,
 scenes=[],
)
 assert budgets == []
 assert buffer == 0

 def test_single_scene_no_estimate(self):
 """Dan scene none Gu Suan Shi length"""
 scenes = [{"scene_number": 1, "summary": "scene1"}]
 budgets, buffer = allocate_scene_budgets(
 total_duration_minutes=3, # 180seconds
 scenes=scenes,
)

 assert len(budgets) == 1
 assert buffer == int(180 * BUFFER_RATIO) # 9seconds

 # Ke Fen Pei time = 180 - 9 = 171seconds
 budget = budgets[0]
 assert budget.scene_number == 1
 assert budget.target_duration_seconds <= 171
 assert budget.target_duration_seconds >= MIN_SCENE_DURATION_SECONDS

 def test_multiple_scenes_with_estimates(self):
 """Duo scene You Gu Suan Shi length, An Bi Li Fen Pei"""
 scenes = [
 {"scene_number": 1, "estimated_duration_seconds": 30},
 {"scene_number": 2, "estimated_duration_seconds": 60},
 {"scene_number": 3, "estimated_duration_seconds": 30},
 ]
 budgets, buffer = allocate_scene_budgets(
 total_duration_minutes=3, # 180seconds
 scenes=scenes,
)

 assert len(budgets) == 3
 assert buffer == int(180 * BUFFER_RATIO)

 # scene2Ying Gai Fen Pei Zui Duo time(Bi Li 60/120 = 0.5)
 assert budgets[1].target_duration_seconds > budgets[0].target_duration_seconds
 assert budgets[1].target_duration_seconds > budgets[2].target_duration_seconds

 # scene1He Chang Jing3Ying Gai Xiang Deng(Dou Shi30seconds, Bi Li Xiang Tong)
 assert budgets[0].target_duration_seconds == budgets[2].target_duration_seconds

 def test_word_count_calculated(self):
 """word count target correct Ji Suan (Kao Lv dialogue Mi Du Yin Zi)"""
 scenes = [{"scene_number": 1, "estimated_duration_seconds": 60}]
 budgets, _ = allocate_scene_budgets(
 total_duration_minutes=2,
 scenes=scenes,
)

 budget = budgets[0]
 # Xin Gong Shi: word count = duration * Dui Bai Mi Du * speech rate
 expected_words = int(
 budget.target_duration_seconds * DIALOGUE_DENSITY_FACTOR * WORDS_PER_SECOND
)
 assert budget.target_word_count == expected_words

 def test_tolerance_range_calculated(self):
 """Rong Cha Fan Wei correct Ji Suan"""
 scenes = [{"scene_number": 1, "estimated_duration_seconds": 60}]
 budgets, _ = allocate_scene_budgets(
 total_duration_minutes=2,
 scenes=scenes,
)

 budget = budgets[0]
 expected_min = int(
 budget.target_duration_seconds * DURATION_TOLERANCE_SCENE_LOW
)
 expected_max = int(
 budget.target_duration_seconds * DURATION_TOLERANCE_SCENE_HIGH
)
 assert budget.min_duration_seconds == expected_min
 assert budget.max_duration_seconds == expected_max

 def test_scene_duration_limits(self):
 """scene duration Bu Chao Guo Zui Da/Zui Xiao Xian Zhi"""
 # Ji Duan Zong Shi Chang
 scenes = [{"scene_number": 1}]
 budgets, _ = allocate_scene_budgets(
 total_duration_minutes=0.1, # 6seconds
 scenes=scenes,
)
 assert budgets[0].target_duration_seconds >= MIN_SCENE_DURATION_SECONDS

 # Ji Zhang Zong Shi Chang, Dan Chang Jing
 budgets2, _ = allocate_scene_budgets(
 total_duration_minutes=10, # 600seconds
 scenes=scenes,
)
 assert budgets2[0].target_duration_seconds <= MAX_SCENE_DURATION_SECONDS


class TestComputeAdjustmentHint:
 """test Tiao Zheng Jian Yi generate"""

 def test_duration_too_short(self):
 """Shi length Bu Zu De Tiao Zheng Jian Yi"""
 reason, hint = compute_adjustment_hint(
 actual_word_count=50,
 actual_duration_ms=20000, # 20seconds
 target_duration_seconds=45, # 45seconds
)

 assert reason == "duration_too_short"
 assert "20.0 seconds" in hint
 assert "45 seconds" in hint
 assert "increase" in hint

 def test_duration_too_long(self):
 """Shi length Guo Chang De Tiao Zheng Jian Yi"""
 reason, hint = compute_adjustment_hint(
 actual_word_count=200,
 actual_duration_ms=80000, # 80seconds
 target_duration_seconds=45, # 45seconds
)

 assert reason == "duration_too_long"
 assert "80.0 seconds" in hint
 assert "45 seconds" in hint
 assert "Shan Jian" in hint

 def test_suggestion_includes_word_count(self):
 """Jian Yi Bao Han word count Gu Suan"""
 reason, hint = compute_adjustment_hint(
 actual_word_count=50,
 actual_duration_ms=20000,
 target_duration_seconds=45,
)

 # Cha Ju 25 seconds, Yue 62 character
 assert "character" in hint


class TestSceneBudget:
 """test SceneBudget Shu Ju Lei"""

 def test_is_within_tolerance_true(self):
 """duration Zai Rong Cha Fan Wei INT"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51, # 60 * 0.85
 max_duration_seconds=69, # 60 * 1.15
 actual_duration_seconds=55,
)
 assert budget.is_within_tolerance() is True

 def test_is_within_tolerance_false_too_short(self):
 """Shi Chang Guo Duan"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 actual_duration_seconds=40,
)
 assert budget.is_within_tolerance() is False

 def test_is_within_tolerance_false_too_long(self):
 """Shi Chang Guo Chang"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 actual_duration_seconds=80,
)
 assert budget.is_within_tolerance() is False

 def test_duration_ratio(self):
 """Shi length Bi Li Ji Suan"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 actual_duration_seconds=45,
)
 assert budget.duration_ratio() == 0.75

 def test_duration_diff_seconds(self):
 """Shi length Cha Yi Ji Suan"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 actual_duration_seconds=75,
)
 assert budget.duration_diff_seconds() == 15 # timeout 15 seconds

 def test_to_dict(self):
 """Zhuan Huan Wei Zi Dian"""
 budget = SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
)
 d = budget.to_dict()
 assert d["scene_number"] == 1
 assert d["target_duration_seconds"] == 60
 assert d["status"] == "pending"


class TestRebalanceRemainingBudgets:
 """test Yu Suan Zai Ping Heng"""

 def test_rebalance_when_over_budget(self):
 """timeout Shi from Hou Xu scene Kou Chu"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
 status=SceneStatus.COMMITTED,
 actual_duration_seconds=40, # timeout 10 seconds
),
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
),
 SceneBudget(
 scene_number=3,
 scene_index=2,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
),
 ]

 rebalance_remaining_budgets(budgets, 0, 40)

 # Hou Xu Liang Ge scene Ying Gai Ge Jian Shao 5 seconds
 assert budgets[1].target_duration_seconds == 25
 assert budgets[2].target_duration_seconds == 25

 def test_rebalance_when_under_budget(self):
 """Qian Shi Shi Gei Hou Xu scene increase"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
 status=SceneStatus.COMMITTED,
 actual_duration_seconds=20, # Qian Shi 10 seconds
),
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
),
 ]

 rebalance_remaining_budgets(budgets, 0, 20)

 # Hou Xu scene Ying Gai increase 10 seconds
 assert budgets[1].target_duration_seconds == 40

 def test_no_rebalance_for_last_scene(self):
 """final Yi Ge scene Bu Xu Yao Zai Ping Heng"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
),
 ]

 original_target = budgets[0].target_duration_seconds
 rebalance_remaining_budgets(budgets, 0, 40)

 # Bu Ying Gai You Bian Hua
 assert budgets[0].target_duration_seconds == original_target


class TestCountDialogueWords:
 """test dialogue Zi Shu Tong Ji"""

 def test_count_words(self):
 """normal dialogue Zi Shu Tong Ji"""
 dialogues = [
 {"character": "Xiao Ming", "content": "Hello, world"},
 {"character": "Xiao Hong", "content": "Goodbye, friend"},
 ]
 assert count_dialogue_words(dialogues) == 8

 def test_empty_dialogues(self):
 """Kong dialogue list"""
 assert count_dialogue_words([]) == 0

 def test_empty_content(self):
 """Kong Nei Rong"""
 dialogues = [
 {"character": "Xiao Ming", "content": ""},
 {"character": "Xiao Hong", "content": "Ni Hao"},
 ]
 assert count_dialogue_words(dialogues) == 2


class TestEstimateDurationFromWords:
 """test Gen Ju word count Gu Suan Shi length"""

 def test_estimate_duration(self):
 """normal word count Gu Suan Shi length"""
 word_count = int(60 * WORDS_PER_SECOND)
 assert estimate_duration_from_words(word_count) == 60

 def test_estimate_zero_words(self):
 """Ling Zi Shu"""
 assert estimate_duration_from_words(0) == 0
