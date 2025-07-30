# Joey-Bot Developer Guide

**Last Updated**: 2025-01-30  
**System**: Universal AI Agent Platform  
**Status**: Transition State - Current system with universal components

## Quick Start

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-org/joey-bot.git
cd joey-bot

# Install dependencies
pip install -r requirements.txt

# Enable safe testing mode (no API charges)
export TESTING_MODE=true

# Start Azure Functions locally  
cd idea-guy && func start --python

# Verify system health
python -c "from common.http_utils import is_testing_mode; print(f'Testing mode: {is_testing_mode()}')"
```

---

## API Reference

### Base URLs
- **Production:** `https://your-function-app.azurewebsites.net`
- **Local Development:** `http://localhost:7071`

### Complete Workflow
1. **Get Instructions** → 2. **Get Price Points** → 3. **Execute Analysis** → 4. **Poll Results**

### Authentication
All endpoints require Azure Function authentication:
```bash
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \
     -H "Content-Type: application/json" \
     "https://your-app.azurewebsites.net/api/endpoint"
```

### Endpoints

#### 1. Get Instructions
Get user-facing instructions for data collection.

**Endpoint:** `GET /api/get_instructions`

**Current Behavior:** Returns instructions for business evaluation agent
**Planned:** Add `?agent={agent_id}` parameter for universal support

**Response:**
```json
{
  "instructions": "Please provide the following information:\n- **Idea Overview**: Brief description of your business idea\n- **Deliverable**: What specific product or service will you deliver\n- **Motivation**: Why should this idea exist? What problem does it solve?",
  "testing_mode": true
}
```

#### 2. Get Price Points
Get available analysis tiers and pricing.

**Endpoint:** `POST /api/get_pricepoints`  
**Current:** Universal budget tiers loaded from `common/prompts.yaml`

**Request Body:**
```json
{
  "user_input": {
    "Idea_Overview": "AI-powered meal planning app",
    "Deliverable": "Mobile app with personalized meal recommendations", 
    "Motivation": "Help people eat healthier with minimal planning effort"
  }
}
```

**Response:**
```json
{
  "pricepoints": [
    {
      "level": "basic",
      "name": "Basic Analysis",
      "max_cost": 1.00,
      "estimated_cost": 1.00,
      "description": "1 optimized call with intelligent architecture planning",
      "time_estimate": "5-10 minutes",
      "deliverables": ["Comprehensive analysis with detailed insights..."]
    },
    {
      "level": "standard", 
      "name": "Standard Analysis",
      "max_cost": 3.00,
      "estimated_cost": 3.00,
      "description": "3 coordinated calls with intelligent architecture planning",
      "time_estimate": "15-20 minutes"
    },
    {
      "level": "premium",
      "name": "Premium Analysis", 
      "max_cost": 5.00,
      "estimated_cost": 5.00,
      "description": "5 coordinated calls with intelligent architecture planning",
      "time_estimate": "20-30 minutes"
    }
  ],
  "user_input": {
    "Idea_Overview": "AI-powered meal planning app",
    "Deliverable": "Mobile app with personalized meal recommendations",
    "Motivation": "Help people eat healthier with minimal planning effort"
  }
}
```

#### 3. Execute Analysis
Start analysis execution.

**Endpoint:** `POST /api/execute_analysis`

**Current Request Body:**
```json
{
  "user_input": {
    "Idea_Overview": "AI-powered meal planning app",
    "Deliverable": "Mobile app with personalized meal recommendations",
    "Motivation": "Help people eat healthier with minimal planning effort"
  },
  "budget_tier": "standard"
}
```

**Planned Request Body:**
```json
{
  "agent": "business_evaluation",
  "user_input": { ... },
  "budget_tier": "standard"
}
```

**Response:**
```json
{
  "analysis_job_id": "thread_abc123_run_def456",
  "status": "initiated",
  "estimated_completion": "2025-01-30T10:15:00Z"
}
```

#### 4. Process Analysis Results
Get analysis results and status.

**Endpoint:** `GET /api/process_idea?id={job_id}`

**Response (Processing):**
```json
{
  "status": "in_progress",
  "job_id": "thread_abc123_run_def456"
}
```

**Response (Complete):**
```json
{
  "status": "completed",
  "job_id": "thread_abc123_run_def456",
  "results": {
    "Novelty_Rating": 7,
    "Feasibility_Rating": 8, 
    "Effort_Rating": 6,
    "Impact_Rating": 8,
    "Risk_Rating": 4,
    "Overall_Rating": 7,
    "Analysis_Summary": "This AI-powered meal planning app shows strong potential...",
    "Potential_Improvements": "Consider partnering with grocery delivery services..."
  },
  "metadata": {
    "analysis_duration": "00:08:34",
    "calls_used": 3,
    "cost": 3.00
  }
}
```

#### 5. Read Sheet (Utility)
Read raw Google Sheets data.

**Endpoint:** `GET /api/read_sheet?id={sheet_id}`  
**Note:** Utility endpoint, unchanged in universal design

---

## Testing Guide

### Testing Mode Protection

Joey-Bot includes comprehensive testing protection to prevent OpenAI API charges and Google Sheets modifications during development.

#### Activation
```bash
# Environment Variable (Recommended)
export TESTING_MODE=true

# Auto-Detection
# Testing mode automatically activates when:
# - TESTING_MODE=true environment variable is set
# - pytest is running (detected via sys.modules)
# - Process name contains 'pytest'
```

#### Testing Mode Features

**🚫 No OpenAI API Charges**
- All OpenAI calls return mock responses immediately
- No actual API requests made to OpenAI
- Zero billing impact during development

**🔒 No Google Sheets Modifications**  
- Google Sheets operations are bypassed
- Uses in-memory mock data for testing
- Safe for parallel test execution

**⚡ Fast Execution**
- Mock responses return immediately
- No network latency or API wait times
- Perfect for rapid development cycles

### Test Structure (5 Core Tests)

The new universal test suite validates the three-layer system:

#### 1. `test_platform_config.py` - Platform Configuration
```bash
python -m pytest tests/test_platform_config.py -v
```
Tests universal platform settings from `common/prompts.yaml`:
- Universal budget tiers ($1/$3/$5)
- Model configuration (gpt-4o-mini)
- Universal prompt templates
- Cost tracking and pricing validation

#### 2. `test_dynamic_configuration.py` - Configuration Pipeline  
```bash
python -m pytest tests/test_dynamic_configuration.py -v
```
Tests YAML → Google Sheets → Runtime configuration flow:
- Agent definition loading from `agents/business_evaluation.yaml`
- Google Sheets schema parsing (rows 1-3)
- Full configuration combining static + dynamic config
- Instruction generation and prompt creation

#### 3. `test_universal_agent_engine.py` - Core Engine
```bash  
python -m pytest tests/test_universal_agent_engine.py -v
```
Tests the planned UniversalAgentEngine:
- Universal agent creation and initialization
- Multi-agent support and type switching
- Budget tier integration across agents
- Universal input validation and error handling

#### 4. `test_workflow_engine.py` - Multi-Call Workflows
```bash
python -m pytest tests/test_workflow_engine.py -v
```
Tests universal workflow patterns:
- Multi-tier workflow scaling (1/3/5 calls)
- Architecture planning and execution order
- Result synthesis and aggregation
- Integration with existing multi-call system

#### 5. `test_universal_endpoints.py` - Azure Functions
```bash
python -m pytest tests/test_universal_endpoints.py -v
```
Tests all HTTP endpoints end-to-end:
- Get instructions endpoint behavior
- Price points calculation
- Analysis execution workflow  
- Result polling and response formatting

### Running Tests
```bash
# Safe development testing (no API charges)
export TESTING_MODE=true
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_platform_config.py -v

# Run with coverage
python -m pytest tests/ --cov=common --cov-report=html

# Test Azure Functions locally
cd idea-guy && func start --python
# In another terminal:
curl "http://localhost:7071/api/get_instructions"
```

### Test Environment Setup
```bash
# Required for testing (mock values work)
export TESTING_MODE=true
export OPENAI_API_KEY=test-key-not-used-in-testing-mode
export IDEA_GUY_SHEET_ID=test-sheet-id
export GOOGLE_SHEETS_KEY_PATH=/path/to/mock/credentials.json
```

---

## Troubleshooting Guide

### Quick Diagnostics

#### System Health Check
```bash
python -c "
from common.http_utils import is_testing_mode
from common.agent_service import AnalysisService
print(f'✅ Testing mode: {is_testing_mode()}')
print('✅ Core imports: OK')
"
```

#### Environment Verification
```bash
python -c "
import os
required = ['OPENAI_API_KEY', 'IDEA_GUY_SHEET_ID']
for var in required:
    value = os.getenv(var, 'NOT SET')
    status = '✅' if value != 'NOT SET' else '❌'
    print(f'{status} {var}: {value[:10]}...' if len(value) > 10 else f'{status} {var}: {value}')
"
```

### Common Issues & Solutions

#### 🚨 API Charges During Development

**Problem:** Accidentally incurring OpenAI costs during testing

**Solution:**
```bash
# Always enable testing mode for development
export TESTING_MODE=true
```

**Verification:**
- All job IDs should start with `"mock_"` or contain `"test"`
- Responses include `"testing_mode": true`
- Analysis completes immediately (no waiting)

#### 🔧 Import Errors in Tests

**Problem:** `ImportError: cannot import name 'AnalysisCall'`

**Current Status:** New universal tests have import errors due to missing UniversalAgentEngine class

**Temporary Workaround:**
```bash
# Run only working tests
python -m pytest tests/test_platform_config.py -v
python -m pytest tests/test_dynamic_configuration.py -v
```

**Permanent Solution:** Implement UniversalAgentEngine class (see TASKLIST.md)

#### 🌐 Azure Functions Not Starting

**Problem:** `func start --python` fails

**Solutions:**
```bash
# Check Azure Functions Core Tools installation
func --version

# Install if missing
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Verify Python requirements
cd idea-guy
pip install -r requirements.txt

# Check for port conflicts
lsof -i :7071
```

#### 📊 Google Sheets Access Issues

**Problem:** Sheet access errors in production

**Solutions:**
```bash
# Verify credentials file exists
ls -la $GOOGLE_SHEETS_KEY_PATH

# Test sheet access
python -c "
from common.utils import get_google_sheets_client, get_spreadsheet
import os
client = get_google_sheets_client()
sheet = get_spreadsheet(client, os.environ['IDEA_GUY_SHEET_ID'])
print(f'✅ Sheet access: {sheet.title}')
"

# Check sheet permissions
# Ensure service account email has edit access to the sheet
```

#### 🤖 OpenAI API Issues

**Problem:** API key or model access issues

**Solutions:**
```bash
# Test API key (in production only)
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
response = client.models.list()
print('✅ OpenAI API access: OK')
"

# Check model access
# Ensure account has access to gpt-4o-mini

# Verify API quotas and billing
# Check OpenAI dashboard for usage limits
```

### Performance Issues

#### Slow Analysis Execution

**Diagnostics:**
```bash
# Check multi-call architecture performance
python -c "
from common.multi_call_architecture import create_multi_call_analysis
from common.agent_service import AnalysisService
import time
start = time.time()
# Run test analysis
print(f'Analysis time: {time.time() - start:.2f}s')
"
```

**Optimizations:**
- Enable testing mode for development to avoid API latency
- Check network connectivity to OpenAI and Google Sheets
- Monitor OpenAI API response times in production

#### Memory Usage Issues

**Diagnostics:**
```bash
# Monitor memory usage during tests
python -m pytest tests/ --profile --profile-svg
```

**Solutions:**
- Ensure proper cleanup of OpenAI client connections
- Use memory-efficient data structures in configuration loading
- Implement caching for frequently accessed configuration data

### Development Workflow Issues

#### Configuration Changes Not Reflected

**Problem:** Changes to YAML or Google Sheets not appearing

**Solutions:**
```bash
# Clear any cached configurations
rm -rf __pycache__/
rm -rf .pytest_cache/

# Restart Azure Functions
cd idea-guy && func start --python

# Verify configuration loading
python -c "
from common.agent_service import AnalysisService
service = AnalysisService('your-sheet-id')
config = service.agent_config
print(f'Agent: {config.definition.name}')
print(f'Budget tiers: {len(config.get_budget_tiers())}')
"
```

### Getting Help

#### Debug Information Collection
```bash
# Collect debug information
python -c "
import sys, os
from common.http_utils import is_testing_mode
from common.agent_service import AnalysisService

print('=== Joey-Bot Debug Information ===')
print(f'Python version: {sys.version}')
print(f'Testing mode: {is_testing_mode()}')
print(f'OpenAI key set: {bool(os.getenv("OPENAI_API_KEY"))}')
print(f'Sheet ID set: {bool(os.getenv("IDEA_GUY_SHEET_ID"))}')

try:
    service = AnalysisService(os.getenv('IDEA_GUY_SHEET_ID', 'test'))
    print(f'Service initialized: ✅')
    config = service.agent_config
    print(f'Agent config loaded: ✅')
    print(f'Budget tiers available: {len(config.get_budget_tiers())}')
except Exception as e:
    print(f'Service initialization failed: {e}')
"
```

#### Contact Information
- **Issues:** https://github.com/your-org/joey-bot/issues
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** See CLAUDE.md for additional resources

---

## Development Best Practices

### Code Quality
- Always use `TESTING_MODE=true` during development
- Run tests before committing changes
- Follow existing code patterns and naming conventions
- Update documentation when making architectural changes

### Configuration Management
- Test configuration changes in testing mode first
- Validate Google Sheets schema changes carefully
- Keep agent configurations minimal and focused
- Use universal templates when possible

### Deployment
- Verify all environment variables are set
- Test Azure Functions deployment with staging environment
- Monitor costs and usage after production deployments
- Keep testing mode disabled in production

This consolidated developer guide provides everything needed for development, testing, and troubleshooting in one comprehensive document.