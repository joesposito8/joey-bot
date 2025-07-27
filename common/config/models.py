"""
Data models for the Universal AI Agent Platform configuration system.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class FieldConfig:
    """Individual field definition from Google Sheet schema."""
    name: str          # Row 3: Column name (e.g., "Idea_Overview")
    type: str          # Row 1: "user input" or "bot output"  
    description: str   # Row 2: Field description for prompts
    column_index: int  # Which column in sheet


@dataclass  
class SheetSchema:
    """Dynamic schema parsed from Google Sheet rows 1-3."""
    input_fields: List[FieldConfig]      # Fields user must provide
    output_fields: List[FieldConfig]     # Fields agent will generate
    
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
    name: str           # "basic", "standard", "premium"
    price: float        # Price in USD
    calls: int          # Number of OpenAI calls
    description: str    # Human-readable description
    deliverables: List[str] = None  # Optional list of deliverables
    
    def __post_init__(self):
        """Set default empty deliverables if None."""
        if self.deliverables is None:
            self.deliverables = []


@dataclass
class AgentDefinition:
    """Static agent configuration from YAML file."""
    agent_id: str                        # URL-safe identifier
    name: str                            # Human-readable name
    sheet_url: str                       # Google Sheet containing schema + data
    starter_prompt: str                  # Core agent expertise/personality
    budget_tiers: List[BudgetTierConfig] # Available pricing options
    
    @classmethod
    def from_yaml(cls, yaml_path):
        """Load agent definition from YAML file."""
        from .agent_definition import load_agent_definition
        return load_agent_definition(yaml_path)
    
    @classmethod  
    def from_dict(cls, data: dict) -> 'AgentDefinition':
        """Create AgentDefinition from dictionary data."""
        from .agent_definition import ValidationError
        
        # Parse budget tiers with validation
        budget_tiers = []
        for tier in data.get('budget_tiers', []):
            try:
                budget_tiers.append(BudgetTierConfig(
                    name=tier.get('name', ''),
                    price=float(tier.get('price', 0)),
                    calls=int(tier.get('calls', 1)),
                    description=tier.get('description', ''),
                    deliverables=tier.get('deliverables', [])
                ))
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid budget tier configuration: {str(e)}")
        
        return cls(
            agent_id=data['agent_id'],
            name=data['name'],
            sheet_url=data['sheet_url'],
            starter_prompt=data['starter_prompt'],
            budget_tiers=budget_tiers
        )


@dataclass
class FullAgentConfig:
    """Complete agent = static definition + dynamic schema."""
    definition: AgentDefinition
    schema: SheetSchema
    
    def generate_instructions(self) -> str:
        """Generate user instructions from schema."""
        input_descriptions = [f"- **{field.name}**: {field.description}" 
                            for field in self.schema.input_fields]
        return f"""
# {self.definition.name}

Please provide the following information:
{chr(10).join(input_descriptions)}
"""
    
    def generate_analysis_prompt(self, user_input: Dict) -> str:
        """Generate complete analysis prompt = starter + schema + input."""
        
        # Format user input with descriptions
        input_section = []
        for field in self.schema.input_fields:
            value = user_input.get(field.name, "")
            input_section.append(f"**{field.name}** ({field.description}): {value}")
        
        # Build output schema
        output_schema = {field.name: field.description 
                        for field in self.schema.output_fields}
        
        return f"""
{self.definition.starter_prompt}

Here is the information provided:
{chr(10).join(input_section)}

Provide your analysis in exactly this JSON format:
{json.dumps(output_schema, indent=2)}
"""
    
    @classmethod
    def from_definition(cls, definition: AgentDefinition, sheets_client=None):
        """Create FullAgentConfig from definition and sheet URL."""
        from .sheet_schema_reader import SheetSchemaReader
        
        # Get sheets client if not provided
        if sheets_client is None:
            from common import get_google_sheets_client
            sheets_client = get_google_sheets_client()
        
        reader = SheetSchemaReader(sheets_client)
        schema = reader.parse_sheet_schema(definition.sheet_url)
        return cls(definition, schema)
