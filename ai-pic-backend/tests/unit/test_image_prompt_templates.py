from app.prompts.manager import prompt_manager
from app.prompts.template_audit import build_prompt_template_audit


def test_virtual_ip_image_prompt_template_renders():
 prompt = prompt_manager.render_prompt(
 "virtual_ip_image",
 {
 "character_name": "Ce Shi Jue Se",
 "character_description": "Duan Fa, Hei Kuang Yan Jing, Shen Xing Qing Shou, Ji Ke Qi Zhi",
 "background_story": None,
 "style": "realistic",
 "category": "portrait",
 "style_prompt": None,
 "additional_prompts": ["studio lighting"],
 },
)

 assert "Virtual IP Character:" in prompt
 assert "Quality:" in prompt
 assert "Constraints:" in prompt
 assert "no watermark" in prompt.lower()
 assert "no collage" in prompt.lower()


def test_virtual_ip_image_variant_prompt_template_renders():
 prompt = prompt_manager.render_prompt(
 "virtual_ip_image_variant",
 {
 "character_name": "Ce Shi Jue Se",
 "variant_prompt": "back-view shot, Quan Shen Zhao, keep Tong Yi Ren Wu Te Zheng",
 "character_description": "Duan Fa, Hei Kuang Yan Jing, Shen Xing Qing Shou, Ji Ke Qi Zhi",
 "background_story": None,
 "style": "realistic",
 "category": "portrait",
 "style_prompt": None,
 "base_prompt": None,
 },
)

 assert "Virtual IP Variant:" in prompt
 assert "Variant Instructions:" in prompt
 assert "no watermark" in prompt.lower()


def test_environment_image_prompt_template_renders_constraints():
 prompt = prompt_manager.render_prompt(
 "environment_image",
 {
 "environment_name": "future Ke Ji office",
 "category": "indoor",
 "tags": "science fiction, office, future",
 "description": "Xuan Fu Ping Mu, Bo Li Ge Duan, Leng Se Diao Deng Guang",
 "prompt": "Leng Se Diao science fiction office, Bo Li Ge Duan Yu Xuan Fu screen",
 "additional_prompts": None,
 },
)

 assert "Environment:" in prompt
 assert "Constraints:" in prompt
 assert "Quality:" in prompt
 assert "no watermark" in prompt.lower()


def test_environment_image_variant_prompt_template_renders_instructions():
 prompt = prompt_manager.render_prompt(
 "environment_image_variant",
 {
 "environment_name": "future Ke Ji office",
 "category": "indoor",
 "tags": "science fiction, office, future",
 "description": "Xuan Fu Ping Mu, Bo Li Ge Duan, Leng Se Diao Deng Guang",
 "base_prompt": "Leng Se Diao science fiction office, Bo Li Ge Duan Yu Xuan Fu screen",
 "variant_prompt": "Gai Wei Ye Jing, increase Bo Li Fan She Yu Geng Qiang Dui Bi Du Deng Guang",
 },
)

 assert "Environment Variant:" in prompt
 assert "Variant Instructions:" in prompt
 assert "Constraints:" in prompt
 assert "no watermark" in prompt.lower()
 assert "no collage" in prompt.lower()


def test_storyboard_image_prompt_template_includes_quality_and_constraints():
 prompt = prompt_manager.render_prompt(
 "storyboard_image_prompt",
 {
 "base_prompt": "Ye Se Zhong De Cang Ku, Jing Bie: medium shot",
 "reference_notes": [{"type": "frame"}],
 },
)

 assert "Quality:" in prompt
 assert "Constraints:" in prompt
 assert "no watermark" in prompt.lower()
 assert "no readable text" in prompt.lower()
 assert "no split-screen" in prompt.lower()
 assert "no multiple faces" not in prompt.lower()


def test_prompt_template_audit_has_version_and_hash():
 audit = build_prompt_template_audit("virtual_ip_image")
 assert audit["resolved_template"] == "virtual_ip_image"
 assert audit["version"]
 assert isinstance(audit["sources_hash"], str)
 assert len(audit["sources_hash"]) == 64
