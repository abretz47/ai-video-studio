"""Prompt manager: Jia Zai, management He Xuan Ran AI Ren Wu prompt text template."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from app.prompts.template_resolver import resolve_template_name
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class PromptManager:
 """Prompt manager"""

 def __init__(self, prompts_dir: Optional[str] = None):
 """
 Initialize the prompt manager

 Args:
 prompts_dir: Prompt file directory, defaults to the templates folder under the current directory
 """
 if prompts_dir is None:
 prompts_dir = os.path.join(os.path.dirname(__file__), "templates")

 self.prompts_dir = Path(prompts_dir)
 self.prompts_dir.mkdir(parents=True, exist_ok=True)

 # Chu Shi HuaJinja2environment
 self.jinja_env = Environment(
 loader=FileSystemLoader(str(self.prompts_dir)),
 trim_blocks=True,
 lstrip_blocks=True,
)
 # Override the default tojson filter to avoid \uXXXX Zhuan Yi, 
 # and consistently output UTF-8 text directly for readability.
 self.jinja_env.filters["tojson"] = lambda value: json.dumps(
 value, ensure_ascii=False
)

 # Cache loaded prompt templates
 self._template_cache: Dict[str, Template] = {}
 self._metadata_cache: Dict[str, Dict] = {}

 def load_template(self, template_name: str) -> Template:
 """
 Load a prompt template

 Args:
 template_name: Template name (without extension)

 Returns:
 Jinja2Mu Ban Dui Xiang
 """
 if template_name in self._template_cache:
 return self._template_cache[template_name]

 try:
 template_file = f"{template_name}.txt"
 template = self.jinja_env.get_template(template_file)
 self._template_cache[template_name] = template
 return template
 except Exception as e:
 logger.error(f"Failed to load template {template_name}: {e}")
 raise ValueError(f"Template {template_name} not found or invalid")

 def load_metadata(self, template_name: str) -> Dict[str, Any]:
 """
 Load template metadata

 Args:
 template_name: Mu Ban Ming Cheng

 Returns:
 Template metadata dictionary
 """
 if template_name in self._metadata_cache:
 return self._metadata_cache[template_name]

 metadata_file = self.prompts_dir / f"{template_name}.yaml"
 if metadata_file.exists():
 try:
 with open(metadata_file, "r", encoding="utf-8") as f:
 metadata = yaml.safe_load(f) or {}
 self._metadata_cache[template_name] = metadata
 return metadata
 except Exception as e:
 logger.warning(f"Failed to load metadata for {template_name}: {e}")

 return {}

 def render_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
 """
 Render prompt

 Args:
 template_name: Mu Ban Ming Cheng
 variables: Mu Ban Bian Liang

 Returns:
 Rendered prompt text
 """
 try:
 resolved_name = resolve_template_name(
 template_name, variables, self.prompts_dir
)
 template = self.load_template(resolved_name)
 return template.render(**variables)
 except Exception as e:
 logger.error(f"Failed to render template {template_name}: {e}")
 raise ValueError(f"Failed to render template {template_name}: {str(e)}")

 def get_template_info(self, template_name: str) -> Dict[str, Any]:
 """
 Get template information

 Args:
 template_name: Mu Ban Ming Cheng

 Returns:
 Dictionary containing template metadata and variable information
 """
 metadata = self.load_metadata(template_name)

 # Analyze variables in the template
 try:
 template = self.load_template(template_name)
 variables = list(
 template.environment.parse(template.source).find_all(
 lambda node: hasattr(node, "name")
)
)
 variable_names = list(
 set([var.name for var in variables if hasattr(var, "name")])
)
 except:
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
 """
 List all available templates

 Args:
 category: Optional category filter

 Returns:
 Template info list
 """
 templates = []

 for template_file in self.prompts_dir.glob("*.txt"):
 template_name = template_file.stem
 try:
 info = self.get_template_info(template_name)
 if category is None or info.get("category") == category:
 templates.append(info)
 except Exception as e:
 logger.warning(f"Failed to get info for template {template_name}: {e}")

 return sorted(templates, key=lambda x: x["name"])

 def get_categories(self) -> List[str]:
 """
 Get all template categories

 Returns:
 Category name list
 """
 categories = set()
 for template in self.list_templates():
 categories.add(template.get("category", "general"))
 return sorted(list(categories))

 def validate_template(
 self, template_name: str, variables: Dict[str, Any]
) -> Dict[str, Any]:
 """
 Validate template variables

 Args:
 template_name: Mu Ban Ming Cheng
 variables: Variables to validate

 Returns:
 Validation result
 """
 resolved_name = resolve_template_name(
 template_name, variables, self.prompts_dir
)
 info = self.get_template_info(resolved_name)
 required_vars = info["variables"]
 metadata = info["metadata"]

 result = {
 "valid": True,
 "missing_vars": [],
 "extra_vars": [],
 "type_errors": [],
 "validation_errors": [],
 }

 # Check required variables
 required_vars_config = metadata.get("variables", {})
 for var_name in required_vars:
 if var_name not in variables:
 var_config = required_vars_config.get(var_name, {})
 if var_config.get("required", True):
 result["missing_vars"].append(var_name)
 result["valid"] = False

 # check additional Bian Liang
 for var_name in variables:
 if var_name not in required_vars:
 result["extra_vars"].append(var_name)

 # check Bian Liang type He Zhi
 for var_name, var_value in variables.items():
 var_config = required_vars_config.get(var_name, {})

 # Lei Xing Jian Cha
 expected_type = var_config.get("type")
 if expected_type:
 if expected_type == "string" and not isinstance(var_value, str):
 result["type_errors"].append(f"{var_name} should be string")
 result["valid"] = False
 elif expected_type == "number" and not isinstance(
 var_value, (int, float)
):
 result["type_errors"].append(f"{var_name} should be number")
 result["valid"] = False
 elif expected_type == "list" and not isinstance(var_value, list):
 result["type_errors"].append(f"{var_name} should be list")
 result["valid"] = False
 elif expected_type == "dict" and not isinstance(var_value, dict):
 result["type_errors"].append(f"{var_name} should be dict")
 result["valid"] = False

 # Zhi Fan Wei check
 if "min_length" in var_config and isinstance(var_value, str):
 if len(var_value) < var_config["min_length"]:
 result["validation_errors"].append(f"{var_name} too short")
 result["valid"] = False

 if "max_length" in var_config and isinstance(var_value, str):
 if len(var_value) > var_config["max_length"]:
 result["validation_errors"].append(f"{var_name} too long")
 result["valid"] = False

 return result

 def create_template(
 self, template_name: str, content: str, metadata: Dict[str, Any]
) -> bool:
 """create new De template file."""
 try:
 # Xie Ru template file
 template_file = self.prompts_dir / f"{template_name}.txt"
 with open(template_file, "w", encoding="utf-8") as f:
 f.write(content)

 # Xie Ru Yuan Shu Ju Wen Jian
 metadata_file = self.prompts_dir / f"{template_name}.yaml"
 with open(metadata_file, "w", encoding="utf-8") as f:
 yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)

 # Qing Li Huan Cun
 if template_name in self._template_cache:
 del self._template_cache[template_name]
 if template_name in self._metadata_cache:
 del self._metadata_cache[template_name]

 return True
 except Exception as e:
 logger.error(f"Failed to create template {template_name}: {e}")
 return False


# Quan JuPrompt managerShi Li
prompt_manager = PromptManager()
