"""
Data models for the Universal AI Agent Platform configuration system.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import json
from ..errors import ValidationError


@dataclass
class FieldConfig:
    """Individual field definition from Google Sheet schema."""

    name: str  # Row 3: Column name (e.g., "Idea_Overview")
    type: str  # Row 1: "user input" or "bot output"
    description: str  # Row 2: Field description for prompts
    column_index: int  # Which column in sheet

    def __post_init__(self):
        """Validate field configuration."""
        if self.type not in ["user input", "bot output", "ID", "Time", "system"]:
            raise ValueError(f"Invalid field type '{self.type}'. Must be one of: user input, bot output, ID, Time, system")


@dataclass
class SheetSchema:
    """Dynamic schema parsed from Google Sheet rows 1-3."""

    input_fields: List[FieldConfig]  # Fields user must provide
    output_fields: List[FieldConfig]  # Fields agent will generate

    def validate_input(self, user_input: Dict[str, Any]) -> bool:
        """Validate that user input contains all required fields."""
        required_fields = {field.name for field in self.input_fields}
        provided_fields = set(user_input.keys())
        return required_fields.issubset(provided_fields)

    def get_header_row(self) -> List[str]:
        """Generate header row for Google Sheets."""
        headers = ["ID", "Time"]  # Standard columns

        # Add input fields
        for field in self.input_fields:
            headers.append(field.name)

        # Add output fields
        for field in self.output_fields:
            headers.append(field.name)

        return headers

    def generate_output_headers(self) -> List[str]:
        """Get output field names in order."""
        return [field.name for field in self.output_fields]


@dataclass
class BudgetTierConfig:
    """Budget tier configuration for agent."""

    name: str  # "basic", "standard", "premium"
    num_research_calls: int  # Number of research calls (planning/synthesis always 1 each)
    description: str  # Human-readable description
    deliverables: List[str] = None  # Optional list of deliverables

    def __post_init__(self):
        """Validate budget tier configuration."""
        if self.deliverables is None:
            self.deliverables = []
        if self.num_research_calls < 0:
            raise ValueError("Number of research calls must be non-negative")
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not self.description or len(self.description.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")

    def calculate_price(self, agent_config: 'FullAgentConfig') -> float:
        """Calculate dynamic price based on model costs and call structure."""
        # Model costs per call
        model_costs = {
            "o4-mini": 0.25,
            "o4-mini-deep-research": 1.00,
            "gpt-4o-mini": 0.05
        }
        
        # Get models from agent config
        planning_model = agent_config.get_model('planning')
        research_model = agent_config.get_model('research')
        synthesis_model = agent_config.get_model('synthesis')
        
        # Calculate total cost: 1 planning + N research + 1 synthesis
        planning_cost = model_costs.get(planning_model, 0.25)
        research_cost = model_costs.get(research_model, 1.00) * self.num_research_calls
        synthesis_cost = model_costs.get(synthesis_model, 0.25)
        
        return planning_cost + research_cost + synthesis_cost

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetTierConfig':
        """Create BudgetTierConfig from dictionary data."""
        return cls(
            name=data['name'],
            num_research_calls=int(data['num_research_calls']),
            description=data['description'],
            deliverables=data.get('deliverables', []),
        )


@dataclass
class AgentDefinition:
    """Static agent configuration from YAML file."""

    agent_id: str  # URL-safe identifier
    name: str  # Human-readable name
    sheet_url: str  # Google Sheet containing schema + data
    starter_prompt: str  # Core agent expertise/personality
    models: Dict[str, str] = (
        None  # Optional model overrides (uses platform defaults if None)
    )

    @classmethod
    def from_yaml(cls, yaml_path):
        """Load agent definition from YAML file."""
        from .agent_definition import load_agent_definition

        return load_agent_definition(yaml_path)

    @classmethod
    def from_dict(cls, data: dict) -> 'AgentDefinition':
        """Create AgentDefinition from dictionary data."""
        from .agent_definition import ValidationError

        return cls(
            agent_id=data['agent_id'],
            name=data['name'],
            sheet_url=data['sheet_url'],
            starter_prompt=data['starter_prompt'],
            models=data.get('models', {}),
        )


@dataclass
class FullAgentConfig:
    """Complete agent = static definition + dynamic schema + universal config."""

    definition: AgentDefinition
    schema: SheetSchema
    universal_config: Dict[str, Any] = None  # Universal prompts, models, budget_tiers

    @property
    def id(self) -> str:
        """Get agent ID from definition."""
        return self.definition.agent_id

    @property
    def starter_prompt(self) -> str:
        """Get agent starter prompt from definition."""
        return self.definition.starter_prompt

    @property
    def input_fields(self) -> List[FieldConfig]:
        """Get input field definitions from schema."""
        return self.schema.input_fields

    @property
    def output_fields(self) -> List[FieldConfig]:
        """Get output field definitions from schema."""
        return self.schema.output_fields

    def validate_input(self, user_input: Dict[str, Any]) -> None:
        """Validate input against schema requirements.

        Args:
            user_input: User's input data

        Raises:
            ValidationError: If validation fails
        """
        if not user_input:
            raise ValidationError("No input provided")

        # Use schema validation
        if not self.schema.validate_input(user_input):
            raise ValidationError("Missing required fields")

    def generate_instructions(self) -> str:
        """Generate instructions for the ChatGPT bot on how to collect user input."""
        from common.prompt_manager import prompt_manager
        
        return prompt_manager.format_user_instructions_prompt(
            agent_name=self.definition.name,
            input_fields=self.schema.input_fields
        )


    def get_universal_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get a universal setting from platform config.
        
        Args:
            setting_name: Name of the setting in universal_settings
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        if not self.universal_config or 'platform' not in self.universal_config:
            return default
            
        universal_settings = self.universal_config['platform'].get('universal_settings', {})
        return universal_settings.get(setting_name, default)

    def get_model(self, model_type: str) -> str:
        """Get model for a specific function, with agent overrides."""
        # Agent-specific override takes precedence
        if self.definition.models and model_type in self.definition.models:
            return self.definition.models[model_type]

        # Check universal platform model configuration
        if not self.universal_config or 'platform' not in self.universal_config:
            raise ValidationError(f"No platform configuration found in platform.yaml")
        
        platform_config = self.universal_config['platform']
        if 'models' not in platform_config:
            raise ValidationError(f"No models configuration found in platform.yaml")
            
        models = platform_config['models']
        if model_type not in models:
            available_models = list(models.keys())
            raise ValidationError(f"Unknown model type '{model_type}'. Available: {available_models}")
        
        return models[model_type]

    def get_budget_tiers(self) -> List[BudgetTierConfig]:
        """Get universal budget tiers for all agents."""
        if not self.universal_config or 'platform' not in self.universal_config:
            raise ValidationError("No platform configuration found - platform.yaml missing or corrupted")

        platform_config = self.universal_config['platform']
        if 'budget_tiers' not in platform_config:
            raise ValidationError("No budget_tiers configuration found in platform.yaml - pricing system requires budget tiers")

        tiers = []
        for tier_data in platform_config['budget_tiers']:
            tiers.append(
                BudgetTierConfig(
                    name=tier_data['name'],
                    num_research_calls=int(tier_data['num_research_calls']),
                    description=tier_data['description'],
                    deliverables=tier_data.get('deliverables', []),
                )
            )
        return tiers

    @classmethod
    def from_definition(cls, definition: AgentDefinition, sheets_client=None):
        """Create FullAgentConfig from definition and sheet URL."""
        from .sheet_schema_reader import SheetSchemaReader

        # Get sheets client if not provided
        if sheets_client is None:
            from common import get_google_sheets_client

            sheets_client = get_google_sheets_client()

        # Load universal configuration
        from common.prompt_manager import prompt_manager

        universal_config = prompt_manager._load_common_config()

        reader = SheetSchemaReader(sheets_client)
        schema = reader.parse_sheet_schema(definition.sheet_url)
        return cls(definition, schema, universal_config)
