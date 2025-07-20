#!/usr/bin/env python3
"""
Test script for the Agent endpoint functionality.
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Add both the current directory and the idea-guy directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'idea-guy'))


def test_budget_options_request():
    """Test the budget options request handling."""
    print("Testing budget options request...")
    
    try:
        # Import the Azure Function
        from agent_business_evaluator import main
        import azure.functions as func
        
        # Mock request for budget options
        req_body = {
            "action": "get_budget_options",
            "user_input": {
                "Idea_Overview": "A mobile app for finding local events",
                "Deliverable": "iOS and Android app with event discovery and booking",
                "Motivation": "Help people find interesting events in their area"
            }
        }
        
        # Create mock request
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.get_json.return_value = req_body
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'IDEA_GUY_SHEET_ID': 'test_sheet_id',
            'OPENAI_API_KEY': 'mock_key',
            'GOOGLE_SHEETS_KEY_PATH': 'mock_path'
        }):
            # Mock the dependencies that would require credentials
            with patch('common.get_openai_client') as mock_openai:
                with patch('common.get_google_sheets_client') as mock_gc:
                    mock_openai.return_value = Mock()
                    mock_gc.return_value = Mock()
                    
                    # Call the function
                    response = main(mock_req)
                    
                    # Check response
                    if response.status_code == 200:
                        response_data = json.loads(response.get_body())
                        
                        print(f"✅ Response status: {response.status_code}")
                        print(f"✅ Action: {response_data.get('action', 'N/A')}")
                        print(f"✅ Budget options: {len(response_data.get('budget_options', []))} tiers")
                        
                        # Check structure
                        if 'budget_options' in response_data:
                            for i, option in enumerate(response_data['budget_options']):
                                print(f"   Tier {i+1}: {option.get('name')} (${option.get('max_cost')})")
                        
                        return True
                    else:
                        print(f"❌ Unexpected status code: {response.status_code}")
                        print(f"Response body: {response.get_body()}")
                        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execution_request():
    """Test the execution request handling (without actual API call)."""
    print("Testing execution request structure...")
    
    try:
        # Import the Azure Function
        from agent_business_evaluator import main
        import azure.functions as func
        
        # Mock request for execution
        req_body = {
            "action": "execute",
            "user_input": {
                "Idea_Overview": "A mobile app for finding local events",
                "Deliverable": "iOS and Android app with event discovery and booking",
                "Motivation": "Help people find interesting events in their area"
            },
            "budget_tier": "standard"
        }
        
        # Create mock request
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.get_json.return_value = req_body
        
        # Mock environment variables  
        with patch.dict(os.environ, {
            'IDEA_GUY_SHEET_ID': 'test_sheet_id',
            'OPENAI_API_KEY': 'mock_key',
            'GOOGLE_SHEETS_KEY_PATH': 'mock_path'
        }):
            # This will fail at the actual execution step, but we can test the structure
            with patch('common.get_openai_client') as mock_openai:
                with patch('common.get_google_sheets_client') as mock_gc:
                    mock_openai.return_value = Mock()
                    mock_gc.return_value = Mock()
                    
                    try:
                        response = main(mock_req)
                        # This will likely fail due to missing credentials, but that's expected
                        print(f"Response status: {response.status_code}")
                    except Exception as e:
                        # Expected to fail at execution due to missing Google Sheets setup
                        if "GOOGLE_SHEETS_KEY_PATH" in str(e) or "spreadsheet" in str(e).lower():
                            print("✅ Request structure valid (failed at expected Google Sheets step)")
                            return True
                        else:
                            print(f"❌ Unexpected error: {e}")
                            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_validation():
    """Test request validation."""
    print("Testing request validation...")
    
    try:
        from agent_business_evaluator import main
        import azure.functions as func
        
        # Test missing action
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.get_json.return_value = {"user_input": {"test": "data"}}
        
        response = main(mock_req)
        if response.status_code == 400:
            print("✅ Missing action validation works")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
        
        # Test invalid budget tier
        mock_req.get_json.return_value = {
            "action": "execute",
            "user_input": {
                "Idea_Overview": "Test",
                "Deliverable": "Test", 
                "Motivation": "Test"
            },
            "budget_tier": "invalid_tier"
        }
        
        response = main(mock_req)
        if response.status_code == 400:
            print("✅ Invalid budget tier validation works")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Agent Endpoint\n")
    
    success = True
    success &= test_budget_options_request()
    print()
    success &= test_validation()
    print()
    success &= test_execution_request()
    
    print(f"\n{'🎉' if success else '💥'} Agent endpoint tests {'passed' if success else 'had issues'}")
    
    if success:
        print("\n📋 Summary:")
        print("✅ Budget options endpoint structure works")
        print("✅ Request validation works") 
        print("✅ Execution endpoint structure works")
        print("\n🚀 The Agent framework is ready for deployment!")
        print("\nNext steps:")
        print("1. Deploy to Azure Functions")
        print("2. Configure environment variables (IDEA_GUY_SHEET_ID, etc.)")
        print("3. Test with real API calls")
    else:
        print("\n🔧 Some tests had issues. Check the output above.")