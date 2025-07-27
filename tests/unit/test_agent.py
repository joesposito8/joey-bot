#!/usr/bin/env python3
"""
Test script for the Universal Agent framework components.
"""

import os
import sys
import pytest

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_budget_system():
    """Test universal budget configuration system."""
    from common.budget_config import BudgetConfigManager
    
    budget_manager = BudgetConfigManager()
    
    # Mock user input
    user_input = {
        "Idea_Overview": "A mobile app that helps people find and book local fitness classes",
        "Deliverable": "iOS and Android app with booking system and payment processing",
        "Motivation": "To make it easier for people to discover and attend fitness classes in their area",
    }

    # Test the production budget configuration system
    tiers = budget_manager.get_all_tiers()
    assert len(tiers) == 3, f"Expected 3 tiers, got {len(tiers)}"

    # Verify tier structure
    tier_levels = {tier.level for tier in tiers}
    expected_levels = {"basic", "standard", "premium"}
    assert tier_levels == expected_levels, f"Expected {expected_levels}, got {tier_levels}"

    # Test pricing
    basic_tier = next(tier for tier in tiers if tier.level == "basic")
    standard_tier = next(tier for tier in tiers if tier.level == "standard") 
    premium_tier = next(tier for tier in tiers if tier.level == "premium")
    
    assert basic_tier.estimated_cost == 1.00, f"Basic tier should cost $1.00, got ${basic_tier.estimated_cost}"
    assert standard_tier.estimated_cost == 3.00, f"Standard tier should cost $3.00, got ${standard_tier.estimated_cost}"
    assert premium_tier.estimated_cost == 5.00, f"Premium tier should cost $5.00, got ${premium_tier.estimated_cost}"


def test_multi_call_architecture():
    """Test that multi-call architecture is available."""
    from common.multi_call_architecture import MultiCallArchitecture
    from unittest.mock import Mock
    
    # Mock OpenAI client
    mock_client = Mock()
    architecture = MultiCallArchitecture(mock_client)
    
    # Test that architecture methods exist
    assert hasattr(architecture, 'plan_architecture'), "Missing plan_architecture method"
    assert hasattr(architecture, 'execute_plan'), "Missing execute_plan method"


def test_config_schema():
    """Test new configuration-based schema functionality.""" 
    from common.config.models import SheetSchema, FieldConfig
    
    # Create test schema using new configuration system
    input_fields = [
        FieldConfig(name="Idea_Overview", type="user input", description="Brief description of the business idea", column_index=2),
        FieldConfig(name="Deliverable", type="user input", description="What product/service will be delivered", column_index=3),
        FieldConfig(name="Motivation", type="user input", description="Why this idea should exist", column_index=4)
    ]
    
    output_fields = [
        FieldConfig(name="Novelty_Rating", type="bot output", description="How novel/unique the idea is", column_index=5),
        FieldConfig(name="Analysis_Summary", type="bot output", description="Summary of the analysis", column_index=6)
    ]
    
    schema = SheetSchema(input_fields=input_fields, output_fields=output_fields)
    
    # Test basic functionality
    assert len(schema.input_fields) == 3
    assert len(schema.output_fields) == 2
    # Header includes ID, Time + 3 input + 2 output = 7 total
    assert len(schema.get_header_row()) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
