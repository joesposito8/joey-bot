"""
Tests for configuration data models.
"""

import pytest
from common.config.models import FieldConfig, SheetSchema, BudgetTierConfig, FullAgentConfig
from unittest.mock import Mock


class TestFieldConfig:
    
    def test_field_config_creation(self):
        """Test creating FieldConfig instances."""
        field = FieldConfig(
            name="Test_Field",
            type="user input", 
            description="Test description",
            column_index=3
        )
        
        assert field.name == "Test_Field"
        assert field.type == "user input"
        assert field.description == "Test description"
        assert field.column_index == 3


class TestSheetSchema:
    
    def test_schema_creation(self, sample_field_configs):
        """Test creating SheetSchema with input and output fields."""
        schema = SheetSchema(
            input_fields=sample_field_configs['input'],
            output_fields=sample_field_configs['output']
        )
        
        assert len(schema.input_fields) == 2
        assert len(schema.output_fields) == 2
        assert schema.input_fields[0].name == "Idea_Overview"
        assert schema.output_fields[0].name == "Novelty_Rating"
    
    def test_validate_input_valid(self, sample_field_configs):
        """Test input validation with valid user input."""
        schema = SheetSchema(
            input_fields=sample_field_configs['input'],
            output_fields=sample_field_configs['output']
        )
        
        valid_input = {
            "Idea_Overview": "Test idea",
            "Deliverable": "Test deliverable"
        }
        
        assert schema.validate_input(valid_input) == True
    
    def test_validate_input_missing_fields(self, sample_field_configs):
        """Test input validation with missing required fields."""
        schema = SheetSchema(
            input_fields=sample_field_configs['input'],
            output_fields=sample_field_configs['output']
        )
        
        invalid_input = {
            "Idea_Overview": "Test idea"
            # Missing Deliverable
        }
        
        assert schema.validate_input(invalid_input) == False
    
    def test_get_header_row(self, sample_field_configs):
        """Test generating header row for Google Sheets."""
        schema = SheetSchema(
            input_fields=sample_field_configs['input'],
            output_fields=sample_field_configs['output']
        )
        
        headers = schema.get_header_row()
        
        # Should start with standard columns
        assert headers[0] == "ID"
        assert headers[1] == "Time"
        
        # Should include all input fields
        assert "Idea_Overview" in headers
        assert "Deliverable" in headers
        
        # Should include all output fields
        assert "Novelty_Rating" in headers
        assert "Analysis_Result" in headers
        
        # Total should be 6 (ID + Time + 2 input + 2 output)
        assert len(headers) == 6


class TestBudgetTierConfig:
    
    def test_budget_tier_creation(self):
        """Test creating BudgetTierConfig instances."""
        tier = BudgetTierConfig(
            name="test_tier",
            price=2.50,
            calls=3,
            description="Test tier description"
        )
        
        assert tier.name == "test_tier"
        assert tier.price == 2.50
        assert tier.calls == 3
        assert tier.description == "Test tier description"


class TestFullAgentConfig:
    
    def test_full_config_creation(self):
        """Test creating FullAgentConfig with mocked dependencies."""
        mock_definition = Mock()
        mock_schema = Mock()
        
        config = FullAgentConfig(mock_definition, mock_schema)
        
        assert config.definition == mock_definition
        assert config.schema == mock_schema
    
    def test_generate_instructions_integration(self, sample_field_configs, sample_budget_tiers):
        """Test instruction generation with real data structures."""
        from common.config.models import AgentDefinition, SheetSchema
        
        # Create real schema
        schema = SheetSchema(
            input_fields=sample_field_configs['input'],
            output_fields=sample_field_configs['output']
        )
        
        # Mock definition with necessary attributes
        mock_definition = Mock()
        mock_definition.name = "Test Agent"
        
        config = FullAgentConfig(mock_definition, schema)
        
        instructions = config.generate_instructions()
        
        # Verify content
        assert "Test Agent" in instructions
        assert "Idea_Overview" in instructions
        assert "Brief desc" in instructions