# Joey-Bot API Reference

**Last Updated**: 2025-01-27  
**Version**: Universal AI Agent Platform

## Base URL
- **Production:** `https://your-function-app.azurewebsites.net`
- **Local Development:** `http://localhost:7071`

## Authentication
All endpoints require Azure Function authentication:
```bash
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \
     -H "Content-Type: application/json" \
     "https://your-app.azurewebsites.net/api/endpoint"
```

## Complete Workflow

### 1. Get Instructions → 2. Get Price Points → 3. Execute Analysis → 4. Poll Results

---

## Endpoints

### 1. Get Instructions
Get user-facing instructions for data collection.

**Endpoint:** `GET /api/get_instructions`

**Response:**
```json
{
  "instructions": "Please provide the following information:\n- **Idea Overview**: Brief description of your business idea\n- **Deliverable**: What specific product or service will you deliver\n- **Motivation**: Why should this idea exist? What problem does it solve?",
  "testing_mode": true
}
```

### 2. Get Price Points
Get available analysis tiers and pricing.

**Endpoint:** `POST /api/get_pricepoints`

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
  "budget_options": [
    {
      "level": "basic",
      "price": 1.00,
      "calls": 1,
      "description": "Quick evaluation with essential insights",
      "estimated_time": "2-5 minutes"
    },
    {
      "level": "standard", 
      "price": 3.00,
      "calls": 3,
      "description": "Detailed analysis with strategic planning",
      "estimated_time": "8-15 minutes"
    },
    {
      "level": "premium",
      "price": 5.00,
      "calls": 5,
      "description": "Comprehensive evaluation with market research",
      "estimated_time": "15-25 minutes"
    }
  ],
  "testing_mode": true
}
```

### 3. Execute Analysis
Start business idea analysis.

**Endpoint:** `POST /api/execute_analysis`

**Request Body:**
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

**Response:**
```json
{
  "job_id": "job_1737999123",
  "status": "processing",
  "budget_tier": "standard",
  "message": "Analysis started. Use job_id to poll for results.",
  "testing_mode": true
}
```

### 4. Process Results
Poll for analysis completion and retrieve results.

**Endpoint:** `GET /api/process_idea?id={job_id}`

**Processing Response (HTTP 202):**
```json
{
  "status": "processing",
  "message": "Analysis in progress. Please check again shortly.",
  "job_id": "job_1737999123"
}
```

**Completed Response (HTTP 200):**
```json
{
  "status": "completed",
  "job_id": "job_1737999123",
  "Novelty_Rating": "8",
  "Novelty_Rationale": "The AI-powered personalization approach shows strong innovation...",
  "Feasibility_Rating": "7", 
  "Feasibility_Rationale": "Technically achievable with current ML frameworks...",
  "Effort_Rating": "6",
  "Effort_Rationale": "Estimated 4-6 months development with 3-person team...",
  "Impact_Rating": "8",
  "Impact_Rationale": "Large addressable market with clear value proposition...",
  "Risk_Rating": "5",
  "Risk_Rationale": "Moderate competition risk, data privacy considerations...",
  "Overall_Rating": "7",
  "Overall_Rationale": "Strong business concept with viable execution path...",
  "Analysis_Summary": "This meal planning app addresses a real market need with innovative AI personalization. The technology is achievable and the market opportunity is substantial...",
  "Potential_Improvements": "Consider partnerships with grocery chains for seamless ingredient ordering...",
  "testing_mode": true
}
```

### 5. Read Sheet Data
Access stored analysis results (utility endpoint).

**Endpoint:** `GET /api/read_sheet?id={optional_row_id}`

**Response:**
```json
{
  "sheet_data": {
    "Sheet1": [
      {
        "ID": "job_1737999123",
        "Time": "2025-01-27 15:45:23",
        "Idea_Overview": "AI-powered meal planning app",
        "Deliverable": "Mobile app with personalized recommendations",
        "Motivation": "Help people eat healthier with minimal effort",
        "Novelty_Rating": "8",
        "Overall_Rating": "7",
        "Analysis_Summary": "Strong business concept with viable execution path..."
      }
    ]
  }
}
```

---

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Input validation failed: Missing required field 'Deliverable'",
  "status": "error",
  "success": false,
  "error_type": "validation_error",
  "testing_mode": true
}
```

### Common Error Types
- `validation_error` (400) - Missing or invalid input fields
- `invalid_budget_tier` (400) - Unknown budget tier
- `missing_job_id` (400) - Job ID not provided
- `server_error` (500) - Internal system error

---

## Testing Mode

### Enable Testing Mode
```bash
export TESTING_MODE=true
```

### Testing Features
- **No OpenAI charges** - All API calls mocked
- **Immediate results** - No waiting for actual analysis
- **Mock job IDs** - Prefixed with `mock_` or `job_`
- **No Google Sheets writes** - Data operations bypassed

---

## Usage Examples

### Complete Workflow (Python)
```python
import requests
import time

# Configuration
BASE_URL = "https://your-app.azurewebsites.net"
HEADERS = {
    'x-functions-key': 'YOUR_FUNCTION_KEY',
    'Content-Type': 'application/json'
}

# User input
user_input = {
    "Idea_Overview": "Smart home energy management system",
    "Deliverable": "IoT platform with mobile app integration",
    "Motivation": "Help homeowners reduce energy costs and carbon footprint"
}

# 1. Get instructions (optional)
instructions = requests.get(f"{BASE_URL}/api/get_instructions", headers=HEADERS)
print("Instructions:", instructions.json()['instructions'])

# 2. Get price points
pricepoints = requests.post(f"{BASE_URL}/api/get_pricepoints", 
                          json={'user_input': user_input}, 
                          headers=HEADERS)
print("Available tiers:", [tier['level'] for tier in pricepoints.json()['budget_options']])

# 3. Execute analysis
analysis = requests.post(f"{BASE_URL}/api/execute_analysis",
                        json={
                            'user_input': user_input,
                            'budget_tier': 'standard'
                        },
                        headers=HEADERS)
job_id = analysis.json()['job_id']
print(f"Analysis started: {job_id}")

# 4. Poll for results
while True:
    result = requests.get(f"{BASE_URL}/api/process_idea?id={job_id}", headers=HEADERS)
    data = result.json()
    
    if data['status'] == 'completed':
        print(f"Analysis complete! Overall rating: {data['Overall_Rating']}")
        print(f"Summary: {data['Analysis_Summary']}")
        break
    elif data['status'] == 'processing':
        print("Still processing... waiting 30 seconds")
        time.sleep(30)
    else:
        print("Error:", data)
        break
```

### ChatGPT Integration
```javascript
// Example ChatGPT Actions integration
async function analyzeBusinessIdea(userInput, budgetTier = 'standard') {
    const baseUrl = 'https://your-app.azurewebsites.net';
    const headers = {
        'x-functions-key': 'YOUR_FUNCTION_KEY',
        'Content-Type': 'application/json'
    };
    
    try {
        // Start analysis
        const analysisResponse = await fetch(`${baseUrl}/api/execute_analysis`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                user_input: userInput,
                budget_tier: budgetTier
            })
        });
        const analysisData = await analysisResponse.json();
        
        // Poll for results
        let attempts = 0;
        const maxAttempts = 60; // 30 minutes max
        
        while (attempts < maxAttempts) {
            const resultResponse = await fetch(`${baseUrl}/api/process_idea?id=${analysisData.job_id}`, {
                headers: headers
            });
            const resultData = await resultResponse.json();
            
            if (resultData.status === 'completed') {
                return {
                    success: true,
                    rating: resultData.Overall_Rating,
                    summary: resultData.Analysis_Summary,
                    details: resultData
                };
            } else if (resultData.status === 'processing') {
                await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
                attempts++;
            } else {
                throw new Error(`Analysis failed: ${JSON.stringify(resultData)}`);
            }
        }
        
        throw new Error('Analysis timed out');
        
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}
```

---

## Performance & Limits

### Response Times
- **Basic Tier**: 2-5 minutes
- **Standard Tier**: 8-15 minutes  
- **Premium Tier**: 15-25 minutes

### Rate Limits
- Maximum 1 concurrent analysis per user
- Recommended polling interval: 30 seconds
- API calls have standard Azure Functions limits

### Best Practices
- Always use testing mode for development
- Implement exponential backoff for polling
- Cache budget tier information
- Handle timeout scenarios gracefully
- Monitor usage through Azure metrics

---

## Support

### Configuration Files
- **Agent Config**: `agents/business_evaluation.yaml`
- **Environment**: `idea-guy/local.settings.json`
- **Dependencies**: `idea-guy/requirements.txt`

### Debugging
- Check `openai_costs.log` for API usage
- Enable Azure Functions logging
- Use testing mode to isolate issues
- Verify Google Sheets access permissions

### System Architecture
See `docs/SYSTEM_ARCHITECTURE.md` for detailed technical implementation.