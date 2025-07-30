#!/usr/bin/env python3
"""
Tests for business evaluator agent implementation using UniversalAgentEngine.
"""

import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    client = Mock()
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message = Mock()
    response.choices[0].message.content = json.dumps({
        "strategy_explanation": "Test strategy",
        "total_calls": 3,
        "calls": [
            {
                "call_id": "market_analysis",
                "purpose": "Analyze market potential",
                "dependencies": []
            },
            {
                "call_id": "risk_assessment",
                "purpose": "Evaluate risks",
                "dependencies": []
            },
            {
                "call_id": "synthesis",
                "purpose": "Final analysis",
                "dependencies": ["market_analysis", "risk_assessment"],
                "is_summarizer": True
            }
        ]
    })
    client.chat.completions.create.return_value = response
    return client


import os

@pytest.fixture
def sheet_id():
    """Get test sheet ID from environment."""
    sheet_id = os.environ.get("IDEA_GUY_SHEET_ID")
    if not sheet_id:
        pytest.skip("IDEA_GUY_SHEET_ID not set")
    return sheet_id


class TestBusinessEvaluatorConfig:
    """Test business evaluator configuration loading."""
    
    def test_load_business_evaluator(self):
        """Test loading business evaluator agent."""
        from common.engine import UniversalAgentEngine
        
        engine = UniversalAgentEngine()
        agent = engine.load_agent("business_evaluation")
        
        assert agent.id == "business_evaluation"
        assert "venture capital" in agent.starter_prompt.lower()
        assert len(agent.input_fields) > 0
        assert len(agent.output_fields) > 0
    
    def test_validate_business_input(self):
        """Test business input validation."""
        from common.engine import UniversalAgentEngine
        from common.errors import ValidationError
        
        engine = UniversalAgentEngine()
        agent = engine.load_agent("business_evaluation")
        
        with pytest.raises(ValidationError):
            agent.validate_input({})  # Empty input
            
        with pytest.raises(ValidationError):
            agent.validate_input({"idea": ""})  # Empty required field
            
        # Valid input should not raise
        agent.validate_input({
            "idea": "AI fitness app",
            "motivation": "Help people stay fit"
        })


class TestBusinessAnalysisExecution:
    """Test business analysis execution."""
    
    @patch("common.utils.get_openai_client")
    def test_basic_tier_execution(self, mock_get_openai, mock_openai):
        """Test basic tier with single call."""
        from common.engine import UniversalAgentEngine
        
        mock_get_openai.return_value = mock_openai
        
        engine = UniversalAgentEngine()
        result = engine.execute_analysis(
            agent_id="business_evaluation",
            user_input={"idea": "AI fitness app"},
            budget_tier="basic"
        )
        
        # Should make exactly one API call
        assert mock_openai.chat.completions.create.call_count == 1
        assert "market_size" in result
        assert "risk_score" in result
    
    @patch("common.utils.get_openai_client")
    def test_standard_tier_planning(self, mock_get_openai, mock_openai):
        """Test standard tier execution plan."""
        from common.engine import UniversalAgentEngine
        
        mock_get_openai.return_value = mock_openai
        
        engine = UniversalAgentEngine()
        agent = engine.load_agent("business_evaluation")
        tier = next(t for t in agent.get_budget_tiers() if t.name == "standard")
        
        plan = engine._plan_execution(
            agent=agent,
            tier=tier,
            user_input={"idea": "AI fitness app"}
        )
        
        assert plan.total_calls == 3
        assert any(c.is_summarizer for c in plan.calls)
        assert all(c.purpose for c in plan.calls)
        
    @patch("common.utils.get_openai_client")
    def test_premium_analysis_execution(self, mock_get_openai, mock_openai):
        """Test premium tier with full analysis."""
        from common.engine import UniversalAgentEngine
        
        mock_get_openai.return_value = mock_openai
        
        engine = UniversalAgentEngine()
        result = engine.execute_analysis(
            agent_id="business_evaluation",
            user_input={
                "idea": "AI fitness app",
                "motivation": "Help people stay fit"
            },
            budget_tier="premium"
        )
        
        assert isinstance(result["market_size"], str)
        assert isinstance(result["risk_score"], (int, float))
        assert len(result) >= 4  # Should have multiple analysis fields
    
    @patch("common.utils.get_openai_client")
    def test_api_error_handling(self, mock_get_openai):
        """Test handling of OpenAI API errors."""
        from common.engine import UniversalAgentEngine
        from common.errors import AnalysisError
        
        mock_get_openai.side_effect = Exception("API Error")
        
        engine = UniversalAgentEngine()
        with pytest.raises(AnalysisError):
            engine.execute_analysis(
                agent_id="business_evaluation",
                user_input={"idea": "test"},
                budget_tier="basic"
            )


class TestBusinessSchemaValidation:
    """Test business evaluator schema validation."""
    
    def test_invalid_schema_detection(self):
        """Test detection of invalid schema."""
        from common.engine import UniversalAgentEngine
        from common.errors import SchemaError
        
        engine = UniversalAgentEngine()
        with pytest.raises(SchemaError):
            # Try to load agent with invalid sheet URL
            engine.load_agent("test_invalid_schema")