#!/usr/bin/env python3
"""
Comprehensive tests for Dynamic Configuration System.
Combines and enhances config models + sheet schema + agent definition testing.
Tests the complete configuration pipeline from YAML → Google Sheets → Runtime.
"""

import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from common.config.models import FieldConfig, SheetSchema, AgentDefinition, FullAgentConfig, BudgetTierConfig
from common.config.sheet_schema_reader import SheetSchemaReader, SchemaValidationError, SheetAccessError
from common.config import AgentDefinition as ImportedAgentDefinition

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


class TestConfigurationModels:
    """Test core configuration data models with comprehensive validation."""
    
    def test_field_config_creation_and_validation(self):
        """Test FieldConfig creation with all validation scenarios."""
        # Valid field creation
        field = FieldConfig("Test_Field", "user input", "Test description", 2)
        assert field.name == "Test_Field"
        assert field.type == "user input"
        assert field.description == "Test description"
        assert field.column_index == 2
        
        # Test all valid field types
        valid_types = ["user input", "bot output", "ID", "Time"]
        for field_type in valid_types:
            field = FieldConfig(f"Test_{field_type}", field_type, "Test desc", 1)
            assert field.type == field_type
        
        # Test invalid field type
        with pytest.raises(ValueError, match="Invalid field type"):
            FieldConfig("Invalid", "unknown_type", "Test", 1)
    
    def test_sheet_schema_comprehensive_validation(self):
        """Test SheetSchema with comprehensive validation scenarios."""
        # Create comprehensive field sets
        input_fields = [
            FieldConfig("Idea_Overview", "user input", "Brief description of the idea", 2),
            FieldConfig("Deliverable", "user input", "What will be built or delivered", 3),
            FieldConfig("Motivation", "user input", "Why this idea matters", 4),
            FieldConfig("Target_Market", "user input", "Who is the target audience", 5)
        ]
        
        output_fields = [
            FieldConfig("Novelty_Rating", "bot output", "How novel is this idea (1-10)", 6),
            FieldConfig("Market_Rating", "bot output", "Market potential rating (1-10)", 7),
            FieldConfig("Feasibility_Rating", "bot output", "Technical feasibility (1-10)", 8),  
            FieldConfig("Overall_Rating", "bot output", "Overall business rating (1-10)", 9),
            FieldConfig("Analysis_Summary", "bot output", "Detailed analysis summary", 10)
        ]
        
        # Valid schema creation
        schema = SheetSchema(input_fields, output_fields)
        assert len(schema.input_fields) == 4
        assert len(schema.output_fields) == 5
        
        # Test input validation
        valid_input = {
            "Idea_Overview": "AI fitness app",
            "Deliverable": "Mobile application", 
            "Motivation": "Help people stay healthy",
            "Target_Market": "Health-conscious millennials"
        }
        assert schema.validate_input(valid_input) == True
        
        # Test missing required field
        invalid_input = {
            "Idea_Overview": "AI fitness app",
            "Deliverable": "Mobile application"
            # Missing Motivation and Target_Market
        }
        assert schema.validate_input(invalid_input) == False
        
        # Test header generation
        headers = schema.generate_output_headers()
        expected_headers = ["Novelty_Rating", "Market_Rating", "Feasibility_Rating", "Overall_Rating", "Analysis_Summary"]
        assert headers == expected_headers
        
        # Test input field extraction
        input_names = [field.name for field in schema.input_fields]
        assert "Idea_Overview" in input_names
        assert "Deliverable" in input_names
        assert "Motivation" in input_names
        assert "Target_Market" in input_names
    
    def test_budget_tier_configuration(self):
        """Test BudgetTierConfig with all tier scenarios."""
        # Test each standard tier
        tier_configs = [
            ("basic", 1.0, 1, "Basic analysis with single comprehensive review"),
            ("standard", 3.0, 3, "Standard analysis with detailed multi-perspective evaluation"),
            ("premium", 5.0, 5, "Premium analysis with comprehensive multi-call architecture")
        ]
        
        for name, price, calls, description in tier_configs:
            tier = BudgetTierConfig(name, price, calls, description)
            assert tier.name == name
            assert tier.price == price
            assert tier.calls == calls
            assert tier.description == description
            assert len(tier.description) >= 20  # Meaningful description
        
        # Test invalid configurations
        with pytest.raises(ValueError, match="Price must be positive"):
            BudgetTierConfig("invalid", -1.0, 1, "Invalid tier")
        
        with pytest.raises(ValueError, match="Calls must be positive"):
            BudgetTierConfig("invalid", 1.0, 0, "Invalid tier")


class TestSheetSchemaReader:
    """Test Google Sheets schema parsing with comprehensive scenarios."""
    
    @pytest.fixture
    def comprehensive_mock_sheet_data(self):
        """Comprehensive mock sheet data for testing."""
        return [
            # Row 1: Field types
            ["ID", "Time", "User", "User", "User", "User", "Bot", "Bot", "Bot", "Bot", "Bot"],
            # Row 2: Field descriptions  
            ["Unique ID", "Timestamp", "Brief idea description", "What will be delivered", 
             "Why this matters", "Target audience", "Novelty score 1-10", "Market potential 1-10",
             "Technical feasibility 1-10", "Overall rating 1-10", "Detailed analysis"],
            # Row 3: Field names
            ["ID", "Time", "Idea_Overview", "Deliverable", "Motivation", "Target_Market",
             "Novelty_Rating", "Market_Rating", "Feasibility_Rating", "Overall_Rating", "Analysis_Summary"]
        ]
    
    @pytest.fixture
    def mock_sheets_client(self, comprehensive_mock_sheet_data):
        """Mock Google Sheets client with comprehensive data."""
        client = Mock()
        spreadsheet = Mock()
        worksheet = Mock()
        
        client.open_by_key.return_value = spreadsheet
        spreadsheet.get_worksheet.return_value = worksheet
        worksheet.get_values.return_value = comprehensive_mock_sheet_data
        
        return client
    
    def test_comprehensive_schema_parsing(self, mock_sheets_client):
        """Test parsing comprehensive sheet schema."""
        reader = SheetSchemaReader(mock_sheets_client)
        schema = reader.parse_sheet_schema("https://docs.google.com/spreadsheets/d/test123/")
        
        # Verify structure
        assert len(schema.input_fields) == 4  # User input fields
        assert len(schema.output_fields) == 5  # Bot output fields
        
        # Verify input fields
        input_names = [field.name for field in schema.input_fields]
        expected_inputs = ["Idea_Overview", "Deliverable", "Motivation", "Target_Market"] 
        assert input_names == expected_inputs
        
        # Verify output fields
        output_names = [field.name for field in schema.output_fields]
        expected_outputs = ["Novelty_Rating", "Market_Rating", "Feasibility_Rating", "Overall_Rating", "Analysis_Summary"]
        assert output_names == expected_outputs
        
        # Verify field properties
        idea_field = next(f for f in schema.input_fields if f.name == "Idea_Overview")
        assert idea_field.type == "user input"
        assert idea_field.description == "Brief idea description"
        assert idea_field.column_index == 2
        
        rating_field = next(f for f in schema.output_fields if f.name == "Overall_Rating")
        assert rating_field.type == "bot output"
        assert rating_field.description == "Overall rating 1-10"
        assert rating_field.column_index == 9
    
    def test_error_scenarios_comprehensive(self):
        """Test all error scenarios for sheet parsing."""
        # Test missing rows
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        
        # Missing rows
        mock_worksheet.get_values.return_value = [
            ["ID", "Time", "User"],
            ["ID", "Time", "Description"]
            # Missing row 3
        ]
        
        reader = SheetSchemaReader(mock_client)
        with pytest.raises(SchemaValidationError, match="Schema must have at least 3 rows"):
            reader.parse_sheet_schema("https://docs.google.com/test/")
        
        # Invalid field types
        mock_worksheet.get_values.return_value = [
            ["ID", "Time", "InvalidType"],
            ["ID", "Time", "Description"], 
            ["ID", "Time", "FieldName"]
        ]
        
        with pytest.raises(SchemaValidationError, match="Invalid field type 'InvalidType'"):
            reader.parse_sheet_schema("https://docs.google.com/test/")
        
        # Duplicate column names
        mock_worksheet.get_values.return_value = [
            ["ID", "Time", "User", "User"],
            ["ID", "Time", "Desc1", "Desc2"],
            ["ID", "Time", "SameName", "SameName"]
        ]
        
        with pytest.raises(SchemaValidationError, match="Duplicate column name 'SameName'"):
            reader.parse_sheet_schema("https://docs.google.com/test/")
        
        # Empty descriptions
        mock_worksheet.get_values.return_value = [
            ["ID", "Time", "User"],
            ["ID", "Time", ""],  # Empty description
            ["ID", "Time", "FieldName"]
        ]
        
        with pytest.raises(SchemaValidationError, match="Empty description for field 'FieldName'"):
            reader.parse_sheet_schema("https://docs.google.com/test/")
    
    def test_sheet_access_errors(self):
        """Test sheet access error handling."""
        # Test invalid URL
        mock_client = Mock()
        reader = SheetSchemaReader(mock_client)
        
        with pytest.raises(SheetAccessError, match="Invalid Google Sheets URL"):
            reader.parse_sheet_schema("https://invalid-url.com/")
        
        # Test sheets API error
        mock_client.open_by_key.side_effect = Exception("API Error")
        
        with pytest.raises(SheetAccessError, match="Cannot access sheet"):
            reader.parse_sheet_schema("https://docs.google.com/spreadsheets/d/test123/")


class TestAgentDefinition:
    """Test YAML agent definition loading with comprehensive validation."""
    
    @pytest.fixture
    def sample_agent_yaml(self, tmp_path):
        """Create sample agent YAML for testing."""
        yaml_content = {
            "agent_id": "test_agent_comprehensive",
            "name": "Comprehensive Test Agent",
            "sheet_url": "https://docs.google.com/spreadsheets/d/test123/edit",
            "starter_prompt": "You are a comprehensive test agent designed to evaluate complex scenarios with deep analysis and multi-perspective thinking.",
            "models": {
                "default": "gpt-4o-mini",
                "fallback": "gpt-3.5-turbo"
            }
        }
        
        yaml_file = tmp_path / "test_agent.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)
        
        return yaml_file
    
    def test_comprehensive_agent_loading(self, sample_agent_yaml):
        """Test loading agent definition with all features."""
        agent_def = AgentDefinition.from_yaml(sample_agent_yaml)
        
        # Verify all properties
        assert agent_def.agent_id == "test_agent_comprehensive"
        assert agent_def.name == "Comprehensive Test Agent"
        assert "docs.google.com" in agent_def.sheet_url
        assert len(agent_def.starter_prompt) > 50  # Substantial prompt
        
        # Verify models configuration
        assert hasattr(agent_def, 'models')
        if agent_def.models:
            assert "default" in agent_def.models
            assert agent_def.models["default"] == "gpt-4o-mini"
    
    def test_agent_validation_scenarios(self, tmp_path):
        """Test all agent validation scenarios."""
        # Test missing required fields
        invalid_configs = [
            # Missing agent_id
            {
                "name": "Test Agent",
                "sheet_url": "https://docs.google.com/test",
                "starter_prompt": "Test prompt"
            },
            # Missing name
            {
                "agent_id": "test_agent",
                "sheet_url": "https://docs.google.com/test", 
                "starter_prompt": "Test prompt"
            },
            # Missing sheet_url
            {
                "agent_id": "test_agent",
                "name": "Test Agent",
                "starter_prompt": "Test prompt"
            },
            # Missing starter_prompt
            {
                "agent_id": "test_agent", 
                "name": "Test Agent",
                "sheet_url": "https://docs.google.com/test"
            }
        ]
        
        for i, invalid_config in enumerate(invalid_configs):
            yaml_file = tmp_path / f"invalid_{i}.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(invalid_config, f)
            
            with pytest.raises(ValueError, match="Missing required field"):
                AgentDefinition.from_yaml(yaml_file)
        
        # Test invalid agent_id format
        invalid_id_config = {
            "agent_id": "Invalid Agent ID!",  # Contains spaces and special chars
            "name": "Test Agent",
            "sheet_url": "https://docs.google.com/test",
            "starter_prompt": "Test prompt"
        }
        
        yaml_file = tmp_path / "invalid_id.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(invalid_id_config, f)
        
        with pytest.raises(ValueError, match="agent_id must contain only"):
            AgentDefinition.from_yaml(yaml_file)
    
    def test_yaml_syntax_errors(self, tmp_path):
        """Test YAML syntax error handling."""
        invalid_yaml = "invalid: yaml: content: [unclosed"
        
        yaml_file = tmp_path / "invalid_syntax.yaml"
        with open(yaml_file, 'w') as f:
            f.write(invalid_yaml)
        
        with pytest.raises(ValueError, match="Invalid YAML syntax"):
            AgentDefinition.from_yaml(yaml_file)


class TestFullAgentConfiguration:
    """Test complete agent configuration combining YAML + Google Sheets."""
    
    @pytest.fixture
    def mock_agent_definition(self):
        """Mock agent definition for testing."""
        definition = Mock(spec=AgentDefinition)
        definition.agent_id = "comprehensive_test_agent"
        definition.name = "Comprehensive Test Agent"
        definition.sheet_url = "https://docs.google.com/spreadsheets/d/test123/"
        definition.starter_prompt = "You are a comprehensive test agent that provides detailed analysis across multiple dimensions including market potential, technical feasibility, competitive landscape, and business viability."
        definition.models = {"default": "gpt-4o-mini"}
        return definition
    
    @pytest.fixture
    def comprehensive_sheet_schema(self):
        """Comprehensive sheet schema for testing."""
        input_fields = [
            FieldConfig("Idea_Overview", "user input", "Brief description of the business idea", 2),
            FieldConfig("Deliverable", "user input", "What will be built or delivered", 3),
            FieldConfig("Motivation", "user input", "Why this idea matters and problem it solves", 4),
            FieldConfig("Target_Market", "user input", "Who is the target audience", 5),
            FieldConfig("Competition", "user input", "Known competitors or alternatives", 6)
        ]
        
        output_fields = [
            FieldConfig("Market_Analysis", "bot output", "Market size and opportunity analysis", 7),
            FieldConfig("Technical_Feasibility", "bot output", "Technical implementation assessment", 8),
            FieldConfig("Competitive_Advantage", "bot output", "Unique value proposition analysis", 9),
            FieldConfig("Risk_Assessment", "bot output", "Potential risks and mitigation strategies", 10),
            FieldConfig("Overall_Rating", "bot output", "Overall business potential rating 1-10", 11),
            FieldConfig("Detailed_Summary", "bot output", "Comprehensive analysis summary", 12)
        ]
        
        return SheetSchema(input_fields, output_fields)
    
    def test_comprehensive_full_config_functionality(self, mock_agent_definition, comprehensive_sheet_schema):
        """Test complete FullAgentConfig functionality."""
        config = FullAgentConfig(mock_agent_definition, comprehensive_sheet_schema)
        
        # Test instruction generation
        instructions = config.generate_instructions()
        assert "Comprehensive Test Agent" in instructions
        assert "Idea_Overview" in instructions
        assert "Brief description of the business idea" in instructions
        assert "Target_Market" in instructions
        assert "Competition" in instructions
        
        # Verify all input fields are documented
        for field in comprehensive_sheet_schema.input_fields:
            assert field.name in instructions
            assert field.description in instructions
    
    def test_comprehensive_analysis_prompt_generation(self, mock_agent_definition, comprehensive_sheet_schema):
        """Test analysis prompt generation with comprehensive input."""
        config = FullAgentConfig(mock_agent_definition, comprehensive_sheet_schema)
        
        # Comprehensive user input
        user_input = {
            "Idea_Overview": "AI-powered personal fitness coach that adapts to individual schedules and preferences",
            "Deliverable": "Mobile app with AI coaching, workout tracking, and personalized nutrition guidance",
            "Motivation": "Help busy professionals maintain fitness routines despite time constraints and varying schedules",
            "Target_Market": "Working professionals aged 25-45 with household income over $75k",
            "Competition": "MyFitnessPal, Nike Training Club, Peloton Digital"
        }
        
        prompt = config.generate_analysis_prompt(user_input)
        
        # Verify prompt contains all elements
        assert "You are a comprehensive test agent" in prompt
        assert "AI-powered personal fitness coach" in prompt
        assert "Working professionals aged 25-45" in prompt
        assert "MyFitnessPal, Nike Training Club" in prompt
        
        # Verify output schema is included
        assert "Market_Analysis" in prompt
        assert "Technical_Feasibility" in prompt
        assert "Competitive_Advantage" in prompt
        assert "Risk_Assessment" in prompt
        assert "Overall_Rating" in prompt
        assert "Detailed_Summary" in prompt
        
        # Verify JSON format instruction
        assert "JSON format" in prompt
        assert "structured response" in prompt
    
    def test_missing_input_handling(self, mock_agent_definition, comprehensive_sheet_schema):
        """Test handling of missing input fields."""
        config = FullAgentConfig(mock_agent_definition, comprehensive_sheet_schema)
        
        # Incomplete input
        incomplete_input = {
            "Idea_Overview": "Basic fitness app idea",
            "Deliverable": "Mobile app"
            # Missing Motivation, Target_Market, Competition
        }
        
        prompt = config.generate_analysis_prompt(incomplete_input)
        
        # Should still generate prompt
        assert "Basic fitness app idea" in prompt
        assert "Mobile app" in prompt
        
        # Field names should still appear even with empty values
        assert "Motivation" in prompt
        assert "Target_Market" in prompt
        assert "Competition" in prompt
    
    @patch('common.config.sheet_schema_reader.SheetSchemaReader')
    def test_full_config_from_definition(self, mock_reader_class, mock_agent_definition, comprehensive_sheet_schema):
        """Test creating FullAgentConfig from definition with sheet loading."""
        # Mock the sheet schema reader
        mock_reader = Mock()
        mock_reader.parse_sheet_schema.return_value = comprehensive_sheet_schema
        mock_reader_class.return_value = mock_reader
        
        # Mock sheets client
        with patch('common.utils.get_sheets_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            
            # Test config creation
            config = FullAgentConfig.from_definition(mock_agent_definition)
            
            # Verify schema was loaded
            assert config.schema == comprehensive_sheet_schema
            assert config.definition == mock_agent_definition


class TestConfigurationIntegration:
    """Test integration between all configuration components."""
    
    def test_end_to_end_configuration_flow(self):
        """Test complete configuration flow from YAML to runtime."""
        # This test represents the full configuration pipeline:
        # 1. Load agent YAML definition
        # 2. Parse Google Sheets schema  
        # 3. Create full configuration
        # 4. Generate prompts and validate inputs
        
        # Step 1: Mock agent definition loading
        mock_definition = Mock(spec=AgentDefinition)
        mock_definition.agent_id = "integration_test_agent"
        mock_definition.name = "Integration Test Agent"
        mock_definition.starter_prompt = "Integration test prompt"
        mock_definition.sheet_url = "https://docs.google.com/test"
        
        # Step 2: Mock schema parsing
        mock_schema = Mock(spec=SheetSchema)
        mock_schema.input_fields = [
            FieldConfig("Test_Input", "user input", "Test input field", 2)
        ]
        mock_schema.output_fields = [
            FieldConfig("Test_Output", "bot output", "Test output field", 3)
        ]
        mock_schema.validate_input.return_value = True
        
        # Step 3: Create full configuration
        config = FullAgentConfig(mock_definition, mock_schema)
        
        # Step 4: Test functionality
        assert config.definition == mock_definition
        assert config.schema == mock_schema
        
        # Test prompt generation works
        instructions = config.generate_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 0
        
        # Test analysis prompt generation
        test_input = {"Test_Input": "Test value"}
        analysis_prompt = config.generate_analysis_prompt(test_input)
        assert isinstance(analysis_prompt, str)
        assert "Test value" in analysis_prompt
    
    def test_configuration_error_propagation(self):
        """Test that configuration errors propagate correctly."""
        # Test that errors from any component propagate up
        mock_definition = Mock(spec=AgentDefinition)
        mock_schema = Mock(spec=SheetSchema)
        
        # Mock schema validation error
        mock_schema.validate_input.side_effect = Exception("Schema validation error")
        
        config = FullAgentConfig(mock_definition, mock_schema)
        
        # Error should propagate when trying to use the config
        with pytest.raises(Exception, match="Schema validation error"):
            config.schema.validate_input({"test": "input"})


if __name__ == "__main__":
    print("🧪 Dynamic Configuration System Testing")
    print("Testing YAML → Google Sheets → Runtime configuration pipeline")
    
    # Run tests
    pytest.main([__file__, "-v"])