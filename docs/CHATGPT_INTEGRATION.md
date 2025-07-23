# ChatGPT Bot Integration Guide

## Overview

The Joey Bot system provides a structured workflow for ChatGPT bots to collect business idea information, present budget options, and deliver comprehensive analysis results.

## Complete Workflow

### 1. Get Instructions
**Endpoint:** `GET /api/get_instructions`

ChatGPT calls this first to understand the workflow and required fields.

```json
{
  "instructions": "You are an expert business analyst...",
  "testing_mode": true,
  "note": "Running in testing mode - no API charges will occur during analysis"
}
```

### 2. Get Budget Options
**Endpoint:** `POST /api/get_pricepoints`

After collecting user's business idea details, get available analysis tiers.

**Request:**
```json
{
  "user_input": {
    "Idea_Overview": "A mobile app for local event discovery",
    "Deliverable": "iOS and Android app with event listings",
    "Motivation": "Help people find and attend local events easily"
  }
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
      "deliverables": ["Basic ratings", "Short rationales"],
      "time_estimate": "5-10 minutes"
    },
    {
      "level": "standard", 
      "name": "Detailed Analysis",
      "max_cost": 1.00,
      "estimated_cost": 0.40,
      "model": "o1-mini",
      "description": "Comprehensive evaluation with market research",
      "deliverables": ["Detailed ratings", "Competitor analysis", "Market size analysis"],
      "time_estimate": "15-20 minutes"
    },
    {
      "level": "premium",
      "name": "Deep Research Analysis", 
      "max_cost": 2.50,
      "estimated_cost": 2.00,
      "model": "o4-mini-deep-research",
      "description": "Exhaustive analysis with extensive market research",
      "deliverables": ["Comprehensive ratings", "Deep competitor research", "Patent analysis"],
      "time_estimate": "20-30 minutes"
    }
  ],
  "message": "Select a budget tier and call /api/execute_analysis to start the analysis",
  "next_endpoint": "/api/execute_analysis"
}
```

### 3. Execute Analysis
**Endpoint:** `POST /api/execute_analysis`

Start the analysis with user's selected budget tier.

**Request:**
```json
{
  "user_input": {
    "Idea_Overview": "A mobile app for local event discovery",
    "Deliverable": "iOS and Android app with event listings", 
    "Motivation": "Help people find and attend local events easily"
  },
  "budget_tier": "standard"
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

### 4. Check Analysis Status
**Endpoint:** `GET /api/process_idea?id={job_id}`

Poll this endpoint until analysis is complete.

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
  "testing_mode": true,
  "mock_results": {
    "Novelty_Rating": "7",
    "Novelty_Rationale": "Mock analysis - this would contain actual evaluation in production",
    "Feasibility_Rating": "8",
    "Feasibility_Rationale": "Technology is mature with proven frameworks available",
    "Effort_Rating": "6", 
    "Effort_Rationale": "Approximately 3-6 months with a team of 3-4 developers",
    "Impact_Rating": "8",
    "Impact_Rationale": "Event discovery market has strong growth potential",
    "Risk_Rating": "5",
    "Risk_Rationale": "Moderate risk due to competitive landscape",
    "Overall_Rating": "7",
    "Overall_Rationale": "Strong concept with good market potential and feasible implementation",
    "Analysis_Summary": "This is a promising idea with clear market demand...",
    "Potential_Improvements": "Consider adding AI-powered personalization features..."
  },
  "timestamp": "2024-01-15T10:35:00.123456"
}
```

## Error Handling

All endpoints return structured error responses with clear messages for users:

```json
{
  "error": "Missing required field: Idea_Overview. Please provide a description of your business idea.",
  "status": "error",
  "success": false,
  "error_type": "missing_field",
  "suggestion": "Please check your request format and required fields",
  "details": {
    "required_fields": ["Idea_Overview", "Deliverable", "Motivation"]
  }
}
```

### Common Error Types

| Error Type | Description | ChatGPT Action |
|------------|-------------|----------------|
| `missing_field` | Required field missing | Ask user for missing information |
| `validation_error` | Input validation failed | Guide user to correct format |
| `invalid_budget_tier` | Unknown budget tier | Show available tier options |
| `server_error` | Internal system error | Suggest trying again later |

## Testing Mode

**Enable testing mode for development:**
```bash
export TESTING_MODE=true
```

**Testing mode features:**
- All responses include `"testing_mode": true`
- Mock job IDs start with `"mock_"`
- No API charges incurred
- Fake analysis results returned immediately
- No spreadsheet modifications

## Best Practices for ChatGPT Bots

### 1. Field Collection Strategy
```
User: "I have an app idea"
Bot: "Great! Let me help you analyze your app idea. First, can you provide an overview of your idea?"
User: "It's a fitness class booking app"
Bot: "Perfect! Now, what specific deliverable would this be? For example, a mobile app, web service, etc."
```

### 2. Budget Presentation
```
Bot: "I found 3 analysis options for your idea:

🟢 **Quick Analysis ($0.20)** - Basic ratings and rationales (5-10 min)
🟡 **Detailed Analysis ($1.00)** - Market research and competitor analysis (15-20 min) 
🔴 **Deep Research ($2.50)** - Comprehensive analysis with patent research (20-30 min)

Which tier would you prefer?"
```

### 3. Status Updates
```
Bot: "Your analysis is in progress... This typically takes 15-20 minutes for the detailed tier. I'll check back in a few minutes."

[After polling]

Bot: "Great news! Your analysis is complete. Here's what I found..."
```

### 4. Error Recovery
```json
// If error occurs:
{
  "error": "Missing required field: Deliverable",
  "suggestion": "Please check your request format and required fields"
}
```

```
Bot: "I need one more piece of information. What specific product or service will you deliver? For example, 'A mobile app with booking features' or 'A web platform for event discovery.'"
```

## Integration Checklist

- [ ] Handle all 4 workflow endpoints
- [ ] Parse structured JSON responses
- [ ] Display budget tiers clearly to users
- [ ] Implement polling for job completion
- [ ] Handle all error types gracefully
- [ ] Test with `TESTING_MODE=true` first
- [ ] Present analysis results in user-friendly format
- [ ] Guide users through field collection process

## Support

For issues:
1. Check error messages for specific guidance
2. Verify all required fields are provided
3. Ensure environment variables are set correctly
4. Use testing mode for development
5. Check logs for detailed error context