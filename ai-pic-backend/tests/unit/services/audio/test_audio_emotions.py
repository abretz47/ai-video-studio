"""Tests for audio emotion normalization."""

from app.services.audio.audio_emotions import (
    ALLOWED_TTS_EMOTIONS,
    normalize_tts_emotion,
)


class TestAllowedTTSEmotions:
    """Tests for ALLOWED_TTS_EMOTIONS constant."""

    def test_contains_expected_emotions(self):
        """Test that all expected emotions are present."""
        expected = {
            "happy",
            "sad",
            "angry",
            "fearful",
            "disgusted",
            "surprised",
            "calm",
            "fluent",
            "whisper",
        }
        assert ALLOWED_TTS_EMOTIONS == expected

    def test_is_set(self):
        """Test that it's a set for O(1) lookup."""
        assert isinstance(ALLOWED_TTS_EMOTIONS, set)


class TestNormalizeTTSEmotion:
    """Tests for normalize_tts_emotion function."""

    def test_direct_emotion_match(self):
        """Test direct emotion string matching."""
        assert normalize_tts_emotion("happy") == "happy"
        assert normalize_tts_emotion("sad") == "sad"
        assert normalize_tts_emotion("ANGRY") == "angry"

    def test_whisper_detection(self):
        """Test whisper-related emotion detection."""
        assert normalize_tts_emotion("Di Sheng Shuo") == "whisper"
        assert normalize_tts_emotion("Qiao Sheng Shuo") == "whisper"
        assert normalize_tts_emotion(None, action="Xiao Sheng Shuo") == "whisper"
        assert normalize_tts_emotion("Di Yu") == "whisper"

    def test_angry_detection(self):
        """Test angry-related emotion detection."""
        assert normalize_tts_emotion("angry Di") == "angry"
        assert normalize_tts_emotion("Sheng Qi") == "angry"
        assert normalize_tts_emotion(None, action="Bao Zao") == "angry"

    def test_sad_detection(self):
        """Test sad-related emotion detection."""
        assert normalize_tts_emotion("Bei Shang") == "sad"
        assert normalize_tts_emotion("Nan Guo") == "sad"
        assert normalize_tts_emotion(None, action="Tan Qi") == "sad"
        assert normalize_tts_emotion(None, action="Tan Yi Kou Qi") == "sad"

    def test_happy_detection(self):
        """Test happy-related emotion detection."""
        assert normalize_tts_emotion("Gao Xing") == "happy"
        assert normalize_tts_emotion("happy") == "happy"
        assert normalize_tts_emotion(None, action="Xing Fen") == "happy"

    def test_surprised_detection(self):
        """Test surprised-related emotion detection."""
        assert normalize_tts_emotion("Jing Ya") == "surprised"
        assert normalize_tts_emotion("Zhen Jing") == "surprised"

    def test_fearful_detection(self):
        """Test fearful-related emotion detection."""
        assert normalize_tts_emotion("Hai Pa") == "fearful"
        assert normalize_tts_emotion("Kong Ju") == "fearful"
        assert normalize_tts_emotion(None, action="tense") == "fearful"

    def test_disgusted_detection(self):
        """Test disgusted-related emotion detection."""
        assert normalize_tts_emotion("Yan Wu") == "disgusted"
        assert normalize_tts_emotion("E Xin") == "disgusted"

    def test_calm_detection(self):
        """Test calm-related emotion detection."""
        assert normalize_tts_emotion("calm") == "calm"
        assert normalize_tts_emotion("calm") == "calm"
        assert normalize_tts_emotion(None, action="Chen Wen") == "calm"

    def test_fluent_detection(self):
        """Test fluent-related emotion detection."""
        assert normalize_tts_emotion("Zi Xin") == "fluent"
        assert normalize_tts_emotion("Jian Ding") == "fluent"
        assert normalize_tts_emotion(None, action="Cong Rong") == "fluent"

    def test_none_values(self):
        """Test None inputs return None."""
        assert normalize_tts_emotion(None) is None
        assert normalize_tts_emotion(None, action=None) is None

    def test_empty_strings(self):
        """Test empty strings return None."""
        assert normalize_tts_emotion("") is None
        assert normalize_tts_emotion("", action="") is None

    def test_unrecognized_emotion(self):
        """Test unrecognized emotion returns None."""
        assert normalize_tts_emotion("unknown_emotion") is None
        assert normalize_tts_emotion("Yi Xie Sui Ji Wen Zi") is None

    def test_combined_emotion_and_action(self):
        """Test emotion detection from combined text."""
        assert normalize_tts_emotion("Shuo Hua", action="Tan Qi") == "sad"
