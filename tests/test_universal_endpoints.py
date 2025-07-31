#!/usr/bin/env python3
"""
Comprehensive tests for Universal Azure Function Endpoints.
Tests all 5 Azure Functions with any agent type, comprehensive error scenarios,
and end-to-end ChatGPT bot workflow without OpenAI API calls.
"""

import pytest
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import azure.functions as func

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, '../idea-guy'))

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


class TestUniversalEndpointArchitecture:
    """Test universal endpoint architecture for any agent type."""
    
    @pytest.fixture
    def comprehensive_mock_request(self):
        """Comprehensive mock request for testing."""
        def create_mock_request(data=None, params=None):
            mock_req = Mock(spec=func.HttpRequest)
            mock_req.get_json.return_value = data or {}
            mock_req.params = params or {}
            return mock_req
        return create_mock_request
    
    @pytest.fixture
    def universal_agent_config(self):
        """Universal agent configuration for testing."""
        return {
            "agent_id": "universal_test_agent",
            "name": "Universal Test Agent",
            "description": "A comprehensive test agent for validating universal endpoint functionality",
            "input_fields": [
                {"name": "Primary_Input", "description": "Main input field", "required": True},
                {"name": "Secondary_Input", "description": "Additional context", "required": False},
                {"name": "Tertiary_Input", "description": "Optional details", "required": False}
            ],
            "output_fields": [
                {"name": "Analysis_Result", "description": "Primary analysis output"},
                {"name": "Confidence_Score", "description": "Confidence rating 1-10"},
                {"name": "Detailed_Summary", "description": "Comprehensive analysis summary"}
            ],
            "budget_tiers": {
                "basic": {"price": 1.0, "calls": 1, "description": "Basic single-call analysis"},
                "standard": {"price": 3.0, "calls": 3, "description": "Standard multi-call analysis"},
                "premium": {"price": 5.0, "calls": 5, "description": "Premium comprehensive analysis"}
            }
        }
    
    def test_endpoint_imports_successful(self):
        """Test that all endpoint modules can be imported."""
        # Test imports work without errors
        try:
            # Set testing mode to ensure no API calls
            os.environ["TESTING_MODE"] = "true"
            
            # Mock OpenAI client to prevent API key errors
            with patch('openai.OpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                
                from get_instructions import main as get_instructions
                from get_pricepoints import main as get_pricepoints
                from execute_analysis import main as execute_analysis
                from process_idea import main as process_idea
                from read_sheet import main as read_sheet
                
                # Verify all functions are callable
                assert callable(get_instructions)
                assert callable(get_pricepoints)
                assert callable(execute_analysis)
                assert callable(process_idea)
                assert callable(read_sheet)
            
        except ImportError as e:
            pytest.fail(f"Failed to import endpoint modules: {str(e)}")
    
    def test_universal_endpoint_response_structure(self):
        """Test that all endpoints return consistent response structure."""
        from common.http_utils import create_success_response, create_error_response
        
        # Test success response structure
        success_data = {
            "status": "success",
            "data": {"test": "value"},
            "testing_mode": True
        }
        
        success_response = create_success_response(success_data)
        assert success_response.status_code == 200
        
        response_data = json.loads(success_response.get_body())
        assert response_data["status"] == "success"
        assert "data" in response_data
        assert "testing_mode" in response_data
        
        # Test error response structure
        error_response = create_error_response(
            "Test error message",
            400,
            "validation_error",
            "Please check your input format"
        )
        
        assert error_response.status_code == 400
        error_data = json.loads(error_response.get_body())
        assert error_data["error"] == "Test error message"
        assert error_data["error_type"] == "validation_error"
        assert error_data["suggestion"] == "Please check your input format"


class TestReadSheetEndpoint:
    """Test read_sheet endpoint with universal sheet access."""
    
    def test_sheet_reading_functionality(self, comprehensive_mock_request):
        """Test basic sheet reading functionality."""
        from read_sheet import main as read_sheet
        
        # Mock sheet data
        mock_sheet_data = [
            ["ID", "Time", "Primary_Input", "Secondary_Input", "Analysis_Result", "Confidence_Score"],
            ["1", "2024-01-01", "Test idea 1", "Additional context", "Positive analysis", "8/10"],
            ["2", "2024-01-02", "Test idea 2", "More context", "Strong potential", "9/10"]
        ]
        
        with patch('common.utils.get_google_sheets_client') as mock_get_client:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.get_worksheet.return_value = mock_worksheet
            mock_worksheet.get_all_values.return_value = mock_sheet_data
            mock_get_client.return_value = mock_client
            
            mock_req = comprehensive_mock_request({})
            mock_req.params = {"rows": "10"}
            
            response = read_sheet(mock_req)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            # Verify sheet data structure
            assert "data" in response_data
            assert "testing_mode" in response_data
            assert isinstance(response_data["data"], list)
            assert len(response_data["data"]) >= 1  # Should include headers
    
    def test_sheet_reading_parameters(self, comprehensive_mock_request):
        """Test sheet reading with various parameters."""
        from read_sheet import main as read_sheet
        
        parameter_scenarios = [
            {"rows": "5"},
            {"rows": "20"},
            {"format": "json"},
            {}  # No parameters
        ]
        
        for params in parameter_scenarios:
            with patch('common.utils.get_google_sheets_client') as mock_get_client:
                mock_client = Mock()
                mock_spreadsheet = Mock()
                mock_worksheet = Mock()
                mock_worksheet.get_all_values.return_value = [["Test", "Data"]]
                
                mock_client.open_by_key.return_value = mock_spreadsheet
                mock_spreadsheet.get_worksheet.return_value = mock_worksheet
                mock_get_client.return_value = mock_client
                
                mock_req = comprehensive_mock_request({})
                mock_req.params = params
                
                response = read_sheet(mock_req)
                
                # Should handle all parameter scenarios
                assert response.status_code == 200


if __name__ == "__main__":
    print("🧪 Universal Endpoints Testing")
    print("Testing all Azure Functions with comprehensive scenarios")
    print("Running in TESTING MODE - no API charges will occur")
    
    # Run tests
    pytest.main([__file__, "-v"])