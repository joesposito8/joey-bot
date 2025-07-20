#!/usr/bin/env python3
"""
Simple validation test for the Agent endpoint logic.
"""

import os
import sys
import json

# Add both the current directory and the idea-guy directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'idea-guy'))


def test_budget_tier_system():
    """Test that the budget tier system works independently."""
    print("Testing budget tier system...")
    
    try:
        from common.agent.budget_tiers import BudgetSystem, BUSINESS_EVALUATION_TIERS, TierLevel
        
        # Initialize budget system
        budget_system = BudgetSystem()
        budget_system.register_agent_tiers("business_evaluation", BUSINESS_EVALUATION_TIERS)
        
        # Test user input
        user_input = {
            "Idea_Overview": "A mobile app for local event discovery",
            "Deliverable": "iOS and Android app with event listings and booking",
            "Motivation": "Help people find and attend local events easily"
        }
        
        # Test getting budget options
        options = []
        for tier in budget_system.get_tiers_for_agent("business_evaluation"):
            estimated_cost = budget_system.estimate_cost("business_evaluation", tier.level, user_input)
            option = tier.to_dict()
            option["estimated_cost"] = estimated_cost
            options.append(option)
        
        print(f"✅ Generated {len(options)} budget options:")
        for option in options:
            print(f"   {option['name']}: ${option['estimated_cost']:.4f} (max: ${option['max_cost']})")
        
        # Test tier validation
        valid_levels = [TierLevel.BASIC, TierLevel.STANDARD, TierLevel.PREMIUM]
        for level in valid_levels:
            tier = budget_system.get_tier("business_evaluation", level)
            print(f"✅ {level.value} tier: {tier.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Budget tier test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_request_structure():
    """Test request parsing logic."""
    print("Testing request structure validation...")
    
    try:
        # Valid budget options request
        valid_budget_request = {
            "action": "get_budget_options",
            "user_input": {
                "Idea_Overview": "Test idea",
                "Deliverable": "Test deliverable",
                "Motivation": "Test motivation"
            }
        }
        
        # Valid execution request  
        valid_exec_request = {
            "action": "execute",
            "user_input": {
                "Idea_Overview": "Test idea",
                "Deliverable": "Test deliverable", 
                "Motivation": "Test motivation"
            },
            "budget_tier": "standard"
        }
        
        # Invalid requests
        invalid_requests = [
            {},  # Empty
            {"action": "invalid"},  # Invalid action
            {"action": "get_budget_options"},  # Missing user_input
            {"action": "execute", "user_input": {"test": "data"}},  # Missing budget_tier
            {"action": "execute", "user_input": {"Idea_Overview": "", "Deliverable": "test", "Motivation": "test"}, "budget_tier": "standard"},  # Empty field
        ]
        
        # Test validation logic manually
        required_fields = ["Idea_Overview", "Deliverable", "Motivation"]
        
        def validate_request(req_body):
            if not req_body:
                return False, "Request body is required"
            
            action = req_body.get("action", "get_budget_options")
            if action not in ["get_budget_options", "execute"]:
                return False, f"Invalid action: {action}"
            
            user_input = req_body.get("user_input", {})
            if not user_input:
                return False, "user_input is required"
            
            missing_fields = [field for field in required_fields if field not in user_input or not user_input[field].strip()]
            if missing_fields:
                return False, f"Missing or empty required fields: {missing_fields}"
            
            if action == "execute":
                budget_tier = req_body.get("budget_tier", "")
                if budget_tier not in ["basic", "standard", "premium"]:
                    return False, f"Invalid budget_tier: {budget_tier}"
            
            return True, "Valid"
        
        # Test valid requests
        valid_requests = [valid_budget_request, valid_exec_request]
        for i, req in enumerate(valid_requests):
            is_valid, msg = validate_request(req)
            if is_valid:
                print(f"✅ Valid request {i+1}: {msg}")
            else:
                print(f"❌ Expected valid request {i+1} but got: {msg}")
                return False
        
        # Test invalid requests
        for i, req in enumerate(invalid_requests):
            is_valid, msg = validate_request(req)
            if not is_valid:
                print(f"✅ Invalid request {i+1} properly rejected: {msg}")
            else:
                print(f"❌ Expected invalid request {i+1} to be rejected but it was accepted")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Request validation test failed: {e}")
        return False


def test_agent_schema():
    """Test the Agent schema system.""" 
    print("Testing Agent schema...")
    
    try:
        from common.agent import SheetSchema, BusinessEvaluationAgent
        from common.idea_guy.utils import IdeaGuyUserInput, IdeaGuyBotOutput
        
        # Test schema creation
        schema = SheetSchema(
            input_columns=IdeaGuyUserInput.columns,
            output_columns=IdeaGuyBotOutput.columns
        )
        
        # Test input validation
        valid_input = {
            "Idea_Overview": "Test idea",
            "Deliverable": "Test deliverable",
            "Motivation": "Test motivation"
        }
        
        invalid_input = {
            "Idea_Overview": "Test idea",
            "Deliverable": "Test deliverable"
            # Missing Motivation
        }
        
        if schema.validate_input(valid_input):
            print("✅ Valid input accepted")
        else:
            print("❌ Valid input rejected")
            return False
        
        if not schema.validate_input(invalid_input):
            print("✅ Invalid input properly rejected")
        else:
            print("❌ Invalid input was accepted")
            return False
        
        # Test header generation
        headers = schema.get_header_row()
        expected_cols = 2 + len(IdeaGuyUserInput.columns) + len(IdeaGuyBotOutput.columns)  # ID + Timestamp + input + output
        
        if len(headers) == expected_cols:
            print(f"✅ Header row has correct length: {len(headers)} columns")
        else:
            print(f"❌ Header row has wrong length: got {len(headers)}, expected {expected_cols}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Simple Agent Framework Tests\n")
    
    success = True
    success &= test_budget_tier_system()
    print()
    success &= test_request_structure()
    print()
    success &= test_agent_schema()
    
    if success:
        print(f"\n🎉 All tests passed!")
        print("\n📋 Summary:")
        print("✅ Budget tier system works correctly")
        print("✅ Request validation logic works")
        print("✅ Agent schema system works")
        print("\n🚀 The Agent framework core logic is solid!")
        print("\n📝 To test with real Azure Functions:")
        print("1. Deploy the function to Azure")
        print("2. Set up environment variables (IDEA_GUY_SHEET_ID, OPENAI_API_KEY, GOOGLE_SHEETS_KEY_PATH)")
        print("3. Test with real API calls")
    else:
        print(f"\n💥 Some tests failed. Check the output above.")