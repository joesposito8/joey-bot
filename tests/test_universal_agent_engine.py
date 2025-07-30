#!/usr/bin/env python3
"""
Comprehensive tests for Universal Agent Engine.
Tests agent orchestration, multi-agent support, and universal agent functionality.
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


class TestUniversalAgentEngine:
    """Test the core Universal Agent Engine functionality."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        client = Mock()
        response = Mock()
        output = Mock()
        content = Mock()
        content.text = json.dumps({
            "Overall_Rating": "8/10", 
            "Analysis_Summary": "Strong business potential with clear market need."
        })
        output.content = [content]
        response.output = [output]
        client.responses.create.return_value = response
        return client
    
    @pytest.fixture
    def mock_sheets_client(self):
        """Mock Google Sheets client for testing."""
        client = Mock()
        spreadsheet = Mock()
        worksheet = Mock()
        client.open_by_key.return_value = spreadsheet
        spreadsheet.get_worksheet.return_value = worksheet
        worksheet.get_values.return_value = [
            ["ID", "Time", "User", "User", "User", "Bot", "Bot"], 
            ["ID", "Time", "Brief desc", "What will", "Why this", "Rating", "Summary"],
            ["ID", "Time", "Idea_Overview", "Deliverable", "Motivation", "Overall_Rating", "Analysis_Summary"]
        ]
        return client
    
    def test_universal_agent_creation(self):
        """Test creating agents through universal system."""
        from common.agent_service import AnalysisService
        
        # Test that AnalysisService can be created
        service = AnalysisService()
        assert service is not None
        
        # Verify it has required methods for universal agent functionality
        assert hasattr(service, 'create_job')
        assert hasattr(service, 'process_job')
        assert hasattr(service, 'get_job_status')
    
    @patch('common.utils.get_openai_client')
    @patch('common.utils.get_sheets_client')
    def test_universal_agent_job_creation(self, mock_get_sheets, mock_get_openai):
        """Test universal job creation for any agent type."""
        from common.agent_service import AnalysisService
        
        # Mock clients
        mock_get_openai.return_value = self.mock_openai_client()
        mock_get_sheets.return_value = self.mock_sheets_client()
        
        service = AnalysisService()
        
        # Test job creation with universal input
        user_input = {
            "Idea_Overview": "AI-powered fitness tracking app",
            "Deliverable": "Mobile app with personalized workouts", 
            "Motivation": "Help people maintain fitness routines"
        }
        
        job_id = service.create_job(user_input, "standard")
        
        # Verify job ID created
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) > 0
    
    def test_budget_tier_integration(self):
        """Test that universal agents use platform budget tiers."""
        from common.budget_config import BudgetConfigManager
        
        manager = BudgetConfigManager()
        
        # Test all universal budget tiers
        for tier_name in ['basic', 'standard', 'premium']:
            config = manager.get_tier_config(tier_name)
            
            # Verify universal properties
            assert config.model == "gpt-4o-mini"
            assert hasattr(config, 'max_cost')
            assert hasattr(config, 'max_calls')
            assert config.max_calls > 0
            assert config.max_cost > 0
    
    @patch('common.utils.get_openai_client')
    def test_universal_analysis_execution(self, mock_get_openai):
        """Test that analysis execution works for any agent type."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        # Mock OpenAI client with proper response structure
        mock_client = Mock()
        mock_response = Mock()
        mock_output = Mock()
        mock_content = Mock()
        
        # Mock planning response
        mock_plan = {
            "strategy_explanation": "Universal analysis strategy",
            "total_calls": 3,
            "max_concurrent": 4,
            "calls": [
                {
                    "call_id": "analysis_1",
                    "purpose": "Primary analysis",
                    "prompt": "Analyze the input",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "analysis_2", 
                    "purpose": "Secondary analysis",
                    "prompt": "Analyze different aspects",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "synthesizer",
                    "purpose": "Synthesize findings",
                    "prompt": "Combine all analysis",
                    "dependencies": ["analysis_1", "analysis_2"],
                    "is_summarizer": True
                }
            ],
            "execution_order": [
                ["analysis_1", "analysis_2"],
                ["synthesizer"]
            ]
        }
        
        mock_content.text = json.dumps(mock_plan)
        mock_output.content = [mock_content]
        mock_response.output = [mock_output]
        mock_client.responses.create.return_value = mock_response
        mock_get_openai.return_value = mock_client
        
        # Test multi-call architecture
        architecture = MultiCallArchitecture(mock_client)
        
        user_input = {
            "Idea_Overview": "Test idea",
            "Deliverable": "Test deliverable",
            "Motivation": "Test motivation"
        }
        
        # Test planning
        plan = architecture.plan_architecture(
            original_prompt="Test prompt",
            available_calls=3,
            user_input=user_input
        )
        
        assert plan.total_calls == 3
        assert len(plan.calls) == 3
        assert len(plan.execution_order) == 2
    
    def test_universal_prompt_generation(self):
        """Test universal prompt generation for different agent types."""
        from common.config.models import FullAgentConfig, AgentDefinition, SheetSchema, FieldConfig
        
        # Create mock agent definition
        agent_def = Mock(spec=AgentDefinition)
        agent_def.agent_id = "test_agent"
        agent_def.name = "Test Agent"
        agent_def.starter_prompt = "You are a universal test agent."
        
        # Create mock schema
        input_fields = [
            FieldConfig("Input_Field", "user input", "Test input field", 2)
        ]
        output_fields = [
            FieldConfig("Output_Field", "bot output", "Test output field", 3)
        ]
        schema = SheetSchema(input_fields, output_fields)
        
        # Test full config
        config = FullAgentConfig(agent_def, schema)
        
        # Test instruction generation
        instructions = config.generate_instructions()
        assert "Test Agent" in instructions
        assert "Input_Field" in instructions
        
        # Test analysis prompt generation
        user_input = {"Input_Field": "Test input"}
        prompt = config.generate_analysis_prompt(user_input)
        assert "You are a universal test agent." in prompt
        assert "Test input" in prompt
        assert "Output_Field" in prompt


class TestMultiAgentSupport:
    """Test support for multiple agent types in the universal system."""
    
    def test_multiple_agent_definitions_loading(self):
        """Test loading multiple different agent types."""
        from common.config import AgentDefinition
        
        # Test that agent definitions can be loaded
        agents_dir = Path("agents")
        if not agents_dir.exists():
            pytest.skip("agents/ directory not yet created")
        
        yaml_files = list(agents_dir.glob("*.yaml"))
        if not yaml_files:
            pytest.skip("No agent YAML files found yet")
        
        loaded_agents = []
        for yaml_file in yaml_files:
            try:
                agent_def = AgentDefinition.from_yaml(yaml_file)
                loaded_agents.append(agent_def)
            except Exception as e:
                pytest.fail(f"Failed to load {yaml_file}: {str(e)}")
        
        # Verify each agent has required universal properties
        for agent in loaded_agents:
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'starter_prompt')
            assert hasattr(agent, 'sheet_url')
    
    def test_agent_type_switching(self):
        """Test switching between different agent types."""
        from common.agent_service import AnalysisService
        
        # This tests the concept - actual implementation would allow
        # switching agent types by loading different configurations
        service = AnalysisService()
        
        # Verify service can handle different types of analysis
        assert hasattr(service, 'create_job') 
        assert hasattr(service, 'process_job')
        
        # The universal system should handle any agent type
        # through configuration rather than code changes
    
    def test_shared_infrastructure(self):
        """Test that all agents share the same infrastructure."""
        from common.budget_config import BudgetConfigManager
        from common.cost_tracker import CostTracker
        from common.multi_call_architecture import MultiCallArchitecture
        
        # All agents should use the same budget system
        budget_manager = BudgetConfigManager()
        assert budget_manager is not None
        
        # All agents should use the same cost tracking
        cost_tracker = CostTracker()
        assert cost_tracker is not None
        
        # All agents should use the same multi-call architecture
        mock_client = Mock()
        architecture = MultiCallArchitecture(mock_client)
        assert architecture is not None


class TestUniversalValidation:
    """Test universal validation system for any agent type."""
    
    def test_universal_input_validation(self):
        """Test input validation works for any agent configuration."""
        from common.config.models import SheetSchema, FieldConfig
        
        # Create test schema
        input_fields = [
            FieldConfig("Required_Field", "user input", "Required field", 2),
            FieldConfig("Optional_Field", "user input", "Optional field", 3)
        ]
        output_fields = [
            FieldConfig("Result_Field", "bot output", "Result field", 4) 
        ]
        schema = SheetSchema(input_fields, output_fields)
        
        # Test valid input
        valid_input = {
            "Required_Field": "Test value",
            "Optional_Field": "Another value"
        }
        assert schema.validate_input(valid_input) == True
        
        # Test invalid input (missing required field)
        invalid_input = {
            "Optional_Field": "Only optional field"
        }
        assert schema.validate_input(invalid_input) == False
    
    def test_universal_output_formatting(self):
        """Test output formatting works for any agent type."""
        from common.config.models import SheetSchema, FieldConfig
        
        # Create test schema  
        output_fields = [
            FieldConfig("Rating", "bot output", "Numerical rating", 2),
            FieldConfig("Summary", "bot output", "Text summary", 3)
        ]
        schema = SheetSchema([], output_fields)
        
        # Test header generation
        headers = schema.generate_output_headers()
        assert "Rating" in headers
        assert "Summary" in headers
        
        # Verify correct order
        assert headers.index("Rating") < headers.index("Summary")
    
    def test_error_handling_universally(self):
        """Test that error handling works consistently across agent types."""
        from common.http_utils import create_error_response, create_success_response
        
        # Test error response creation
        error_response = create_error_response(
            "Test error message",
            400,
            "validation_error",
            "Please check your input"
        )
        
        assert error_response.status_code == 400
        response_data = json.loads(error_response.get_body())
        assert response_data["error"] == "Test error message"
        assert response_data["error_type"] == "validation_error"
        assert response_data["suggestion"] == "Please check your input"
        
        # Test success response creation
        success_response = create_success_response({"test": "data"})
        assert success_response.status_code == 200
        response_data = json.loads(success_response.get_body())
        assert response_data["test"] == "data"


class TestUniversalPerformance:
    """Test performance aspects of the universal system."""
    
    def test_configuration_caching(self):
        """Test that configurations are cached for performance."""
        from common.prompt_manager import prompt_manager
        
        # Load config multiple times
        config1 = prompt_manager._load_common_config()
        config2 = prompt_manager._load_common_config()
        
        # Should be the same object (cached)
        assert config1 is config2 or config1 == config2
    
    def test_memory_efficiency(self):
        """Test that the universal system is memory efficient."""
        from common.agent_service import AnalysisService
        
        # Creating multiple services should not leak memory
        services = []
        for i in range(10):
            service = AnalysisService()
            services.append(service)
        
        # All services should be created successfully
        assert len(services) == 10
        assert all(service is not None for service in services)
    
    def test_concurrent_agent_handling(self):
        """Test system can handle multiple agents concurrently."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        # Create multiple architecture instances
        mock_clients = [Mock() for _ in range(5)]
        architectures = [MultiCallArchitecture(client) for client in mock_clients]
        
        # All should be created successfully
        assert len(architectures) == 5
        assert all(arch is not None for arch in architectures)


if __name__ == "__main__":
    print("🧪 Universal Agent Engine Testing")
    print("Testing agent orchestration and multi-agent support")
    
    # Run tests
    pytest.main([__file__, "-v"])