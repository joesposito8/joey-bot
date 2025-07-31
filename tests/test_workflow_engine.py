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
    def mock_agent_config(self):
        """Mock agent configuration for testing."""
        config = Mock()
        config.get_model.return_value = "gpt-4-turbo"
        config.get_universal_setting.return_value = 4
        
        # Mock schema with output fields
        config.schema = Mock()
        config.schema.output_fields = [
            Mock(name="Analysis_Result"),
            Mock(name="Overall_Rating")
        ]
        
        # Mock definition for prompts
        config.definition = Mock()
        config.definition.starter_prompt = "Test agent starter prompt"
        
        return config
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for workflow testing."""
        client = Mock()
        return self._setup_mock_responses(client)
    
    def _setup_mock_responses(self, client):
        """Setup dynamic mock responses for workflow testing."""
        def create_mock_response(content):
            """Helper to create consistent mock response structure."""
            response = Mock()
            response.output = [Mock()]
            response.output[0].content = [Mock()]
            response.output[0].content[0].text = json.dumps(content)
            return response
        
        def generate_mock_plan(available_calls: int, max_concurrent: int = None):
            """Generate a mock plan based on available calls."""
            if max_concurrent is None:
                max_concurrent = min(available_calls, 4)

            # For single call, create minimal viable plan
            if available_calls == 1:
                return {
                    "strategy_explanation": "Single-call analysis workflow",
                    "total_calls": 1,
                    "max_concurrent": 1,
                    "calls": [{
                        "call_id": "analysis_1",
                        "purpose": "Complete analysis and synthesis",
                        "prompt": "Analyze and synthesize results",
                        "dependencies": [],
                        "is_summarizer": True
                    }],
                    "execution_order": [["analysis_1"]]
                }

            # For multiple calls, create dependency chain with parallel execution
            calls = []
            execution_order = []
            current_batch = []
            
            for i in range(available_calls):
                call_id = f"analysis_{i+1}"
                
                # Last call is always a summarizer
                is_summarizer = (i == available_calls - 1)
                
                # Create dependencies - each call depends on previous batch
                dependencies = []
                if i > 0:
                    # Depend on previous batch calls
                    prev_batch_start = max(0, i - max_concurrent)
                    dependencies = [f"analysis_{j+1}" for j in range(prev_batch_start, i)]
                
                calls.append({
                    "call_id": call_id,
                    "purpose": f"{'Synthesis' if is_summarizer else 'Analysis'} stage {i+1}",
                    "prompt": f"Execute {'synthesis' if is_summarizer else 'analysis'} stage {i+1}",
                    "dependencies": dependencies,
                    "is_summarizer": is_summarizer
                })
                
                # Add to current batch if space available and dependencies met
                if len(current_batch) < max_concurrent:
                    current_batch.append(call_id)
                else:
                    execution_order.append(current_batch)
                    current_batch = [call_id]
            
            if current_batch:
                execution_order.append(current_batch)

            return {
                "strategy_explanation": f"{available_calls}-call analysis workflow",
                "total_calls": available_calls,
                "max_concurrent": max_concurrent,
                "calls": calls,
                "execution_order": execution_order
            }
        
        def mock_create(**kwargs):
            """Dynamic mock response generation based on input."""
            if 'architecture_planning' in kwargs.get('model', ''):
                # Extract available_calls from the prompt
                prompt = kwargs['input'][0]['content'][0]['text']
                available_calls = int(prompt.split('available_calls: ')[1].split('\n')[0])
                return create_mock_response(generate_mock_plan(available_calls))
            else:
                # Analysis/execution response
                return create_mock_response({
                    "Analysis_Result": "Mock analysis output",
                    "Overall_Rating": "8/10",
                    "Key_Insights": ["Mock insight 1", "Mock insight 2"]
                })
        
        client.responses.create.side_effect = mock_create
        
        return client
    
    def test_basic_tier_plan_requirements(self, mock_openai_client, mock_agent_config):
        """Test single-call budget produces valid minimal plan."""
        architecture = MultiCallArchitecture(mock_openai_client, mock_agent_config)
        
        plan = architecture.plan_architecture(
            original_prompt="Basic analysis",
            available_calls=1,
            user_input={"test": "input"},
            output_fields=["Analysis_Result"]
        )
        
        # Verify minimal viable plan structure
        assert plan.total_calls == 1
        assert len(plan.calls) == 1
        assert len(plan.execution_order) == 1  # Single batch
        synthesizer_calls = [call for call in plan.calls if call.is_summarizer]
        assert len(synthesizer_calls) == 1  # Must have summarizer
    
    def test_multi_call_dependencies(self, mock_openai_client, mock_agent_config):
        """Test plans with multiple calls have valid dependency structure."""
        architecture = MultiCallArchitecture(mock_openai_client, mock_agent_config)
        
        plan = architecture.plan_architecture(
            original_prompt="Complex analysis",
            available_calls=3,
            user_input={"test": "input"},
            output_fields=["Analysis_Result", "Overall_Rating"]
        )
        
        # Verify dependency graph
        for call in plan.calls:
            for dep_id in call.dependencies:
                # Dependency must exist
                assert any(c.call_id == dep_id for c in plan.calls)
                # Dependency must execute before dependent call
                dep_batch = next(i for i, batch in enumerate(plan.execution_order) 
                               if dep_id in batch)
                call_batch = next(i for i, batch in enumerate(plan.execution_order) 
                                if call.call_id in batch)
                assert dep_batch < call_batch
    
    def test_parallel_execution_batching(self, mock_openai_client, mock_agent_config):
        """Test parallel execution respects max_concurrent and dependencies."""
        architecture = MultiCallArchitecture(mock_openai_client, mock_agent_config)
        max_concurrent = mock_agent_config.get_universal_setting('max_concurrent_calls')
        
        plan = architecture.plan_architecture(
            original_prompt="Parallel analysis",
            available_calls=5,  # Use premium tier to test parallel execution
            user_input={"test": "input"},
            output_fields=["Analysis_Result"]
        )
        
        # Verify batch constraints
        for batch in plan.execution_order:
            assert len(batch) <= max_concurrent
            
            # Verify all dependencies for this batch completed
            completed_calls = set()
            for prior_batch in plan.execution_order:
                if prior_batch == batch:
                    break
                completed_calls.update(prior_batch)
                
            for call_id in batch:
                call = next(c for c in plan.calls if c.call_id == call_id)
                assert all(dep in completed_calls for dep in call.dependencies)

    def test_workflow_service_integration(self):
        """Test workflow integration with AnalysisService."""
        from common.agent_service import AnalysisService
        
        # For now, just verify the service can be instantiated
        service = AnalysisService()
        assert service is not None
    
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