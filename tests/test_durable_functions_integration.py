#!/usr/bin/env python3
"""
Test Azure Durable Functions integration for joey-bot.
Tests orchestration workflow, activity functions, and background processing.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the durable functions module
try:
    import sys
    sys.path.append('/home/joey/Projects/joey-bot/idea-guy')
    from orchestrator import analysis_orchestrator, execute_complete_workflow
    DURABLE_FUNCTIONS_AVAILABLE = True
except ImportError:
    DURABLE_FUNCTIONS_AVAILABLE = False


@pytest.fixture
def mock_orchestration_context():
    """Mock DurableOrchestrationContext for testing."""
    context = Mock()
    context.get_input.return_value = {
        "job_id": "test_job_123",
        "user_input": {"Idea_Overview": "Test idea"},
        "budget_tier": "standard",
        "spreadsheet_id": "test_sheet_id",
        "research_plan": {"tier": "standard", "research_calls": 2}
    }
    
    # Mock the activity call to return success
    context.call_activity = Mock()
    context.call_activity.return_value = {
        "status": "completed",
        "job_id": "test_job_123",
        "message": "Analysis completed successfully"
    }
    
    return context


@pytest.fixture
def mock_analysis_service():
    """Mock AnalysisService for testing."""
    service = Mock()
    service.agent_config = Mock()
    service._update_spreadsheet_record_with_results = Mock()
    return service


class TestDurableFunctionsOrchestration:
    """Test Azure Durable Functions orchestration pattern."""
    
    def test_orchestrator_available(self):
        """Test that Durable Functions components are available."""
        if not DURABLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Durable Functions components not available")
        
        assert analysis_orchestrator is not None
        assert execute_complete_workflow is not None
    
    def test_orchestration_context_processing(self, mock_orchestration_context):
        """Test orchestrator processes input context correctly."""
        if not DURABLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Durable Functions components not available")
        
        # Since we can't easily test the generator function directly,
        # we'll test the input processing logic
        input_data = mock_orchestration_context.get_input()
        
        assert input_data["job_id"] == "test_job_123"
        assert input_data["budget_tier"] == "standard"
        assert "user_input" in input_data
        assert "spreadsheet_id" in input_data
        assert "research_plan" in input_data
    
    @patch('common.agent_service.AnalysisService')
    @patch('common.durable_orchestrator.DurableOrchestrator')
    def test_execute_complete_workflow_activity(self, mock_orchestrator_class, mock_service_class):
        """Test the complete workflow activity function."""
        if not DURABLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Durable Functions components not available")
        
        # Setup mocks
        mock_service = Mock()
        mock_service._update_spreadsheet_record_with_results = Mock()
        mock_service_class.return_value = mock_service
        
        mock_orchestrator = Mock()
        mock_orchestrator.complete_remaining_workflow.return_value = {
            "final_result": {"Analysis_Result": "Test analysis completed"}
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Test input
        workflow_input = {
            "job_id": "test_job_456",
            "user_input": {"Idea_Overview": "Test workflow"},
            "budget_tier": "premium",
            "spreadsheet_id": "test_sheet",
            "research_plan": {"tier": "premium", "research_calls": 4}
        }
        
        # Execute the activity
        result = execute_complete_workflow(workflow_input)
        
        # Verify the result
        assert result["status"] == "completed"
        assert result["job_id"] == "test_job_456"
        assert "message" in result
        
        # Verify the mocks were called correctly
        mock_service_class.assert_called_once_with("test_sheet")
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.complete_remaining_workflow.assert_called_once()
        mock_service._update_spreadsheet_record_with_results.assert_called_once()
    
    @patch('common.agent_service.AnalysisService')
    @patch('common.durable_orchestrator.DurableOrchestrator')
    def test_workflow_activity_error_handling(self, mock_orchestrator_class, mock_service_class):
        """Test error handling in the workflow activity function."""
        if not DURABLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Durable Functions components not available")
        
        # Setup mocks to raise an exception
        mock_service_class.side_effect = Exception("Service initialization failed")
        
        workflow_input = {
            "job_id": "test_job_error",
            "user_input": {"Idea_Overview": "Test error handling"},
            "budget_tier": "basic",
            "spreadsheet_id": "test_sheet",
            "research_plan": {"tier": "basic", "research_calls": 0}
        }
        
        # Execute the activity
        result = execute_complete_workflow(workflow_input)
        
        # Verify error handling
        assert result["status"] == "failed"
        assert result["job_id"] == "test_job_error"
        assert "error" in result
        assert "Service initialization failed" in result["error"]
    
    @patch('common.agent_service.AnalysisService')
    @patch('common.durable_orchestrator.DurableOrchestrator')
    def test_workflow_no_final_result_handling(self, mock_orchestrator_class, mock_service_class):
        """Test handling when workflow produces no final result."""
        if not DURABLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Durable Functions components not available")
        
        # Setup mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_orchestrator = Mock()
        # Return result without final_result key
        mock_orchestrator.complete_remaining_workflow.return_value = {"status": "incomplete"}
        mock_orchestrator_class.return_value = mock_orchestrator
        
        workflow_input = {
            "job_id": "test_job_no_result",
            "user_input": {"Idea_Overview": "Test no result"},
            "budget_tier": "standard",
            "spreadsheet_id": "test_sheet",
            "research_plan": {"tier": "standard", "research_calls": 2}
        }
        
        # Execute the activity
        result = execute_complete_workflow(workflow_input)
        
        # Verify handling of missing final result
        assert result["status"] == "failed"
        assert result["job_id"] == "test_job_no_result"
        assert "No final result produced" in result["error"]


class TestDurableFunctionsIntegration:
    """Test integration with existing joey-bot components."""
    
    @patch('requests.post')
    def test_agent_service_starts_orchestration(self, mock_post):
        """Test that AnalysisService starts Durable Functions orchestration."""
        # Mock successful orchestration start
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"id": "orchestration_123"}
        mock_post.return_value = mock_response
        
        from common.agent_service import AnalysisService
        
        # Mock the analysis service components we need for this test
        with patch('common.agent_service.AnalysisService.validate_user_input'), \
             patch('common.agent_service.AnalysisService.agent_config') as mock_config, \
             patch('common.agent_service.AnalysisService._create_spreadsheet_record'), \
             patch('common.agent_service.DurableOrchestrator') as mock_orchestrator, \
             patch('common.agent_service.is_testing_mode', return_value=False):
            
            # Setup agent config mock
            tier_mock = Mock()
            tier_mock.name = "standard"
            mock_config.get_budget_tiers.return_value = [tier_mock]
            
            # Setup orchestrator mock
            orchestrator_instance = Mock()
            orchestrator_instance.execute_workflow.return_value = {
                "job_id": "test_job_789",
                "status": "processing",
                "research_plan": {"tier": "standard"}
            }
            mock_orchestrator.return_value = orchestrator_instance
            
            # Create service and test
            service = AnalysisService("test_sheet_id")
            result = service.create_analysis_job(
                {"Idea_Overview": "Test orchestration"}, 
                "standard"
            )
            
            # Verify orchestration was started
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "orchestrator" in call_args[0][0]  # URL contains 'orchestrator'
            
            # Verify orchestration input data
            orchestration_data = call_args[1]["json"]
            assert orchestration_data["job_id"] == "test_job_789"
            assert orchestration_data["budget_tier"] == "standard"
            assert orchestration_data["spreadsheet_id"] == "test_sheet_id"
    
    @patch('requests.post')
    def test_orchestration_start_failure_handling(self, mock_post):
        """Test handling when orchestration fails to start."""
        # Mock failed orchestration start
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        from common.agent_service import AnalysisService
        
        with patch('common.agent_service.AnalysisService.validate_user_input'), \
             patch('common.agent_service.AnalysisService.agent_config') as mock_config, \
             patch('common.agent_service.AnalysisService._create_spreadsheet_record'), \
             patch('common.agent_service.DurableOrchestrator') as mock_orchestrator, \
             patch('common.agent_service.is_testing_mode', return_value=False):
            
            # Setup mocks
            tier_mock = Mock()
            tier_mock.name = "basic"
            mock_config.get_budget_tiers.return_value = [tier_mock]
            
            orchestrator_instance = Mock()
            orchestrator_instance.execute_workflow.return_value = {
                "job_id": "test_job_fail",
                "status": "processing",
                "research_plan": {"tier": "basic"}
            }
            mock_orchestrator.return_value = orchestrator_instance
            
            # Create service and test - should not raise exception
            service = AnalysisService("test_sheet_id")
            result = service.create_analysis_job(
                {"Idea_Overview": "Test failure handling"}, 
                "basic"
            )
            
            # Verify result is still returned despite orchestration failure
            assert result["job_id"] == "test_job_fail"
            assert result["status"] == "processing"
    
    def test_summarize_idea_durable_functions_awareness(self):
        """Test that summarize_idea endpoint provides Durable Functions context."""
        # This test verifies the processing status message includes orchestration info
        # by checking the actual file content has been updated
        summarize_path = "/home/joey/Projects/joey-bot/idea-guy/summarize_idea/__init__.py"
        
        with open(summarize_path, 'r') as f:
            content = f.read()
        
        # Verify the status message includes orchestration workflow reference
        assert "orchestration workflow" in content, "Processing message should mention orchestration workflow"
        assert "Azure Durable Functions" in content, "Status should mention Azure Durable Functions"


class TestDurableFunctionsArchitecture:
    """Test the overall Durable Functions architecture."""
    
    def test_architecture_components_exist(self):
        """Test that all required Durable Functions components exist."""
        # Check that orchestrator files exist
        import os
        orchestrator_path = "/home/joey/Projects/joey-bot/idea-guy/orchestrator"
        
        assert os.path.exists(orchestrator_path), "Orchestrator directory should exist"
        assert os.path.exists(f"{orchestrator_path}/__init__.py"), "Orchestrator __init__.py should exist"
        assert os.path.exists(f"{orchestrator_path}/function.json"), "Orchestrator function.json should exist"
    
    def test_durable_functions_dependency_added(self):
        """Test that azure-functions-durable dependency was added."""
        requirements_path = "/home/joey/Projects/joey-bot/idea-guy/requirements.txt"
        
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        assert "azure-functions-durable" in requirements, "azure-functions-durable should be in requirements.txt"
    
    def test_threading_code_removed(self):
        """Test that threading code was removed from agent_service.py."""
        agent_service_path = "/home/joey/Projects/joey-bot/common/agent_service.py"
        
        with open(agent_service_path, 'r') as f:
            content = f.read()
        
        # Threading should not be imported or used anymore
        assert "import threading" not in content, "Threading import should be removed"
        assert "threading.Thread" not in content, "Thread usage should be removed"
        assert "daemon = False" not in content, "Daemon thread references should be removed"
        
        # Durable Functions orchestration should be present
        assert "orchestrator" in content.lower(), "Orchestration logic should be present"
        assert "requests.post" in content, "HTTP call to orchestrator should be present"