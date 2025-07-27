"""
Tests for agent definition loading from YAML configuration files.
"""

import pytest
from pathlib import Path
from common.config.agent_definition import load_agent_definition, ValidationError
from common.config.models import AgentDefinition


class TestAgentDefinition:
    
    def test_load_valid_agent_definition(self, temp_yaml_file):
        """Test loading valid agent definition from YAML."""
        yaml_content = """
agent_id: "business_evaluation"
name: "Business Idea Evaluator"
sheet_url: "https://docs.google.com/spreadsheets/d/test123/"
starter_prompt: |
  You are a senior partner at a VC firm.
  Evaluate this business idea thoroughly.
budget_tiers:
  - name: "basic"
    price: 1.00
    calls: 1
    description: "Quick evaluation"
  - name: "standard"
    price: 3.00
    calls: 3
    description: "Detailed analysis"
"""
        yaml_file = temp_yaml_file(yaml_content)
        
        agent = load_agent_definition(yaml_file)
        
        assert agent.agent_id == "business_evaluation"
        assert agent.name == "Business Idea Evaluator"
        assert "VC firm" in agent.starter_prompt
        assert len(agent.budget_tiers) == 2
        assert agent.budget_tiers[0].name == "basic"
    
    def test_missing_required_fields(self, temp_yaml_file):
        """Test YAML missing required fields raises error."""
        incomplete_yaml = """
name: "Test Agent"
# Missing agent_id, sheet_url, starter_prompt
"""
        yaml_file = temp_yaml_file(incomplete_yaml)
        
        with pytest.raises(ValidationError, match="Missing required field"):
            load_agent_definition(yaml_file)
    
    def test_invalid_agent_id_format(self, temp_yaml_file):
        """Test invalid agent_id format raises error."""
        invalid_yaml = """
agent_id: "Invalid Agent ID!"  # Contains spaces and punctuation
name: "Test Agent"
sheet_url: "https://docs.google.com/test"
starter_prompt: "Test prompt"
budget_tiers: []
"""
        yaml_file = temp_yaml_file(invalid_yaml)
        
        with pytest.raises(ValidationError, match="agent_id must be URL-safe"):
            load_agent_definition(yaml_file)
    
    def test_invalid_yaml_syntax(self, temp_yaml_file):
        """Test invalid YAML syntax raises appropriate error."""
        invalid_yaml = """
agent_id: "test"
name: "Test Agent
# Missing closing quote creates invalid YAML
sheet_url: "https://docs.google.com/test"
"""
        yaml_file = temp_yaml_file(invalid_yaml)
        
        with pytest.raises(ValidationError, match="Invalid YAML syntax"):
            load_agent_definition(yaml_file)
    
    def test_invalid_budget_tiers(self, temp_yaml_file):
        """Test invalid budget tier configuration raises error."""
        invalid_yaml = """
agent_id: "test_agent"
name: "Test Agent"
sheet_url: "https://docs.google.com/test"
starter_prompt: "Test prompt"
budget_tiers:
  - name: "basic"
    price: "invalid_price"  # Should be numeric
    calls: 1
    description: "Test"
"""
        yaml_file = temp_yaml_file(invalid_yaml)
        
        with pytest.raises(ValidationError, match="Invalid budget tier configuration"):
            load_agent_definition(yaml_file)
    
    def test_missing_file(self):
        """Test loading non-existent file raises appropriate error."""
        non_existent_file = Path("/non/existent/path.yaml")
        
        with pytest.raises(ValidationError, match="Agent definition file not found"):
            load_agent_definition(non_existent_file)