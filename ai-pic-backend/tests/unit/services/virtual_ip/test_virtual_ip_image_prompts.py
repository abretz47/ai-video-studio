import pytest
from app.services.virtual_ip.virtual_ip_image_prompts import (
    render_virtual_ip_image_variant_prompt,
)


@pytest.mark.unit
def test_render_virtual_ip_image_variant_prompt_renders_template():
    rendered = render_virtual_ip_image_variant_prompt(
        character_name="Mia",
        character_description="22 years oldfemale，Yin Se Duan Fa，Hei Se Gao Ling Mao Yi",
        variant_prompt="back-view shot，full-body shot，keep consistent character features",
        style="realistic",
        category="portrait",
        style_prompt="studio lighting",
    )

    assert "Virtual IP Variant:" in rendered
    assert "Mia" in rendered
    assert "back-view shot" in rendered


@pytest.mark.unit
def test_render_virtual_ip_image_variant_prompt_falls_back_when_template_missing():
    fallback = render_virtual_ip_image_variant_prompt(
        character_name="Mia",
        variant_prompt="back-view shot",
        template_name="__missing_template__",
    )
    assert fallback == "back-view shot"
