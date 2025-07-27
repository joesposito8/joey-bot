# Joey-Bot Troubleshooting Guide

**Last Updated**: 2025-01-27  
**System**: Universal AI Agent Platform

## Quick Diagnostics

### System Health Check
```bash
# Verify system components
python -c "
from common.http_utils import is_testing_mode
from common.agent_service import AnalysisService
print(f'✅ Testing mode: {is_testing_mode()}')
print('✅ Core imports: OK')
"
```

### Environment Verification
```bash
# Check required environment variables
python -c "
import os
required = ['OPENAI_API_KEY', 'IDEA_GUY_SHEET_ID']
for var in required:
    value = os.getenv(var, 'NOT SET')
    status = '✅' if value != 'NOT SET' else '❌'
    print(f'{status} {var}: {value[:10]}...' if len(value) > 10 else f'{status} {var}: {value}')
"
```

---

## Common Issues & Solutions

### 🚨 **API Charges During Development**

**Problem:** Accidentally incurring OpenAI costs during testing

**Solution:**
```bash
# Always enable testing mode for development
export TESTING_MODE=true
```

**Verification:**
- All job IDs should start with `"mock_"` or `"job_"`
- Responses include `"testing_mode": true`
- Analysis completes immediately (no waiting)

**Prevention:**
```python
# Add to development scripts
from common.http_utils import is_testing_mode
assert is_testing_mode(), "Testing mode must be enabled for development"
```

---

### 🔑 **Environment Variables Missing**

**Problem:** `ValueError: OpenAI API key is required`

**Development Solution:**
```bash
export TESTING_MODE=true
export OPENAI_API_KEY=dummy_key_for_testing
export IDEA_GUY_SHEET_ID=dummy_sheet_id
```

**Production Solution:**
```bash
export OPENAI_API_KEY=sk-your-actual-api-key
export IDEA_GUY_SHEET_ID=your-google-sheet-id
export GOOGLE_SHEETS_KEY_PATH=path/to/service-account.json
```

**Azure Function App Settings:**
```json
{
  "OPENAI_API_KEY": "sk-your-actual-key",
  "IDEA_GUY_SHEET_ID": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "GOOGLE_SHEETS_KEY_PATH": "/home/site/wwwroot/.keys/service-account.json"
}
```

---

### 📊 **Google Sheets Access Issues**

**Problem:** `SheetAccessError: Cannot access sheet at {url}`

**Diagnosis:**
```python
# Test sheet access
from common.config.sheet_schema_reader import SheetSchemaReader
from common.utils import get_google_sheets_client

try:
    gc = get_google_sheets_client()
    reader = SheetSchemaReader(gc)
    schema = reader.parse_sheet_schema("your-sheet-url")
    print("✅ Sheet access OK")
except Exception as e:
    print(f"❌ Sheet access failed: {e}")
```

**Solutions:**

1. **Service Account Permissions:**
   - Share Google Sheet with service account email
   - Grant "Editor" permissions
   - Verify service account key file path

2. **URL Format:**
   ```python
   # Correct format
   sheet_url = "https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0"
   
   # Extract sheet ID
   import re
   sheet_id = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url).group(1)
   ```

3. **Schema Validation:**
   - Ensure rows 1-3 contain schema definition
   - Row 1: Field types ("user input" or "bot output")  
   - Row 2: Field descriptions
   - Row 3: Field names (column headers)

---

### 🔄 **Analysis Stuck in Processing**

**Problem:** `GET /api/process_idea` returns `"status": "processing"` indefinitely

**Diagnosis:**
```bash
# Check OpenAI job status directly
python -c "
from common.utils import get_openai_client
client = get_openai_client()
job_id = 'your-job-id'
try:
    response = client.responses.retrieve(job_id)
    print(f'OpenAI status: {response.status}')
except Exception as e:
    print(f'Job not found or failed: {e}')
"
```

**Solutions:**

1. **Check OpenAI Dashboard:**
   - Log into OpenAI platform
   - Check API usage and quotas
   - Verify job completion status

2. **Timeout Handling:**
   ```python
   # Implement timeout in client code
   import time
   max_wait = 1800  # 30 minutes
   start_time = time.time()
   
   while time.time() - start_time < max_wait:
       result = check_analysis_status(job_id)
       if result['status'] == 'completed':
           break
       time.sleep(30)
   else:
       raise TimeoutError("Analysis timed out")
   ```

3. **Manual Result Retrieval:**
   ```python
   # Force result retrieval for debugging
   from idea_guy.process_idea import main
   import azure.functions as func
   
   # Create mock request
   req = func.HttpRequest(
       method='GET',
       body=b'',
       url=f'http://localhost/api/process_idea?id={job_id}',
       headers={}
   )
   response = main(req)
   print(response.get_body().decode())
   ```

---

### 🎯 **Validation Errors**

**Problem:** `ValidationError: Missing required input fields`

**Diagnosis:**
```python
# Check agent configuration
from common.config import AgentDefinition, FullAgentConfig
from pathlib import Path

config_path = Path("agents/business_evaluation.yaml")
agent_def = AgentDefinition.from_yaml(config_path)
full_config = FullAgentConfig.from_definition(agent_def)

# Check required fields
required_fields = [field.name for field in full_config.schema.input_fields]
print(f"Required fields: {required_fields}")

# Test validation
user_input = {"Idea_Overview": "Test"}  # Incomplete
try:
    full_config.schema.validate_input(user_input)
    print("✅ Validation passed")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

**Solution:**
Ensure all required fields are provided:
```json
{
  "user_input": {
    "Idea_Overview": "Brief description of your business idea",
    "Deliverable": "What specific product or service will you deliver", 
    "Motivation": "Why should this idea exist? What problem does it solve?"
  }
}
```

---

### 🏗️ **Import Errors**

**Problem:** `ModuleNotFoundError: No module named 'common'`

**Solutions:**

1. **Python Path:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python your_script.py
   ```

2. **Azure Functions:**
   ```python
   # Add to top of Azure Function
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
   ```

3. **Package Installation:**
   ```bash
   # Install in development mode
   pip install -e .
   
   # Or install requirements
   pip install -r requirements.txt
   ```

---

### 💰 **Cost Tracking Issues**

**Problem:** `openai_costs.log` not updating or missing cost information

**Diagnosis:**
```bash
# Check log file permissions and content
ls -la openai_costs.log
tail -n 5 openai_costs.log

# Test cost logging
python -c "
from common.cost_tracker import log_openai_cost
log_openai_cost('test', 'gpt-4o-mini', 'standard', 'test_job', 
                {'total_tokens': 1000}, 0.01, {'test': 'data'})
print('Cost logged successfully')
"
```

**Solutions:**

1. **File Permissions:**
   ```bash
   # Ensure write permissions
   chmod 644 openai_costs.log
   touch openai_costs.log  # Create if missing
   ```

2. **Log Rotation:**
   ```bash
   # Archive large log files
   mv openai_costs.log openai_costs.log.backup
   touch openai_costs.log
   ```

3. **Cost Calculation:**
   ```python
   # Verify cost calculation
   from common.cost_tracker import calculate_cost_from_usage
   
   usage = {"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500}
   cost = calculate_cost_from_usage("gpt-4o-mini", usage)
   print(f"Calculated cost: ${cost:.4f}")
   ```

---

### 🔧 **Azure Functions Issues**

**Problem:** Functions not starting or returning 500 errors

**Local Development:**
```bash
# Check function runtime
cd idea-guy
func --version

# Start with verbose logging
func start --python --verbose

# Test specific function
func new --name test_function --template "HTTP trigger" --authlevel anonymous
```

**Deployment Issues:**
```bash
# Check deployment logs
az functionapp log tail --name your-function-app --resource-group your-rg

# Verify function app settings
az functionapp config appsettings list --name your-function-app --resource-group your-rg
```

---

### 🔍 **Configuration Issues**

**Problem:** Agent configuration not loading or schema parsing fails

**Diagnosis:**
```python
# Test YAML loading
from common.config.agent_definition import AgentDefinition
from pathlib import Path

try:
    config = AgentDefinition.from_yaml(Path("agents/business_evaluation.yaml"))
    print(f"✅ Config loaded: {config.agent_id}")
    print(f"Budget tiers: {len(config.budget_tiers)}")
except Exception as e:
    print(f"❌ Config failed: {e}")

# Test schema parsing
from common.config.sheet_schema_reader import SheetSchemaReader
from common.utils import get_google_sheets_client

try:
    gc = get_google_sheets_client()
    reader = SheetSchemaReader(gc)
    schema = reader.parse_sheet_schema(config.sheet_url)
    print(f"✅ Schema parsed: {len(schema.input_fields)} input, {len(schema.output_fields)} output")
except Exception as e:
    print(f"❌ Schema failed: {e}")
```

**Solutions:**

1. **YAML Syntax:**
   ```bash
   # Validate YAML syntax
   python -c "
   import yaml
   with open('agents/business_evaluation.yaml') as f:
       yaml.safe_load(f)
   print('YAML syntax valid')
   "
   ```

2. **Schema Format:**
   Ensure Google Sheet has proper schema in rows 1-3:
   ```
   Row 1: | ID | Time | user input | user input | user input | bot output | bot output |
   Row 2: | ID | Time | Brief desc | What will  | Why this   | How novel  | Detailed   |
   Row 3: | ID | Time | Idea_Overvw| Deliverable| Motivation | Novelty_Rtg| Analysis   |
   ```

---

## Performance Issues

### 🐌 **Slow Response Times**

**Problem:** API endpoints taking too long to respond

**Monitoring:**
```python
# Add timing to requests
import time
start_time = time.time()

# Your API call here
response = make_api_request()

duration = time.time() - start_time
print(f"Request took {duration:.2f} seconds")
```

**Optimization:**
1. **Enable caching** for budget tier configurations
2. **Use testing mode** for development to avoid OpenAI delays
3. **Implement request timeouts** in client code
4. **Monitor Azure Function performance** metrics

### 📊 **Memory Usage**

**Problem:** High memory consumption or out-of-memory errors

**Monitoring:**
```python
# Check memory usage
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f} MB")
```

**Solutions:**
1. **Clear large variables** after use
2. **Use generators** for large data processing
3. **Increase Azure Function memory allocation**

---

## Debugging Tools

### 🔍 **Enable Debug Logging**

```python
# Add to any module for detailed logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use in Azure Functions
import azure.functions as func
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function started')
    
    # Your code here
    
    logging.info('Function completed')
```

### 📝 **Request/Response Tracing**

```python
# Add request tracing
def trace_request(req: func.HttpRequest):
    logging.info(f"Method: {req.method}")
    logging.info(f"URL: {req.url}")
    logging.info(f"Headers: {dict(req.headers)}")
    logging.info(f"Body: {req.get_body().decode()}")

def trace_response(response: func.HttpResponse):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Body: {response.get_body().decode()}")
```

### 🧪 **Interactive Testing**

```python
# Use IPython for interactive debugging
# pip install ipython

def debug_analysis():
    from IPython import embed
    
    # Set up test data
    user_input = {
        "Idea_Overview": "Test idea",
        "Deliverable": "Test deliverable", 
        "Motivation": "Test motivation"
    }
    
    # Start interactive session
    embed()  # This will open an interactive Python shell

# Run: python -c "from debug import debug_analysis; debug_analysis()"
```

---

## Getting Help

### 📋 **Information to Gather**

When reporting issues, include:

1. **Environment Details:**
   ```bash
   python --version
   echo $TESTING_MODE
   echo $OPENAI_API_KEY | head -c 10
   ```

2. **Error Messages:**
   - Full error stack trace
   - Relevant log entries
   - Request/response data

3. **Reproduction Steps:**
   - Exact commands run
   - Input data used
   - Expected vs actual behavior

### 📞 **Support Resources**

- **System Architecture**: `docs/SYSTEM_ARCHITECTURE.md`
- **API Reference**: `docs/API.md` 
- **Testing Guide**: `docs/TESTING.md`
- **Configuration Files**: `agents/business_evaluation.yaml`
- **Cost Logs**: `openai_costs.log`

### 🔧 **Emergency Recovery**

**System won't start:**
```bash
# Reset to testing mode
export TESTING_MODE=true
unset OPENAI_API_KEY

# Test basic imports
python -c "from common.agent_service import AnalysisService; print('OK')"
```

**Clear all state:**
```bash
# Remove cached data
rm -rf __pycache__
rm -rf common/__pycache__
rm -rf idea-guy/__pycache__

# Restart Azure Functions
cd idea-guy && func start --python
```

For critical production issues, always enable testing mode first to prevent additional API charges while debugging.