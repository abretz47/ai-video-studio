from app.services.ai_service import _build_storyboard_context


def test_build_storyboard_context_includes_scene_details():
 script_payload = {
 "story": {
 "title": "City Adventure",
 "genre": "urban",
 "theme": "trust between people",
 "world_building": "a modern city under neon night lights",
 },
 "episode": {
 "episode_number": 1,
 "title": "First Encounter",
 "summary": "The protagonist meets a mysterious woman at the night market and gets drawn into a misunderstanding",
 "duration_minutes": 15,
 "scene_count": 3,
 },
 "scenes": [
 {
 "description": "Xiao Li Zai Ye Shi Tan Wei Tiao Xuan Shi Pin, Deng Guang Hun Huang, Ren Sheng Ding Fei.",
 "location": "Night Market Main Street",
 "time": "night",
 "characters": ["Alex Li", "Tan Zhu A Yi"],
 },
 {
 "description": "The mysterious woman turns around in the alley as neon reflects on the wet road.",
 "location": "Night Market Back Alley",
 "time": "post-rain night",
 "characters": ["Mysterious Woman"],
 "notes": "Xu Yao Biao Da tense Fen Wei",
 },
 ],
 "scene_indices": [1, 2],
 "dialogues": [
 {"scene_number": 1, "content": "Alex Li: Zhe only Shou Lian Duo Shao Qian?"},
 {"scene_number": 2, "content": "Mysterious Woman: Stop following me."},
 ],
 "stage_directions": [
 {"scene_number": 1, "content": "camera Gen Sui Shou Bu action, Qian Jing Shen"},
 {"scene_number": 2, "content": "Bei Guang Jian Ying, Man Tui"},
 ],
 "content": "Xiao Li weaves through the night-market crowd, looking around...",
 }

 context = _build_storyboard_context(script_payload)

 assert "Gu Shi Bei Jing" in context
 assert "Ju Ji Xin Xi" in context
 assert "scene 1" in context
 assert "location:Night Market Main Street" in context
 assert "dialogue:Alex Li: Zhe only Shou Lian Duo Shao Qian?" in context
 assert "Wu Tai:camera Gen Sui Shou Bu action" in context
 assert "script Wen Ben Pian Duan" in context
 assert "scene 2" in context
 assert "Bei Zhu:Xu Yao Biao Da tense Fen Wei" in context
 assert "character:Mysterious Woman" in context
