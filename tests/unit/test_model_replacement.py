#!/usr/bin/env python3
"""Test script to verify that o4-mini-deep-research has been replaced with gpt-4o-mini."""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_replacement():
    """Test that all deep research model references have been replaced."""
    project_root = Path(__file__).parent
    
    # Key files that should have been updated
    key_files = [
        "common/multi_call_architecture.py",
        "common/agent/langchain_workflows.py", 
        "common/agent/workflow_engine.py",
        "common/budget_config.py",
        "common/cost_tracker.py"
    ]
    
    print("🔍 Testing model replacement in key files...")
    
    all_clean = True
    
    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Check for old model references
            old_model_count = content.count("o4-mini-deep-research")
            new_model_count = content.count("gpt-4o-mini")
            
            print(f"📄 {file_path}:")
            print(f"   Old model (o4-mini-deep-research): {old_model_count} occurrences")
            print(f"   New model (gpt-4o-mini): {new_model_count} occurrences")
            
            if old_model_count > 0:
                print(f"   ❌ Still contains old model references!")
                all_clean = False
            else:
                print(f"   ✅ Clean - no old model references")
                
        else:
            print(f"📄 {file_path}: File not found")
    
    # Test configuration objects
    print("\n🧪 Testing configuration objects...")
    
    try:
        from common.budget_config import BudgetConfigManager
        manager = BudgetConfigManager()
        
        for tier in ['basic', 'standard', 'premium']:
            config = manager.get_tier_config(tier)
            print(f"   {tier} tier: {config.model}")
            if config.model != "gpt-4o-mini":
                print(f"   ❌ {tier} tier still uses old model!")
                all_clean = False
            else:
                print(f"   ✅ {tier} tier updated correctly")
                
    except Exception as e:
        print(f"   ❌ Error testing configuration: {e}")
        all_clean = False
    
    # Test cost tracker
    print("\n💰 Testing cost tracker...")
    try:
        from common.cost_tracker import OPENAI_PRICING
        
        if "o4-mini-deep-research" in OPENAI_PRICING:
            print("   ❌ Cost tracker still contains old model pricing!")
            all_clean = False
        else:
            print("   ✅ Cost tracker cleaned up")
            
        if "gpt-4o-mini" in OPENAI_PRICING:
            print("   ✅ Cost tracker has new model pricing")
        else:
            print("   ℹ️ Cost tracker doesn't have new model pricing (expected)")
            
    except Exception as e:
        print(f"   ❌ Error testing cost tracker: {e}")
        all_clean = False
    
    print(f"\n{'✅ All tests passed! Model replacement successful.' if all_clean else '❌ Some issues found. Check the output above.'}")
    return all_clean

if __name__ == "__main__":
    success = test_model_replacement()
    sys.exit(0 if success else 1)