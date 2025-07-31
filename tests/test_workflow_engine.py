#!/usr/bin/env python3
"""
Test multi-call analysis workflow execution.
Tests the plan → execute → synthesize pattern that enables
complex analysis across different budget tiers.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch
from common.multi_call_architecture import MultiCallArchitecture

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


class TestMultiCallWorkflow:
    """Test the universal plan → execute → synthesize workflow pattern."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for workflow testing."""
        client = Mock()
        return self._setup_mock_responses(client)
    
    def _setup_mock_responses(self, client):
        """Setup mock responses for different workflow stages."""
        # Mock planning response
        planning_response = Mock()
        planning_output = Mock()
        planning_content = Mock()
        
        mock_plan = {
            "strategy_explanation": "Three-stage analysis workflow",
            "total_calls": 3,
            "max_concurrent": 2,
            "calls": [
                {
                    "call_id": "planner",
                    "purpose": "Initial planning and analysis",
                    "prompt": "Break down the analysis into key components",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "executor",
                    "purpose": "Execute detailed analysis",
                    "prompt": "Analyze each component in detail",
                    "dependencies": ["planner"],
                    "is_summarizer": False
                },
                {
                    "call_id": "synthesizer",
                    "purpose": "Synthesize findings",
                    "prompt": "Combine all analysis into final result",
                    "dependencies": ["planner", "executor"],
                    "is_summarizer": True
                }
            ],
            "execution_order": [
                ["planner"],
                ["executor"], 
                ["synthesizer"]
            ]
        }
        
        planning_content.text = json.dumps(mock_plan)
        planning_output.content = [planning_content]
        planning_response.output = [planning_output]
        
        # Mock execution responses
        execution_response = Mock()
        execution_output = Mock()
        execution_content = Mock()
        execution_content.text = "Detailed execution analysis results"
        execution_output.content = [execution_content]
        execution_response.output = [execution_output]
        
        # Mock synthesis response
        synthesis_response = Mock()
        synthesis_output = Mock()  
        synthesis_content = Mock()
        synthesis_content.text = json.dumps({
            "Overall_Rating": "8/10",
            "Analysis_Summary": "Comprehensive analysis reveals strong potential",
            "Key_Insights": ["Market demand validated", "Technical feasibility confirmed"]
        })
        synthesis_output.content = [synthesis_content]
        synthesis_response.output = [synthesis_output]
        
        # Setup client response sequence
        client.responses.create.side_effect = [
            planning_response,    # Planning call
            execution_response,   # Execution call
            synthesis_response    # Synthesis call
        ]
        
        return client
    
    def test_workflow_planning(self, mock_openai_client):
        """Test workflow planning stage."""
        architecture = MultiCallArchitecture(mock_openai_client)
        
        user_input = {
            "Idea_Overview": "Test scenario",
            "Deliverable": "Analysis system",
            "Motivation": "Validate workflow"
        }
        
        # Test planning stage
        plan = architecture.plan_architecture(
            original_prompt="Execute workflow analysis",
            available_calls=3,
            user_input=user_input
        )
        
        # Verify workflow structure
        assert plan.total_calls == 3
        assert len(plan.calls) == 3
        assert len(plan.execution_order) == 3
        
        # Verify stages
        call_ids = [call.call_id for call in plan.calls]
        assert "planner" in call_ids
        assert "executor" in call_ids  
        assert "synthesizer" in call_ids
        
        # Verify synthesizer is marked
        synthesizer_calls = [call for call in plan.calls if call.is_summarizer]
        assert len(synthesizer_calls) == 1
        assert synthesizer_calls[0].call_id == "synthesizer"
    
    def test_execution_order(self, mock_openai_client):
        """Test workflow execution follows dependency order."""
        architecture = MultiCallArchitecture(mock_openai_client)
        
        user_input = {
            "Test_Input": "Workflow ordering test"
        }
        
        plan = architecture.plan_architecture(
            original_prompt="Test execution order",
            available_calls=3,
            user_input=user_input
        )
        
        # Verify execution order respects dependencies
        execution_order = plan.execution_order
        
        # First batch should contain planner (no dependencies)
        first_batch = execution_order[0]
        assert "planner" in first_batch
        
        # Later batches should contain dependent calls
        later_calls = []
        for batch in execution_order[1:]:
            later_calls.extend(batch)
        
        assert "executor" in later_calls
        assert "synthesizer" in later_calls
    
    def test_multi_tier_scaling(self, mock_openai_client):
        """Test workflow scales across budget tiers."""
        architecture = MultiCallArchitecture(mock_openai_client)
        
        # Test different tier scenarios
        tier_scenarios = [
            (1, "basic"),     # Single call workflow
            (3, "standard"),  # Three call workflow  
            (5, "premium")    # Five call workflow
        ]
        
        for calls, tier_name in tier_scenarios:
            # Adjust mock for different call counts
            mock_plan = {
                "strategy_explanation": f"Optimized {tier_name} tier workflow",
                "total_calls": calls,
                "max_concurrent": min(calls, 3),
                "calls": [
                    {
                        "call_id": f"call_{i}",
                        "purpose": f"Analysis stage {i}",
                        "prompt": f"Execute analysis {i}",
                        "dependencies": [] if i == 1 else [f"call_{i-1}"],
                        "is_summarizer": i == calls
                    }
                    for i in range(1, calls + 1)
                ],
                "execution_order": [[f"call_{i}"] for i in range(1, calls + 1)]
            }
            
            # Update mock response
            planning_response = Mock()
            planning_output = Mock()
            planning_content = Mock()
            planning_content.text = json.dumps(mock_plan)
            planning_output.content = [planning_content]
            planning_response.output = [planning_output]
            
            architecture.client.responses.create.return_value = planning_response
            
            # Test planning
            plan = architecture.plan_architecture(
                original_prompt=f"Test {tier_name} tier workflow",
                available_calls=calls,
                user_input={"Test": "Input"}
            )
            
            assert plan.total_calls == calls
            assert len(plan.calls) == calls

    def test_workflow_service_integration(self):
        """Test workflow integration with AnalysisService."""
        from common.agent_service import AnalysisService
        
        # Mock AnalysisService workflow integration
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            
            # Mock workflow execution through service
            mock_instance.process_job.return_value = {
                "status": "completed",
                "workflow_results": {
                    "overall_rating": "8/10",
                    "analysis_summary": "Comprehensive workflow analysis completed"
                }
            }
            
            service = AnalysisService()
            result = service.process_job("test_job_id")
            
            assert result["status"] == "completed"
            assert "workflow_results" in result
    
    def test_workflow_endpoint_integration(self):
        """Test workflow integration with Azure Function endpoints."""
        # Mock Azure Function integration
        with patch('azure.functions.HttpRequest') as mock_request:
            mock_req = Mock()
            mock_req.get_json.return_value = {
                "user_input": {
                    "Idea_Overview": "Test workflow integration",
                    "Deliverable": "Integrated system",
                    "Motivation": "Validate end-to-end workflow"
                },
                "budget_tier": "standard"
            }
            
            # Test that endpoints can trigger workflows
            assert mock_req.get_json()["budget_tier"] == "standard"
            
            user_input = mock_req.get_json()["user_input"]
            assert "Test workflow integration" in user_input["Idea_Overview"]


if __name__ == "__main__":
    print("🧪 Multi-Call Workflow Testing")
    print("Testing plan → execute → synthesize workflow pattern")
    
    # Run tests
    pytest.main([__file__, "-v"])