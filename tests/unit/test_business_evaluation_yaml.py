"""
Unit tests for business evaluation YAML configuration.
Tests YAML loading, validation, and structure.
"""

import pytest
import yaml
from pathlib import Path
from common.config import AgentDefinition, BudgetTierConfig


class TestBusinessEvaluationYAML:
    """Test business_evaluation.yaml configuration file."""
    
    def test_yaml_file_exists(self):
        """Test that the YAML configuration file exists."""
        config_path = Path("agents/business_evaluation.yaml")
        assert config_path.exists(), "agents/business_evaluation.yaml should exist"
    
    def test_yaml_syntax_valid(self):
        """Test that YAML file has valid syntax."""
        config_path = Path("agents/business_evaluation.yaml")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert isinstance(data, dict), "YAML should parse to dictionary"
        assert len(data) > 0, "YAML should not be empty"
    
    def test_required_fields_present(self):
        """Test that all required fields are present in YAML."""
        config_path = Path("agents/business_evaluation.yaml")
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # Test required fields
        assert agent_def.agent_id == "business_evaluation"
        assert agent_def.name == "Business Idea Evaluator"  
        assert agent_def.sheet_url.startswith("https://docs.google.com/spreadsheets")
        assert len(agent_def.starter_prompt) > 500
        assert len(agent_def.budget_tiers) == 3
    
    def test_budget_tiers_configuration(self):
        """Test budget tier configuration is correct."""
        config_path = Path("agents/business_evaluation.yaml")
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # Check we have expected tiers
        tier_names = {tier.name for tier in agent_def.budget_tiers}
        assert tier_names == {"basic", "standard", "premium"}
        
        # Check basic tier
        basic = next(t for t in agent_def.budget_tiers if t.name == "basic")
        assert basic.price == 1.0
        assert basic.calls == 1
        assert "optimized call" in basic.description.lower()
        
        # Check standard tier  
        standard = next(t for t in agent_def.budget_tiers if t.name == "standard")
        assert standard.price == 3.0
        assert standard.calls == 3
        assert "coordinated calls" in standard.description.lower()
        
        # Check premium tier
        premium = next(t for t in agent_def.budget_tiers if t.name == "premium") 
        assert premium.price == 5.0
        assert premium.calls == 5
        assert "coordinated calls" in premium.description.lower()
    
    def test_starter_prompt_quality(self):
        """Test that starter prompt contains key elements."""
        config_path = Path("agents/business_evaluation.yaml")
        agent_def = AgentDefinition.from_yaml(config_path)
        
        prompt = agent_def.starter_prompt.lower()
        
        # Should contain VC-style language
        assert "venture capital" in prompt or "vc" in prompt
        assert "investment" in prompt
        assert "backing" in prompt or "money" in prompt
        
        # Should contain research guidelines
        assert "recent" in prompt or "recency" in prompt
        assert "source" in prompt
        assert "data" in prompt
        
        # Should be substantial
        assert len(agent_def.starter_prompt) > 1000
    
    def test_deliverables_consistency(self):
        """Test that deliverables are consistent across tiers."""
        config_path = Path("agents/business_evaluation.yaml")
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # All tiers should have same deliverables (per architecture)
        basic_deliverables = set(agent_def.budget_tiers[0].deliverables)
        
        for tier in agent_def.budget_tiers[1:]:
            tier_deliverables = set(tier.deliverables)
            assert tier_deliverables == basic_deliverables, f"Tier {tier.name} has different deliverables"
    
    def test_agent_id_url_safe(self):
        """Test that agent_id is URL-safe."""
        config_path = Path("agents/business_evaluation.yaml")
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # Should only contain URL-safe characters
        import re
        assert re.match(r'^[a-zA-Z0-9_-]+$', agent_def.agent_id), "agent_id should be URL-safe"
    
    def test_sheet_url_format(self):
        """Test that sheet_url is a valid Google Sheets URL."""
        config_path = Path("agents/business_evaluation.yaml") 
        agent_def = AgentDefinition.from_yaml(config_path)
        
        # Should be Google Sheets URL with ID
        import re
        pattern = r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+/?'
        assert re.match(pattern, agent_def.sheet_url), "sheet_url should be valid Google Sheets URL"


class TestBudgetTierConfig:
    """Test BudgetTierConfig data class."""
    
    def test_budget_tier_creation(self):
        """Test creating BudgetTierConfig instances."""
        tier = BudgetTierConfig(
            name="test",
            price=2.50,
            calls=2,
            description="Test tier"
        )
        
        assert tier.name == "test"
        assert tier.price == 2.50
        assert tier.calls == 2
        assert tier.description == "Test tier"
    
    def test_budget_tier_from_dict(self):
        """Test creating BudgetTierConfig from dictionary."""
        tier_data = {
            "name": "custom",
            "price": 10.0,
            "calls": 8,
            "description": "Custom analysis tier"
        }
        
        tier = BudgetTierConfig(**tier_data)
        assert tier.name == "custom"
        assert tier.price == 10.0
        assert tier.calls == 8
        assert tier.description == "Custom analysis tier"


if __name__ == "__main__":
    # Run basic tests
    test_yaml = TestBusinessEvaluationYAML()
    test_yaml.test_yaml_file_exists()
    test_yaml.test_yaml_syntax_valid()
    test_yaml.test_required_fields_present()
    test_yaml.test_budget_tiers_configuration()
    test_yaml.test_starter_prompt_quality()
    print("✅ All YAML configuration tests passed!")