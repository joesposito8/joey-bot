"""
Pytest configuration and shared fixtures for Universal AI Agent Platform tests.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path
from common.config.models import FieldConfig, BudgetTierConfig


@pytest.fixture
def mock_google_sheets_client():
    """Mock Google Sheets client for testing."""
    client = Mock()
    client.get_sheet_data = Mock()
    return client


@pytest.fixture
def sample_budget_tiers():
    """Sample budget tier configurations for testing."""
    return [
        BudgetTierConfig(
            name="basic",
            price=1.00,
            calls=1,
            description="Quick evaluation"
        ),
        BudgetTierConfig(
            name="standard", 
            price=3.00,
            calls=3,
            description="Detailed analysis"
        ),
        BudgetTierConfig(
            name="premium",
            price=5.00,
            calls=5,
            description="Comprehensive evaluation"
        )
    ]


@pytest.fixture
def sample_field_configs():
    """Sample field configurations for testing."""
    return {
        'input': [
            FieldConfig(name="Idea_Overview", type="user input", description="Brief desc", column_index=2),
            FieldConfig(name="Deliverable", type="user input", description="What will be built", column_index=3)
        ],
        'output': [
            FieldConfig(name="Novelty_Rating", type="bot output", description="How novel", column_index=4),
            FieldConfig(name="Analysis_Result", type="bot output", description="Final result", column_index=5)
        ]
    }


@pytest.fixture
def valid_sheet_data():
    """Valid 3-row sheet data for schema parsing tests."""
    return [
        ["ID", "Time", "user input", "user input", "user input", "bot output", "bot output"],
        ["ID", "Time", "Brief desc", "What will", "Why this", "How novel", "Detailed"],
        ["ID", "Time", "Idea_Overview", "Deliverable", "Motivation", "Novelty_Rating", "Novelty_Rationale"]
    ]


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return {
        "Idea_Overview": "Mobile fitness app",
        "Deliverable": "iOS/Android app with workout plans",
        "Motivation": "Help people stay healthy"
    }


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    def _create_yaml(content: str) -> Path:
        yaml_file = tmp_path / "test_agent.yaml"
        yaml_file.write_text(content)
        return yaml_file
    return _create_yaml