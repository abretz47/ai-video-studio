"""
Voice service constants and option definitions.

Provides UI option lists for voice synthesis configuration including
voice types, models, emotions, languages, formats, and quality settings.
"""

from typing import Any, Dict, List

# Default voice ID for MiniMax TTS
DEFAULT_MINIMAX_VOICE_ID = "Chinese (Mandarin)_Lyrical_Voice"

# Voice type options
VOICE_TYPE_OPTIONS: List[Dict[str, str]] = [
    {"value": "system", "label_zh": "system voice timbre", "label_en": "System voices"},
    {"value": "voice_cloning", "label_zh": "quick Fu Ke", "label_en": "Voice cloning"},
    {
        "value": "voice_generation",
        "label_zh": "Wen Sheng voice timbre",
        "label_en": "Voice generation",
    },
    {"value": "all", "label_zh": "Quan Bu", "label_en": "All"},
]

# TTS model options
TTS_MODEL_OPTIONS: List[Dict[str, str]] = [
    {
        "value": "speech-2.6-hd",
        "label_zh": "Speech 2.6 Gao Qing",
        "label_en": "Speech 2.6 HD",
    },
    {
        "value": "speech-2.6-turbo",
        "label_zh": "Speech 2.6 Ji Su",
        "label_en": "Speech 2.6 Turbo",
    },
    {"value": "speech-02-hd", "label_zh": "Speech 02 Gao Qing", "label_en": "Speech 02 HD"},
    {
        "value": "speech-02-turbo",
        "label_zh": "Speech 02 Ji Su",
        "label_en": "Speech 02 Turbo",
    },
    {"value": "speech-01-hd", "label_zh": "Speech 01 Gao Qing", "label_en": "Speech 01 HD"},
    {
        "value": "speech-01-turbo",
        "label_zh": "Speech 01 Ji Su",
        "label_en": "Speech 01 Turbo",
    },
]

# Emotion options
EMOTION_OPTIONS: List[Dict[str, str]] = [
    {"value": "happy", "label_zh": "happy", "label_en": "Happy"},
    {"value": "sad", "label_zh": "sad", "label_en": "Sad"},
    {"value": "angry", "label_zh": "angry", "label_en": "Angry"},
    {"value": "fearful", "label_zh": "afraid", "label_en": "Fearful"},
    {"value": "disgusted", "label_zh": "Yan Wu", "label_en": "Disgusted"},
    {"value": "surprised", "label_zh": "surprised", "label_en": "Surprised"},
    {"value": "calm", "label_zh": "Zhong Xing", "label_en": "Calm"},
    {"value": "fluent", "label_zh": "Sheng Dong", "label_en": "Fluent"},
    {"value": "whisper", "label_zh": "Di Yu", "label_en": "Whisper"},
]

# Language boost options
LANGUAGE_BOOST_OPTIONS: List[Dict[str, str]] = [
    {"value": "Chinese", "label_zh": "Zhong Wen", "label_en": "Chinese"},
    {"value": "Chinese,Yue", "label_zh": "Yue Yu", "label_en": "Cantonese"},
    {"value": "English", "label_zh": "Ying Yu", "label_en": "English"},
    {"value": "Japanese", "label_zh": "Ri Yu", "label_en": "Japanese"},
    {"value": "Korean", "label_zh": "Han Yu", "label_en": "Korean"},
    {"value": "French", "label_zh": "Fa Yu", "label_en": "French"},
    {"value": "Spanish", "label_zh": "Xi Ban Ya Yu", "label_en": "Spanish"},
    {"value": "German", "label_zh": "De Yu", "label_en": "German"},
    {"value": "Italian", "label_zh": "Yi Da Li Yu", "label_en": "Italian"},
    {"value": "Russian", "label_zh": "E Yu", "label_en": "Russian"},
    {"value": "Thai", "label_zh": "Tai Yu", "label_en": "Thai"},
    {"value": "Vietnamese", "label_zh": "Yue Nan Yu", "label_en": "Vietnamese"},
    {"value": "Indonesian", "label_zh": "Yin Ni Yu", "label_en": "Indonesian"},
    {"value": "Turkish", "label_zh": "Tu Er Qi Yu", "label_en": "Turkish"},
    {"value": "Arabic", "label_zh": "A La Bo Yu", "label_en": "Arabic"},
    {"value": "auto", "label_zh": "automatic", "label_en": "Auto detect"},
]

# Output format options
OUTPUT_FORMAT_OPTIONS: List[Dict[str, str]] = [
    {"value": "url", "label_zh": "temporary Lian Jie(24Xiao Shi)", "label_en": "URL (24h)"},
    {"value": "hex", "label_zh": "HEX Bian Ma", "label_en": "Hex encoded"},
]

# Audio format options
AUDIO_FORMAT_OPTIONS: List[Dict[str, str]] = [
    {"value": "mp3", "label_zh": "MP3", "label_en": "MP3"},
    {"value": "wav", "label_zh": "WAV", "label_en": "WAV"},
    {"value": "pcm", "label_zh": "PCM", "label_en": "PCM"},
    {"value": "flac", "label_zh": "FLAC", "label_en": "FLAC"},
]

# Sample rate options
SAMPLE_RATE_OPTIONS: List[Dict[str, Any]] = [
    {"value": 8000, "label_zh": "8kHz", "label_en": "8000 Hz"},
    {"value": 16000, "label_zh": "16kHz", "label_en": "16000 Hz"},
    {"value": 22050, "label_zh": "22.05kHz", "label_en": "22050 Hz"},
    {"value": 24000, "label_zh": "24kHz", "label_en": "24000 Hz"},
    {"value": 32000, "label_zh": "32kHz", "label_en": "32000 Hz"},
    {"value": 44100, "label_zh": "44.1kHz", "label_en": "44100 Hz"},
]

# Bitrate options
BITRATE_OPTIONS: List[Dict[str, Any]] = [
    {"value": 32000, "label_zh": "32 kbps", "label_en": "32 kbps"},
    {"value": 64000, "label_zh": "64 kbps", "label_en": "64 kbps"},
    {"value": 128000, "label_zh": "128 kbps", "label_en": "128 kbps"},
    {"value": 256000, "label_zh": "256 kbps", "label_en": "256 kbps"},
]

# Channel options
CHANNEL_OPTIONS: List[Dict[str, Any]] = [
    {"value": 1, "label_zh": "Dan Sheng Dao", "label_en": "Mono"},
    {"value": 2, "label_zh": "Shuang Sheng Dao", "label_en": "Stereo"},
]

# Music model options
MUSIC_MODEL_OPTIONS: List[Dict[str, str]] = [
    {"value": "music-2.0", "label_zh": "Music 2.0", "label_en": "Music 2.0"},
]
