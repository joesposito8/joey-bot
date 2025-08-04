"""
Test duplicate request prevention mechanisms.
"""

import pytest
import hashlib
import json
import os
from unittest.mock import Mock, patch

from common.agent_service import AnalysisService


@pytest.fixture
def analysis_service():
    """Create analysis service for testing."""
    # Set testing mode environment variable
    os.environ['TESTING_MODE'] = 'true'
    return AnalysisService("test_spreadsheet_id")


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return {
        "Idea_Overview": "AI-powered fitness app",
        "Deliverable": "Mobile application with personalized workouts",
        "Motivation": "Help people achieve fitness goals with AI guidance"
    }


class TestDuplicatePrevention:
    """Test suite for duplicate request prevention."""

    def test_job_fingerprint_generation(self, analysis_service, sample_user_input):
        """Test that identical inputs generate identical fingerprints."""
        budget_tier = "standard"
        
        # Generate fingerprint twice with same inputs
        fingerprint1 = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        fingerprint2 = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        
        # Should be identical
        assert fingerprint1 == fingerprint2
        assert len(fingerprint1) == 16  # Should be 16-character hex
        
    def test_job_fingerprint_uniqueness(self, analysis_service, sample_user_input):
        """Test that different inputs generate different fingerprints."""
        fingerprint1 = analysis_service._generate_job_fingerprint(sample_user_input, "basic")
        fingerprint2 = analysis_service._generate_job_fingerprint(sample_user_input, "premium")
        
        # Different budget tiers should generate different fingerprints
        assert fingerprint1 != fingerprint2
        
        modified_input = sample_user_input.copy()
        modified_input["Idea_Overview"] = "Different idea"
        fingerprint3 = analysis_service._generate_job_fingerprint(modified_input, "basic")
        
        # Different user input should generate different fingerprint
        assert fingerprint1 != fingerprint3

    def test_deterministic_job_id_generation(self, analysis_service, sample_user_input):
        """Test that job IDs are deterministic for duplicate prevention."""
        budget_tier = "standard"
        
        fingerprint = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        expected_job_id = f"fp_{fingerprint}"
        
        # Verify fingerprint format
        assert len(fingerprint) == 16
        assert expected_job_id.startswith("fp_")
        
    @patch('common.agent_service.AnalysisService.spreadsheet')
    def test_existing_job_detection(self, mock_spreadsheet, analysis_service, sample_user_input):
        """Test detection of existing jobs with same fingerprint."""
        budget_tier = "standard"
        fingerprint = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        
        # Mock worksheet to simulate existing job
        mock_worksheet = Mock()
        mock_cell = Mock()
        mock_cell.row = 5
        mock_cell.value = f"fp_{fingerprint}"
        
        # Mock finding existing job
        mock_worksheet.find.return_value = mock_cell
        mock_worksheet.cell.return_value = Mock(value="existing_job_123")
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        
        # Check for existing job
        existing_job = analysis_service._check_existing_job(fingerprint)
        
        # Should find existing job
        assert existing_job is not None
        assert existing_job["job_id"] == "existing_job_123"
        assert existing_job["is_duplicate"] is True
        assert "already being processed" in existing_job["message"]

    @patch('common.agent_service.AnalysisService.spreadsheet')
    def test_no_existing_job(self, mock_spreadsheet, analysis_service, sample_user_input):
        """Test when no existing job is found."""
        budget_tier = "standard"
        fingerprint = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        
        # Mock worksheet to simulate no existing job
        mock_worksheet = Mock()
        mock_worksheet.find.return_value = None  # No existing job found
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        
        # Check for existing job
        existing_job = analysis_service._check_existing_job(fingerprint)
        
        # Should not find existing job
        assert existing_job is None

    @patch('common.agent_service.AnalysisService._check_existing_job')
    @patch('common.agent_service.AnalysisService.validate_user_input')
    def test_duplicate_request_handling(self, mock_validate, mock_check_existing, analysis_service, sample_user_input):
        """Test that duplicate requests return existing job instead of creating new one."""
        budget_tier = "standard"
        
        # Mock validation to pass
        mock_validate.return_value = None
        
        # Mock existing job found
        mock_check_existing.return_value = {
            "job_id": "existing_fp_abc123",
            "status": "processing",
            "is_duplicate": True,
            "message": "Request already being processed"
        }
        
        # Call create_analysis_job
        result = analysis_service.create_analysis_job(sample_user_input, budget_tier)
        
        # Should return existing job
        assert result["job_id"] == "existing_fp_abc123"
        assert result["is_duplicate"] is True
        assert "already being processed" in result["message"]
        
        # Validate should have been called
        mock_validate.assert_called_once_with(sample_user_input)
        
        # Check existing job should have been called
        mock_check_existing.assert_called_once()

    def test_fingerprint_includes_all_relevant_data(self, analysis_service, sample_user_input):
        """Test that fingerprint includes all data needed for proper deduplication."""
        budget_tier = "standard"
        
        # Get agent config components
        agent_id = analysis_service.agent_config.definition.agent_id
        spreadsheet_id = analysis_service.spreadsheet_id
        
        # Manually create expected fingerprint data
        expected_data = {
            "user_input": sample_user_input,
            "budget_tier": budget_tier,
            "agent_id": agent_id,
            "spreadsheet_id": spreadsheet_id
        }
        content = json.dumps(expected_data, sort_keys=True)
        expected_fingerprint = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Generate actual fingerprint
        actual_fingerprint = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
        
        # Should match
        assert actual_fingerprint == expected_fingerprint

    def test_orchestration_instance_id_setup(self, analysis_service, sample_user_input):
        """Test that orchestration input includes instance ID for deduplication."""
        budget_tier = "standard"
        
        # Mock the parts we need to isolate the orchestration setup
        with patch('common.agent_service.is_testing_mode', return_value=False), \
             patch('common.durable_orchestrator.DurableOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            
            # Mock initial result with deterministic job ID
            fingerprint = analysis_service._generate_job_fingerprint(sample_user_input, budget_tier)
            expected_job_id = f"fp_{fingerprint}"
            
            mock_orchestrator.create_initial_workflow_response.return_value = {
                "job_id": expected_job_id,
                "status": "processing",
                "research_calls_made": 0,
                "synthesis_calls_made": 0,
                "research_plan": {"topics": []},
                "final_result": None
            }
            
            with patch('common.agent_service.requests.post') as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {"id": "instance_123"}
                
                # Mock spreadsheet operations
                with patch.object(analysis_service, '_create_spreadsheet_record'), \
                     patch.object(analysis_service, '_check_existing_job', return_value=None):
                    # Call create_analysis_job
                    result = analysis_service.create_analysis_job(sample_user_input, budget_tier)
                    
                    # Verify orchestration call includes instance_id
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args
                    orchestration_input = call_args[1]["json"]
                    
                    assert "instance_id" in orchestration_input
                    assert orchestration_input["instance_id"] == expected_job_id
                    assert orchestration_input["job_id"] == expected_job_id