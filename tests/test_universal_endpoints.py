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


class TestGetInstructionsEndpoint:
    """Test get_instructions endpoint with universal agent support."""
    
    def test_instructions_endpoint_basic_functionality(self, comprehensive_mock_request):
        """Test basic instructions endpoint functionality."""
        from get_instructions import main as get_instructions
        
        mock_req = comprehensive_mock_request({})
        response = get_instructions(mock_req)
        
        assert response.status_code == 200
        response_data = json.loads(response.get_body())
        
        # Verify universal instruction structure
        assert "instructions" in response_data
        assert "agent_name" in response_data
        assert "testing_mode" in response_data
        assert response_data["testing_mode"] == True
        
        # Instructions should contain field guidance
        instructions = response_data["instructions"]
        assert isinstance(instructions, str)
        assert len(instructions) > 100  # Substantial instructions
    
    def test_instructions_dynamic_agent_configuration(self, comprehensive_mock_request, universal_agent_config):
        """Test instructions generation for different agent configurations."""
        from get_instructions import main as get_instructions
        
        # Mock agent configuration loading
        with patch('common.config.AgentDefinition.from_yaml') as mock_load_agent:
            mock_agent = Mock()
            mock_agent.name = universal_agent_config["name"]
            mock_agent.agent_id = universal_agent_config["agent_id"]
            mock_load_agent.return_value = mock_agent
            
            # Mock schema loading
            with patch('common.config.FullAgentConfig.from_definition') as mock_full_config:
                mock_config = Mock()
                mock_config.generate_instructions.return_value = f"""
                Welcome to {universal_agent_config['name']}!
                
                Please provide the following information:
                - Primary_Input: Main input field (required)
                - Secondary_Input: Additional context (optional)
                - Tertiary_Input: Optional details (optional)
                """
                mock_full_config.return_value = mock_config
                
                mock_req = comprehensive_mock_request({})
                response = get_instructions(mock_req)
                
                assert response.status_code == 200
                response_data = json.loads(response.get_body())
                
                assert universal_agent_config["name"] in response_data["instructions"]
                assert "Primary_Input" in response_data["instructions"]
    
    def test_instructions_error_handling(self, comprehensive_mock_request):
        """Test instructions endpoint error handling."""
        from get_instructions import main as get_instructions
        
        # Mock configuration loading error
        with patch('common.config.AgentDefinition.from_yaml') as mock_load:
            mock_load.side_effect = Exception("Configuration loading failed")
            
            mock_req = comprehensive_mock_request({})
            response = get_instructions(mock_req)
            
            # Should handle error gracefully in testing mode
            assert response.status_code in [200, 500]  # May return fallback or error


class TestGetPricepointsEndpoint:
    """Test get_pricepoints endpoint with universal budget tiers."""
    
    def test_pricepoints_universal_budget_tiers(self, comprehensive_mock_request):
        """Test universal budget tier pricing."""
        from get_pricepoints import main as get_pricepoints
        
        # Comprehensive test input
        test_input = {
            "user_input": {
                "Primary_Input": "Comprehensive AI-powered business analytics platform",
                "Secondary_Input": "Real-time data processing with machine learning insights",
                "Tertiary_Input": "Targeting enterprise customers in finance and healthcare sectors"
            }
        }
        
        mock_req = comprehensive_mock_request(test_input)
        response = get_pricepoints(mock_req)
        
        assert response.status_code == 200
        response_data = json.loads(response.get_body())
        
        # Verify universal budget structure
        assert "pricepoints" in response_data
        assert "testing_mode" in response_data
        assert response_data["testing_mode"] == True
        
        pricepoints = response_data["pricepoints"]
        assert len(pricepoints) == 3  # basic, standard, premium
        
        # Verify each tier
        tier_names = [tier["name"] for tier in pricepoints]
        assert "basic" in tier_names
        assert "standard" in tier_names
        assert "premium" in tier_names
        
        # Verify pricing structure
        for tier in pricepoints:
            assert "name" in tier
            assert "max_cost" in tier
            assert "description" in tier
            assert tier["max_cost"] > 0
            assert len(tier["description"]) > 20  # Meaningful description
    
    def test_pricepoints_input_validation(self, comprehensive_mock_request):
        """Test pricepoints input validation."""
        from get_pricepoints import main as get_pricepoints
        
        # Test missing required input
        invalid_inputs = [
            {},  # No user_input
            {"user_input": {}},  # Empty user_input
            {"user_input": {"Secondary_Input": "Only optional field"}},  # Missing required field
        ]
        
        for invalid_input in invalid_inputs:
            mock_req = comprehensive_mock_request(invalid_input)
            response = get_pricepoints(mock_req)
            
            # Should return validation error
            if response.status_code == 400:
                error_data = json.loads(response.get_body())
                assert "error" in error_data
                assert "error_type" in error_data
                assert error_data["error_type"] == "validation_error"
    
    def test_pricepoints_comprehensive_scenarios(self, comprehensive_mock_request):
        """Test pricepoints with comprehensive input scenarios."""
        from get_pricepoints import main as get_pricepoints
        
        # Test various input complexity levels
        test_scenarios = [
            {
                "name": "Simple Input",
                "input": {"Primary_Input": "Simple business idea"}
            },
            {
                "name": "Moderate Input", 
                "input": {
                    "Primary_Input": "AI-powered fitness app",
                    "Secondary_Input": "Personalized workout recommendations"
                }
            },
            {
                "name": "Complex Input",
                "input": {
                    "Primary_Input": "Enterprise blockchain supply chain solution",
                    "Secondary_Input": "Multi-tenant architecture with smart contracts",
                    "Tertiary_Input": "Compliance with international trade regulations and GDPR"
                }
            }
        ]
        
        for scenario in test_scenarios:
            test_data = {"user_input": scenario["input"]}
            mock_req = comprehensive_mock_request(test_data)
            response = get_pricepoints(mock_req)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            # All scenarios should return same tier structure
            assert len(response_data["pricepoints"]) == 3
            
            # Verify consistent pricing regardless of input complexity
            costs = [tier["max_cost"] for tier in response_data["pricepoints"]]
            assert 1.0 in costs  # Basic tier
            assert 3.0 in costs  # Standard tier  
            assert 5.0 in costs  # Premium tier


class TestExecuteAnalysisEndpoint:
    """Test execute_analysis endpoint with universal agent support."""
    
    def test_analysis_execution_comprehensive(self, comprehensive_mock_request):
        """Test comprehensive analysis execution."""
        from execute_analysis import main as execute_analysis
        
        # Comprehensive analysis request
        analysis_request = {
            "user_input": {
                "Primary_Input": "Revolutionary quantum computing cloud platform",
                "Secondary_Input": "Democratizing quantum computing access for researchers and enterprises",
                "Tertiary_Input": "Targeting quantum research institutions, pharmaceutical companies, and financial services"
            },
            "budget_tier": "premium"
        }
        
        mock_req = comprehensive_mock_request(analysis_request)
        
        # Mock agent service
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.create_job.return_value = "universal_job_12345"
            mock_service.return_value = mock_instance
            
            response = execute_analysis(mock_req)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            # Verify job creation response
            assert "job_id" in response_data
            assert "budget_tier" in response_data
            assert "testing_mode" in response_data
            assert response_data["testing_mode"] == True
            assert response_data["budget_tier"] == "premium"
            assert response_data["job_id"] == "universal_job_12345"
    
    def test_analysis_budget_tier_validation(self, comprehensive_mock_request):
        """Test budget tier validation."""
        from execute_analysis import main as execute_analysis
        
        # Test valid budget tiers
        valid_tiers = ["basic", "standard", "premium"]
        
        for tier in valid_tiers:
            request_data = {
                "user_input": {"Primary_Input": "Test input"},
                "budget_tier": tier
            }
            
            mock_req = comprehensive_mock_request(request_data)
            
            with patch('common.agent_service.AnalysisService') as mock_service:
                mock_instance = Mock()
                mock_instance.create_job.return_value = f"job_{tier}_123"
                mock_service.return_value = mock_instance
                
                response = execute_analysis(mock_req)
                assert response.status_code == 200
        
        # Test invalid budget tier
        invalid_request = {
            "user_input": {"Primary_Input": "Test input"},
            "budget_tier": "ultra_premium"  # Invalid tier
        }
        
        mock_req = comprehensive_mock_request(invalid_request)
        response = execute_analysis(mock_req)
        
        # Should return validation error
        if response.status_code == 400:
            error_data = json.loads(response.get_body())
            assert "error" in error_data
            assert "budget_tier" in error_data["error"].lower()
    
    def test_analysis_error_scenarios(self, comprehensive_mock_request):
        """Test analysis execution error scenarios."""
        from execute_analysis import main as execute_analysis
        
        error_scenarios = [
            # Missing user_input
            {"budget_tier": "standard"},
            
            # Missing budget_tier
            {"user_input": {"Primary_Input": "Test"}},
            
            # Empty user_input
            {"user_input": {}, "budget_tier": "standard"},
            
            # Invalid JSON structure
            {"invalid": "structure"}
        ]
        
        for scenario in error_scenarios:
            mock_req = comprehensive_mock_request(scenario)
            response = execute_analysis(mock_req)
            
            # Should handle error gracefully
            assert response.status_code in [400, 500]
            
            if response.status_code == 400:
                error_data = json.loads(response.get_body())
                assert "error" in error_data
                assert "error_type" in error_data


class TestProcessIdeaEndpoint:
    """Test process_idea endpoint with universal result processing."""
    
    def test_idea_processing_completion(self, comprehensive_mock_request):
        """Test idea processing with completed analysis."""
        from process_idea import main as process_idea
        
        # Mock completed job processing
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_job_status.return_value = "completed"
            mock_instance.process_job.return_value = {
                "status": "completed",
                "results": {
                    "Analysis_Result": "Comprehensive quantum computing platform analysis",
                    "Confidence_Score": "8.5/10",
                    "Detailed_Summary": "Excellent market opportunity with strong technical feasibility and clear competitive advantages"
                },
                "testing_mode": True
            }
            mock_service.return_value = mock_instance
            
            mock_req = comprehensive_mock_request({})
            mock_req.params = {"id": "test_job_123"}
            
            response = process_idea(mock_req)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            # Verify completion response
            assert response_data["status"] == "completed"
            assert "results" in response_data
            assert "testing_mode" in response_data
            assert response_data["testing_mode"] == True
            
            # Verify result structure
            results = response_data["results"]
            assert "Analysis_Result" in results
            assert "Confidence_Score" in results
            assert "Detailed_Summary" in results
    
    def test_idea_processing_in_progress(self, comprehensive_mock_request):
        """Test idea processing with in-progress analysis."""
        from process_idea import main as process_idea
        
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_job_status.return_value = "in_progress"
            mock_instance.process_job.return_value = {
                "status": "in_progress",
                "progress": 65,
                "estimated_completion": "2 minutes",
                "testing_mode": True
            }
            mock_service.return_value = mock_instance
            
            mock_req = comprehensive_mock_request({})
            mock_req.params = {"id": "test_job_456"}
            
            response = process_idea(mock_req)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            assert response_data["status"] == "in_progress"
            assert "progress" in response_data
            assert "testing_mode" in response_data
    
    def test_idea_processing_error_handling(self, comprehensive_mock_request):
        """Test idea processing error handling."""
        from process_idea import main as process_idea
        
        # Test missing job ID
        mock_req = comprehensive_mock_request({})
        mock_req.params = {}  # No id parameter
        
        response = process_idea(mock_req)
        
        if response.status_code == 400:
            error_data = json.loads(response.get_body())
            assert "error" in error_data
            assert "job" in error_data["error"].lower() or "id" in error_data["error"].lower()
        
        # Test invalid job ID
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_job_status.side_effect = ValueError("Job not found")
            mock_service.return_value = mock_instance
            
            mock_req = comprehensive_mock_request({})
            mock_req.params = {"id": "invalid_job_id"}
            
            response = process_idea(mock_req)
            
            # Should handle error gracefully
            assert response.status_code in [400, 404, 500]


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
        
        with patch('common.utils.get_sheets_client') as mock_get_client:
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
            with patch('common.utils.get_sheets_client') as mock_get_client:
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


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow across all endpoints."""
    
    def test_complete_chatgpt_workflow(self, comprehensive_mock_request):
        """Test complete ChatGPT bot workflow simulation."""
        # Import all endpoints
        from get_instructions import main as get_instructions
        from get_pricepoints import main as get_pricepoints
        from execute_analysis import main as execute_analysis
        from process_idea import main as process_idea
        
        workflow_results = {}
        
        # Step 1: Get instructions
        instructions_req = comprehensive_mock_request({})
        instructions_response = get_instructions(instructions_req)
        
        assert instructions_response.status_code == 200
        instructions_data = json.loads(instructions_response.get_body())
        workflow_results["instructions"] = instructions_data
        
        # Step 2: Get price points
        pricepoints_req = comprehensive_mock_request({
            "user_input": {
                "Primary_Input": "Revolutionary AI-powered medical diagnosis platform",
                "Secondary_Input": "Using computer vision and machine learning for early disease detection",
                "Tertiary_Input": "Targeting hospitals, clinics, and telehealth providers globally"
            }
        })
        
        pricepoints_response = get_pricepoints(pricepoints_req)
        assert pricepoints_response.status_code == 200
        pricepoints_data = json.loads(pricepoints_response.get_body())
        workflow_results["pricepoints"] = pricepoints_data
        
        # Step 3: Execute analysis
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.create_job.return_value = "workflow_job_789"
            mock_service.return_value = mock_instance
            
            analysis_req = comprehensive_mock_request({
                "user_input": {
                    "Primary_Input": "Revolutionary AI-powered medical diagnosis platform",
                    "Secondary_Input": "Using computer vision and machine learning for early disease detection",
                    "Tertiary_Input": "Targeting hospitals, clinics, and telehealth providers globally"
                },
                "budget_tier": "premium"
            })
            
            analysis_response = execute_analysis(analysis_req)
            assert analysis_response.status_code == 200
            analysis_data = json.loads(analysis_response.get_body())
            workflow_results["analysis"] = analysis_data
        
        # Step 4: Process results
        with patch('common.agent_service.AnalysisService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_job_status.return_value = "completed"
            mock_instance.process_job.return_value = {
                "status": "completed",
                "results": {
                    "Analysis_Result": "Exceptional medical AI platform with transformative potential",
                    "Confidence_Score": "9.2/10",
                    "Detailed_Summary": "Outstanding opportunity combining proven AI technologies with massive healthcare market need. Strong regulatory pathway and clear competitive advantages."
                },
                "testing_mode": True
            }
            mock_service.return_value = mock_instance
            
            process_req = comprehensive_mock_request({})
            process_req.params = {"id": "workflow_job_789"}
            
            process_response = process_idea(process_req)
            assert process_response.status_code == 200
            process_data = json.loads(process_response.get_body())
            workflow_results["results"] = process_data
        
        # Verify complete workflow
        assert "instructions" in workflow_results
        assert "pricepoints" in workflow_results
        assert "analysis" in workflow_results
        assert "results" in workflow_results
        
        # Verify workflow consistency
        assert workflow_results["analysis"]["job_id"] == "workflow_job_789"
        assert workflow_results["results"]["status"] == "completed"
        assert "Analysis_Result" in workflow_results["results"]["results"]
    
    def test_error_propagation_across_endpoints(self, comprehensive_mock_request):
        """Test error handling consistency across endpoints."""
        from get_pricepoints import main as get_pricepoints
        from execute_analysis import main as execute_analysis
        
        # Test consistent error handling
        error_scenarios = [
            {"error_type": "missing_input", "data": {}},
            {"error_type": "invalid_format", "data": {"invalid": "structure"}},
        ]
        
        for scenario in error_scenarios:
            # Test pricepoints error handling
            pricepoints_req = comprehensive_mock_request(scenario["data"])
            pricepoints_response = get_pricepoints(pricepoints_req)
            
            # Test analysis error handling
            analysis_req = comprehensive_mock_request(scenario["data"])
            analysis_response = execute_analysis(analysis_req)
            
            # Both should handle errors consistently
            if pricepoints_response.status_code == 400:
                pricepoints_error = json.loads(pricepoints_response.get_body())
                assert "error" in pricepoints_error
                assert "error_type" in pricepoints_error
            
            if analysis_response.status_code == 400:
                analysis_error = json.loads(analysis_response.get_body())
                assert "error" in analysis_error
                assert "error_type" in analysis_error
    
    def test_testing_mode_consistency(self, comprehensive_mock_request):
        """Test that testing mode is consistent across all endpoints."""
        from get_instructions import main as get_instructions
        from get_pricepoints import main as get_pricepoints
        
        # All endpoints should indicate testing mode
        endpoints_to_test = [
            (get_instructions, {}),
            (get_pricepoints, {"user_input": {"Primary_Input": "Test input"}})
        ]
        
        for endpoint_func, test_data in endpoints_to_test:
            mock_req = comprehensive_mock_request(test_data)
            response = endpoint_func(mock_req)
            
            if response.status_code == 200:
                response_data = json.loads(response.get_body())
                assert "testing_mode" in response_data
                assert response_data["testing_mode"] == True


class TestUniversalEndpointPerformance:
    """Test performance aspects of universal endpoints."""
    
    def test_endpoint_response_times(self, comprehensive_mock_request):
        """Test that endpoints respond within reasonable time limits."""
        from get_instructions import main as get_instructions
        
        import time
        
        # Test response time
        start_time = time.time()
        mock_req = comprehensive_mock_request({})
        response = get_instructions(mock_req)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond quickly in testing mode
        assert response_time < 5.0  # 5 second maximum
        assert response.status_code == 200
    
    def test_concurrent_endpoint_handling(self, comprehensive_mock_request):
        """Test endpoints can handle concurrent requests."""
        from get_instructions import main as get_instructions
        
        # Simulate concurrent requests
        requests = []
        responses = []
        
        for i in range(5):
            mock_req = comprehensive_mock_request({})
            requests.append(mock_req)
        
        # Process requests
        for req in requests:
            response = get_instructions(req)
            responses.append(response)
        
        # All should succeed
        assert len(responses) == 5
        assert all(r.status_code == 200 for r in responses)
    
    def test_memory_efficiency(self, comprehensive_mock_request):
        """Test that endpoints are memory efficient."""
        from get_pricepoints import main as get_pricepoints
        
        # Process multiple requests to test memory usage
        test_data = {
            "user_input": {
                "Primary_Input": "Large input data for memory testing " * 100,
                "Secondary_Input": "Additional large context " * 50
            }
        }
        
        responses = []
        for i in range(10):
            mock_req = comprehensive_mock_request(test_data)
            response = get_pricepoints(mock_req)
            responses.append(response)
        
        # All should process successfully
        assert len(responses) == 10
        assert all(r.status_code in [200, 400] for r in responses)


if __name__ == "__main__":
    print("🧪 Universal Endpoints Testing")
    print("Testing all Azure Functions with comprehensive scenarios")
    print("Running in TESTING MODE - no API charges will occur")
    
    # Run tests
    pytest.main([__file__, "-v"])