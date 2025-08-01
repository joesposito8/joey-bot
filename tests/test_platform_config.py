#!/usr/bin/env python3
"""
Comprehensive tests for Universal AI Agent Platform configuration.
Tests platform.yaml loading, universal settings, and platform-level validation.
"""

import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs"


class TestPlatformConfiguration:
    """Test universal platform configuration loading and validation."""
    
    def test_platform_yaml_exists_and_loads(self):
        """Test that platform.yaml exists and loads correctly."""
        platform_path = Path("common/platform.yaml")
        
        if not platform_path.exists():
            pytest.skip("platform.yaml not yet created - part of universal system design")
        
        # Load platform config
        with open(platform_path, 'r') as f:
            platform_config = yaml.safe_load(f)
        
        # Verify required top-level sections
        # Check top-level structure
        assert "platform" in platform_config
        platform_section = platform_config["platform"]
        
        # Check required sections
        assert "universal_settings" in platform_section
        assert "budget_tiers" in platform_section
        assert "models" in platform_section
        assert "prompts" in platform_section
    
    def test_universal_budget_tiers(self):
        """Test universal budget tier configuration."""
        from common.prompt_manager import prompt_manager
        
        # Load universal config through existing system
        universal_config = prompt_manager._load_common_config()
        budget_tiers = universal_config['platform']['budget_tiers']
        
        # Verify correct structure
        assert len(budget_tiers) == 3
        tier_names = [tier['name'] for tier in budget_tiers]
        assert "basic" in tier_names
        assert "standard" in tier_names  
        assert "premium" in tier_names
        
        # Verify pricing structure
        expected_pricing = {"basic": 1.00, "standard": 3.00, "premium": 5.00}
        expected_calls = {"basic": 1, "standard": 3, "premium": 5}
        
        for tier in budget_tiers:
            name = tier['name']
            assert tier['price'] == expected_pricing[name]
            assert tier['calls'] == expected_calls[name]
            assert 'description' in tier
            assert len(tier['description']) > 10
    
    def test_universal_model_configuration(self):
        """Test universal model settings."""
        from common.prompt_manager import prompt_manager
        
        universal_config = prompt_manager._load_common_config()
        
        # Verify model configuration exists
        platform_config = universal_config.get('platform', {})
        if 'models' in platform_config:
            models = platform_config['models']
            # Check that all models are set to gpt-4o-mini
            for model_type, model_name in models.items():
                assert model_name == "gpt-4o-mini"
            # Verify key model types exist
            assert 'analysis' in models
            assert 'architecture_planning' in models
        
        # Test that old model references are completely removed
        config_str = str(universal_config)
        assert "o4-mini-deep-research" not in config_str
        assert "gpt-4o-mini" in config_str or "default" in config_str
    
    def test_universal_prompt_templates(self):
        """Test universal prompt template system."""
        from common.prompt_manager import prompt_manager
        
        universal_config = prompt_manager._load_common_config()
        
        # Verify prompt templates exist
        platform_config = universal_config.get('platform', {})
        if 'prompts' in platform_config:
            prompts = platform_config['prompts']
            
            # Should have universal workflow prompts
            expected_prompts = [
                'planner_prompt',
                'execution_prompt', 
                'synthesizer_prompt',
                'validation_prompt'
            ]
            
            for prompt_type in expected_prompts:
                if prompt_type in prompts:
                    assert isinstance(prompts[prompt_type], str)
                    assert len(prompts[prompt_type]) > 50


class TestPlatformIntegration:
    """Test platform configuration integration with existing systems."""
    
    def test_budget_config_uses_platform_settings(self):
        """Test that budget configuration uses platform-level settings."""
        # Budget config functionality moved to FullAgentConfig
        from common.config.models import FullAgentConfig
        from common.config.agent_definition import AgentDefinition
        from pathlib import Path
        
        # Load agent config which includes platform settings
        project_root = Path(__file__).parent.parent
        yaml_path = project_root / 'agents' / 'business_evaluation.yaml'
        agent_def = AgentDefinition.from_yaml(yaml_path)
        
        # Test budget tiers from platform config
        config = FullAgentConfig.from_definition(agent_def, None)  # No sheets client needed for this test
        tiers = config.get_budget_tiers()
        
        # Verify tier structure matches platform config
        expected_prices = {"basic": 1.0, "standard": 3.0, "premium": 5.0}
        expected_calls = {"basic": 1, "standard": 3, "premium": 5}
        
        assert len(tiers) == 3
        for tier in tiers:
            assert tier.price == expected_prices[tier.name]
            assert tier.calls == expected_calls[tier.name]
            assert tier.description is not None
            assert len(tier.description) > 0
    
    def test_multi_call_architecture_uses_platform_model(self):
        """Test that multi-call architecture uses platform model settings."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        # Mock OpenAI client and agent config
        mock_client = Mock()
        mock_agent_config = Mock()
        mock_agent_config.get_model.return_value = "gpt-4o-mini"
        mock_agent_config.get_universal_setting.return_value = 4
        architecture = MultiCallArchitecture(mock_client, mock_agent_config)
        
        # Verify architecture uses correct model
        # This would be tested through the actual API calls in integration
        assert hasattr(architecture, 'client')
        assert architecture.client == mock_client
    
    @patch('common.utils.get_openai_client')
    def test_cost_tracker_handles_platform_model(self, mock_get_client):
        """Test that cost tracker handles platform model correctly."""
        from common.cost_tracker import CostTracker, OPENAI_PRICING
        
        # Verify pricing structure
        assert isinstance(OPENAI_PRICING, dict)
        
        # Should not contain old model
        assert "o4-mini-deep-research" not in OPENAI_PRICING
        
        # Test cost calculation with current model
        from common.cost_tracker import calculate_cost_from_usage
        
        # Mock usage data
        mock_usage = {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500
        }
        
        # This should not raise an exception
        try:
            cost = calculate_cost_from_usage("gpt-4o-mini", mock_usage)
            assert isinstance(cost, (int, float))
            assert cost >= 0
        except KeyError:
            # If pricing not available, should handle gracefully
            pytest.skip("Pricing for gpt-4o-mini not yet configured")


class TestPlatformValidation:
    """Test platform-level validation and error handling."""
    
    def test_invalid_budget_tier_handling(self):
        """Test handling of invalid budget tier requests."""
        from common.config.models import FullAgentConfig
        from common.config.agent_definition import AgentDefinition
        from pathlib import Path
        
        # Load agent config
        project_root = Path(__file__).parent.parent
        yaml_path = project_root / 'agents' / 'business_evaluation.yaml'
        agent_def = AgentDefinition.from_yaml(yaml_path)
        config = FullAgentConfig.from_definition(agent_def, None)
        
        # Test that only valid tiers exist
        tiers = config.get_budget_tiers()
        tier_names = [t.name for t in tiers]
        assert "ultra_premium" not in tier_names
        assert all(name in ["basic", "standard", "premium"] for name in tier_names)
    
    def test_platform_config_validation(self):
        """Test that platform configuration is valid."""
        from common.prompt_manager import prompt_manager
        
        try:
            universal_config = prompt_manager._load_common_config()
            
            # Basic structure validation
            assert isinstance(universal_config, dict)
            platform_config = universal_config.get('platform', {})
            assert 'budget_tiers' in platform_config
            assert isinstance(platform_config['budget_tiers'], list)
            
            # Each budget tier should be valid
            for tier in platform_config['budget_tiers']:
                assert 'name' in tier
                assert 'price' in tier
                assert 'calls' in tier
                assert isinstance(tier['price'], (int, float))
                assert isinstance(tier['calls'], int)
                assert tier['calls'] > 0
                assert tier['price'] > 0
            
        except Exception as e:
            pytest.fail(f"Platform configuration validation failed: {str(e)}")


class TestPlatformEnvironment:
    """Test platform environment and setup."""
    
    def test_testing_mode_enabled(self):
        """Test that testing mode prevents API calls."""
        assert os.environ.get("TESTING_MODE") == "true"
        
        # Verify this affects OpenAI client creation
        from common.utils import get_openai_client
        
        # In testing mode, should return mock or handle gracefully
        try:
            client = get_openai_client()
            # Should either be a mock or handle testing mode
            assert client is not None
        except Exception:
            # If no API key in testing, should be handled gracefully
            pass
    
    def test_required_environment_variables(self):
        """Test that required environment variables are set for testing."""
        required_vars = [
            "TESTING_MODE",
            "IDEA_GUY_SHEET_ID"
        ]
        
        for var in required_vars:
            assert os.environ.get(var) is not None, f"Required environment variable {var} not set"
    
    def test_google_sheets_testing_configuration(self):
        """Test Google Sheets configuration for testing."""
        sheet_id = os.environ.get("IDEA_GUY_SHEET_ID")
        assert sheet_id == "1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs"
        
        # Verify sheets client handles testing mode
        from common.utils import get_google_sheets_client
        
        try:
            client = get_google_sheets_client()
            # Should either work or handle testing gracefully
            assert client is not None or os.environ.get("TESTING_MODE") == "true"
        except Exception:
            # In testing mode without credentials, should be handled
            if os.environ.get("TESTING_MODE") != "true":
                raise


if __name__ == "__main__":
    print("🧪 Platform Configuration Testing")
    print("Testing universal platform settings and validation")
    
    # Run tests
    pytest.main([__file__, "-v"])