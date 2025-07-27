"""
Agent definition loader for YAML configuration files.
"""

import re
import yaml
from pathlib import Path
from typing import List
from .models import AgentDefinition


class ValidationError(Exception):
    """Raised when agent definition validation fails."""
    pass


def _validate_agent_id(agent_id: str) -> None:
    """Validate that agent_id is URL-safe."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', agent_id):
        raise ValidationError("agent_id must be URL-safe (alphanumeric, underscores, hyphens only)")


def _validate_required_fields(data: dict, required_fields: List[str]) -> None:
    """Validate that all required fields are present."""
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def load_agent_definition(yaml_path: Path) -> AgentDefinition:
    """
    Load agent definition from YAML file.
    
    Args:
        yaml_path: Path to YAML configuration file
        
    Returns:
        AgentDefinition instance
        
    Raises:
        ValidationError: If YAML format is invalid or missing required fields
    """
    if not yaml_path.exists():
        raise ValidationError(f"Agent definition file not found: {yaml_path}")
    
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML syntax: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Cannot read file {yaml_path}: {str(e)}")
    
    if not isinstance(data, dict):
        raise ValidationError("YAML file must contain a dictionary")
    
    # Validate required fields
    required_fields = ['agent_id', 'name', 'sheet_url', 'starter_prompt']
    _validate_required_fields(data, required_fields)
    
    # Validate agent_id format
    _validate_agent_id(data['agent_id'])
    
    # Budget tier validation happens in AgentDefinition.from_dict()
    return AgentDefinition.from_dict(data)
