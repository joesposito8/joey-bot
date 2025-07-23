#!/usr/bin/env python3
"""
Quick test script for the Agent framework.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.agent import BusinessEvaluationAgent, TierLevel


def test_budget_options():
    """Test getting budget options."""
    print("Testing budget options...")

    # Mock user input
    user_input = {
        "Idea_Overview": "A mobile app that helps people find and book local fitness classes",
        "Deliverable": "iOS and Android app with booking system and payment processing",
        "Motivation": "To make it easier for people to discover and attend fitness classes in their area",
    }

    try:
        # Note: This would need actual credentials to work fully
        # For now we'll just test the structure
        from common.agent.budget_tiers import BudgetSystem, BUSINESS_EVALUATION_TIERS

        budget_system = BudgetSystem()
        budget_system.register_agent_tiers(
            "business_evaluation", BUSINESS_EVALUATION_TIERS
        )

        # Test getting tiers
        tiers = budget_system.get_tiers_for_agent("business_evaluation")
        print(f"Found {len(tiers)} budget tiers:")

        for tier in tiers:
            estimated_cost = budget_system.estimate_cost(
                "business_evaluation", tier.level, user_input
            )
            print(f"  {tier.name}: ${estimated_cost:.4f} (max: ${tier.max_cost})")
            print(f"    Model: {tier.model}")
            print(f"    Time: {tier.time_estimate}")
            print(f"    Deliverables: {len(tier.deliverables)} items")
            print()

        print("✅ Budget system test passed!")

    except Exception as e:
        print(f"❌ Budget system test failed: {e}")
        return False

    return True


def test_schema():
    """Test the schema system."""
    print("Testing schema system...")

    try:
        from common.agent import SheetSchema
        from common.idea_guy.utils import IdeaGuyUserInput, IdeaGuyBotOutput

        schema = SheetSchema(
            input_columns=IdeaGuyUserInput.columns,
            output_columns=IdeaGuyBotOutput.columns,
        )

        print(f"Schema has {len(schema.input_columns)} input columns")
        print(f"Schema has {len(schema.output_columns)} output columns")

        # Test validation
        user_input = {
            "Idea_Overview": "Test idea",
            "Deliverable": "Test deliverable",
            "Motivation": "Test motivation",
        }

        valid = schema.validate_input(user_input)
        print(f"User input validation: {'✅' if valid else '❌'}")

        # Test header row
        headers = schema.get_header_row()
        print(f"Header row has {len(headers)} columns")
        print(f"First few headers: {headers[:5]}")

        print("✅ Schema test passed!")

    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

    return True


import sys
from common.idea_guy.utils import IdeaGuyUserInput, get_idea_analysis_prompt


def main():
    print("Enter sample business idea input. Leave blank to use defaults.")
    idea = (
        input("Idea Overview: ")
        or "A mobile app that helps people find and book local fitness classes."
    )
    deliverable = (
        input("Deliverable: ")
        or "A mobile application with booking system and payment integration."
    )
    motivation = (
        input("Motivation: ")
        or "To solve the problem of people struggling to find and book fitness classes in their area."
    )

    user_input = IdeaGuyUserInput(
        {
            "Idea_Overview": idea,
            "Deliverable": deliverable,
            "Motivation": motivation,
        }
    )

    prompt = get_idea_analysis_prompt(user_input)
    print("\n--- Business Evaluation Prompt ---\n")
    print(prompt)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    print("🧪 Testing Agent Framework\n")

    success = True
    success &= test_schema()
    print()
    success &= test_budget_options()

    if success:
        print("\n🎉 All tests passed! Agent framework is working.")
    else:
        print("\n💥 Some tests failed. Check the output above.")
