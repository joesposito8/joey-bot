# Joey-Bot Testing Guide

**Last Updated**: 2025-01-27  
**System**: Universal AI Agent Platform

## Overview

Joey-Bot includes comprehensive testing protection to prevent OpenAI API charges and Google Sheets modifications during development, testing, and CI/CD pipelines.

## Testing Mode

### Activation Methods

**Environment Variable (Recommended):**
```bash
export TESTING_MODE=true
```

**Auto-Detection:**
Testing mode automatically activates when:
- `TESTING_MODE=true` environment variable is set
- `pytest` is running (detected via `sys.modules`)
- Process name contains 'pytest'

### Testing Mode Features

#### 🚫 **No OpenAI API Charges**
- All OpenAI calls return mock responses immediately
- No actual API requests made to OpenAI
- Zero billing impact during development

```python
# Production: Real OpenAI call
response = openai_client.responses.create(model="gpt-4o-mini", input=messages)

# Testing: Mock response
if is_testing_mode():
    return MockResponse(job_id="mock_12345", status="completed")
```

#### 🔒 **No Google Sheets Modifications**  
- Google Sheets operations are bypassed
- Uses in-memory mock data for testing
- Safe for parallel test execution

```python
# Production: Real sheet write  
worksheet.append_row([job_id, timestamp, user_data])

# Testing: Mock operation
if is_testing_mode():
    logging.info(f"[TESTING] Mock sheet write: {job_id}")
    return
```

#### 🎭 **Mock Job System**
All testing responses include clear indicators:

```json
{
  "job_id": "mock_1737999123",
  "status": "processing",
  "testing_mode": true,
  "note": "Mock analysis - no API charges incurred"
}
```

#### ⚡ **Immediate Results**
Testing mode provides instant analysis completion:

```python
# Testing mode returns completed analysis immediately
GET /api/process_idea?id=mock_1737999123

# Response:
{
  "status": "completed",
  "Novelty_Rating": "7",
  "Analysis_Summary": "Mock analysis result for testing purposes",
  "testing_mode": true
}
```

## Test Suites

### Unit Tests
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_agent.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=common --cov-report=html
```

### Integration Tests  
```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Test full workflow
python -m pytest tests/integration/test_new_analysis.py -v

# Test multi-call architecture
python -m pytest tests/integration/test_multi_call_architecture.py -v
```

### API Endpoint Tests
```bash
# Test individual endpoints
python -c "
import sys
sys.path.append('idea-guy')
from execute_analysis import main
print('Execute analysis endpoint: OK')
"

# Test complete workflow
python tests/integration/test_chatgpt_flow.py
```

## Testing Configuration

### Environment Setup
```bash
# Local development
export TESTING_MODE=true
export OPENAI_API_KEY=dummy_key_for_testing
export IDEA_GUY_SHEET_ID=dummy_sheet_id

# Run tests
python -m pytest tests/ -v
```

### Azure Functions Testing
```bash
# Test Azure Functions locally
cd idea-guy
func start --python

# In another terminal, test endpoints
curl -X GET "http://localhost:7071/api/get_instructions"
curl -X POST "http://localhost:7071/api/get_pricepoints" \
  -H "Content-Type: application/json" \
  -d '{"user_input": {"Idea_Overview": "Test", "Deliverable": "Test", "Motivation": "Test"}}'
```

## Test Data and Fixtures

### Sample User Input
```python
# Standard test input (tests/conftest.py)
SAMPLE_USER_INPUT = {
    "Idea_Overview": "AI-powered productivity app", 
    "Deliverable": "Mobile app with smart scheduling",
    "Motivation": "Help users optimize their daily workflows"
}

# Use in tests
def test_analysis_validation():
    from common.agent_service import AnalysisService
    service = AnalysisService()
    result = service.validate_user_input(SAMPLE_USER_INPUT)
    assert result is True
```

### Mock Responses
```python
# Mock OpenAI response structure (testing mode)
MOCK_ANALYSIS_RESULT = {
    "status": "completed",
    "Novelty_Rating": "7",
    "Novelty_Rationale": "Mock analysis rationale",
    "Feasibility_Rating": "8", 
    "Feasibility_Rationale": "Mock feasibility assessment",
    "Overall_Rating": "7",
    "Analysis_Summary": "Mock comprehensive analysis summary",
    "testing_mode": True
}
```

## Cost Protection Verification

### Verify Testing Mode Active
```python
def test_no_api_charges():
    """Verify testing mode prevents API charges."""
    from common.http_utils import is_testing_mode
    from common.agent_service import AnalysisService
    
    # Confirm testing mode
    assert is_testing_mode() == True
    
    # Verify mock responses
    service = AnalysisService()
    job_id = service.create_analysis_job(SAMPLE_USER_INPUT, "standard")
    assert job_id.startswith("mock_")
```

### Monitor Test Logs
```bash
# Check for testing mode indicators in logs
python -m pytest tests/ -v -s | grep "TESTING"

# Expected output:
# [TESTING] Mock OpenAI call - no charges incurred
# [TESTING] Mock sheet write bypassed
# [TESTING] Mock analysis result returned
```

## Development Workflow

### Safe Development Process
```bash
# 1. Always start with testing mode
export TESTING_MODE=true

# 2. Develop and test locally
python -m pytest tests/unit/ -v

# 3. Test Azure Functions locally  
cd idea-guy && func start --python

# 4. Test integration
python -m pytest tests/integration/ -v

# 5. Only disable testing for production deployment
unset TESTING_MODE  # Production only!
```

### Debugging Tests
```python
# Add debugging to any test
def test_with_debug():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from common.http_utils import is_testing_mode
    print(f"Testing mode: {is_testing_mode()}")
    
    # Your test code here
    assert True
```

## Common Testing Scenarios

### Test Complete Analysis Workflow
```python
def test_full_analysis_workflow():
    """Test complete analysis from start to finish."""
    from common.agent_service import AnalysisService
    from common.http_utils import is_testing_mode
    
    # Ensure testing mode
    assert is_testing_mode()
    
    service = AnalysisService()
    
    # Test user input validation
    assert service.validate_user_input(SAMPLE_USER_INPUT)
    
    # Test budget options
    budget_options = service.get_budget_options(SAMPLE_USER_INPUT)
    assert len(budget_options) == 3
    
    # Test analysis creation
    job_id = service.create_analysis_job(SAMPLE_USER_INPUT, "standard")
    assert job_id.startswith("mock_")
    
    # Test result retrieval (immediate in testing mode)
    result = service.get_analysis_result(job_id)
    assert result["status"] == "completed"
    assert result["testing_mode"] == True
```

### Test Configuration Loading
```python
def test_agent_configuration():
    """Test dynamic agent configuration system."""
    from common.config import AgentDefinition, FullAgentConfig
    from pathlib import Path
    
    # Test YAML loading
    config_path = Path("agents/business_evaluation.yaml")
    agent_def = AgentDefinition.from_yaml(config_path)
    assert agent_def.agent_id == "business_evaluation"
    
    # Test instruction generation
    full_config = FullAgentConfig.from_definition(agent_def)
    instructions = full_config.generate_instructions()
    assert "Idea Overview" in instructions
```

### Test Error Conditions
```python
def test_validation_errors():
    """Test various validation error scenarios."""
    from common.agent_service import AnalysisService, ValidationError
    
    service = AnalysisService()
    
    # Test missing fields
    incomplete_input = {"Idea_Overview": "Test idea"}
    with pytest.raises(ValidationError):
        service.validate_user_input(incomplete_input)
    
    # Test invalid budget tier
    with pytest.raises(ValidationError):
        service.create_analysis_job(SAMPLE_USER_INPUT, "invalid_tier")
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Joey-Bot
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      env:
        TESTING_MODE: true
        OPENAI_API_KEY: dummy_key
        IDEA_GUY_SHEET_ID: dummy_sheet
      run: |
        python -m pytest tests/ -v --cov=common --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Security Considerations

### Prevent Accidental Production API Usage
```python
# Environment validation in production
def validate_production_environment():
    import os
    from common.http_utils import is_testing_mode
    
    # Never allow testing mode in production
    if os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') == 'production':
        assert not is_testing_mode(), "Testing mode must be disabled in production"
    
    # Require real API keys in production
    if not is_testing_mode():
        assert os.getenv('OPENAI_API_KEY', '').startswith('sk-'), "Valid OpenAI API key required"
```

### Test Data Isolation  
```python
# Use separate test sheet (if needed)
TEST_SHEET_ID = "test_sheet_id_12345"

def test_with_isolation():
    """Test with isolated data sources."""
    import os
    
    # Override sheet ID for testing
    original_sheet = os.getenv('IDEA_GUY_SHEET_ID')
    os.environ['IDEA_GUY_SHEET_ID'] = TEST_SHEET_ID
    
    try:
        # Run test with isolated sheet
        pass
    finally:
        # Restore original
        if original_sheet:
            os.environ['IDEA_GUY_SHEET_ID'] = original_sheet
```

## Troubleshooting

### Common Issues

**Testing mode not activating:**
```bash
# Check environment
python -c "import os; print('TESTING_MODE:', os.getenv('TESTING_MODE'))"

# Check detection logic
python -c "from common.http_utils import is_testing_mode; print('Testing mode:', is_testing_mode())"
```

**Tests still making API calls:**
```bash
# Verify mock system
python -c "
from common.http_utils import is_testing_mode
if is_testing_mode():
    print('✅ Testing mode active - no API calls will be made')
else:
    print('❌ WARNING: Testing mode not active - API calls may occur')
"
```

**Import errors in tests:**
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/ -v
```

## Performance Testing

### Load Testing (Testing Mode)
```python
def test_concurrent_requests():
    """Test system under concurrent load (mock mode)."""
    import concurrent.futures
    from common.agent_service import AnalysisService
    
    def create_analysis():
        service = AnalysisService()
        return service.create_analysis_job(SAMPLE_USER_INPUT, "standard")
    
    # Test 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_analysis) for _ in range(10)]
        results = [future.result() for future in futures]
    
    # All should succeed with mock job IDs
    assert all(job_id.startswith("mock_") for job_id in results)
```

For detailed system implementation, see `docs/SYSTEM_ARCHITECTURE.md`.