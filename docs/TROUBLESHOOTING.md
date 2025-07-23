# Troubleshooting Guide

## Common Issues & Solutions

### 🚨 API Charges During Development

**Problem:** Accidentally incurring OpenAI costs during testing

**Solution:**
```bash
export TESTING_MODE=true
```

**Verification:**
```python
from common.http_utils import is_testing_mode
print(f"Testing mode active: {is_testing_mode()}")
```

**Expected behavior:**
- All job IDs start with `"mock_"`
- Responses include `"testing_mode": true`
- No actual API calls made

---

### 🔑 Missing Environment Variables

**Problem:** `ValueError: OpenAI API key is required`

**Solution:**
```bash
# Required for production
export OPENAI_API_KEY=your_api_key
export IDEA_GUY_SHEET_ID=your_sheet_id
export GOOGLE_SHEETS_KEY_PATH=path/to/credentials.json

# For testing only
export TESTING_MODE=true
export IDEA_GUY_SHEET_ID=test_sheet_id  # Any value works in testing mode
```

**Azure Function App Settings:**
```json
{
  "OPENAI_API_KEY": "sk-...",
  "IDEA_GUY_SHEET_ID": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "GOOGLE_SHEETS_KEY_PATH": "/home/site/wwwroot/credentials.json",
  "TESTING_MODE": "false"
}
```

---

### 📊 Google Sheets Access Issues

**Problem:** `Failed to initialize Google Sheets client`

**Symptoms:**
```
ERROR: [Errno 2] No such file or directory: 'mock_path'
ERROR: Failed to initialize Google Sheets client
```

**Solutions:**

1. **For Testing:**
   ```bash
   export TESTING_MODE=true  # Bypasses Google Sheets completely
   ```

2. **For Production:**
   ```bash
   # Verify service account file exists
   ls -la $GOOGLE_SHEETS_KEY_PATH
   
   # Check file permissions
   chmod 600 $GOOGLE_SHEETS_KEY_PATH
   
   # Verify JSON format
   python -c "import json; json.load(open('$GOOGLE_SHEETS_KEY_PATH'))"
   ```

3. **Service Account Setup:**
   - Enable Google Sheets API in Google Cloud Console
   - Create service account with Sheets access
   - Download JSON key file
   - Share spreadsheet with service account email

---

### 🔄 Analysis Jobs Not Completing

**Problem:** Jobs stuck in "processing" status

**Debug steps:**

1. **Check job ID format:**
   ```python
   # Mock jobs (testing mode)
   if job_id.startswith("mock_"):
       print("This is a test job - should complete immediately")
   
   # Real jobs (production mode)
   else:
       print("This is a production job - may take 5-30 minutes")
   ```

2. **Verify OpenAI job status:**
   ```python
   from common import get_openai_client
   client = get_openai_client()
   response = client.responses.retrieve(job_id)
   print(f"OpenAI job status: {response.status}")
   ```

3. **Check budget tier configuration:**
   ```python
   from common.budget_config import BudgetConfigManager
   manager = BudgetConfigManager()
   try:
       tier = manager.get_tier_config("your_tier")
       print(f"Tier config: {tier}")
   except KeyError as e:
       print(f"Invalid tier: {e}")
   ```

---

### 🤖 ChatGPT Bot Integration Issues

**Problem:** Bot receives unclear error messages

**Error Response Structure:**
```json
{
  "error": "Clear user-facing message",
  "status": "error",
  "success": false,
  "error_type": "validation_error",
  "suggestion": "Actionable guidance for user",
  "details": {"additional": "context"}
}
```

**Common Error Types:**

| Error Type | Cause | Bot Action |
|------------|-------|------------|
| `missing_field` | Required field empty/missing | Ask user for specific field |
| `invalid_budget_tier` | Unknown tier selected | Show available options |
| `validation_error` | Input format incorrect | Guide user to correct format |
| `server_error` | Internal system issue | Suggest retry or contact support |

**Debug ChatGPT workflow:**
```python
# Test complete workflow
python test_chatgpt_flow.py

# Check specific endpoint
curl -X POST /api/get_pricepoints \
  -H "Content-Type: application/json" \
  -d '{"user_input": {"Idea_Overview": "test", "Deliverable": "test", "Motivation": "test"}}'
```

---

### 🏗️ Import and Module Issues

**Problem:** `ModuleNotFoundError` or import failures

**Solution:**
```python
# Add project root to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# For Azure Functions, add idea-guy directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'idea-guy'))
```

**Verify imports work:**
```python
try:
    from common.agent_service import AnalysisService
    from common.budget_config import BudgetConfigManager
    from common.http_utils import build_json_response
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

---

### 🔧 Azure Functions Deployment Issues

**Problem:** Functions don't appear in Azure portal

**Checklist:**
- [ ] `function.json` files exist in each endpoint directory
- [ ] `requirements.txt` includes all dependencies
- [ ] Environment variables set in Function App settings
- [ ] Python version matches (`python -V`)
- [ ] No syntax errors in code (`python -m py_compile filename.py`)

**Debug deployment:**
```bash
# Test locally first
func start

# Check function discovery
func azure functionapp list-functions your-function-app

# View deployment logs
func azure functionapp logstream your-function-app
```

---

### 📈 Performance Issues

**Problem:** Slow response times or timeouts

**Optimization checklist:**

1. **Enable lazy initialization:**
   ```python
   # ✅ Good - lazy loading
   @property
   def openai_client(self):
       if self._client is None:
           self._client = get_openai_client()
       return self._client
   
   # ❌ Bad - import-time loading
   client = get_openai_client()  # At module level
   ```

2. **Use testing mode for development:**
   ```bash
   export TESTING_MODE=true  # Instant mock responses
   ```

3. **Monitor Azure Function execution times:**
   ```bash
   # Check function logs
   func azure functionapp logstream your-function-app
   ```

4. **Optimize budget tier selection:**
   ```python
   # Basic tier (fastest, cheapest)
   budget_tier = "basic"  # 5-10 minutes, $0.20
   
   # Premium tier (slowest, most comprehensive)  
   budget_tier = "premium"  # 20-30 minutes, $2.50
   ```

---

### 🔍 Debugging Production Issues

**Log Analysis:**

1. **Find detailed error context:**
   ```bash
   # Look for structured error logs
   grep "Error Details:" function_logs.txt
   ```

2. **Check error patterns:**
   ```json
   {
     "error_type": "validation_error",
     "endpoint": "execute_analysis",
     "budget_tier": "premium",
     "exception_type": "ValidationError",
     "testing_mode": false
   }
   ```

3. **Trace request flow:**
   ```bash
   # Follow job through workflow
   grep "job_id_12345" function_logs.txt | sort
   ```

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in Azure Functions
logging.getLogger().setLevel(logging.DEBUG)
```

---

### 🧪 Test Failures

**Problem:** Tests failing unexpectedly

**Debug steps:**

1. **Verify testing mode:**
   ```bash
   echo $TESTING_MODE  # Should be "true"
   ```

2. **Check environment isolation:**
   ```python
   # Clear environment between tests
   import os
   for key in list(os.environ.keys()):
       if key.startswith(('TESTING_', 'IDEA_GUY_')):
           del os.environ[key]
   ```

3. **Run tests individually:**
   ```bash
   python -c "
   import sys
   sys.path.append('.')
   from test_simple_endpoint import test_budget_tier_system
   test_budget_tier_system()
   "
   ```

4. **Validate mock data:**
   ```python
   from common.agent_service import AnalysisService
   service = AnalysisService('test_id')
   
   # Should not trigger real API calls
   result = service.get_budget_options(test_input)
   assert result.get('testing_mode') is True
   ```

---

## Getting Help

### 1. Check Logs First
```bash
# Azure Functions
func azure functionapp logstream your-function-app

# Local development
func start --verbose
```

### 2. Enable Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Test Endpoints Individually
```bash
# Test each part of the workflow
python test_simple_endpoint.py      # Core logic
python test_chatgpt_flow.py         # End-to-end workflow
```

### 4. Verify Configuration
```python
# Check all environment variables
import os
for key, value in os.environ.items():
    if any(x in key for x in ['OPENAI', 'GOOGLE', 'IDEA_GUY', 'TESTING']):
        print(f"{key}: {'*' * len(value) if 'KEY' in key else value}")
```

### 5. Contact Support
When reporting issues, include:
- Error messages with full stack traces
- Environment variable configuration (redact API keys)
- Testing mode status
- Endpoint and request data that caused the issue
- Expected vs actual behavior