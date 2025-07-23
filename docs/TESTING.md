# Testing Guide

## Overview

The Joey Bot system includes comprehensive testing protection to prevent API charges and data modifications during development, testing, and CI/CD pipelines.

## Testing Mode

### Activation

**Environment Variable:**
```bash
export TESTING_MODE=true
```

**Auto-Detection:**
Testing mode automatically activates when:
- `TESTING_MODE=true` environment variable is set
- `PYTEST_CURRENT_TEST` environment variable exists (pytest runner)
- `AZURE_FUNCTIONS_ENVIRONMENT` contains "test"

### Features

#### 🚫 **No API Charges**
- Creates mock OpenAI jobs instead of real API calls
- Returns fake analysis results immediately
- Prevents accidental billing during development

#### 🔒 **No Data Modifications**  
- Skips Google Sheets operations
- Uses in-memory mock data
- Safe for parallel test execution

#### 🏷️ **Clear Indicators**
All responses include testing markers:
```json
{
  "testing_mode": true,
  "note": "Running in testing mode - no API charges incurred"
}
```

#### 🎭 **Mock Job System**
```json
{
  "job_id": "mock_d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "message": "[TESTING MODE] Mock analysis started with standard tier. No API charges incurred.",
  "testing_mode": true
}
```

## Test Suites

### 1. Core Functionality Tests
```bash
python test_simple_endpoint.py
```

**Coverage:**
- Budget tier system validation
- Request structure validation  
- Agent schema validation
- Configuration management

**Expected Output:**
```
🧪 Simple Agent Framework Tests
✅ Generated 3 budget options
✅ basic tier: Context + Deep Research
✅ Request validation logic works
✅ Agent schema system works
🎉 All tests passed!
```

### 2. End-to-End Workflow Tests
```bash
TESTING_MODE=true python test_chatgpt_flow.py
```

**Coverage:**
- Complete ChatGPT bot workflow
- Error handling scenarios
- Mock job processing
- Response structure validation

**Expected Output:**
```
🧪 ChatGPT Bot Workflow Testing
✅ Instructions retrieved successfully
✅ Budget options retrieved successfully  
✅ Analysis started successfully
✅ Analysis completed successfully
✅ Error messages are clear and actionable
🎉 All ChatGPT Bot Tests Passed!
```

### 3. Agent Endpoint Tests
```bash
python test_agent_endpoint.py
```

**Coverage:**
- HTTP request/response handling
- Azure Functions compatibility
- Error response formatting
- Mock external dependencies

## Testing Best Practices

### 1. Always Use Testing Mode
```python
import os
os.environ["TESTING_MODE"] = "true"
```

### 2. Mock External Dependencies
```python
from unittest.mock import Mock, patch

with patch('common.get_openai_client') as mock_openai:
    with patch('common.get_google_sheets_client') as mock_sheets:
        mock_openai.return_value = Mock()
        mock_sheets.return_value = Mock()
        # Run tests
```

### 3. Validate Error Responses
```python
def test_error_handling():
    response = simulate_request(invalid_data)
    assert response["status_code"] == 400
    assert "error" in response["response_data"]
    assert "suggestion" in response["response_data"]
```

### 4. Check Testing Mode Indicators
```python
def test_testing_mode():
    response = get_budget_options(test_data)
    assert response["testing_mode"] is True
    assert "no API charges" in response["note"]
```

## Mock Data Examples

### Mock Job Creation
```json
{
  "job_id": "mock_12345-abcd-6789-efgh",
  "status": "processing",
  "testing_mode": true,
  "note": "This is a mock job for testing purposes"
}
```

### Mock Analysis Results
```json
{
  "status": "completed",
  "testing_mode": true,
  "mock_results": {
    "Novelty_Rating": "7",
    "Novelty_Rationale": "Mock analysis - this would contain actual evaluation in production",
    "Overall_Rating": "7",
    "Analysis_Summary": "This is a mock analysis result for testing purposes"
  }
}
```

### Mock Error Responses
```json
{
  "error": "Missing required field: Idea_Overview",
  "status": "error",
  "success": false,
  "error_type": "missing_field",
  "testing_mode": true,
  "suggestion": "Please check your request format and required fields"
}
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Joey Bot
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      TESTING_MODE: true
      IDEA_GUY_SHEET_ID: test_sheet_id
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run core tests
      run: python test_simple_endpoint.py
    
    - name: Run workflow tests  
      run: python test_chatgpt_flow.py
```

### Azure DevOps Example
```yaml
- task: PythonScript@0
  displayName: 'Run Tests'
  inputs:
    scriptSource: 'filePath'
    scriptPath: 'test_simple_endpoint.py'
  env:
    TESTING_MODE: true
    IDEA_GUY_SHEET_ID: $(TEST_SHEET_ID)
```

## Debugging Failed Tests

### 1. Check Environment Variables
```bash
echo $TESTING_MODE
echo $IDEA_GUY_SHEET_ID
```

### 2. Examine Error Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Run tests to see detailed logs
```

### 3. Validate Mock Data
```python
# Check if testing mode is properly detected
from common.http_utils import is_testing_mode
print(f"Testing mode: {is_testing_mode()}")
```

### 4. Test Individual Components
```python
# Test budget manager in isolation
from common.budget_config import BudgetConfigManager
manager = BudgetConfigManager()
tiers = manager.get_all_tiers()
print(f"Available tiers: {len(tiers)}")
```

## Performance Testing

### Load Testing with Mock Mode
```python
import concurrent.futures
import requests

def test_concurrent_requests():
    def make_request():
        return requests.post("/api/get_pricepoints", 
                           json={"user_input": test_data})
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
    
    # All should return mock responses
    assert all(r.json().get("testing_mode") for r in results)
```

## Integration Testing

### Test Real vs Mock Behavior
```python
def test_production_vs_testing():
    # Test with TESTING_MODE=false (requires real credentials)
    os.environ["TESTING_MODE"] = "false"
    prod_response = create_analysis_job(test_data, "basic")
    
    # Test with TESTING_MODE=true
    os.environ["TESTING_MODE"] = "true" 
    test_response = create_analysis_job(test_data, "basic")
    
    # Structure should be identical, content different
    assert prod_response.keys() == test_response.keys()
    assert test_response["testing_mode"] is True
    assert prod_response.get("testing_mode") is False
```

## Troubleshooting

### Common Issues

1. **Tests fail with API errors**
   - ✅ Ensure `TESTING_MODE=true` is set
   - ✅ Check environment variable detection

2. **Mock jobs not created**
   - ✅ Verify job IDs start with "mock_"
   - ✅ Check testing mode activation

3. **Real API calls during testing**
   - ✅ Look for missing `testing_mode: true` in logs
   - ✅ Verify environment variable scope

4. **Inconsistent test results**
   - ✅ Clear environment between tests
   - ✅ Use isolated test data

### Debug Commands
```bash
# Check testing mode detection
python -c "from common.http_utils import is_testing_mode; print(is_testing_mode())"

# Test mock job creation
python -c "
from common.agent_service import AnalysisService
service = AnalysisService('test')
result = service.create_analysis_job({'Idea_Overview': 'test', 'Deliverable': 'test', 'Motivation': 'test'}, 'basic')
print(result['job_id'])
"

# Verify budget tiers
python -c "
from common.budget_config import BudgetConfigManager
manager = BudgetConfigManager()
print([tier.level for tier in manager.get_all_tiers()])
"
```