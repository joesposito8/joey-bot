#!/usr/bin/env python3
"""
Test the multi-call architecture system.
"""
import os
import sys
import json
from unittest.mock import Mock

# Add project to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"


def test_budget_tier_updates():
    """Test that budget tiers have been updated to new pricing."""
    print("🧪 Testing Updated Budget Tiers")
    print("=" * 40)
    
    from common.budget_config import BudgetConfigManager
    
    manager = BudgetConfigManager()
    user_input = {
        'Idea_Overview': 'AI-powered fitness app',
        'Deliverable': 'Mobile app with personalized workouts',
        'Motivation': 'Help people stay fit'
    }

    pricepoints = manager.calculate_pricepoints(user_input)
    
    expected_costs = {"basic": 1.00, "standard": 3.00, "premium": 5.00}
    expected_calls = {"basic": 1, "standard": 3, "premium": 5}
    
    print("Checking tier configurations:")
    for tier in pricepoints:
        level = tier['level']
        actual_cost = tier['estimated_cost']
        expected_cost = expected_costs[level]
        
        tier_config = manager.get_tier_config(level)
        actual_calls = tier_config.call_count
        expected_call_count = expected_calls[level]
        
        print(f"  {level.upper()}: ${actual_cost} ({actual_calls} calls)")
        
        if actual_cost != expected_cost:
            print(f"    ❌ Cost mismatch: expected ${expected_cost}, got ${actual_cost}")
            return False
        
        if actual_calls != expected_call_count:
            print(f"    ❌ Call count mismatch: expected {expected_call_count}, got {actual_calls}")
            return False
        
        print(f"    ✅ Correct: ${actual_cost} with {actual_calls} calls")
    
    return True


def test_multi_call_architecture_planning():
    """Test the architecture planning system."""
    print("\n🏗️ Testing Architecture Planning")
    print("=" * 40)
    
    from common.multi_call_architecture import MultiCallArchitecture, get_architecture_planning_prompt
    
    # Mock OpenAI client for testing
    mock_client = Mock()
    mock_response = Mock()
    mock_output = Mock()
    mock_content = Mock()
    
    # Mock successful planning response
    mock_plan = {
        "strategy_explanation": "Test strategy",
        "total_calls": 3,
        "max_concurrent": 4,
        "calls": [
            {
                "call_id": "market_analysis",
                "purpose": "Market research",
                "prompt": "Analyze the market for this idea",
                "dependencies": [],
                "is_summarizer": False
            },
            {
                "call_id": "competitive_analysis", 
                "purpose": "Competitive landscape",
                "prompt": "Analyze competitors",
                "dependencies": [],
                "is_summarizer": False
            },
            {
                "call_id": "final_summary",
                "purpose": "Synthesize findings",
                "prompt": "Synthesize all findings",
                "dependencies": ["market_analysis", "competitive_analysis"],
                "is_summarizer": True
            }
        ],
        "execution_order": [
            ["market_analysis", "competitive_analysis"],
            ["final_summary"]
        ]
    }
    
    mock_content.text = json.dumps(mock_plan)
    mock_output.content = [mock_content]
    mock_response.output = [mock_output]
    mock_client.responses.create.return_value = mock_response
    
    architecture = MultiCallArchitecture(mock_client)
    
    user_input = {
        'Idea_Overview': 'Test fitness app',
        'Deliverable': 'Mobile app',
        'Motivation': 'Help users'
    }
    
    try:
        plan = architecture.plan_architecture(
            original_prompt="Analyze this business idea",
            available_calls=3,
            user_input=user_input
        )
        
        print(f"✅ Created plan with {plan.total_calls} calls")
        print(f"✅ Execution order: {len(plan.execution_order)} batches")
        print(f"✅ Found {len([c for c in plan.calls if c.is_summarizer])} summarizer calls")
        
        return True
        
    except Exception as e:
        print(f"❌ Planning failed: {str(e)}")
        return False


def test_integration_with_existing_flow():
    """Test that the multi-call system integrates with existing workflow."""
    print("\n🔄 Testing Integration with Existing Flow")
    print("=" * 40)
    
    # This should still work with existing test
    sys.path.append(os.path.join(current_dir, 'idea-guy'))
    from execute_analysis import main as execute_analysis
    from unittest.mock import Mock
    import azure.functions as func
    
    mock_req = Mock(spec=func.HttpRequest)
    mock_req.get_json.return_value = {
        "user_input": {
            "Idea_Overview": "A mobile app for fitness tracking",
            "Deliverable": "iOS and Android app with workout plans",
            "Motivation": "Help people stay healthy and active"
        },
        "budget_tier": "standard"  # 3-call tier
    }
    
    try:
        response = execute_analysis(mock_req)
        
        if response.status_code == 200:
            response_data = json.loads(response.get_body())
            print(f"✅ Analysis started with job ID: {response_data.get('job_id')}")
            print(f"✅ Budget tier: {response_data.get('budget_tier')}")
            print(f"✅ Testing mode: {response_data.get('testing_mode')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 Multi-Call Architecture Testing")
    print("Running in TESTING MODE")
    
    success = True
    success &= test_budget_tier_updates()
    success &= test_multi_call_architecture_planning()
    success &= test_integration_with_existing_flow()
    
    if success:
        print(f"\n🎉 All Multi-Call Architecture Tests Passed!")
        print("\n📋 Summary:")
        print("✅ Budget tiers updated to $1/$3/$5 pricing")
        print("✅ Call count configuration working")
        print("✅ Architecture planning system functional")
        print("✅ Integration with existing workflow maintained")
        print("\n🚀 Multi-call architecture system is ready!")
    else:
        print(f"\n💥 Some tests failed. Check the output above.")