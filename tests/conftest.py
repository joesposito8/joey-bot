"""Common test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from common.config.models import FieldConfig, BudgetTierConfig

# Set testing mode
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "test_sheet_id_for_testing"
os.environ["GOOGLE_SHEETS_KEY_PATH"] = "/tmp/mock_key.json"
os.environ["OPENAI_API_KEY"] = "test-key-12345"

@pytest.fixture(autouse=True)
def mock_openai():
    """Mock OpenAI client to prevent API calls."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.api_key = "mock-key"
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture(autouse=True)
def mock_sheets():
    """Mock Google Sheets client to prevent API calls."""
    with patch('gspread.authorize') as mock_authorize:
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = [["Test", "Data"]]
        
        mock_authorize.return_value = mock_client
        yield mock_client

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