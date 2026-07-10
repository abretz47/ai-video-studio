"""Prompt manager: load, manage, and render AI task prompt templates."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from app.prompts.template_resolver import resolve_template_name
from jinja2 import Environment, FileSystemLoader, Template, meta

logger = logging.getLogger(__name__)


class PromptManager:
    """Prompt manager."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """Initialize the prompt manager."""
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(__file__), "templates")

        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.jinja_env.filters["tojson"] = lambda value: json.dumps(
            value, ensure_ascii=False
        )

        self._template_cache: Dict[str, Template] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

    def load_template(self, template_name: str) -> Template:
        """Load a prompt template."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        try:
            template = self.jinja_env.get_template(f"{template_name}.txt")
        except Exception as exc:
            logger.error("Failed to load template %s: %s", template_name, exc)
            raise ValueError(f"Template {template_name} not found or invalid") from exc

        self._template_cache[template_name] = template
        return template

    def load_metadata(self, template_name: str) -> Dict[str, Any]:
        """Load template metadata."""
        if template_name in self._metadata_cache:
            return self._metadata_cache[template_name]

        metadata_file = self.prompts_dir / f"{template_name}.yaml"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f) or {}
                self._metadata_cache[template_name] = metadata
                return metadata
            except Exception as exc:
                logger.warning(
                    "Failed to load metadata for %s: %s", template_name, exc
                )

        return {}

    def render_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a prompt."""
        try:
            resolved_name = resolve_template_name(
                template_name, variables, self.prompts_dir
            )
            template = self.load_template(resolved_name)
            return template.render(**variables)
        except Exception as exc:
            logger.error("Failed to render template %s: %s", template_name, exc)
            raise ValueError(f"Failed to render template {template_name}: {exc}") from exc

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get template metadata and variable information."""
        metadata = self.load_metadata(template_name)
        variable_names: List[str] = []

        template_file = self.prompts_dir / f"{template_name}.txt"
        if template_file.exists():
            try:
                source = template_file.read_text(encoding="utf-8")
                parsed = self.jinja_env.parse(source)
                variable_names = sorted(meta.find_undeclared_variables(parsed))
            except Exception:
                variable_names = []

        return {
            "name": template_name,
            "metadata": metadata,
            "variables": variable_names,
            "description": metadata.get("description", ""),
            "category": metadata.get("category", "general"),
            "version": metadata.get("version", "1.0"),
            "author": metadata.get("author", ""),
            "created_at": metadata.get("created_at", ""),
            "updated_at": metadata.get("updated_at", ""),
        }

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available templates."""
        templates: List[Dict[str, Any]] = []
        for template_file in self.prompts_dir.glob("*.txt"):
            template_name = template_file.stem
            try:
                info = self.get_template_info(template_name)
                if category is None or info.get("category") == category:
                    templates.append(info)
            except Exception as exc:
                logger.warning("Failed to get info for template %s: %s", template_name, exc)

        return sorted(templates, key=lambda item: item["name"])

    def get_categories(self) -> List[str]:
        """Get all template categories."""
        categories = {template.get("category", "general") for template in self.list_templates()}
        return sorted(categories)

    def validate_template(
        self, template_name: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate template variables."""
        resolved_name = resolve_template_name(template_name, variables, self.prompts_dir)
        info = self.get_template_info(resolved_name)
        required_vars = info["variables"]
        metadata = info["metadata"]
        required_vars_config = metadata.get("variables", {})

        result = {
            "valid": True,
            "missing_vars": [],
            "extra_vars": [],
            "type_errors": [],
            "validation_errors": [],
        }

        for var_name in required_vars:
            var_config = required_vars_config.get(var_name, {})
            if var_name not in variables and var_config.get("required", True):
                result["missing_vars"].append(var_name)
                result["valid"] = False

        for var_name in variables:
            if var_name not in required_vars:
                result["extra_vars"].append(var_name)

        for var_name, var_value in variables.items():
            var_config = required_vars_config.get(var_name, {})
            expected_type = var_config.get("type")
            if expected_type == "string" and not isinstance(var_value, str):
                result["type_errors"].append(f"{var_name} should be string")
                result["valid"] = False
            elif expected_type == "number" and not isinstance(var_value, (int, float)):
                result["type_errors"].append(f"{var_name} should be number")
                result["valid"] = False
            elif expected_type == "list" and not isinstance(var_value, list):
                result["type_errors"].append(f"{var_name} should be list")
                result["valid"] = False
            elif expected_type == "dict" and not isinstance(var_value, dict):
                result["type_errors"].append(f"{var_name} should be dict")
                result["valid"] = False

            if isinstance(var_value, str):
                min_length = var_config.get("min_length")
                max_length = var_config.get("max_length")
                if min_length is not None and len(var_value) < min_length:
                    result["validation_errors"].append(f"{var_name} too short")
                    result["valid"] = False
                if max_length is not None and len(var_value) > max_length:
                    result["validation_errors"].append(f"{var_name} too long")
                    result["valid"] = False

        return result

    def create_template(
        self, template_name: str, content: str, metadata: Dict[str, Any]
    ) -> bool:
        """Create a new template file."""
        try:
            template_file = self.prompts_dir / f"{template_name}.txt"
            template_file.write_text(content, encoding="utf-8")

            metadata_file = self.prompts_dir / f"{template_name}.yaml"
            with open(metadata_file, "w", encoding="utf-8") as f:
                yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)

            self._template_cache.pop(template_name, None)
            self._metadata_cache.pop(template_name, None)
            return True
        except Exception as exc:
            logger.error("Failed to create template %s: %s", template_name, exc)
            return False


prompt_manager = PromptManager()
