"""Unit tests for TimelineQualityValidator."""

from __future__ import annotations

import pytest

from app.services.validators.timeline_quality_validator import (
 EmotionCurveAnalysis,
 EmotionPoint,
 TimelineQualityIssue,
 TimelineQualityIssueType,
 TimelineQualityResult,
 TimelineQualitySeverity,
 TimelineQualityValidator,
)


@pytest.fixture
def validator() -> TimelineQualityValidator:
 """Create a validator instance."""
 return TimelineQualityValidator()


class TestTimelineQualityIssue:
 """Tests for TimelineQualityIssue dataclass."""

 def test_to_dict(self) -> None:
 """Test serialization."""
 issue = TimelineQualityIssue(
 issue_type=TimelineQualityIssueType.RHYTHM_TOO_FAST,
 severity=TimelineQualitySeverity.WARNING,
 message="Test message",
 beat_index=5,
 time_range_ms=(1000, 2000),
 details={"key": "value"},
 suggestions=["Fix it"],
)
 result = issue.to_dict()
 assert result["issue_type"] == "rhythm_too_fast"
 assert result["severity"] == "warning"
 assert result["beat_index"] == 5
 assert result["time_range_ms"] == (1000, 2000)


class TestEmotionCurveAnalysis:
 """Tests for EmotionCurveAnalysis dataclass."""

 def test_to_dict(self) -> None:
 """Test serialization."""
 analysis = EmotionCurveAnalysis(
 points=[
 EmotionPoint(time_ms=0, emotion_value=0.0),
 EmotionPoint(time_ms=1000, emotion_value=0.5),
 EmotionPoint(time_ms=2000, emotion_value=1.0),
 ],
 average_intensity=0.5,
 variance=0.25,
 peaks=[2],
 valleys=[0],
 has_arc=True,
)
 d = analysis.to_dict()
 assert d["point_count"] == 3
 assert d["average_intensity"] == 0.5
 assert d["has_arc"] is True


class TestTimelineQualityResult:
 """Tests for TimelineQualityResult dataclass."""

 def test_to_dict_minimal(self) -> None:
 """Test serialization with minimal data."""
 result = TimelineQualityResult(passed=True)
 d = result.to_dict()
 assert d["passed"] is True
 assert d["issues"] == []
 assert d["emotion_curve"] is None

 def test_to_dict_full(self) -> None:
 """Test serialization with full data."""
 result = TimelineQualityResult(
 passed=True,
 average_wps=4.5,
 detected_language="zh",
 total_duration_ms=60000,
 pause_ratio=0.1,
)
 d = result.to_dict()
 assert d["average_wps"] == 4.5
 assert d["detected_language"] == "zh"


class TestTimelineQualityValidator:
 """Tests for TimelineQualityValidator."""

 def test_validate_empty_beats(
 self, validator: TimelineQualityValidator
) -> None:
 """Test validation with empty beats."""
 result = validator.validate([])
 assert result.passed is True
 assert len(result.issues) == 0

 def test_calculate_total_duration(
 self, validator: TimelineQualityValidator
) -> None:
 """Test total duration calculation."""
 beats = [
 {"start_ms": 0, "end_ms": 1000},
 {"start_ms": 1000, "end_ms": 3000},
 {"start_ms": 3000, "end_ms": 5000},
 ]
 duration = validator._calculate_total_duration(beats)
 assert duration == 5000

 def test_detect_language_chinese(
 self, validator: TimelineQualityValidator
) -> None:
 """Test Chinese language detection."""
 beats = [
 {"text": "Zhe Shi Yi Duan Zhong Wen dialogue"},
 {"text": "Ce Shi Yu Yan Jian Ce function"},
 ]
 lang = validator._detect_language(beats)
 assert lang == "zh"

 def test_detect_language_english(
 self, validator: TimelineQualityValidator
) -> None:
 """Test English language detection."""
 beats = [
 {"text": "This is English dialogue"},
 {"text": "Testing language detection"},
 ]
 lang = validator._detect_language(beats)
 assert lang == "en"

 def test_detect_language_japanese(
 self, validator: TimelineQualityValidator
) -> None:
 """Test Japanese language detection."""
 beats = [
 {"text": "これはRi Ben Yuのテストです"},
 {"text": "Yan Yu Jian Chuをテストしています"},
 ]
 lang = validator._detect_language(beats)
 assert lang == "ja"

 def test_calculate_average_wps(
 self, validator: TimelineQualityValidator
) -> None:
 """Test WPS calculation."""
 beats = [
 {
 "beat_type": "dialogue",
 "text": "Zhe Shi Shi Ge character De test", # 8 chars
 "start_ms": 0,
 "end_ms": 2000, # 2 seconds
 },
 ]
 wps = validator._calculate_average_wps(beats, "zh")
 assert wps == 4.0 # 8 chars / 2 sec = 4 chars/sec

 def test_check_rhythm_normal(
 self, validator: TimelineQualityValidator
) -> None:
 """Test rhythm check with normal speed."""
 issues = validator._check_rhythm(4.5, "zh")
 assert len(issues) == 0 # 4.5 is within normal range

 def test_check_rhythm_too_slow(
 self, validator: TimelineQualityValidator
) -> None:
 """Test rhythm check with slow speed."""
 issues = validator._check_rhythm(2.0, "zh")
 assert len(issues) > 0
 assert issues[0].issue_type == TimelineQualityIssueType.RHYTHM_TOO_SLOW

 def test_check_rhythm_too_fast(
 self, validator: TimelineQualityValidator
) -> None:
 """Test rhythm check with fast speed."""
 issues = validator._check_rhythm(8.0, "zh")
 assert len(issues) > 0
 assert issues[0].issue_type == TimelineQualityIssueType.RHYTHM_TOO_FAST

 def test_calculate_emotion_intensity_high(
 self, validator: TimelineQualityValidator
) -> None:
 """Test emotion intensity for high intensity content."""
 intensity = validator._calculate_emotion_intensity(
 "Zhen Jing!crisis Bao Fa Le!", "angry"
)
 assert intensity > 0.3

 def test_calculate_emotion_intensity_low(
 self, validator: TimelineQualityValidator
) -> None:
 """Test emotion intensity for low intensity content."""
 intensity = validator._calculate_emotion_intensity(
 "calm De Yi Tian", "calm"
)
 assert intensity < 0.3

 def test_analyze_emotion_curve(
 self, validator: TimelineQualityValidator
) -> None:
 """Test emotion curve analysis."""
 beats = [
 {"start_ms": 0, "text": "calm De start", "emotion": "calm"},
 {"start_ms": 1000, "text": "Jin Zhang Qi Lai", "emotion": "tense"},
 {"start_ms": 2000, "text": "Gao Chao Bao Fa!crisis!", "emotion": "angry"},
 {"start_ms": 3000, "text": "Ping Jing Jie Shu", "emotion": "calm"},
 ]
 analysis = validator._analyze_emotion_curve(beats)
 assert len(analysis.points) == 4
 assert analysis.variance > 0

 def test_check_emotion_curve_flat(
 self, validator: TimelineQualityValidator
) -> None:
 """Test emotion curve check with flat curve."""
 analysis = EmotionCurveAnalysis(
 points=[
 EmotionPoint(time_ms=0, emotion_value=0.2),
 EmotionPoint(time_ms=1000, emotion_value=0.2),
 EmotionPoint(time_ms=2000, emotion_value=0.2),
 ],
 variance=0.0,
)
 issues = validator._check_emotion_curve(analysis)
 flat_issues = [
 i for i in issues
 if i.issue_type == TimelineQualityIssueType.EMOTION_CURVE_FLAT
 ]
 assert len(flat_issues) > 0

 def test_check_emotion_curve_choppy(
 self, validator: TimelineQualityValidator
) -> None:
 """Test emotion curve check with choppy curve."""
 analysis = EmotionCurveAnalysis(
 points=[EmotionPoint(time_ms=i * 100, emotion_value=0.5) for i in range(10)],
 peaks=[1, 3, 5, 7, 9], # Too many peaks
 variance=0.5,
)
 issues = validator._check_emotion_curve(analysis)
 choppy_issues = [
 i for i in issues
 if i.issue_type == TimelineQualityIssueType.EMOTION_CURVE_CHOPPY
 ]
 assert len(choppy_issues) > 0

 def test_calculate_pause_ratio(
 self, validator: TimelineQualityValidator
) -> None:
 """Test pause ratio calculation."""
 beats = [
 {"beat_type": "dialogue", "start_ms": 0, "end_ms": 1000},
 {"beat_type": "pause", "start_ms": 1000, "end_ms": 1500},
 {"beat_type": "dialogue", "start_ms": 1500, "end_ms": 2500},
 ]
 ratio = validator._calculate_pause_ratio(beats)
 assert ratio == 0.2 # 500ms pause / 2500ms total

 def test_check_dramatic_pauses_missing(
 self, validator: TimelineQualityValidator
) -> None:
 """Test missing dramatic pause detection."""
 beats = [
 {"beat_type": "dialogue", "text": "Zhe Shi Yi Ge Xiao Dian Ha Ha", "start_ms": 0, "end_ms": 1000},
 {"beat_type": "dialogue", "text": "Ji Xu Shuo", "start_ms": 1000, "end_ms": 2000},
 ]
 issues = validator._check_dramatic_pauses(beats)
 missing_issues = [
 i for i in issues
 if i.issue_type == TimelineQualityIssueType.MISSING_DRAMATIC_PAUSE
 ]
 assert len(missing_issues) > 0

 def test_check_dramatic_pauses_present(
 self, validator: TimelineQualityValidator
) -> None:
 """Test when dramatic pause is present."""
 beats = [
 {"beat_type": "dialogue", "text": "Zhe Shi Yi Ge Xiao Dian Ha Ha", "start_ms": 0, "end_ms": 1000},
 {"beat_type": "pause", "start_ms": 1000, "end_ms": 1800}, # 800ms pause
 {"beat_type": "dialogue", "text": "Ji Xu Shuo", "start_ms": 1800, "end_ms": 2800},
 ]
 issues = validator._check_dramatic_pauses(beats)
 missing_issues = [
 i for i in issues
 if i.issue_type == TimelineQualityIssueType.MISSING_DRAMATIC_PAUSE
 ]
 assert len(missing_issues) == 0

 def test_check_excessive_pause(
 self, validator: TimelineQualityValidator
) -> None:
 """Test excessive pause detection."""
 beats = [
 {"beat_type": "dialogue", "text": "Shuo Hua", "start_ms": 0, "end_ms": 1000},
 {"beat_type": "pause", "start_ms": 1000, "end_ms": 5000}, # 4000ms pause
 {"beat_type": "dialogue", "text": "continue", "start_ms": 5000, "end_ms": 6000},
 ]
 issues = validator._check_dramatic_pauses(beats)
 excessive_issues = [
 i for i in issues
 if i.issue_type == TimelineQualityIssueType.EXCESSIVE_PAUSE
 ]
 assert len(excessive_issues) > 0

 def test_check_duration_drift(
 self, validator: TimelineQualityValidator
) -> None:
 """Test duration drift detection."""
 # 50% drift (150000 vs 100000)
 issues = validator._check_duration_drift(150000, 100000)
 assert len(issues) > 0
 assert issues[0].issue_type == TimelineQualityIssueType.DURATION_ESTIMATE_DRIFT

 def test_check_duration_drift_acceptable(
 self, validator: TimelineQualityValidator
) -> None:
 """Test acceptable duration drift."""
 # 10% drift (110000 vs 100000)
 issues = validator._check_duration_drift(110000, 100000)
 assert len(issues) == 0

 def test_estimate_duration_syllable_level_chinese(
 self, validator: TimelineQualityValidator
) -> None:
 """Test syllable-level duration estimation for Chinese."""
 text = "Zhe Shi Yi Duan test Wen Ben, Yong Yu validate Shi length Gu Suan."
 duration = validator.estimate_duration_syllable_level(text, "zh", "normal")
 # ~16 chars + 2 punctuation pauses
 assert duration > 3000 # Should be around 3-4 seconds

 def test_estimate_duration_syllable_level_english(
 self, validator: TimelineQualityValidator
) -> None:
 """Test syllable-level duration estimation for English."""
 text = "This is a test sentence for duration estimation."
 duration = validator.estimate_duration_syllable_level(text, "en", "normal")
 assert duration > 0

 def test_validate_full_timeline_good(
 self, validator: TimelineQualityValidator
) -> None:
 """Test full validation with good timeline."""
 beats = [
 {
 "beat_type": "dialogue",
 "text": "calm De opening dialogue",
 "emotion": "calm",
 "start_ms": 0,
 "end_ms": 2000,
 },
 {
 "beat_type": "dialogue",
 "text": "tense Qi Lai Le!",
 "emotion": "tense",
 "start_ms": 2000,
 "end_ms": 4000,
 },
 {
 "beat_type": "pause",
 "start_ms": 4000,
 "end_ms": 4500,
 },
 {
 "beat_type": "dialogue",
 "text": "Gao Chao Bao Fa!crisis!",
 "emotion": "angry",
 "start_ms": 4500,
 "end_ms": 6500,
 },
 ]

 result = validator.validate(beats, "zh")

 assert result.passed is True
 assert result.detected_language == "zh"
 assert result.total_duration_ms == 6500
 assert result.emotion_curve is not None

 def test_validate_full_timeline_with_issues(
 self, validator: TimelineQualityValidator
) -> None:
 """Test full validation with problematic timeline."""
 beats = [
 {
 "beat_type": "dialogue",
 "text": "Duan", # Very short
 "emotion": "calm",
 "start_ms": 0,
 "end_ms": 100, # Very fast
 },
 {
 "beat_type": "pause",
 "start_ms": 100,
 "end_ms": 5000, # Excessive pause
 },
 ]

 result = validator.validate(beats, "zh", target_duration_ms=60000)

 # Should have issues for:
 # - Rhythm too fast
 # - Excessive pause
 # - Duration drift
 assert len(result.issues) > 0
