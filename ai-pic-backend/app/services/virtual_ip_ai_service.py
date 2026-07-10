"""
Virtual IP AI Generation Service
Zhuan Men as Xu NiIPcreate Ti GongAISheng Cheng feature

Zhu Yi: 
- Bu Zai directly Yi Lai AsyncOpenAI, Er Shi Fu Yong unified AIService/AIServiceManager.
- text prompt Ci change to through prompt_manager + virtual_ip_creation template Guan Li.
"""

import time
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.services.ai_service import ai_service
from app.services.providers.deepseek_models import DEEPSEEK_V4_FLASH_MODEL
from app.services.virtual_ip.ai_prompt_helpers import (
    build_content_from_profile,
    generate_template_content,
    generate_template_style_prompt,
)
from app.utils.json_utils import extract_json_block

VIRTUAL_IP_CONTENT_FILL_PROVIDER = "deepseek"
VIRTUAL_IP_CONTENT_FILL_MODEL = DEEPSEEK_V4_FLASH_MODEL


class VirtualIPAIService:
    """Xu NiIP AISheng Cheng service"""

    def __init__(self):
        # Fu Yong Quan Ju AIService manager, keep model Xuan Ze and log unified
        self.ai_service = ai_service
        self.ai_manager = getattr(ai_service, "ai_manager", None)
        self.logger = get_logger(__name__)

    async def generate_complete_ip_with_details(
        self,
        name: str,
        basic_info: Optional[str] = None,
        style_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
 Gen Ju Ji Ben Xin Xi Sheng Cheng complete Xu NiIP, Bao Han detailed Sheng Cheng Xin Xi.

 Luo Ji: 
 - priority through prompt_manager + virtual_ip_creation template Sheng Cheng Jie Gou Hua JSON, then Ying She to description/background/Xiao Zhuan.
 - Dang AI manager not allowed Yong or parse failed when, fallback to local template Wen An.
        """
        temperature = 0.7
        start_time = time.time()

        # default Shi Yong local template Zuo Wei fallback
        content: Dict[str, Any] = generate_template_content(name, basic_info)
        prompts_used: List[str] = ["Template-based generation"]
        tokens_used = 0
        model_used = "template"
        steps: List[str] = []

        if self.ai_manager:
            try:
                steps.append("Zheng Zai Sheng Cheng Xu NiIPcomplete setting(description/background/Xiao Zhuan)...")
                profile, prompt, model_used, usage = (
                    await self._generate_profile_with_ai(
                        name=name,
                        basic_info=basic_info,
                        style_preference=style_preference,
                        temperature=temperature,
                    )
                )
                content = profile
                if prompt:
                    prompts_used = [f"Xu NiIPShe Ding: {prompt[:100]}..."]
                usage = usage or {}
                tokens_used = int(usage.get("total_tokens") or 0)
                steps.append("Sheng Cheng complete!")
            except Exception as e:
                # failed when Ji Lu and fallback to template
                self.logger.warning(
                    "VirtualIPAIService.generate_complete_ip_with_details Chu Cuo, Shi Yong template fallback: %s",
                    e,
                )
                steps.append("AI Sheng Cheng failed, Shi Yong template fallback")
        else:
            steps.append("AI manager not allowed Yong, Shi Yong template fallback")

        generation_details = {
            "model": model_used,
            "temperature": temperature,
            "prompts_used": prompts_used,
            "tokens_used": tokens_used,
            "generation_time": round(time.time() - start_time, 2),
            "steps": steps or ["Sheng Cheng complete!"],
        }

        return {
            "content": content,
            "generation_details": generation_details,
        }

    async def generate_complete_ip(
        self,
        name: str,
        basic_info: Optional[str] = None,
        style_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
 Gen Ju Ji Ben Xin Xi Sheng Cheng complete Xu NiIP(Jian Hua Ban, keep Xiang after Jian Rong)
        """
        result = await self.generate_complete_ip_with_details(
            name, basic_info, style_preference
        )
        return result["content"]

    async def generate_style_prompt(
        self,
        name: str,
        description: str,
        biography: str,
        image_category: str = "portrait",
    ) -> str:
        """
 Gen JuCharacter informationSheng Cheng Yong YuAIHui Hua style prompt Ci.
 priority through unified AI manager Sheng Cheng Zhong Wen prompt Ci, failed when fallback to local template.
        """
        if not self.ai_manager:
            return generate_template_style_prompt(name, description, image_category)

        prompt = prompt_manager.render_prompt(
            PromptTemplate.VIRTUAL_IP_STYLE_PROMPT.value,
            {
                "name": name,
                "description": description,
                "biography": biography,
                "image_category": image_category,
            },
        )

        try:
            response = await self.ai_manager.generate_text(
                prompt=prompt,
                temperature=0.7,
                model=VIRTUAL_IP_CONTENT_FILL_MODEL,
                prefer_provider=VIRTUAL_IP_CONTENT_FILL_PROVIDER,
                system_prompt=None,
                json_schema=None,
                stream=False,
            )
            text = ""
            if isinstance(response.data, str):
                text = response.data
            elif response.data is not None:
                text = str(response.data)
            text = (text or "").strip()
            if not text:
                return generate_template_style_prompt(name, description, image_category)
            return text
        except Exception as e:
            self.logger.warning(
                "VirtualIPAIService.generate_style_prompt failed, Shi Yong template fallback: %s",
                e,
            )
            return generate_template_style_prompt(name, description, image_category)

    async def _generate_profile_with_ai(
        self,
        name: str,
        basic_info: Optional[str],
        style_preference: Optional[str],
        temperature: float = 0.7,
    ) -> tuple[Dict[str, Any], Optional[str], str, Dict[str, Any]]:
        """
 Shi Yong prompt_manager + virtual_ip_creation template Sheng Cheng complete character setting, 
 and Ying She to description/background_story/biography San Duan Wen An.
        """
        variables: Dict[str, Any] = {
            "name": name,
            "description": basic_info,
            "age": None,
            "gender": None,
            "personality_traits": None,
            "style_preference": style_preference,
            "target_audience": None,
            "content_type": None,
        }

        prompt = prompt_manager.render_prompt(
            PromptTemplate.VIRTUAL_IP_CREATION.value,
            variables,
        )
        self.logger.info("VirtualIP Generation prompt: %s", prompt[:200])

        response = await self.ai_manager.generate_text(
            prompt=prompt,
            temperature=temperature,
            model=VIRTUAL_IP_CONTENT_FILL_MODEL,
            prefer_provider=VIRTUAL_IP_CONTENT_FILL_PROVIDER,
            system_prompt=None,
            json_schema=None,
            stream=False,
        )

        text = ""
        if isinstance(response.data, str):
            text = response.data
        elif response.data is not None:
            text = str(response.data)

        profile: Optional[Dict[str, Any]] = None
        if text:
            try:
                data = extract_json_block(text)
                if isinstance(data, dict):
                    profile = data
            except Exception as e:
                self.logger.warning(
                    "VirtualIPAIService._generate_profile_with_ai parseJSONfailed, Shi Yong template fallback: %s",
                    e,
                )

        if not profile:
            # Shi Yong template content fallback
            return (
                generate_template_content(name, basic_info),
                prompt,
                response.model or "unknown",
                response.usage or {},
            )

        content = build_content_from_profile(
            profile,
            name=name,
            basic_info=basic_info,
        )
        return content, prompt, response.model or "unknown", response.usage or {}


# Quan Ju instance
virtual_ip_ai_service = VirtualIPAIService()
