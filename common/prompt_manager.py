"""Prompt and model configuration manager for Universal AI Agent Platform."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from common.http_utils import is_testing_mode


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
            model_type: Type of model ('architecture_planning', 'analysis', 'synthesis')
            
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
    
    
    def format_synthesis_call_prompt(
        self,
        research_results: list,  # List of ResearchOutput objects
        user_input: dict,       # Original user input
        agent_personality: str, # Agent starter prompt
        output_fields: list     # List of FieldConfig objects from agent schema
    ) -> str:
        """Format universal synthesis call prompt with ResearchOutput list and Jinja2.
        
        Args:
            research_results: List of ResearchOutput objects from research phase
            user_input: Original user input dictionary
            agent_personality: Agent's starter prompt/personality
            output_fields: List of FieldConfig objects with .name, .description, .type
            
        Returns:
            Formatted synthesis call prompt with Jinja2 template rendered
        """
        from jinja2 import Template
        
        template_str = self.get_prompt_template('synthesis_call')
        
        # Generate JSON schema structure
        json_fields = []
        field_definitions = []
        
        for field in output_fields:
            json_fields.append(f'  "{field.name}": "string"')
            field_definitions.append(f"- **{field.name}**: {field.description}")
        
        json_schema = "{\n" + ",\n".join(json_fields) + "\n}"
        field_definitions_str = "\n".join(field_definitions)
        
        # Create Jinja2 template and render with ResearchOutput objects
        jinja_template = Template(template_str)
        
        return jinja_template.render(
            agent_personality=agent_personality,
            research_results=research_results,
            user_input=user_input,
            json_schema=json_schema,
            field_definitions=field_definitions_str
        )
    
    def format_research_planning_prompt(
        self,
        agent_personality: str,
        user_input: Dict[str, Any],
        num_topics: int
    ) -> str:
        """Format the research planning prompt with specific parameters.
        
        Args:
            agent_personality: Agent's starter prompt/personality
            user_input: User's input data
            num_topics: Number of research topics to generate
            
        Returns:
            Formatted research planning prompt
        """
        template = self.get_prompt_template('research_planning')
        
        # Format user input summary
        user_input_summary = "\n".join([f"**{key}**: {value}" for key, value in user_input.items()])
        
        return template.format(
            agent_personality=agent_personality,
            user_input_summary=user_input_summary,
            num_topics=num_topics
        )
    
    def format_research_call_prompt(
        self,
        starter_prompt: str,
        research_topic: str,
        user_input: Dict[str, Any],
        json_format_instructions: str
    ) -> str:
        """Format the research call prompt with specific parameters.
        
        Args:
            starter_prompt: Agent's starter prompt/personality
            research_topic: Specific research topic to investigate
            user_input: User's input data
            json_format_instructions: JSON format instructions from parser
            
        Returns:
            Formatted research call prompt
        """
        template = self.get_prompt_template('research_call')
        
        # Format user input generically
        formatted_user_input = "\n".join([f"**{key}**: {value}" for key, value in user_input.items()])
        
        return template.format(
            starter_prompt=starter_prompt,
            research_topic=research_topic,
            formatted_user_input=formatted_user_input,
            json_format_instructions=json_format_instructions
        )
    
    def format_user_instructions_prompt(
        self,
        agent_name: str,
        input_fields: list  # List of FieldConfig objects
    ) -> str:
        """Format the user instructions prompt with field descriptions.
        
        Args:
            agent_name: Human-readable name of the agent
            input_fields: List of FieldConfig objects with .name and .description
            
        Returns:
            Formatted user instructions with field descriptions and better formatting
        """
        from jinja2 import Template
        import json
        
        template_str = self.get_prompt_template('user_instructions')
        
        # Create field names JSON for API calls
        field_names = [field.name for field in input_fields]
        field_names_json = json.dumps({name: "user_provided_value" for name in field_names}, indent=2)
        
        # Create Jinja2 template and render
        jinja_template = Template(template_str)
        
        return jinja_template.render(
            agent_name=agent_name,
            input_fields=input_fields,
            field_names_json=field_names_json
        )


# Global instance
prompt_manager = PromptManager()