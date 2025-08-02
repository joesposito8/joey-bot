#!/usr/bin/env python3
"""
Test DurableOrchestrator for research→synthesis workflow.
Tests sequential execution, LangChain integration, and budget tier allocation.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

# TODO: Import after implementation
try:
    from common.durable_orchestrator import DurableOrchestrator
    from common.research_models import ResearchOutput
except ImportError:
    DurableOrchestrator = None
    ResearchOutput = None


@pytest.fixture
def mock_agent_config():
    """Mock agent configuration with budget tiers."""
    config = Mock()
    config.get_model.return_value = "gpt-4o-mini"
    config.definition.starter_prompt = "You are a business analyst..."
    
    # Mock budget tiers: Basic(0+1), Standard(2+1), Premium(4+1)
    basic_tier = Mock()
    basic_tier.name = "basic"
    basic_tier.calls = 1  # 0 research + 1 synthesis
    
    standard_tier = Mock()  
    standard_tier.name = "standard"
    standard_tier.calls = 3  # 2 research + 1 synthesis
    
    premium_tier = Mock()
    premium_tier.name = "premium" 
    premium_tier.calls = 5  # 4 research + 1 synthesis
    
    config.get_budget_tiers.return_value = [basic_tier, standard_tier, premium_tier]
    return config


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return {
        "Idea_Overview": "AI-powered meal planning app",
        "Deliverable": "Mobile app with personalized meal recommendations",
        "Motivation": "Help people eat healthier with less planning effort"
    }


class TestDurableOrchestrator:
    """Test DurableOrchestrator sequential workflow execution."""
    
    def test_orchestrator_initialization(self, mock_agent_config):
        """Test DurableOrchestrator can be initialized with agent config."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        assert orchestrator.agent_config == mock_agent_config
        # TODO: Add more initialization checks once implementation exists
    
    def test_create_research_plan_basic_tier(self, mock_agent_config, sample_user_input):
        """Test research plan creation for basic tier (0 research calls)."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # Basic tier should have 0 research calls + 1 synthesis
        research_plan = orchestrator.create_research_plan(sample_user_input, "basic")
        
        assert research_plan["tier"] == "basic"
        assert research_plan["research_calls"] == 0
        assert research_plan["synthesis_calls"] == 1
        assert len(research_plan["research_topics"]) == 0
    
    def test_create_research_plan_standard_tier(self, mock_agent_config, sample_user_input):
        """Test research plan creation for standard tier (2 research calls)."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # Standard tier should have 2 research calls + 1 synthesis
        research_plan = orchestrator.create_research_plan(sample_user_input, "standard")
        
        assert research_plan["tier"] == "standard"
        assert research_plan["research_calls"] == 2
        assert research_plan["synthesis_calls"] == 1
        assert len(research_plan["research_topics"]) == 2
        # TODO: Validate research topics are relevant to user input
    
    def test_create_research_plan_premium_tier(self, mock_agent_config, sample_user_input):
        """Test research plan creation for premium tier (4 research calls)."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # Premium tier should have 4 research calls + 1 synthesis  
        research_plan = orchestrator.create_research_plan(sample_user_input, "premium")
        
        assert research_plan["tier"] == "premium"
        assert research_plan["research_calls"] == 4
        assert research_plan["synthesis_calls"] == 1
        assert len(research_plan["research_topics"]) == 4
        # Validate topics cover different aspects
        topics = research_plan["research_topics"]
        assert len(set(topics)) == len(topics)  # No duplicate topics
    
    @patch('common.http_utils.is_testing_mode', return_value=True)
    def test_execute_research_call_testing_mode(self, mock_testing_mode, mock_agent_config):
        """Test research call execution in testing mode."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        research_topic = "Market size analysis for meal planning apps"
        result = orchestrator.execute_research_call(research_topic)
        
        # Should return mock ResearchOutput in testing mode
        assert isinstance(result, ResearchOutput)
        assert result.research_topic == research_topic
        assert result.summary is not None
        assert len(result.key_findings) > 0
        assert "mock" in result.summary.lower() or "test" in result.summary.lower()
    
    @patch('common.http_utils.is_testing_mode', return_value=False)
    @patch('langchain_openai.ChatOpenAI')
    def test_execute_research_call_production_mode(self, mock_chat_openai, mock_testing_mode, mock_agent_config):
        """Test research call execution with real LangChain integration."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        # Mock LangChain chat response
        mock_response = Mock()
        mock_response.content = json.dumps({
            "research_topic": "Market analysis",
            "summary": "Growing market with opportunities",
            "key_findings": ["$5B market", "15% growth"],
            "confidence_level": "medium"
        })
        
        mock_chat = Mock()
        mock_chat.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        research_topic = "Market size analysis for meal planning apps"
        
        result = orchestrator.execute_research_call(research_topic)
        
        # Should use LangChain with PydanticOutputParser
        assert isinstance(result, ResearchOutput)
        assert result.research_topic == "Market analysis"
        mock_chat.invoke.assert_called_once()
    
    def test_execute_synthesis_call_with_research_results(self, mock_agent_config):
        """Test synthesis call combines research results using Jinja templates."""
        if DurableOrchestrator is None or ResearchOutput is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        # Mock research results
        research_results = [
            ResearchOutput(
                research_topic="Market analysis",
                summary="Large growing market", 
                key_findings=["$5B market", "15% CAGR"]
            ),
            ResearchOutput(
                research_topic="Competition analysis",
                summary="Fragmented competitive landscape",
                key_findings=["No dominant player", "Room for innovation"]
            )
        ]
        
        user_input = {
            "Idea_Overview": "AI meal planning app",
            "Deliverable": "Mobile app"
        }
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        synthesis_result = orchestrator.execute_synthesis_call(research_results, user_input)
        
        # Should combine research into final analysis
        assert isinstance(synthesis_result, dict)
        assert "Analysis_Result" in synthesis_result  # TODO: Match actual output schema
        # Should reference findings from research
        analysis_text = str(synthesis_result)
        assert "$5B" in analysis_text or "market" in analysis_text.lower()
    
    def test_sequential_workflow_execution_order(self, mock_agent_config, sample_user_input):
        """Test full workflow executes research→synthesis sequentially."""
        if DurableOrchestrator is None or ResearchOutput is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # Track execution order
        execution_log = []
        
        def mock_research_call(topic):
            execution_log.append(f"research: {topic}")
            return ResearchOutput(
                research_topic=topic,
                summary="Mock research",
                key_findings=["Finding 1"]
            )
        
        def mock_synthesis_call(research_results, user_input):
            execution_log.append("synthesis")
            return {"Analysis_Result": "Mock synthesis"}
        
        orchestrator.execute_research_call = Mock(side_effect=mock_research_call)
        orchestrator.execute_synthesis_call = Mock(side_effect=mock_synthesis_call)
        
        # Execute standard tier workflow (2 research + 1 synthesis)
        result = orchestrator.execute_workflow(sample_user_input, "standard")
        
        # Verify execution order: all research first, then synthesis
        assert len(execution_log) == 3
        assert execution_log[0].startswith("research:")
        assert execution_log[1].startswith("research:")  
        assert execution_log[2] == "synthesis"
        
        # Verify final result
        assert "job_id" in result
        assert result["status"] == "completed"  # TODO: Match actual status values


class TestErrorHandling:
    """Test error handling and fallback behavior."""
    
    def test_research_call_failure_handling(self, mock_agent_config):
        """Test graceful handling when research call fails."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # TODO: Mock LangChain to raise exception
        with patch('langchain_openai.ChatOpenAI') as mock_chat:
            mock_chat.side_effect = Exception("API Error")
            
            # Should handle error gracefully
            result = orchestrator.execute_research_call("Test topic")
            
            # Should return fallback ResearchOutput or raise specific exception
            # TODO: Define exact error handling behavior
            assert result is not None or isinstance(result, Exception)
    
    def test_invalid_budget_tier_handling(self, mock_agent_config, sample_user_input):
        """Test handling of invalid budget tier selection."""
        if DurableOrchestrator is None:
            pytest.skip("DurableOrchestrator not implemented yet")
        
        orchestrator = DurableOrchestrator(mock_agent_config)
        
        # Should raise appropriate error for invalid tier
        with pytest.raises(ValueError) as exc_info:
            orchestrator.create_research_plan(sample_user_input, "invalid_tier")
        
        assert "invalid_tier" in str(exc_info.value).lower()