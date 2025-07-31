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


@dataclass
class BudgetTierConfig:
    """Budget tier configuration for agent."""

    name: str  # "basic", "standard", "premium"
    price: float  # Price in USD
    calls: int  # Number of OpenAI calls
    description: str  # Human-readable description
    deliverables: List[str] = None  # Optional list of deliverables

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetTierConfig':
        """Create BudgetTierConfig from dictionary data."""
        return cls(
            name=data['name'],
            price=float(data['price']),
            calls=int(data['calls']),
            description=data['description'],
            deliverables=data.get('deliverables', []),
        )

    def __post_init__(self):
        """Set default empty deliverables if None."""
        if self.deliverables is None:
            self.deliverables = []


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
        # List all required fields with descriptions and exact field names
        field_descriptions = []
        field_names = []
        for field in self.schema.input_fields:
            field_descriptions.append(f"- **{field.name}**: {field.description}")
            field_names.append(field.name)

        return f"""You are helping a user with {self.definition.name.lower()} analysis. 

Your task is to collect ALL of the following information from the user, one field at a time:

{chr(10).join(field_descriptions)}

COLLECTION PROCESS:
1. Ask for each field in order, explaining what information you need based on the field description
2. When the user provides input, repeat it back and ask for confirmation  
3. If they confirm, move to the next field
4. If they want to change it, ask for the information again
5. Continue until you have collected ALL fields listed above

IMPORTANT: Once all fields are collected, when you call the get_pricepoints endpoint, you MUST use these exact field names as keys in the user_input object:
{', '.join([f'"{name}"' for name in field_names])}

Begin by asking for the first field."""

    def generate_analysis_prompt(self, user_input: Dict) -> str:
        """Generate complete analysis prompt = starter + schema + input."""

        # Format user input with descriptions
        input_section = []
        for field in self.schema.input_fields:
            value = user_input.get(field.name, "")
            input_section.append(f"**{field.name}** ({field.description}): {value}")

        # Build output schema
        output_schema = {
            field.name: field.description for field in self.schema.output_fields
        }

        return f"""
{self.definition.starter_prompt}

Here is the information provided:
{chr(10).join(input_section)}

Provide your analysis in exactly this JSON format:
{json.dumps(output_schema, indent=2)}
"""

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

        # Fall back to universal platform model
        if self.universal_config and 'models' in self.universal_config:
            return self.universal_config['models'].get(model_type, 'gpt-4o-mini')

        return 'gpt-4o-mini'  # Final fallback

    def get_budget_tiers(self) -> List[BudgetTierConfig]:
        """Get universal budget tiers for all agents."""
        if not self.universal_config or 'platform' not in self.universal_config:
            return []

        platform_config = self.universal_config['platform']
        if 'budget_tiers' not in platform_config:
            return []

        tiers = []
        for tier_data in platform_config['budget_tiers']:
            tiers.append(
                BudgetTierConfig(
                    name=tier_data['name'],
                    price=float(tier_data['price']),
                    calls=int(tier_data['calls']),
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
