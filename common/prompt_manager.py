"""Prompt and model configuration manager for Universal AI Agent Platform."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class PromptManager:
    """Manages prompts and model configurations for the platform."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self._common_config = None
        self._config_path = None
        
    def _load_common_config(self) -> Dict[str, Any]:
        """Load common prompts configuration."""
        if self._common_config is None:
            # Load platform configuration
            current_path = Path(__file__).parent
            config_path = current_path / 'platform.yaml'
            
            if not config_path.exists():
                raise ValueError(f"Platform configuration not found at: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self._common_config = yaml.safe_load(f)
                self._config_path = config_path
            
            logging.info(f"Loaded common prompts config from: {config_path}")
        
        return self._common_config
    
    def get_model(self, model_type: str) -> str:
        """Get model name for a specific function.
        
        Args:
            model_type: Type of model ('architecture_planning', 'user_interaction')
            
        Returns:
            Model name string
        """
        config = self._load_common_config()
        platform_config = config.get('platform', {})
        models = platform_config.get('models', {})
        
        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(models.keys())}")
        
        return models[model_type]
    
    def get_prompt_template(self, prompt_name: str) -> str:
        """Get a common prompt template.
        
        Args:
            prompt_name: Name of the prompt template
            
        Returns:
            Prompt template string
        """
        config = self._load_common_config()
        platform_config = config.get('platform', {})
        prompts = platform_config.get('prompts', {})
        
        if prompt_name not in prompts:
            raise ValueError(f"Unknown prompt: {prompt_name}. Available: {list(prompts.keys())}")
        
        return prompts[prompt_name]
    
    
    def format_architecture_planning_prompt(
        self, 
        available_calls: int,
        model: str,
        original_prompt: str,
        user_input: Dict[str, Any],
        output_fields: list
    ) -> str:
        """Format the architecture planning prompt with specific parameters.
        
        Args:
            available_calls: Number of API calls available
            model: Model being used for analysis
            original_prompt: The analysis prompt to execute
            user_input: User's input data
            output_fields: List of output field names
            
        Returns:
            Formatted architecture planning prompt
        """
        template = self.get_prompt_template('architecture_planning')
        
        # Format user input summary
        user_input_summary = "\\n".join([f"{key}: {value}" for key, value in user_input.items()])
        
        # Format output fields list
        output_fields_str = ", ".join(output_fields)
        
        return template.format(
            available_calls=available_calls,
            model=model,
            original_prompt=original_prompt,
            user_input_summary=user_input_summary,
            output_fields=output_fields_str
        )
    
    def format_analysis_call_prompt(
        self,
        starter_prompt: str,
        call_purpose: str,
        user_input: Dict[str, Any],
        specific_instructions: str = ""
    ) -> str:
        """Format universal analysis call prompt.
        
        Args:
            starter_prompt: Agent-specific starter prompt
            call_purpose: What this call should focus on
            user_input: User's input data
            specific_instructions: Additional instructions for this call
            
        Returns:
            Formatted analysis call prompt
        """
        template = self.get_prompt_template('analysis_call')
        
        # Format user input generically
        formatted_user_input = "\\n".join([f"**{key}**: {value}" for key, value in user_input.items()])
        
        return template.format(
            starter_prompt=starter_prompt,
            call_purpose=call_purpose,
            formatted_user_input=formatted_user_input,
            specific_instructions=specific_instructions
        )
    
    def format_synthesis_call_prompt(
        self,
        previous_findings: str,
        output_fields: list  # List of FieldConfig objects from agent schema
    ) -> str:
        """Format universal synthesis call prompt with dynamic schema.
        
        Args:
            previous_findings: Results from previous analysis calls
            output_fields: List of FieldConfig objects with .name, .description, .type
            
        Returns:
            Formatted synthesis call prompt with JSON schema and field definitions
        """
        template = self.get_prompt_template('synthesis_call')
        
        # Generate JSON schema structure
        json_fields = []
        field_definitions = []
        
        for field in output_fields:
            json_fields.append(f'  "{field.name}": "string"')
            field_definitions.append(f"- **{field.name}**: {field.description}")
        
        json_schema = "{\n" + ",\n".join(json_fields) + "\n}"
        field_definitions_str = "\n".join(field_definitions)
        
        return template.format(
            previous_findings=previous_findings,
            json_schema=json_schema,
            field_definitions=field_definitions_str
        )
    
    


# Global instance
prompt_manager = PromptManager()