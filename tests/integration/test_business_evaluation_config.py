"""
Integration tests for business evaluation agent configuration system.
Tests the complete flow from YAML config + Google Sheets schema to prompt generation.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch

from common.config import AgentDefinition, FullAgentConfig, FieldConfig, SheetSchema
from common.config.sheet_schema_reader import SheetSchemaReader, SchemaValidationError, SheetAccessError


class TestBusinessEvaluationConfig:
    """Test business evaluation agent configuration."""
    
    def test_yaml_config_loading(self):
        """Test that business_evaluation.yaml loads correctly."""
        config_path = Path("agents/business_evaluation.yaml")
        assert config_path.exists(), "business_evaluation.yaml should exist"
        
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # Verify basic properties
        assert agent_def.agent_id == "business_evaluation"
        assert agent_def.name == "Business Idea Evaluator"
        assert "docs.google.com/spreadsheets" in agent_def.sheet_url
        assert len(agent_def.starter_prompt) > 1000  # Should be substantial prompt
        assert len(agent_def.budget_tiers) == 3  # basic, standard, premium
        
        # Verify budget tiers
        tier_names = [tier.name for tier in agent_def.budget_tiers]
        assert "basic" in tier_names
        assert "standard" in tier_names
        assert "premium" in tier_names
        
        # Verify tier pricing
        basic_tier = next(t for t in agent_def.budget_tiers if t.name == "basic")
        assert basic_tier.price == 1.0
        assert basic_tier.calls == 1


class TestSheetSchemaReader:
    """Test Google Sheets schema reading functionality."""
    
    def test_sheet_schema_parsing_with_mock_data(self):
        """Test schema parsing with mock Google Sheets data."""
        # Mock sheet data: Row 1 = types, Row 2 = descriptions, Row 3 = names
        mock_sheet_data = [
            ["ID", "Time", "User", "User", "User", "Bot", "Bot", "Bot"],
            ["ID", "Time", "Brief desc", "What will", "Why this", "How novel", "Detailed", "Overall"],
            ["ID", "Time", "Idea_Overview", "Deliverable", "Motivation", "Novelty_Rating", "Novelty_Rationale", "Overall_Rating"]
        ]
        
        # Mock sheets client
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        mock_worksheet.get_values.return_value = mock_sheet_data
        
        # Test schema parsing
        reader = SheetSchemaReader(mock_client)
        schema = reader.parse_sheet_schema("https://docs.google.com/spreadsheets/d/test123/")
        
        # Verify schema structure
        assert len(schema.input_fields) == 3
        assert len(schema.output_fields) == 3
        
        # Verify input fields
        input_names = [field.name for field in schema.input_fields]
        assert "Idea_Overview" in input_names
        assert "Deliverable" in input_names
        assert "Motivation" in input_names
        
        # Verify output fields
        output_names = [field.name for field in schema.output_fields]
        assert "Novelty_Rating" in output_names
        assert "Novelty_Rationale" in output_names
        assert "Overall_Rating" in output_names
        
        # Verify field properties
        idea_field = next(f for f in schema.input_fields if f.name == "Idea_Overview")
        assert idea_field.type == "user input"
        assert idea_field.description == "Brief desc"
        assert idea_field.column_index == 2
    
    def test_invalid_field_types(self):
        """Test error handling for invalid field types."""
        mock_sheet_data = [
            ["ID", "Time", "Invalid"],
            ["ID", "Time", "Description"],
            ["ID", "Time", "Column_Name"]
        ]
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        mock_worksheet.get_values.return_value = mock_sheet_data
        
        reader = SheetSchemaReader(mock_client)
        
        with pytest.raises(SchemaValidationError) as exc_info:
            reader.parse_sheet_schema("https://docs.google.com/spreadsheets/d/test123/")
        
        assert "Invalid field type 'Invalid'" in str(exc_info.value)
    
    def test_duplicate_column_names(self):
        """Test error handling for duplicate column names."""
        mock_sheet_data = [
            ["ID", "Time", "User", "User"],
            ["ID", "Time", "Desc1", "Desc2"],
            ["ID", "Time", "Same_Name", "Same_Name"]
        ]
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        mock_worksheet.get_values.return_value = mock_sheet_data
        
        reader = SheetSchemaReader(mock_client)
        
        with pytest.raises(SchemaValidationError) as exc_info:
            reader.parse_sheet_schema("https://docs.google.com/spreadsheets/d/test123/")
        
        assert "Duplicate column name 'Same_Name'" in str(exc_info.value)


class TestFullAgentConfig:
    """Test complete agent configuration functionality."""
    
    def test_instruction_generation(self):
        """Test user instruction generation from schema."""
        # Create mock schema
        input_fields = [
            FieldConfig("Idea_Overview", "user input", "Brief description of idea", 2),
            FieldConfig("Deliverable", "user input", "What will be delivered", 3),
            FieldConfig("Motivation", "user input", "Why does this matter", 4)
        ]
        output_fields = [
            FieldConfig("Rating", "bot output", "Overall rating 1-10", 5)
        ]
        schema = SheetSchema(input_fields, output_fields)
        
        # Create mock agent definition
        agent_def = Mock()
        agent_def.name = "Test Agent"
        
        # Test instruction generation
        config = FullAgentConfig(agent_def, schema)
        instructions = config.generate_instructions()
        
        assert "Test Agent" in instructions
        assert "Idea_Overview" in instructions
        assert "Brief description of idea" in instructions
        assert "Deliverable" in instructions
        assert "Motivation" in instructions
    
    def test_analysis_prompt_generation(self):  
        """Test analysis prompt generation with user input."""
        # Create mock schema
        input_fields = [
            FieldConfig("Idea_Overview", "user input", "Brief description", 2)
        ]
        output_fields = [
            FieldConfig("Rating", "bot output", "Overall rating", 3),
            FieldConfig("Rationale", "bot output", "Detailed explanation", 4)
        ]
        schema = SheetSchema(input_fields, output_fields)
        
        # Create mock agent definition
        agent_def = Mock()
        agent_def.starter_prompt = "You are an expert analyst."
        
        # Test prompt generation
        config = FullAgentConfig(agent_def, schema)
        user_input = {"Idea_Overview": "A revolutionary parking app"}
        
        prompt = config.generate_analysis_prompt(user_input)
        
        assert "You are an expert analyst." in prompt
        assert "A revolutionary parking app" in prompt
        assert "Rating" in prompt
        assert "Rationale" in prompt
        assert "JSON format" in prompt


@pytest.mark.integration
class TestRealGoogleSheetsIntegration:
    """Integration tests with real Google Sheets (requires environment setup)."""
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_SHEETS_KEY_PATH"),
        reason="Google Sheets credentials not available"
    )
    def test_real_sheets_integration(self):
        """Test with actual Google Sheets (when credentials available)."""
        config_path = Path("agents/business_evaluation.yaml")
        
        if not config_path.exists():
            pytest.skip("business_evaluation.yaml not found")
        
        # Load and test full configuration
        agent_def = AgentDefinition.from_yaml(config_path)
        full_config = FullAgentConfig.from_definition(agent_def)
        
        # Verify schema was read
        assert len(full_config.schema.input_fields) > 0
        assert len(full_config.schema.output_fields) > 0
        
        # Test instruction generation
        instructions = full_config.generate_instructions()
        assert "Business Idea Evaluator" in instructions
        assert len(instructions) > 100
        
        # Test prompt generation
        sample_input = {
            field.name: f"Sample {field.name}" 
            for field in full_config.schema.input_fields
        }
        prompt = full_config.generate_analysis_prompt(sample_input)
        assert len(prompt) > 1000
        assert "JSON format" in prompt
        
        print(f"✅ Real integration test passed!")
        print(f"   Input fields: {len(full_config.schema.input_fields)}")
        print(f"   Output fields: {len(full_config.schema.output_fields)}")


if __name__ == "__main__":
    # Run integration test directly
    test_real = TestRealGoogleSheetsIntegration()
    test_real.test_real_sheets_integration()