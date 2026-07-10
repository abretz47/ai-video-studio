from app.api.v1 import ai_providers, ai_text_generation, voice
from app.api.v1.endpoints import (
    admin,
    auth,
    diagnostic,
    episodes,
    image_gen_profiles,
    migrations,
    production_canvas,
    prompts,
    scoring,
    scripts,
    stories,
    story_structure,
    styles,
    task_control,
    tasks,
    timeline_clip_tasks,
    timeline_keyframes,
    timeline_resolved_videos,
    timelines,
    virtual_ip,
    virtual_ip_images,
    virtual_ip_voice_samples,
    workbench,
)
from fastapi import APIRouter

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Administrator routes
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Virtual IP routes
api_router.include_router(virtual_ip.router, tags=["virtual-ips"])
api_router.include_router(
    virtual_ip_images.router, prefix="/virtual-ips", tags=["virtual-ip-images"]
)
api_router.include_router(
    virtual_ip_voice_samples.router, prefix="/virtual-ips", tags=["virtual-ips"]
)

# Script routes
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(episodes.router, prefix="/episodes", tags=["episodes"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(
    story_structure.router, prefix="/story-structure", tags=["story-structure"]
)
api_router.include_router(timelines.router, tags=["timelines"])
api_router.include_router(timeline_keyframes.router, tags=["timelines"])
api_router.include_router(timeline_clip_tasks.router, tags=["timelines"])
api_router.include_router(timeline_resolved_videos.router, tags=["timelines"])
api_router.include_router(task_control.router, tags=["tasks"])

# Database migration routes
api_router.include_router(migrations.router, prefix="/migrations", tags=["migrations"])

# Prompt management routes
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])

# Image generation profiles (backend is the single source of truth)
api_router.include_router(
    image_gen_profiles.router, prefix="/image-gen", tags=["image-gen"]
)

# AI service provider routes
api_router.include_router(
    ai_text_generation.router, prefix="/ai", tags=["ai-providers"]
)
api_router.include_router(ai_providers.router, prefix="/ai", tags=["ai-providers"])
# Voice/music routes
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])

# Style schema / presets (backend is the single source of truth)
api_router.include_router(styles.router, prefix="/styles", tags=["styles"])

# Diagnostic routes
api_router.include_router(diagnostic.router, prefix="/diagnostic", tags=["diagnostic"])

# Task routes
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Workspace aggregation routes
api_router.include_router(workbench.router, prefix="/workbench", tags=["workbench"])
api_router.include_router(
    production_canvas.router,
    prefix="/production-canvas",
    tags=["production-canvas"],
)

# Script scoring and traffic-sheet routes
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
