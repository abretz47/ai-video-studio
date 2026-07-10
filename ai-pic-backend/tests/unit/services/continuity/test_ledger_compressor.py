"""Tests for priority-based continuity ledger compression."""

from app.services.continuity.ledger_compressor import (
 CompressionConfig,
 compress_ledger_by_priority,
 score_fact,
 score_info_event,
 score_thread,
 score_timeline_item,
)


class TestScoreFact:
 """Tests for fact scoring function."""

 def test_empty_fact_returns_zero(self):
 assert score_fact("", set()) == 0.0
 assert score_fact(None, set()) == 0.0

 def test_base_score_for_simple_fact(self):
 score = score_fact("Zhang San Qu Le Shang Dian", set())
 assert score >= 1.0 # Base score

 def test_high_importance_keywords_boost_score(self):
 base = score_fact("Zhang San Qu Le Shang Dian", set())
 important = score_fact("John Doe De truth identity Bei reveal", set())
 assert important > base

 def test_character_involvement_boosts_score(self):
 chars = {"John Doe", "Jane Roe"}
 no_chars = score_fact("someone Qu Le Shang Dian", chars)
 one_char = score_fact("Zhang San Qu Le Shang Dian", chars)
 two_chars = score_fact("John Doe He Jane Roe Qu Le Shang Dian", chars)

 assert one_char > no_chars
 assert two_chars > one_char

 def test_longer_facts_get_slight_bonus(self):
 short = score_fact("Zhang San Qu Le Shang Dian", set()) # 6 chars
 # Need > 50 chars for first bonus, > 100 for second bonus
 medium_text = "Zhang San Zai Shen Ye Du Zi Qu Le Cheng Dong De Shang Dian Mai Dong Xi Hui Jia" * 3 # ~54 chars (>50)
 medium = score_fact(medium_text, set())
 very_long_text = (
 "Zhang San Zai Shen Ye Du Zi Qu Le Cheng Dong De Shang Dian Mai Le Yi Xie Shi Wu He Sheng Huo Yong Pin Ran Hou Hui Jia" * 4
) # ~116 chars (>100)
 long = score_fact(very_long_text, set())
 assert medium > short
 assert long > medium

 def test_english_keywords_detected(self):
 base = score_fact("person went to store", set())
 important = score_fact("the critical truth about identity was revealed", set())
 assert important > base


class TestScoreTimelineItem:
 """Tests for timeline item scoring function."""

 def test_empty_item_returns_zero(self):
 assert score_timeline_item({}, 10, set()) == 0.0
 assert score_timeline_item(None, 10, set()) == 0.0

 def test_recent_episodes_score_higher(self):
 older = {"episode_number": 1}
 newer = {"episode_number": 10}
 score_old = score_timeline_item(older, 10, set())
 score_new = score_timeline_item(newer, 10, set())
 assert score_new > score_old

 def test_reveals_boost_score(self):
 no_reveals = {"episode_number": 5, "reveals": []}
 with_reveals = {"episode_number": 5, "reveals": ["revealA", "revealB"]}
 assert score_timeline_item(with_reveals, 10, set()) > score_timeline_item(
 no_reveals, 10, set()
)

 def test_end_state_boosts_score(self):
 no_state = {"episode_number": 5}
 with_state = {"episode_number": 5, "end_state": "John Doe Li Kai Le city"}
 assert score_timeline_item(with_state, 10, set()) > score_timeline_item(
 no_state, 10, set()
)

 def test_anchors_boost_score(self):
 no_anchors = {"episode_number": 5}
 with_anchors = {
 "episode_number": 5,
 "time_anchor": "Di Er Tian",
 "location_anchor": "Cheng Shi Zhong Xin",
 }
 assert score_timeline_item(with_anchors, 10, set()) > score_timeline_item(
 no_anchors, 10, set()
)


class TestScoreThread:
 """Tests for thread scoring function."""

 def test_empty_thread_returns_zero(self):
 assert score_thread("", set()) == 0.0
 assert score_thread(None, set()) == 0.0

 def test_question_marks_boost_score(self):
 statement = "John Doe Li Kai Le city"
 question = "John Doe why Li Kai Le city?"
 assert score_thread(question, set()) > score_thread(statement, set())

 def test_importance_keywords_boost_score(self):
 simple = "Zhang San Zai Deng Dai"
 suspense = "Guan Jian Xuan Nian: John Doe De Mi Mi identity"
 assert score_thread(suspense, set()) > score_thread(simple, set())

 def test_character_mention_boosts_score(self):
 chars = {"John Doe", "Jane Roe"}
 no_char = "someone Zai Deng Dai"
 with_char = "Zhang San Zai Deng Dai"
 assert score_thread(with_char, chars) > score_thread(no_char, chars)


class TestScoreInfoEvent:
 """Tests for info acquisition event scoring function."""

 def test_empty_event_returns_zero(self):
 assert score_info_event({}, 10, set()) == 0.0
 assert score_info_event(None, 10, set()) == 0.0

 def test_recent_episodes_score_higher(self):
 older = {"episode_number": 1, "who": "audience", "what": "information", "how": "reveal"}
 newer = {"episode_number": 10, "who": "audience", "what": "information", "how": "reveal"}
 assert score_info_event(newer, 10, set()) > score_info_event(older, 10, set())

 def test_known_character_boosts_score(self):
 chars = {"John Doe"}
 unknown_who = {
 "episode_number": 5,
 "who": "passerby",
 "what": "information",
 "how": "reveal",
 }
 known_who = {"episode_number": 5, "who": "John Doe", "what": "information", "how": "reveal"}
 assert score_info_event(known_who, 10, chars) > score_info_event(
 unknown_who, 10, chars
)

 def test_audience_knowledge_boosts_score(self):
 other = {"episode_number": 5, "who": "passerby", "what": "information", "how": "conversation"}
 audience = {"episode_number": 5, "who": "audience", "what": "information", "how": "conversation"}
 assert score_info_event(audience, 10, set()) > score_info_event(
 other, 10, set()
)

 def test_important_how_method_boosts_score(self):
 simple = {"episode_number": 5, "who": "audience", "what": "information", "how": "conversation"}
 reveal = {"episode_number": 5, "who": "audience", "what": "information", "how": "Jie Shi Zhen Xiang"}
 assert score_info_event(reveal, 10, set()) > score_info_event(simple, 10, set())


class TestCompressionConfig:
 """Tests for compression configuration."""

 def test_default_config_values(self):
 config = CompressionConfig()
 assert config.max_facts == 25
 assert config.max_timeline == 30
 assert config.max_open_threads == 25
 assert config.max_resolved_threads == 25
 assert config.max_info_events == 60

 def test_custom_config_values(self):
 config = CompressionConfig(max_facts=10, max_timeline=5)
 assert config.max_facts == 10
 assert config.max_timeline == 5


class TestCompressLedgerByPriority:
 """Tests for the main compression function."""

 def test_empty_ledger(self):
 result = compress_ledger_by_priority({})
 assert result["version"] == 1
 assert result["facts"] == []
 assert result["timeline"] == []
 assert result["characters"] == {}
 assert result["info_acquisition_events"] == []
 assert result["open_threads"] == []
 assert result["resolved_threads"] == []

 def test_preserves_characters_unchanged(self):
 ledger = {
 "characters": {
 "John Doe": {"status": "active", "goal": "Zhao Dao Zhen Xiang"},
 "Jane Roe": {"status": "hidden", "goal": "Bao Shou Mi Mi"},
 }
 }
 result = compress_ledger_by_priority(ledger)
 assert result["characters"] == ledger["characters"]

 def test_respects_max_limits(self):
 # Create ledger with many items
 ledger = {
 "facts": [f"Shi Shi{i}" for i in range(50)],
 "open_threads": [f"Xian Suo{i}" for i in range(50)],
 }
 config = CompressionConfig(max_facts=5, max_open_threads=3)
 result = compress_ledger_by_priority(ledger, config)

 assert len(result["facts"]) == 5
 assert len(result["open_threads"]) == 3

 def test_prioritizes_important_facts(self):
 ledger = {
 "facts": [
 "Pu Tong Shi Shi1",
 "key identity truth Bei reveal",
 "Pu Tong Shi Shi2",
 "Zhong Yao Mi Mi discover",
 "Pu Tong Shi Shi3",
 ],
 }
 config = CompressionConfig(max_facts=2)
 result = compress_ledger_by_priority(ledger, config)

 # Important facts should be kept
 assert "key identity truth Bei reveal" in result["facts"]
 assert "Zhong Yao Mi Mi discover" in result["facts"]
 assert "Pu Tong Shi Shi1" not in result["facts"]

 def test_prioritizes_recent_timeline_items(self):
 ledger = {
 "timeline": [
 {"episode_number": 1, "events": ["Shi Jian1"]},
 {"episode_number": 5, "reveals": ["Zhong Da Jie Shi"], "end_state": "Guan Jian Jie Ju"},
 {"episode_number": 3, "events": ["Shi Jian3"]},
 ],
 }
 config = CompressionConfig(max_timeline=2)
 result = compress_ledger_by_priority(ledger, config)

 # Episode 5 has most content, should be kept
 ep_numbers = [item["episode_number"] for item in result["timeline"]]
 assert 5 in ep_numbers

 def test_timeline_sorted_chronologically_after_compression(self):
 ledger = {
 "timeline": [
 {"episode_number": 3, "reveals": ["reveal"]},
 {"episode_number": 1, "reveals": ["reveal"]},
 {"episode_number": 5, "reveals": ["reveal"]},
 {"episode_number": 2, "reveals": ["reveal"]},
 ],
 }
 result = compress_ledger_by_priority(ledger)

 # Should be sorted chronologically
 ep_numbers = [item["episode_number"] for item in result["timeline"]]
 assert ep_numbers == sorted(ep_numbers)

 def test_prioritizes_threads_with_characters(self):
 ledger = {
 "characters": {"John Doe": {}, "Jane Roe": {}},
 "open_threads": [
 "Mou Ren Zai Deng Dai",
 "John Doe De Mi Mi identity Xuan Nian",
 "Tian Qi Bian Hua",
 "Jane Roe De key Ren Wu?",
 ],
 }
 config = CompressionConfig(max_open_threads=2)
 result = compress_ledger_by_priority(ledger, config)

 # Threads mentioning characters should be prioritized
 assert any("John Doe" in t or "Jane Roe" in t for t in result["open_threads"])

 def test_preserves_version_number(self):
 ledger = {"version": 3}
 result = compress_ledger_by_priority(ledger)
 assert result["version"] == 3

 def test_handles_non_dict_items_gracefully(self):
 ledger = {
 "facts": ["Zheng Chang Shi Shi", None, "", "Ling Yi Ge Shi Shi"],
 "timeline": [{"episode_number": 1}, None, "invalid"],
 }
 result = compress_ledger_by_priority(ledger)

 # Should filter out invalid items
 assert None not in result["facts"]
 assert "" not in result["facts"]
 assert all(isinstance(item, dict) for item in result["timeline"])

 def test_integration_with_realistic_ledger(self):
 """Test with a realistic ledger structure."""
 ledger = {
 "version": 2,
 "facts": [
 "Zhang San Shi company Gao Guan",
 "Guan Jian Zhen Xiang: Jane Roe Shi undercover",
 "office Zai Shi Zhong Xin",
 "Mi Mi identity Shang Wei reveal",
 ],
 "timeline": [
 {
 "episode_number": 1,
 "time_anchor": "Zhou Yi",
 "location_anchor": "company",
 "events": ["Zhang San Dao Da"],
 "end_state": "Gu Shi Kai Shi",
 "reveals": [],
 },
 {
 "episode_number": 2,
 "time_anchor": "Zhou Er",
 "location_anchor": "conference room",
 "events": ["Zhong Yao Hui Yi"],
 "end_state": "Fa Xian Xian Suo",
 "reveals": ["key information reveal"],
 },
 ],
 "characters": {
 "John Doe": {
 "status": "Diao Cha Zhong",
 "goal": "Zhao Chu Zhen Xiang",
 "relationships": {"Jane Roe": "Tong Shi"},
 "known_info": ["company You issue"],
 "unknown_info": ["Jane Roe Shi undercover"],
 },
 "Jane Roe": {
 "status": "Yin Cang Shen Fen",
 "goal": "Wan Cheng Ren Wu",
 "relationships": {"John Doe": "target"},
 "known_info": ["Zhang San Zai Diao Cha"],
 "unknown_info": [],
 },
 },
 "info_acquisition_events": [
 {
 "episode_number": 1,
 "who": "audience",
 "what": "John Doe De Bei Jing",
 "how": "voiceover",
 },
 {
 "episode_number": 2,
 "who": "John Doe",
 "what": "Fa Xian Zheng Ju",
 "how": "Mu Ji",
 },
 ],
 "open_threads": [
 "Jane Roe De Zhen Shi identity Shi Shen Me?",
 "company De Mi Mi?",
 ],
 "resolved_threads": ["John Doe De Dong Ji Yi Ming Que"],
 }

 result = compress_ledger_by_priority(ledger)

 # Verify structure preserved
 assert result["version"] == 2
 assert len(result["characters"]) == 2
 assert "John Doe" in result["characters"]
 assert "Jane Roe" in result["characters"]

 # Verify important items preserved
 assert any("truth" in f or "identity" in f for f in result["facts"])
 assert len(result["timeline"]) == 2
 assert len(result["open_threads"]) == 2


class TestEdgeCases:
 """Tests for edge cases and error handling."""

 def test_none_ledger(self):
 result = compress_ledger_by_priority(None)
 assert result["version"] == 1
 assert result["facts"] == []

 def test_non_dict_ledger(self):
 result = compress_ledger_by_priority("invalid")
 assert result["version"] == 1
 assert result["facts"] == []

 def test_missing_fields(self):
 ledger = {"version": 1} # Only version, no other fields
 result = compress_ledger_by_priority(ledger)
 assert result["facts"] == []
 assert result["timeline"] == []
 assert result["characters"] == {}

 def test_wrong_type_fields(self):
 ledger = {
 "facts": "not a list",
 "timeline": 123,
 "characters": ["not", "a", "dict"],
 }
 result = compress_ledger_by_priority(ledger)
 assert result["facts"] == []
 assert result["timeline"] == []
 assert result["characters"] == {}

 def test_zero_max_config(self):
 """Test with zero limits returns empty lists."""
 ledger = {
 "facts": ["fact1", "fact2"],
 "timeline": [{"episode_number": 1}],
 }
 config = CompressionConfig(
 max_facts=0,
 max_timeline=0,
 max_open_threads=0,
 max_resolved_threads=0,
 max_info_events=0,
)
 result = compress_ledger_by_priority(ledger, config)
 assert result["facts"] == []
 assert result["timeline"] == []
