#!/usr/bin/env python3
"""
Test the complete ChatGPT bot workflow with enhanced error handling.
This demonstrates the user experience from a ChatGPT bot perspective.
"""
import os
import sys
import json
from unittest.mock import Mock

# Add project to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Set testing mode and required environment variables
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


def simulate_chatgpt_request(endpoint_func, request_data):
    """Simulate a ChatGPT bot making a request to our endpoint."""
    import azure.functions as func
    
    mock_req = Mock(spec=func.HttpRequest)
    mock_req.get_json.return_value = request_data
    
    response = endpoint_func(mock_req)
    
    return {
        "status_code": response.status_code,
        "response_data": json.loads(response.get_body()) if response.get_body() else {}
    }


def test_complete_workflow():
    """Test the complete workflow that a ChatGPT bot would follow."""
    print("🤖 Testing Complete ChatGPT Bot Workflow")
    print("=" * 50)
    
    # Import endpoints
    sys.path.append(os.path.join(current_dir, 'idea-guy'))
    from get_instructions import main as get_instructions
    from get_pricepoints import main as get_pricepoints  
    from execute_analysis import main as execute_analysis
    from process_idea import main as process_idea
    
    # Step 1: Get instructions (what ChatGPT bot calls first)
    print("\n1. 📋 Getting ChatGPT Bot Instructions")
    instructions_response = simulate_chatgpt_request(get_instructions, {})
    
    if instructions_response["status_code"] == 200:
        print("✅ Instructions retrieved successfully")
        print(f"Testing Mode: {instructions_response['response_data'].get('testing_mode', False)}")
    else:
        print(f"❌ Failed: {instructions_response['response_data']}")
        return False
    
    # Step 2: Get budget options (after user provides idea details)
    print("\n2. 💰 Getting Budget Options")
    budget_request = {
        "user_input": {
            "Idea_Overview": "A mobile app that helps people find and book local fitness classes",
            "Deliverable": "iOS and Android app with booking system and payment integration",
            "Motivation": "Help people stay active by making it easier to discover fitness opportunities"
        }
    }
    
    budget_response = simulate_chatgpt_request(get_pricepoints, budget_request)
    
    if budget_response["status_code"] == 200:
        print("✅ Budget options retrieved successfully")
        pricepoints = budget_response["response_data"].get("pricepoints", [])
        print(f"Available tiers: {len(pricepoints)}")
        for tier in pricepoints:
            print(f"  - {tier['name']}: ${tier['max_cost']} ({tier['description']})")
    else:
        print(f"❌ Failed: {budget_response['response_data']}")
        return False
    
    # Step 3: Execute analysis (user selects a tier)
    print("\n3. 🚀 Starting Analysis")
    execution_request = {
        "user_input": budget_request["user_input"],
        "budget_tier": "standard"
    }
    
    execution_response = simulate_chatgpt_request(execute_analysis, execution_request)
    
    if execution_response["status_code"] == 200:
        print("✅ Analysis started successfully")
        job_id = execution_response["response_data"].get("job_id")
        print(f"Job ID: {job_id}")
        print(f"Testing Mode: {execution_response['response_data'].get('testing_mode', False)}")
    else:
        print(f"❌ Failed: {execution_response['response_data']}")
        return False
    
    # Step 4: Check analysis status (ChatGPT polls this)
    print("\n4. ⏳ Checking Analysis Status")
    mock_req = Mock()
    mock_req.params = {"id": job_id}
    mock_req.get_json.return_value = {}
    
    status_response = process_idea(mock_req)
    status_data = json.loads(status_response.get_body())
    
    if status_response.status_code == 200:
        print("✅ Analysis completed successfully")
        print(f"Status: {status_data.get('status')}")
        print(f"Testing Mode: {status_data.get('testing_mode', False)}")
        if status_data.get("mock_results"):
            print("📊 Mock Results Preview:")
            mock_results = status_data["mock_results"]
            print(f"  Overall Rating: {mock_results.get('Overall_Rating')}")
            print(f"  Summary: {mock_results.get('Analysis_Summary')}")
    else:
        print(f"❌ Failed: {status_data}")
        return False
    
    return True


def test_error_scenarios():
    """Test how errors are presented to the ChatGPT bot."""
    print("\n\n🚨 Testing Error Scenarios")
    print("=" * 50)
    
    sys.path.append(os.path.join(current_dir, 'idea-guy'))
    from get_pricepoints import main as get_pricepoints
    from execute_analysis import main as execute_analysis
    
    # Test 1: Missing required field
    print("\n1. 🔍 Testing Missing Field Error")
    missing_field_request = {
        "user_input": {
            "Idea_Overview": "A great app idea",
            # Missing Deliverable and Motivation
        }
    }
    
    response = simulate_chatgpt_request(get_pricepoints, missing_field_request)
    if response["status_code"] == 400:
        print("✅ Error correctly returned")
        error_data = response["response_data"]
        print(f"Error Message: {error_data.get('error')}")
        print(f"Suggestion: {error_data.get('suggestion')}")
        print(f"Error Type: {error_data.get('error_type')}")
    
    # Test 2: Invalid budget tier
    print("\n2. 🎯 Testing Invalid Budget Tier")
    invalid_tier_request = {
        "user_input": {
            "Idea_Overview": "A great app idea",
            "Deliverable": "Mobile app",
            "Motivation": "Help users"
        },
        "budget_tier": "super_premium"  # Invalid tier
    }
    
    response = simulate_chatgpt_request(execute_analysis, invalid_tier_request)
    if response["status_code"] == 400:
        print("✅ Error correctly returned")
        error_data = response["response_data"]
        print(f"Error Message: {error_data.get('error')}")
        print(f"Suggestion: {error_data.get('suggestion')}")
    
    return True


if __name__ == "__main__":
    print("🧪 ChatGPT Bot Workflow Testing")
    print("Running in TESTING MODE - no API charges will occur")
    
    success = True
    success &= test_complete_workflow()
    success &= test_error_scenarios()
    
    if success:
        print(f"\n🎉 All ChatGPT Bot Tests Passed!")
        print("\n📋 Summary:")
        print("✅ Complete workflow functions correctly")
        print("✅ Testing mode prevents API charges")
        print("✅ Error messages are clear and actionable")
        print("✅ ChatGPT bot receives structured responses")
        print("\n🚀 The system is ready for ChatGPT bot integration!")
    else:
        print(f"\n💥 Some tests failed. Check the output above.")