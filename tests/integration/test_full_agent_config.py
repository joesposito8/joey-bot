"""
Integration tests for FullAgentConfig combining agent definitions and sheet schemas.
"""

import pytest
from unittest.mock import Mock, patch
from common.config.models import FullAgentConfig, AgentDefinition, SheetSchema, FieldConfig, BudgetTierConfig


class TestFullAgentConfig:
    
    @pytest.fixture
    def mock_agent_definition(self, sample_budget_tiers):
        """Mock agent definition for testing."""
        definition = Mock(spec=AgentDefinition)
        definition.agent_id = "test_agent"
        definition.name = "Test Agent"
        definition.sheet_url = "https://docs.google.com/test"
        definition.starter_prompt = "You are a test agent."
        definition.budget_tiers = sample_budget_tiers
        return definition
    
    @pytest.fixture
    def mock_sheet_schema(self, sample_field_configs):
        """Mock sheet schema with input/output fields."""
        schema = Mock(spec=SheetSchema)
        schema.input_fields = sample_field_configs['input']
        schema.output_fields = sample_field_configs['output']
        return schema
    
    def test_generate_instructions(self, mock_agent_definition, mock_sheet_schema):
        """Test generating user instructions from schema."""
        config = FullAgentConfig(mock_agent_definition, mock_sheet_schema)
        
        instructions = config.generate_instructions()
        
        # Verify instructions contain expected elements
        assert "Test Agent" in instructions
        assert "Idea_Overview" in instructions
        assert "Brief desc" in instructions
        assert "Deliverable" in instructions
        assert "What will be built" in instructions
    
    def test_generate_analysis_prompt(self, mock_agent_definition, mock_sheet_schema, sample_user_input):
        """Test generating complete analysis prompt."""
        config = FullAgentConfig(mock_agent_definition, mock_sheet_schema)
        
        prompt = config.generate_analysis_prompt(sample_user_input)
        
        # Verify prompt contains all expected elements
        assert "You are a test agent." in prompt
        assert "Mobile fitness app" in prompt
        assert "iOS/Android app with workout plans" in prompt
        assert "Novelty_Rating" in prompt  # Output schema field
        assert "Analysis_Result" in prompt  # Output schema field
    
    def test_generate_analysis_prompt_with_missing_input(self, mock_agent_definition, mock_sheet_schema):
        """Test prompt generation handles missing input fields gracefully."""
        incomplete_input = {
            "Idea_Overview": "Test idea"
            # Missing Deliverable field
        }
        
        config = FullAgentConfig(mock_agent_definition, mock_sheet_schema)
        
        prompt = config.generate_analysis_prompt(incomplete_input)
        
        # Should still generate prompt but with empty values for missing fields
        assert "Test idea" in prompt
        assert "Deliverable" in prompt  # Field name should still appear
    
    def test_create_from_definition_and_sheet(self, mock_agent_definition):
        """Test creating FullAgentConfig from definition and sheet URL."""
        # This should fail because we don't have a real sheets client
        # The current implementation tries to use None as sheets_client
        from common.config.sheet_schema_reader import SheetAccessError
        
        with pytest.raises(SheetAccessError, match="Cannot access sheet"):
            config = FullAgentConfig.from_definition(mock_agent_definition)
    
    def test_schema_validation_integration(self, mock_agent_definition, mock_sheet_schema, sample_user_input):
        """Test that schema validation works with full config."""
        config = FullAgentConfig(mock_agent_definition, mock_sheet_schema)
        
        # Mock schema validation
        mock_sheet_schema.validate_input.return_value = True
        
        # Should be able to validate input through schema
        is_valid = config.schema.validate_input(sample_user_input)
        assert is_valid == True
        
        # Verify validation was called
        mock_sheet_schema.validate_input.assert_called_once_with(sample_user_input)
    
    def test_budget_tier_integration(self, mock_agent_definition, mock_sheet_schema):
        """Test that budget tiers are accessible through full config."""
        config = FullAgentConfig(mock_agent_definition, mock_sheet_schema)
        
        # Should be able to access budget tiers from definition
        tiers = config.definition.budget_tiers
        assert len(tiers) == 3  # From sample_budget_tiers fixture
        
        tier_names = [tier.name for tier in tiers]
        assert "basic" in tier_names
        assert "standard" in tier_names
        assert "premium" in tier_names