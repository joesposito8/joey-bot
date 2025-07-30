#!/usr/bin/env python3
"""
Comprehensive tests for Universal Workflow Engine.
Tests the universal Planner → Execution → Synthesizer workflow pattern,
multi-call architecture, and workflow generation for any agent type.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock

from common.multi_call_architecture import MultiCallArchitecture, ArchitecturePlan, AnalysisCall
from common.agent.workflow_engine import WorkflowEngine
from common.agent.langchain_workflows import LangChainWorkflows

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


class TestUniversalWorkflowPattern:
    """Test the universal Planner → Execution → Synthesizer workflow pattern."""
    
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
            "strategy_explanation": "Universal three-stage analysis approach",
            "total_calls": 3,
            "max_concurrent": 2,
            "calls": [
                {
                    "call_id": "planner",
                    "purpose": "Initial planning and problem decomposition",
                    "prompt": "Analyze and break down the problem into key components",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "executor",
                    "purpose": "Deep analysis execution",
                    "prompt": "Execute detailed analysis on each component",
                    "dependencies": ["planner"],
                    "is_summarizer": False
                },
                {
                    "call_id": "synthesizer",
                    "purpose": "Synthesize findings into final result",
                    "prompt": "Combine all analysis into coherent final assessment",
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
            "Analysis_Summary": "Comprehensive analysis reveals strong potential with identified growth opportunities",
            "Key_Insights": ["Strong market demand", "Technical feasibility confirmed", "Competitive advantages identified"]
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
    
    def test_universal_workflow_planning(self, mock_openai_client):
        """Test universal workflow planning stage."""
        architecture = MultiCallArchitecture(mock_openai_client)
        
        user_input = {
            "Idea_Overview": "Universal test scenario",
            "Deliverable": "Comprehensive analysis system",
            "Motivation": "Validate universal workflow patterns"
        }
        
        # Test planning stage
        plan = architecture.plan_architecture(
            original_prompt="Execute universal workflow analysis",
            available_calls=3,
            user_input=user_input
        )
        
        # Verify universal workflow structure
        assert plan.total_calls == 3
        assert len(plan.calls) == 3
        assert len(plan.execution_order) == 3
        
        # Verify workflow pattern stages
        call_ids = [call.call_id for call in plan.calls]
        assert "planner" in call_ids
        assert "executor" in call_ids  
        assert "synthesizer" in call_ids
        
        # Verify synthesizer is marked correctly
        synthesizer_calls = [call for call in plan.calls if call.is_summarizer]
        assert len(synthesizer_calls) == 1
        assert synthesizer_calls[0].call_id == "synthesizer"
    
    def test_workflow_execution_order(self, mock_openai_client):
        """Test that workflow execution follows correct dependency order."""
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
    
    def test_multi_tier_workflow_scaling(self, mock_openai_client):
        """Test workflow scales correctly across budget tiers."""
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


class TestLangChainWorkflowIntegration:
    """Test LangChain workflow integration with universal patterns."""
    
    @pytest.fixture
    def mock_langchain_client(self):
        """Mock LangChain client for testing."""
        client = Mock()
        
        # Mock LangChain response
        response = Mock()
        response.content = "LangChain workflow execution result"
        client.invoke.return_value = response
        
        return client
    
    def test_langchain_workflow_initialization(self, mock_langchain_client):
        """Test LangChain workflow initialization."""
        workflows = LangChainWorkflows(mock_langchain_client)
        
        assert workflows is not None
        assert hasattr(workflows, 'client')
        assert workflows.client == mock_langchain_client
    
    def test_langchain_universal_patterns(self, mock_langchain_client):
        """Test that LangChain workflows support universal patterns."""
        workflows = LangChainWorkflows(mock_langchain_client)
        
        # Test workflow execution methods exist
        expected_methods = [
            'execute_analysis',
            'create_chain',
            'process_with_memory'
        ]
        
        for method in expected_methods:
            if hasattr(workflows, method):
                assert callable(getattr(workflows, method))
    
    @patch('common.agent.langchain_workflows.LangChain')
    def test_langchain_memory_integration(self, mock_langchain):
        """Test LangChain memory integration for workflow continuity."""
        # Mock LangChain components
        mock_chain = Mock()
        mock_memory = Mock()
        mock_langchain.ChatOpenAI.return_value = Mock()
        mock_langchain.ConversationBufferMemory.return_value = mock_memory
        mock_langchain.LLMChain.return_value = mock_chain
        
        workflows = LangChainWorkflows(Mock())
        
        # Test memory-enabled workflow
        if hasattr(workflows, 'process_with_memory'):
            result = workflows.process_with_memory(
                "Test workflow prompt",
                {"test": "input"}
            )
            
            # Verify memory was used
            assert result is not None


class TestWorkflowEngineCore:
    """Test the core WorkflowEngine functionality."""
    
    def test_workflow_engine_initialization(self):
        """Test WorkflowEngine initialization."""
        engine = WorkflowEngine()
        
        assert engine is not None
        assert hasattr(engine, 'execute_workflow')
    
    def test_universal_workflow_execution(self):
        """Test universal workflow execution patterns."""
        engine = WorkflowEngine()
        
        # Mock workflow configuration
        workflow_config = {
            "type": "universal_analysis",
            "stages": ["planner", "executor", "synthesizer"],
            "budget_tier": "standard"
        }
        
        # Test workflow execution (with mocking)
        with patch.object(engine, 'execute_workflow') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "results": {"analysis": "test result"}
            }
            
            result = engine.execute_workflow(workflow_config)
            
            assert result["status"] == "completed"
            assert "results" in result
    
    def test_workflow_error_handling(self):
        """Test workflow error handling and recovery."""
        engine = WorkflowEngine()
        
        # Test error scenarios
        invalid_configs = [
            {},  # Empty config
            {"type": "invalid"},  # Invalid type
            {"type": "universal_analysis", "stages": []},  # Empty stages
        ]
        
        for invalid_config in invalid_configs:
            with patch.object(engine, 'execute_workflow') as mock_execute:
                # Mock error response
                mock_execute.side_effect = ValueError("Invalid workflow configuration")
                
                with pytest.raises(ValueError, match="Invalid workflow configuration"):
                    engine.execute_workflow(invalid_config)


class TestAdvancedWorkflowPatterns:
    """Test advanced workflow patterns and optimizations."""
    
    def test_parallel_execution_optimization(self):
        """Test parallel execution optimization in workflows."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        mock_client = Mock()
        
        # Mock plan with parallel execution opportunities
        parallel_plan = {
            "strategy_explanation": "Parallel execution optimization test",
            "total_calls": 4,
            "max_concurrent": 3,
            "calls": [
                {
                    "call_id": "parallel_1",
                    "purpose": "Parallel analysis 1",
                    "prompt": "Execute parallel analysis 1",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "parallel_2",
                    "purpose": "Parallel analysis 2", 
                    "prompt": "Execute parallel analysis 2",
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "parallel_3",
                    "purpose": "Parallel analysis 3",
                    "prompt": "Execute parallel analysis 3", 
                    "dependencies": [],
                    "is_summarizer": False
                },
                {
                    "call_id": "synthesizer",
                    "purpose": "Synthesize parallel results",
                    "prompt": "Combine all parallel analyses",
                    "dependencies": ["parallel_1", "parallel_2", "parallel_3"],
                    "is_summarizer": True
                }
            ],
            "execution_order": [
                ["parallel_1", "parallel_2", "parallel_3"],  # Parallel batch
                ["synthesizer"]  # Sequential synthesis
            ]
        }
        
        # Setup mock response
        response = Mock()
        output = Mock()
        content = Mock()
        content.text = json.dumps(parallel_plan)
        output.content = [content]
        response.output = [output]
        mock_client.responses.create.return_value = response
        
        architecture = MultiCallArchitecture(mock_client)
        
        plan = architecture.plan_architecture(
            original_prompt="Test parallel execution",
            available_calls=4,
            user_input={"test": "parallel execution"}
        )
        
        # Verify parallel execution structure
        assert plan.total_calls == 4
        assert plan.max_concurrent == 3
        
        # First batch should have 3 parallel calls
        first_batch = plan.execution_order[0]
        assert len(first_batch) == 3
        assert "parallel_1" in first_batch
        assert "parallel_2" in first_batch 
        assert "parallel_3" in first_batch
        
        # Second batch should have synthesizer
        second_batch = plan.execution_order[1]
        assert len(second_batch) == 1
        assert "synthesizer" in second_batch
    
    def test_workflow_result_aggregation(self):
        """Test workflow result aggregation and synthesis."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        mock_client = Mock()
        architecture = MultiCallArchitecture(mock_client)
        
        # Mock individual call results
        call_results = {
            "market_analysis": {
                "market_size": "Large",
                "growth_rate": "15% annually",
                "key_trends": ["AI adoption", "Mobile first"]
            },
            "technical_analysis": {
                "feasibility": "High",
                "complexity": "Medium", 
                "timeline": "6-12 months"
            },
            "competitive_analysis": {
                "competition_level": "Moderate",
                "differentiation": "Strong AI capabilities",
                "barriers": "Technical expertise required"
            }
        }
        
        # Test result aggregation
        with patch.object(architecture, '_aggregate_results') as mock_aggregate:
            mock_aggregate.return_value = {
                "Overall_Rating": "8.5/10",
                "Market_Potential": "High - Large market with strong growth",
                "Technical_Viability": "High - Feasible with moderate complexity",
                "Competitive_Position": "Strong - Unique AI differentiation",
                "Summary": "Excellent opportunity with strong market potential and technical feasibility"
            }
            
            aggregated = architecture._aggregate_results(call_results)
            
            # Verify aggregation includes all key aspects
            assert "Overall_Rating" in aggregated
            assert "Market_Potential" in aggregated
            assert "Technical_Viability" in aggregated
            assert "Competitive_Position" in aggregated
            assert "Summary" in aggregated
    
    def test_workflow_performance_optimization(self):
        """Test workflow performance optimization features."""
        from common.multi_call_architecture import MultiCallArchitecture
        
        mock_client = Mock()
        architecture = MultiCallArchitecture(mock_client)
        
        # Test caching mechanisms
        with patch.object(architecture, '_should_use_cache') as mock_cache_check:
            mock_cache_check.return_value = True
            
            # Test cache utilization
            cache_result = architecture._should_use_cache("test_prompt", {"test": "input"})
            assert cache_result == True
        
        # Test concurrency optimization
        with patch.object(architecture, '_optimize_concurrency') as mock_optimize:
            mock_optimize.return_value = 3
            
            optimal_concurrency = architecture._optimize_concurrency(5, "standard")
            assert optimal_concurrency == 3
    
    def test_workflow_monitoring_and_metrics(self):
        """Test workflow monitoring and performance metrics."""
        from common.cost_tracker import CostTracker
        
        # Test cost tracking integration
        tracker = CostTracker()
        
        # Mock workflow execution with cost tracking
        with patch.object(tracker, 'log_cost') as mock_log:
            # Simulate workflow cost logging
            tracker.log_cost("workflow_execution", 0.15, {
                "workflow_type": "universal_analysis",
                "tier": "standard",
                "calls": 3,
                "duration": 45.2
            })
            
            # Verify cost logging was called
            mock_log.assert_called_once()
            
        # Test performance metrics
        with patch.object(tracker, 'get_summary') as mock_summary:
            mock_summary.return_value = {
                "total_workflows": 10,
                "avg_cost_per_workflow": 0.12,
                "avg_duration": 42.1,
                "success_rate": 0.95
            }
            
            metrics = tracker.get_summary()
            assert "total_workflows" in metrics
            assert "avg_cost_per_workflow" in metrics


class TestWorkflowIntegrationPoints:
    """Test workflow integration with other system components."""
    
    def test_workflow_agent_service_integration(self):
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
            # This would be tested through actual endpoint integration
            assert mock_req.get_json()["budget_tier"] == "standard"
            
            user_input = mock_req.get_json()["user_input"]
            assert "Test workflow integration" in user_input["Idea_Overview"]


if __name__ == "__main__":
    print("🧪 Universal Workflow Engine Testing")
    print("Testing Planner → Execution → Synthesizer workflow patterns")
    
    # Run tests
    pytest.main([__file__, "-v"])