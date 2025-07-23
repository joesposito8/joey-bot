# API Reference

## Base URL
- **Production:** `https://your-function-app.azurewebsites.net`
- **Local Development:** `http://localhost:7071`

## Authentication
All endpoints require Azure Function authentication via `x-functions-key` header:
```bash
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \
     -H "Content-Type: application/json" \
     "https://your-app.azurewebsites.net/api/endpoint"
```

## Endpoints

### 1. Get Instructions
Get workflow instructions for ChatGPT bot integration.

**Endpoint:** `GET /api/get_instructions`

**Response:**
```json
{
  "instructions": "You are an expert business analyst who evaluates startup ideas...",
  "testing_mode": true,
  "note": "Running in testing mode - no API charges will occur during analysis"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### 2. Get Price Points
Get available budget tiers and pricing options.

**Endpoint:** `POST /api/get_pricepoints`

**Request Body:**
```json
{
  "user_input": {
    "Idea_Overview": "A mobile app for local event discovery",
    "Deliverable": "iOS and Android app with event listings and booking",
    "Motivation": "Help people find and attend local events easily"
  },
  "spreadsheet_id": "optional_sheet_id"
}
```

**Response:**
```json
{
  "agent_type": "business_evaluation",
  "pricepoints": [
    {
      "level": "basic",
      "name": "Quick Analysis",
      "max_cost": 0.20,
      "estimated_cost": 0.02,
      "model": "gpt-4o-mini",
      "description": "Fast basic evaluation with core metrics",
      "deliverables": [
        "Basic ratings (1-10 scale)",
        "Short rationales (1-2 sentences)",
        "Simple assessment summary"
      ],
      "time_estimate": "5-10 minutes"
    },
    {
      "level": "standard",
      "name": "Detailed Analysis",
      "max_cost": 1.00,
      "estimated_cost": 0.40,
      "model": "o1-mini",
      "description": "Comprehensive evaluation with market research",
      "deliverables": [
        "Detailed ratings with full rationales",
        "Competitor analysis and benchmarking",
        "Market size analysis (TAM/SAM/SOM)",
        "Risk assessment with mitigation strategies"
      ],
      "time_estimate": "15-20 minutes"
    },
    {
      "level": "premium",
      "name": "Deep Research Analysis",
      "max_cost": 2.50,
      "estimated_cost": 2.00,
      "model": "o4-mini-deep-research",
      "description": "Exhaustive analysis with extensive market research",
      "deliverables": [
        "Comprehensive ratings with detailed analysis",
        "Deep competitor research with specific examples",
        "Market sizing with multiple data sources",
        "Patent and prior art analysis",
        "Regulatory and compliance considerations",
        "Implementation roadmap suggestions"
      ],
      "time_estimate": "20-30 minutes"
    }
  ],
  "user_input": {
    "Idea_Overview": "A mobile app for local event discovery",
    "Deliverable": "iOS and Android app with event listings and booking",
    "Motivation": "Help people find and attend local events easily"
  },
  "message": "Select a budget tier and call /api/execute_analysis to start the analysis",
  "next_endpoint": "/api/execute_analysis",
  "timestamp": "2024-01-15T10:30:00.123456",
  "testing_mode": true,
  "note": "Running in testing mode - no API charges will occur"
}
```

**Status Codes:**
- `200` - Success
- `400` - Validation error (missing/invalid fields)
- `500` - Server error

---

### 3. Execute Analysis
Start business idea analysis with selected budget tier.

**Endpoint:** `POST /api/execute_analysis`

**Request Body:**
```json
{
  "user_input": {
    "Idea_Overview": "A mobile app for local event discovery",
    "Deliverable": "iOS and Android app with event listings and booking",
    "Motivation": "Help people find and attend local events easily"
  },
  "budget_tier": "standard",
  "spreadsheet_id": "optional_sheet_id"
}
```

**Response:**
```json
{
  "job_id": "mock_d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "status": "processing",
  "agent_type": "business_evaluation",
  "budget_tier": "standard",
  "spreadsheet_record_id": "d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "message": "Analysis started with standard tier. Use job_id to poll /api/process_idea",
  "next_endpoint": "/api/process_idea?id=mock_d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "timestamp": "2024-01-15T10:30:00.123456",
  "testing_mode": true,
  "note": "This is a mock job for testing purposes - no actual analysis will be performed"
}
```

**Status Codes:**
- `200` - Analysis started successfully
- `400` - Validation error (invalid budget tier, missing fields)
- `500` - Server error

---

### 4. Process Idea (Check Status)
Check analysis job status and retrieve results when complete.

**Endpoint:** `GET /api/process_idea?id={job_id}`

**Query Parameters:**
- `id` (required) - Job ID returned from execute_analysis

**Processing Response (HTTP 202):**
```json
{
  "status": "processing",
  "message": "The idea analysis is still being processed. Please try again later.",
  "job_id": "mock_d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Completed Response (HTTP 200):**
```json
{
  "status": "completed",
  "message": "Idea analysis completed successfully",
  "job_id": "mock_d24b7d43-4e91-4a3b-9e14-218d18d18930",
  "Novelty_Rating": "7",
  "Novelty_Rationale": "This idea shows moderate novelty with AI-powered personalization features...",
  "Feasibility_Rating": "8",
  "Feasibility_Rationale": "The technology stack is mature with proven frameworks available...",
  "Effort_Rating": "6",
  "Effort_Rationale": "This project would require approximately 3-6 months with a team of 3-4 developers...",
  "Impact_Rating": "8",
  "Impact_Rationale": "The event discovery market has strong growth potential...",
  "Risk_Rating": "5",
  "Risk_Rationale": "Moderate risk due to competitive landscape and market saturation...",
  "Overall_Rating": "7",
  "Overall_Rationale": "Strong concept with good market potential and feasible implementation...",
  "Analysis_Summary": "This is a promising idea with clear market demand. The event discovery space has shown consistent growth...",
  "Potential_Improvements": "Consider adding AI-powered personalization features to differentiate from existing competitors...",
  "timestamp": "2024-01-15T10:35:00.123456",
  "testing_mode": true
}
```

**Status Codes:**
- `200` - Analysis completed
- `202` - Analysis still processing (poll again)
- `400` - Missing job ID
- `422` - Analysis completed but validation failed
- `500` - Server error

---

### 5. Read Sheet (Legacy)
Read data from Google Sheets spreadsheet.

**Endpoint:** `GET /api/read_sheet?id={optional_id}`

**Query Parameters:**
- `id` (optional) - Filter by specific row ID

**Response:**
```json
{
  "sheet_data": {
    "Sheet1": [
      {
        "ID": "12345-abcd-6789-efgh",
        "Timestamp": "2024-01-15 10:30:00",
        "Idea_Overview": "A mobile app for fitness class booking",
        "Deliverable": "Mobile application with booking system",
        "Motivation": "Solve fitness class discovery problem",
        "Novelty_Rating": "7",
        "Novelty_Rationale": "Moderate novelty with incremental improvements",
        "Overall_Rating": "7",
        "Analysis_Summary": "Promising idea with good market potential"
      }
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - No matching row found (when using ID filter)
- `500` - Server error

---

## Error Responses

All endpoints return structured error responses:

```json
{
  "error": "Clear user-facing error message",
  "status": "error",
  "success": false,
  "error_type": "validation_error",
  "suggestion": "Actionable guidance for fixing the issue",
  "details": {
    "additional": "context information"
  },
  "testing_mode": true
}
```

### Error Types

| Type | Description | HTTP Status |
|------|-------------|-------------|
| `missing_field` | Required field not provided | 400 |
| `validation_error` | Input validation failed | 400 |
| `invalid_budget_tier` | Unknown budget tier selected | 400 |
| `missing_job_id` | Job ID not provided for status check | 400 |
| `output_validation_error` | Analysis output validation failed | 422 |
| `server_error` | Internal system error | 500 |
| `service_unavailable` | External service unavailable | 500 |

## Request/Response Examples

### Workflow Example

1. **Get Instructions:**
```bash
curl -X GET \
  -H "x-functions-key: YOUR_KEY" \
  "https://your-app.azurewebsites.net/api/get_instructions"
```

2. **Get Price Points:**
```bash
curl -X POST \
  -H "x-functions-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "Idea_Overview": "AI-powered recipe app",
      "Deliverable": "Mobile app with recipe recommendations",
      "Motivation": "Help people cook healthier meals"
    }
  }' \
  "https://your-app.azurewebsites.net/api/get_pricepoints"
```

3. **Execute Analysis:**
```bash
curl -X POST \
  -H "x-functions-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "Idea_Overview": "AI-powered recipe app",
      "Deliverable": "Mobile app with recipe recommendations", 
      "Motivation": "Help people cook healthier meals"
    },
    "budget_tier": "standard"
  }' \
  "https://your-app.azurewebsites.net/api/execute_analysis"
```

4. **Check Status:**
```bash
curl -X GET \
  -H "x-functions-key: YOUR_KEY" \
  "https://your-app.azurewebsites.net/api/process_idea?id=job_12345"
```

### Error Handling Examples

**Missing Field Error:**
```bash
# Request with missing Deliverable field
curl -X POST \
  -H "x-functions-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "Idea_Overview": "Great app idea"
    }
  }' \
  "https://your-app.azurewebsites.net/api/get_pricepoints"

# Response (400):
{
  "error": "Input validation failed: Missing or empty required input fields: ['Deliverable', 'Motivation']",
  "status": "error",
  "success": false,
  "error_type": "input_validation_error",
  "suggestion": "Please check your request format and required fields",
  "details": {
    "endpoint": "get_pricepoints"
  }
}
```

**Invalid Budget Tier:**
```bash
# Request with invalid tier
curl -X POST \
  -H "x-functions-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "Idea_Overview": "Great app idea",
      "Deliverable": "Mobile app",
      "Motivation": "Help users"
    },
    "budget_tier": "super_premium"
  }' \
  "https://your-app.azurewebsites.net/api/execute_analysis"

# Response (400):
{
  "error": "Invalid budget tier selected: \"Invalid budget tier 'super_premium'. Available: ['basic', 'standard', 'premium']\". Available tiers: basic, standard, premium",
  "status": "error",
  "success": false,
  "error_type": "invalid_budget_tier",
  "suggestion": "Please check your request format and required fields"
}
```

## Testing

### Enable Testing Mode
```bash
export TESTING_MODE=true
```

### Testing Mode Features
- All responses include `"testing_mode": true`
- Mock job IDs start with `"mock_"`
- No OpenAI API calls (no charges)
- Immediate fake results for completed analysis
- No Google Sheets modifications

### Test Complete Workflow
```bash
# Run comprehensive test suite
python test_chatgpt_flow.py

# Test individual endpoints
python test_simple_endpoint.py
```

## Rate Limits & Usage

### OpenAI API Limits
- **Basic Tier:** ~1 request every 3 seconds
- **Standard Tier:** ~1 request every 8 seconds  
- **Premium Tier:** ~1 request every 14 seconds

### Recommended Usage Patterns
- Use testing mode for development and CI/CD
- Implement exponential backoff for polling process_idea
- Cache budget tier configurations
- Monitor API usage through Azure Function metrics

## SDK Examples

### Python
```python
import requests
import time

class JoeyBotClient:
    def __init__(self, base_url, function_key):
        self.base_url = base_url
        self.headers = {
            'x-functions-key': function_key,
            'Content-Type': 'application/json'
        }
    
    def get_instructions(self):
        response = requests.get(f"{self.base_url}/api/get_instructions", 
                               headers=self.headers)
        return response.json()
    
    def get_pricepoints(self, user_input):
        response = requests.post(f"{self.base_url}/api/get_pricepoints",
                                json={'user_input': user_input},
                                headers=self.headers)
        return response.json()
    
    def execute_analysis(self, user_input, budget_tier):
        response = requests.post(f"{self.base_url}/api/execute_analysis",
                                json={
                                    'user_input': user_input,
                                    'budget_tier': budget_tier
                                },
                                headers=self.headers)
        return response.json()
    
    def wait_for_completion(self, job_id, max_wait=1800):
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = requests.get(f"{self.base_url}/api/process_idea?id={job_id}",
                                   headers=self.headers)
            result = response.json()
            
            if result.get('status') == 'completed':
                return result
            elif result.get('status') == 'processing':
                time.sleep(30)  # Wait 30 seconds before next poll
            else:
                raise Exception(f"Analysis failed: {result}")
        
        raise TimeoutError("Analysis did not complete within maximum wait time")

# Usage
client = JoeyBotClient("https://your-app.azurewebsites.net", "your-function-key")

user_input = {
    "Idea_Overview": "AI-powered fitness coaching app",
    "Deliverable": "Mobile app with personalized workout plans",
    "Motivation": "Help people achieve fitness goals with AI guidance"
}

# Get budget options
pricepoints = client.get_pricepoints(user_input)
print("Available tiers:", [tier['name'] for tier in pricepoints['pricepoints']])

# Start analysis
job = client.execute_analysis(user_input, "standard")
print(f"Analysis started with job ID: {job['job_id']}")

# Wait for completion
result = client.wait_for_completion(job['job_id'])
print(f"Analysis completed with overall rating: {result['Overall_Rating']}")
```

### JavaScript/Node.js
```javascript
class JoeyBotClient {
    constructor(baseUrl, functionKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'x-functions-key': functionKey,
            'Content-Type': 'application/json'
        };
    }

    async getInstructions() {
        const response = await fetch(`${this.baseUrl}/api/get_instructions`, {
            headers: this.headers
        });
        return response.json();
    }

    async getPricepoints(userInput) {
        const response = await fetch(`${this.baseUrl}/api/get_pricepoints`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ user_input: userInput })
        });
        return response.json();
    }

    async executeAnalysis(userInput, budgetTier) {
        const response = await fetch(`${this.baseUrl}/api/execute_analysis`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                user_input: userInput,
                budget_tier: budgetTier
            })
        });
        return response.json();
    }

    async waitForCompletion(jobId, maxWait = 1800000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < maxWait) {
            const response = await fetch(`${this.baseUrl}/api/process_idea?id=${jobId}`, {
                headers: this.headers
            });
            const result = await response.json();
            
            if (result.status === 'completed') {
                return result;
            } else if (result.status === 'processing') {
                await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
            } else {
                throw new Error(`Analysis failed: ${JSON.stringify(result)}`);
            }
        }
        
        throw new Error('Analysis did not complete within maximum wait time');
    }
}

// Usage
const client = new JoeyBotClient('https://your-app.azurewebsites.net', 'your-function-key');

const userInput = {
    "Idea_Overview": "Smart home energy management system",
    "Deliverable": "IoT platform with mobile app and smart devices",
    "Motivation": "Help homeowners reduce energy costs and environmental impact"
};

(async () => {
    try {
        // Get budget options
        const pricepoints = await client.getPricepoints(userInput);
        console.log('Available tiers:', pricepoints.pricepoints.map(tier => tier.name));
        
        // Start analysis
        const job = await client.executeAnalysis(userInput, 'premium');
        console.log(`Analysis started with job ID: ${job.job_id}`);
        
        // Wait for completion
        const result = await client.waitForCompletion(job.job_id);
        console.log(`Analysis completed with overall rating: ${result.Overall_Rating}`);
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```