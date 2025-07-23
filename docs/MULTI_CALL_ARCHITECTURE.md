# Multi-Call Architecture System

## Overview

The Multi-Call Architecture System intelligently plans and executes business analysis workflows using multiple coordinated OpenAI API calls. Each budget tier receives a custom execution strategy optimized for determining exact expected financial value within resource constraints.

## Architecture Tiers

### Basic Tier - $1.00 (1 Call)
**Strategy:** Single comprehensive analysis with embedded financial modeling
- **Execution:** 1 optimized call with the full VC evaluation prompt
- **Focus:** Complete business analysis with integrated financial projections
- **Output:** All standard metrics plus Expected Value Analysis

### Standard Tier - $3.00 (3 Calls) 
**Strategy:** Specialized analysis with dedicated financial modeling
- **Batch 1:** Market research + Financial modeling (2 concurrent calls)
- **Batch 2:** Synthesis with expected value calculation (1 call)
- **Focus:** Deep market analysis combined with rigorous financial projections
- **Output:** Enhanced market insights with detailed DCF analysis

### Premium Tier - $5.00 (5 Calls)
**Strategy:** Maximum specialization across all business dimensions
- **Batch 1:** Market + Competitive + Technical + Financial analysis (4 concurrent calls)
- **Batch 2:** Comprehensive synthesis with advanced valuation (1 call)  
- **Focus:** Exhaustive analysis with professional-grade financial modeling
- **Output:** Investment-grade analysis with multiple valuation approaches

## Usage Example

```python
from common.multi_call_architecture import create_multi_call_analysis
from common.budget_config import BudgetConfigManager

# Initialize components
manager = BudgetConfigManager()
config = manager.get_tier_config('standard')  # 3-call tier

user_input = {
    'Idea_Overview': 'AI-powered robo-advisor for retirement planning',
    'Deliverable': 'Mobile app with portfolio management and rebalancing',
    'Motivation': 'Democratize professional investment strategies'
}

# Execute multi-call analysis
job_id = create_multi_call_analysis(user_input, config, openai_client)
print(f"Analysis started with job ID: {job_id}")

# Results will include Expected Value Analysis with:
# - Revenue projections (Years 1-5)
# - Probability-weighted scenarios  
# - Comparable company valuations
# - Expected investor returns
# - DCF analysis with assumptions
```

## Key Parameters

### Architecture Planning
- **`available_calls`**: Number of API calls (1, 3, or 5)
- **`max_concurrent`**: Maximum simultaneous calls (4)
- **`financial_focus`**: Mandatory emphasis on expected value calculation
- **`dependency_constraints`**: Call execution order requirements

### Execution Configuration
- **`model`**: `o4-mini-deep-research` for all tiers
- **`tools`**: Web search and reasoning capabilities
- **`background`**: Async execution for polling-based results
- **`cost_tracking`**: Detailed logging with execution plan context

### Financial Requirements
All architecture plans must include:
- **Revenue Projections**: Specific dollar amounts for Years 1-5
- **Market Analysis**: TAM/SAM/SOM with capture potential estimates
- **Valuation Modeling**: DCF analysis or comparable company multiples  
- **Risk Assessment**: Probability-weighted scenarios with percentages
- **Investment Returns**: Expected IRR and multiple calculations

## Error Cases

### Planning Failures
```python
# Architecture planning timeout or invalid response
ValueError: "Architecture planning failed: invalid JSON response"
# → Falls back to simple sequential plan
```

### Execution Failures  
```python
# API call failure in batch execution
ValueError: "Plan execution failed: API timeout in batch 1"
# → Individual call marked as failed, execution continues
```

### Dependency Errors
```python
# Missing dependency results for subsequent calls
ValueError: "No final summarizer call found in execution results"
# → System identifies missing final synthesis call
```

### Cost Tracking Issues
```python
# Cost logging failure (non-blocking)
Warning: "Failed to log API cost: execution_plan serialization error"
# → Analysis continues, only logging is affected
```

## Cost Tracking Integration

Each API call is logged with detailed execution context:

```json
{
  "timestamp": "2025-07-23T05:13:09.255026Z",
  "endpoint": "multi_call_batch_1", 
  "model": "o4-mini-deep-research",
  "budget_tier": "standard",
  "job_id": "analysis_job_456",
  "tokens": {"input": 2500, "output": 4000, "total": 6500},
  "cost_usd": 1.0,
  "execution_plan": {
    "total_calls": 3,
    "call_id": "financial_modeling",
    "call_purpose": "Revenue projections and valuation analysis", 
    "is_summarizer": false,
    "batch_index": 1,
    "dependencies": []
  },
  "additional_context": {
    "call_count": 3,
    "is_multi_call": true
  }
}
```

## Testing Mode

In testing mode (`TESTING_MODE=true`):
- **Mock Execution**: Returns fake job IDs without API calls
- **Cost Logging**: Logs $0.00 costs with `testing_mode: true` flag  
- **Full Planning**: Architecture planning still executes for testing
- **Batch Simulation**: Simulates concurrent execution timing

```python
# Testing mode example
os.environ['TESTING_MODE'] = 'true'
job_id = create_multi_call_analysis(user_input, config, mock_client)
# Returns: "mock_financial_modeling_1234567890"
```

## Architecture Planning Details

### Planning Prompt Features
- **Financial Bias**: "STRONG EMPHASIS on determining exact expected financial value"
- **Resource Optimization**: Efficient use of all available API calls
- **Constraint Awareness**: Max 4 concurrent calls, dependency management
- **Output Requirements**: Final summarizer must include Expected Value Analysis

### Example Architecture Plan (Standard Tier)
```json
{
  "strategy_explanation": "Divide analysis into market research, financial modeling, and synthesis for maximum financial insight",
  "total_calls": 3,
  "max_concurrent": 4,
  "calls": [
    {
      "call_id": "market_research",
      "purpose": "TAM/SAM/SOM analysis and user adoption patterns",
      "prompt": "Focus exclusively on market analysis...",
      "dependencies": [],
      "is_summarizer": false
    },
    {
      "call_id": "financial_modeling", 
      "purpose": "Revenue projections and DCF valuation",
      "prompt": "Develop comprehensive financial model...",
      "dependencies": [],
      "is_summarizer": false
    },
    {
      "call_id": "synthesis_evaluation",
      "purpose": "Complete VC evaluation with Expected Value Analysis",
      "prompt": "Synthesize market and financial findings...",
      "dependencies": ["market_research", "financial_modeling"],
      "is_summarizer": true
    }
  ],
  "execution_order": [
    ["market_research", "financial_modeling"],
    ["synthesis_evaluation"] 
  ]
}
```

## Performance Characteristics

### Execution Times
- **Basic (1 call)**: 5-10 minutes
- **Standard (3 calls)**: 15-20 minutes  
- **Premium (5 calls)**: 20-30 minutes

### Concurrency Limits
- **Maximum concurrent calls**: 4 (OpenAI API constraint)
- **Batch processing**: Dependent calls wait for prerequisites
- **Thread pool execution**: Concurrent API calls within batches

### Cost Efficiency
- **Basic**: $1.00 for comprehensive analysis with financial focus
- **Standard**: $3.00 for specialized analysis with dedicated financial modeling  
- **Premium**: $5.00 for investment-grade analysis with multiple approaches

## Future Work

### Enhanced Dependency Management
- **Result Injection**: Pass actual analysis results between dependent calls
- **Dynamic Prompting**: Modify subsequent prompts based on previous findings
- **Failure Recovery**: Retry strategies for failed dependency calls

### Advanced Planning
- **Adaptive Architectures**: Adjust call plans based on idea complexity
- **Cost Optimization**: Dynamic resource allocation based on requirements
- **Parallel Tracks**: Independent analysis streams that merge at synthesis

### Real-time Monitoring
- **Progress Tracking**: Real-time updates on batch execution status
- **Cost Alerts**: Live cost tracking with budget threshold notifications
- **Performance Metrics**: Analysis quality correlation with execution strategy

## Integration Points

### Agent Service Integration
```python
# common/agent_service.py
def create_analysis_job(self, user_input, budget_tier):
    # Multi-call architecture replaces single API call
    job_id = create_multi_call_analysis(user_input, tier_config, self.openai_client)
    return {"job_id": job_id, "status": "processing"}
```

### Cost Tracking Integration  
```python
# Each call in the execution plan is logged
log_openai_cost(
    endpoint=f"multi_call_batch_{batch_index}",
    execution_plan=call_plan_summary,
    call_count=total_calls,
    is_multi_call=True
)
```

### Testing Integration
```python
# test_multi_call_architecture.py validates:
# - Architecture planning functionality
# - Cost tracking with execution plans  
# - Integration with existing workflow
# - Budget tier configurations
```