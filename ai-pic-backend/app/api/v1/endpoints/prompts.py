"""
Prompt management API endpoints
"""

from typing import Any, Dict, List, Optional

from app.core.middleware import get_current_active_user
from app.models.user import User
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptCategory, PromptTemplate
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class PromptTemplateInfo(BaseModel):
    """Prompt template information"""

    name: str
    description: str
    category: str
    version: str
    author: str
    variables: List[str]
    created_at: str
    updated_at: str


class PromptRenderRequest(BaseModel):
    """Prompt render request"""

    template_name: str
    variables: Dict[str, Any]


class PromptRenderResponse(BaseModel):
    """Prompt render response"""

    rendered_prompt: str
    template_name: str
    validation_result: Dict[str, Any]


class PromptCreateRequest(BaseModel):
    """Create prompt template request"""

    template_name: str
    content: str
    metadata: Dict[str, Any]


@router.get("/templates", response_model=List[PromptTemplateInfo])
async def list_templates(
    category: Optional[str] = Query(None, description="Template category filter"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all available prompt templates"""
    try:
        templates = prompt_manager.list_templates(category)
        return [
            PromptTemplateInfo(
                name=template["name"],
                description=template["description"],
                category=template["category"],
                version=template["version"],
                author=template["author"],
                variables=template["variables"],
                created_at=template.get("created_at", ""),
                updated_at=template.get("updated_at", ""),
            )
            for template in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template list: {str(e)}")


@router.get("/categories")
async def list_categories(current_user: User = Depends(get_current_active_user)):
    """Get all template categories"""
    try:
        categories = prompt_manager.get_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category list: {str(e)}")


@router.get("/templates/{template_name}")
async def get_template_info(
    template_name: str, current_user: User = Depends(get_current_active_user)
):
    """Get details for the specified template"""
    try:
        info = prompt_manager.get_template_info(template_name)
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Template does not exist: {str(e)}")


@router.post("/render", response_model=PromptRenderResponse)
async def render_prompt(
    request: PromptRenderRequest, current_user: User = Depends(get_current_active_user)
):
    """Render prompt template"""
    try:
        # Validate template variables
        validation_result = prompt_manager.validate_template(
            request.template_name, request.variables
        )

        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, detail=f"Template variable validation failed: {validation_result}"
            )

        # Render prompt
        rendered_prompt = prompt_manager.render_prompt(
            request.template_name, request.variables
        )

        return PromptRenderResponse(
            rendered_prompt=rendered_prompt,
            template_name=request.template_name,
            validation_result=validation_result,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {str(e)}")


@router.post("/templates")
async def create_template(
    request: PromptCreateRequest, current_user: User = Depends(get_current_active_user)
):
    """Create a new prompt template"""
    try:
        success = prompt_manager.create_template(
            request.template_name, request.content, request.metadata
        )

        if success:
            return {
                "success": True,
                "message": f"Template {request.template_name} created successfully",
            }
        else:
            raise HTTPException(status_code=500, detail="Template creation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.post("/validate")
async def validate_template_variables(
    template_name: str,
    variables: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
):
    """Validate template variables"""
    try:
        validation_result = prompt_manager.validate_template(template_name, variables)
        return {"success": True, "data": validation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# Predefined prompt template enum endpoints
@router.get("/enums/templates")
async def get_template_enums():
    """Get all predefined template enums"""
    templates = [
        {
            "name": template.value,
            "display_name": template.name,
            "category": template.name.split("_")[0].lower(),
        }
        for template in PromptTemplate
    ]
    return {"success": True, "data": templates}


@router.get("/enums/categories")
async def get_category_enums():
    """Get all predefined category enums"""
    categories = [
        {"name": category.value, "display_name": category.name}
        for category in PromptCategory
    ]
    return {"success": True, "data": categories}


# Prompt generation APIs for specific workflows
@router.post("/generate/character")
async def generate_character_prompt(
    name: str,
    description: Optional[str] = None,
    age: Optional[str] = None,
    gender: Optional[str] = None,
    personality_traits: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Generate character creation prompt"""
    try:
        variables = {
            "name": name,
            "description": description,
            "age": age,
            "gender": gender,
            "personality_traits": personality_traits or [],
        }

        prompt = prompt_manager.render_prompt(
            PromptTemplate.VIRTUAL_IP_CREATION.value, variables
        )

        return {
            "success": True,
            "data": {
                "prompt": prompt,
                "template": PromptTemplate.VIRTUAL_IP_CREATION.value,
                "variables": variables,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate character prompt: {str(e)}")


@router.post("/generate/story")
async def generate_story_prompt(
    title: str,
    genre: str,
    characters: List[Dict[str, Any]],
    theme: Optional[str] = None,
    target_audience: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Generate story outline prompt"""
    try:
        variables = {
            "title": title,
            "genre": genre,
            "characters": characters,
            "theme": theme,
            "target_audience": target_audience,
        }

        prompt = prompt_manager.render_prompt(
            PromptTemplate.STORY_OUTLINE.value, variables
        )

        return {
            "success": True,
            "data": {
                "prompt": prompt,
                "template": PromptTemplate.STORY_OUTLINE.value,
                "variables": variables,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate story prompt: {str(e)}")


@router.post("/generate/image")
async def generate_image_prompt(
    character_name: str,
    style: str,
    category: str,
    character_description: Optional[str] = None,
    additional_prompts: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Generate imageGeneration prompt"""
    try:
        variables = {
            "character_name": character_name,
            "character_description": character_description,
            "style": style,
            "category": category,
            "additional_prompts": additional_prompts or [],
            "is_default": category == "portrait",
        }

        prompt = prompt_manager.render_prompt(
            PromptTemplate.IMAGE_GENERATION.value, variables
        )

        return {
            "success": True,
            "data": {
                "prompt": prompt,
                "template": PromptTemplate.IMAGE_GENERATION.value,
                "variables": variables,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image prompt: {str(e)}")
