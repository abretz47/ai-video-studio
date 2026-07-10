"""
Duration Orchestrator Chang Liang configuration

all when Zhang related Yu Zhi, Rong Cha, Su Lv Deng configuration Ji Zhong Guan Li.
"""

# =============================================================================
# duration Rong Cha configuration
# =============================================================================

# scene Ji duration Rong Cha (±15%)
DURATION_TOLERANCE_SCENE_LOW = 0.85
DURATION_TOLERANCE_SCENE_HIGH = 1.15
DURATION_TOLERANCE_SCENE = (DURATION_TOLERANCE_SCENE_LOW, DURATION_TOLERANCE_SCENE_HIGH)

# episode Ji duration Rong Cha (±10%)
DURATION_TOLERANCE_EPISODE_LOW = 0.90
DURATION_TOLERANCE_EPISODE_HIGH = 1.10
DURATION_TOLERANCE_EPISODE = (
    DURATION_TOLERANCE_EPISODE_LOW,
    DURATION_TOLERANCE_EPISODE_HIGH,
)

# TTS Gu Suan Rong Cha (Shi Yong Shi Ji duration when ±20%, Gu Suan duration when ±40%)
TTS_TOLERANCE_ACTUAL = (0.80, 1.20)
TTS_TOLERANCE_ESTIMATED = (0.60, 1.40)

# =============================================================================
# retry configuration
# =============================================================================

# Dan scene maximum retry Ci Shu
MAX_RETRY_ATTEMPTS = 3

# TTS sampling Gu Suan when Yang Ben Shu Liang
TTS_SAMPLE_COUNT = 3

# dialogue Shu Liang Yu Zhi: Di Yu Ci Zhi when Quan Liang TTS, Fou Ze sampling
TTS_FULL_GENERATION_THRESHOLD = 5

# =============================================================================
# Yu Su and word count configuration
# =============================================================================

# Zhong Wen TTS Yu Su (character/seconds)
#
# Zhong Yao: here"character"An Dai Ma Shi Xian Yue Ding Deng Tong Yu `len(text)` Zi Fu Shu(Zhong Wen Wei Zhu).
# Zao Qi Cai Yong 2.25 character/seconds(135 character/minutes)will Xian Zhu Gao Gu dialogue when Zhang, Dao Zhi: 
# - Sheng Cheng Jie Duan dialogue word count Pian Shao
# - subsequent dialogue audio/timeline Chu Xian Ming Xian"audio Guo Duan, Jian Xi Guo Da"Piao Yi
#
# Shi Ce Jiao Zhun: Ji Yu MySQL `scene_beats` in `beat_type='dialogue'` Tong Ji, 
# Ping Jun Yu Su Yue 4.7 character/seconds(≈282 character/minutes).
WORDS_PER_SECOND_SLOW = 3.8
WORDS_PER_SECOND_NORMAL = 4.7
WORDS_PER_SECOND_FAST = 5.6
WORDS_PER_SECOND = WORDS_PER_SECOND_NORMAL  # default Shi Yong Zheng Chang Yu Su(and Xian on data Jiao Zhun)

# Mei Zi Ping Jun TTS when Zhang (Hao Miao)
MS_PER_CHAR_DEFAULT = 150

# Mei Ju dialogue Ping Jun word count
WORDS_PER_DIALOGUE = 25

# =============================================================================
# Yu Suan Fen Pei configuration
# =============================================================================

# Yu Liu buffer ratio (Yong Yu scene Jian Guo Du, Kong shot, action Deng Fei dialogue time)
# 0.05 = 5% - Tai Shao, Shi Ji short drama Zhong Fei dialogue time Yue Zhan 15-25%
# 0.15 = 15% - Ping Heng: Gei Zhuan Chang, BGM Liu Kong Jian, Dan Bao Zheng Zu Gou dialogue
# 0.30 = 30% - Tai multiple, Dao Zhi dialogue insufficient
BUFFER_RATIO = 0.15

# dialogue Mi Du Yin Zi (Yong Yu Ji Suan target word count)
# Ji Shi Shi dialogue scene, Ye Bu Shi 100% all in Shuo Hua, need consider: 
# - Ting Dun, Yu Qi Ci, EmotionBiao Da
# - character Fan Ying Shi Jian
# - environment Yin/BGM Duan Luo
# 0.90 = 90% time Yong Yu dialogue Lang Du(short drama Jie Zou Kuai, dialogue Mi Ji)
DIALOGUE_DENSITY_FACTOR = 0.90

# default scene when Zhang (seconds), Dang scene none estimated_duration_seconds when Shi Yong
DEFAULT_SCENE_DURATION_SECONDS = 30

# Zui Xiao scene when Zhang (seconds)
MIN_SCENE_DURATION_SECONDS = 10

# maximum scene when Zhang (seconds)
MAX_SCENE_DURATION_SECONDS = 120

# =============================================================================
# adjust suggestion configuration
# =============================================================================

# adjust suggestion in Mei Ju dialogue Ping Jun word count
ADJUSTMENT_WORDS_PER_DIALOGUE = 20

# when Zhang insufficient when Zui Xiao increase word count
MIN_WORD_ADJUSTMENT = 20

# when Zhang Guo Chang when Zui Xiao Shan Jian word count
MIN_WORD_REDUCTION = 20
