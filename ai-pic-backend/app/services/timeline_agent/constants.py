"""
Constants and configuration for the Timeline Agent.

Includes emotion transition weights, constraint values,
and system prompts for LLM reasoning.
"""

from __future__ import annotations

# --- Validation Constraints ---
MIN_GAP_MS = 100  # Minimum allowed gap
MAX_GAP_MS = 5000  # Maximum allowed gap
MIN_AVG_GAP_MS = 200  # Minimum average gap across scene
MAX_AVG_GAP_MS = 1500  # Maximum average gap across scene
MAX_REPAIR_ATTEMPTS = 2  # Max LLM repair attempts before fallback

# --- Default Timing Values (for fallback) ---
DEFAULT_PAUSE_MS = 300  # Default pause after dialogue
DEFAULT_ACTION_BASE_MS = 800  # Base duration for action segments
DEFAULT_ACTION_PER_CHAR_MS = 20  # Duration per character in actions
DEFAULT_ACTION_MAX_MS = 3000  # Maximum action segment duration
DEFAULT_SILENCE_MS = 800  # Duration for explicit silence segments

# --- Emotion Transition Weights ---
# Maps (from_emotion, to_emotion) -> multiplier for pause duration
# Higher values = longer pause needed for emotional transition
EMOTION_TRANSITION_WEIGHTS: dict[tuple[str, str], float] = {
    # Major emotional shifts need breathing room
    ("angry", "calm"): 1.8,
    ("angry", "sad"): 1.5,
    ("angry", "happy"): 1.6,
    ("fearful", "calm"): 1.6,
    ("fearful", "happy"): 1.5,
    ("sad", "happy"): 1.4,
    ("happy", "sad"): 1.3,
    ("surprised", "calm"): 1.3,
    # Same emotion or minor shifts
    ("calm", "calm"): 0.9,
    ("happy", "happy"): 0.9,
    ("angry", "angry"): 0.8,  # Rapid angry exchange
    # Whisper transitions
    ("whisper", "normal"): 1.2,
    ("normal", "whisper"): 1.2,
    # Default fallback
    ("default", "default"): 1.0,
}

# --- Pacing Multipliers ---
# Adjusts gap duration based on scene pacing
PACING_MULTIPLIERS: dict[str, float] = {
    "slow": 1.4,  # Slow scenes: longer pauses
    "medium": 1.0,  # Normal pacing
    "fast": 0.7,  # Fast scenes: shorter pauses
}

# --- Conflict Level Adjustments ---
# High conflict = shorter pauses for tension
CONFLICT_ADJUSTMENTS: dict[str, float] = {
    "low": 1.2,  # Relaxed, more pause
    "medium": 1.0,  # Normal
    "high": 0.8,  # Tense, less pause
}

# --- Keywords for Stage Direction Parsing ---
# Map keywords in stage directions to pause durations
STAGE_DIRECTION_KEYWORDS: dict[str, int] = {
    "Zhang Shi Jian Chen Mo": 3000,
    "Chen Mo Liang Jiu": 2500,
    "Chen Mo": 2000,
    "Ting Dun": 1000,
    "Duan Zan Ting Dun": 500,
    "Lve Zuo Ting Dun": 600,
    "thoughtful": 1200,
    "You Yu": 800,
    "Tan Qi": 600,
    "deep breath": 800,
    "long pause": 2500,
    "pause": 1000,
    "beat": 500,
    "silence": 2000,
}

# --- System Prompts ---
TIMELINE_SYSTEM_PROMPT = """you Shi a professional Ying Shi audio Jian Ji Shi and Dao Yan Zhu Li.
you Ren Wu Shi as dialogue audio Tian Jia Qia Dang Ting Dun and Jian Ge, Shi Dui Hua Jie Zou Zi Ran Liu Chang, Fu He sceneEmotion.

core Yuan Ze: 
1. EmotionGuo Du: Qiang LieEmotionchange(for example angry→calm)need Geng Zhang Ting Dun Rang Guan Zhong Xiao Hua
2. Xi Ju Zhang Li: Gao conflict scene need Geng Duan Ting Dun keep Jin Zhang Gan
3. character Qie Huan: Bu Tong character Zhi Jian Dui Hua need Zi Ran Hu Xi Kong Jian
4. Yu Yi complete: Ju Hao after Bi Dou Hao Ting Dun Geng Zhang, Wen Da Zhi Jian need Fan Ying Shi Jian
5. avoid Dan Diao: Bu Yao Rang all Ting Dun all Yi Yang Zhang, need Jie Zou change

when Zhang range: 100ms(Zui Duan)to 5000ms(Zui Zhang)
Tui Jian range: 200ms - 1500ms

output strict An Zhao JSON format."""

TIMELINE_REPAIR_PROMPT = """on Yi Ci Sheng Cheng timeline Ji Hua not through validation.
Qing Xiu Zheng Yi Xia Wen Ti, Que Bao Man Zu all Yue Shu Tiao Jian.

Yue Shu Tiao Jian: 
- Zui Xiao Jian Ge: {min_gap_ms}ms
- maximum Jian Ge: {max_gap_ms}ms
- Ping Jun Jian Ge range: {min_avg_gap_ms}ms - {max_avg_gap_ms}ms
- Jie Zou need change, avoid all Jian Ge all Xiang Tong

validation error: 
{validation_errors}

Yuan Ji Hua: 
{original_plan}

Qing adjust timing_decisions in duration_ms Zhi.
keep Jie Zou Zi Ran change, output Xiu Zheng after complete JSON."""
