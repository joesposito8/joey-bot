"""Common test configuration and fixtures."""

import os
import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from common.config.models import FieldConfig, BudgetTierConfig

# Set testing mode
os.environ["TESTING_MODE"] = "true"
# Use real Google Sheets credentials for testing (API is free)
os.environ["IDEA_GUY_SHEET_ID"] = "1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs"  
os.environ["GOOGLE_SHEETS_KEY_PATH"] = "/home/joey/Projects/joey-bot/.keys/joey-bot-465403-d2eb14543555.json"
os.environ["OPENAI_API_KEY"] = "test-key-12345"


@pytest.fixture(autouse=True)
def mock_openai():
    """Mock OpenAI client to prevent API calls."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.api_key = "mock-key"
        
        def create_mock_response(content):
            """Helper to create consistent mock response structure."""
            response = Mock()
            response.output = [Mock()]
            response.output[0].content = [Mock()]
            response.output[0].content[0].text = json.dumps(content)
            return response
        
        def generate_mock_plan(available_calls: int, max_concurrent: int = None):
            """Generate a mock plan based on available calls."""
            if max_concurrent is None:
                max_concurrent = min(available_calls, 4)

            # For single call, create minimal viable plan
            if available_calls == 1:
                return {
                    "strategy_explanation": "Single-call analysis workflow",
                    "total_calls": 1,
                    "max_concurrent": 1,
                    "calls": [{
                        "call_id": "analysis_1",
                        "purpose": "Complete analysis and synthesis",
                        "prompt": "Analyze and synthesize results",
                        "dependencies": [],
                        "is_summarizer": True
                    }],
                    "execution_order": [["analysis_1"]]
                }

            # For multiple calls, create dependency chain with parallel execution
            calls = []
            execution_order = []
            current_batch = []
            
            for i in range(available_calls):
                call_id = f"analysis_{i+1}"
                is_summarizer = (i == available_calls - 1)
                dependencies = []
                if i > 0:
                    prev_batch_start = max(0, i - max_concurrent)
                    dependencies = [f"analysis_{j+1}" for j in range(prev_batch_start, i)]
                
                calls.append({
                    "call_id": call_id,
                    "purpose": f"{'Synthesis' if is_summarizer else 'Analysis'} stage {i+1}",
                    "prompt": f"Execute {'synthesis' if is_summarizer else 'analysis'} stage {i+1}",
                    "dependencies": dependencies,
                    "is_summarizer": is_summarizer
                })
                
                if len(current_batch) < max_concurrent:
                    current_batch.append(call_id)
                else:
                    execution_order.append(current_batch)
                    current_batch = [call_id]
            
            if current_batch:
                execution_order.append(current_batch)

            return {
                "strategy_explanation": f"{available_calls}-call analysis workflow",
                "total_calls": available_calls,
                "max_concurrent": max_concurrent,
                "calls": calls,
                "execution_order": execution_order
            }
        
        def mock_create(**kwargs):
            """Dynamic mock response generation based on input."""
            if 'architecture_planning' in kwargs.get('model', ''):
                prompt = kwargs['input'][0]['content'][0]['text']
                available_calls = int(prompt.split('available_calls: ')[1].split('\n')[0])
                return create_mock_response(generate_mock_plan(available_calls))
            else:
                return create_mock_response({
                    "Analysis_Result": "Mock analysis output",
                    "Overall_Rating": "8/10",
                    "Key_Insights": ["Mock insight 1", "Mock insight 2"]
                })
        
        mock_instance.responses = Mock()
        mock_instance.responses.create = Mock(side_effect=mock_create)
        mock_client.return_value = mock_instance
        yield mock_instance

# Google Sheets API is free - no need to mock it
# Tests will use real Google Sheets API with test spreadsheet

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