# Joey-Bot System Architecture

**Last Updated**: 2025-01-28  
**System Status**: Universal AI Agent Platform with Universal Prompt Configuration System

## Overview

Joey-Bot is a Universal AI Agent Platform that provides AI-powered analysis through Azure Functions with Google Sheets storage and OpenAI multi-call architecture. The system features:

- **Universal Prompt Configuration**: Shared prompts for all agents with agent-specific customization
- **Dynamic Schema**: Input/output fields defined in Google Sheets, not hardcoded
- **Multi-Agent Support**: Single codebase supports any analysis type (business, HR, product, etc.)
- **Intelligent Architecture Planning**: AI-designed multi-call execution strategies

## Universal Configuration Architecture

### File Structure
```
common/prompts.yaml              # 🔧 SHARED - Easy to tune for ALL agents
common/prompt_manager.py         # Universal prompt management system
agents/business_evaluation.yaml  # Agent-specific starter_prompt + models
agents/[agent_name].yaml         # Future agents use same structure
```

### Configuration Hierarchy
1. **Platform-Level** (`common/prompts.yaml`): Architecture planning, universal templates
2. **Agent-Level** (`agents/*.yaml`): Starter prompts, models, expertise
3. **Dynamic-Level** (Google Sheets): Input/output schema defined by users

## System Flow (Semi-Pseudocode)

### 1. User Interaction Flow

```
User Request → Azure Function → AnalysisService → MultiCallArchitecture → OpenAI → Google Sheets
```

### 2. Detailed Request Processing

#### A. Get Instructions Endpoint
```python
GET /api/get_instructions
│
├─ get_instructions/__init__.py:main()
│  ├─ AnalysisService.get_user_instructions()
│  │  ├─ Load agent config: AgentDefinition.from_yaml('agents/business_evaluation.yaml')
│  │  ├─ Parse dynamic schema: SheetSchemaReader.parse_sheet_schema(sheet_url)
│  │  ├─ Create FullAgentConfig(definition, schema)
│  │  └─ Generate instructions: full_config.generate_instructions()
│  └─ Return formatted instructions to user
```

#### B. Get Price Points Endpoint
```python
GET /api/get_pricepoints
│
├─ get_pricepoints/__init__.py:main()
│  ├─ AnalysisService.get_budget_options()
│  │  ├─ BudgetConfigManager.get_all_tiers()
│  │  │  └─ Return [Basic($1, 1 call), Standard($3, 3 calls), Premium($5, 5 calls)]
│  │  └─ Format budget options with deliverables
│  └─ Return budget tiers to user
```

#### C. Execute Analysis Endpoint
```python
POST /api/execute_analysis
Body: {user_input: {...}, budget_tier: "standard"}
│
├─ execute_analysis/__init__.py:main()
│  ├─ validate_json_request(req) → Extract user_input & budget_tier
│  ├─ AnalysisService.create_analysis_job(user_input, budget_tier)
│  │  ├─ Load agent config: AgentDefinition + SheetSchemaReader → FullAgentConfig
│  │  ├─ Validate input: full_config.schema.validate_input(user_input)
│  │  ├─ Get tier config: BudgetConfigManager.get_tier_config(budget_tier)
│  │  ├─ Generate job_id: f"job_{int(time.time())}"
│  │  ├─ Write to Google Sheets:
│  │  │  ├─ sheets_client.open_by_key(sheet_id)
│  │  │  ├─ worksheet.append_row([job_id, timestamp, ...user_input_values])
│  │  │  └─ Find cell with job_id for later updates
│  │  └─ Execute analysis: create_multi_call_analysis()
│  │     ├─ MultiCallArchitecture(openai_client)
│  │     ├─ plan = architecture.plan_architecture(prompt, calls, user_input)
│  │     │  ├─ Generate planning prompt with user input
│  │     │  ├─ Call OpenAI: "Design optimal {N}-call execution strategy"
│  │     │  └─ Parse JSON response → ArchitecturePlan
│  │     └─ Execute plan: architecture.execute_plan(plan, tier_config, user_input)
│  │        ├─ For each batch in execution_order:
│  │        │  ├─ Execute calls concurrently (max 4 parallel)
│  │        │  ├─ Log costs: CostTracker.log_openai_cost()
│  │        │  └─ Store results for dependencies
│  │        └─ Return final_job_id
│  └─ Return {job_id: final_job_id} to user
```

#### D. Process Analysis Results
```python
GET /api/process_idea?id={job_id}
│
├─ process_idea/__init__.py:main()
│  ├─ Extract job_id from query params
│  ├─ get_openai_client().responses.retrieve(job_id)
│  ├─ If analysis complete:
│  │  ├─ Load agent config: FullAgentConfig for output parsing
│  │  ├─ Parse result: extract_json_from_text(response)
│  │  ├─ Update Google Sheets:
│  │  │  ├─ Find row with job_id
│  │  │  ├─ Write analysis results to output columns
│  │  │  └─ Calculate column positions from schema
│  │  └─ Return analysis results
│  └─ Else return {status: "processing"}
```

### 3. Core System Components

#### Configuration System (`common/config/`)
```python
class FullAgentConfig:
    definition: AgentDefinition     # Static YAML config  
    schema: SheetSchema            # Dynamic from Google Sheets rows 1-3

    def generate_analysis_prompt(user_input):
        return f"{starter_prompt}\n\nInput: {user_input}\n\nOutput JSON: {output_schema}"
```

#### Analysis Service (`common/agent_service.py`)
```python
class AnalysisService:
    def create_analysis_job(user_input, budget_tier):
        config = load_agent_config()
        validate_input(config, user_input)
        job_id = write_to_sheets(user_input)
        analysis_job_id = execute_multi_call_analysis(config, user_input, tier)
        return analysis_job_id
```

#### Multi-Call Architecture (`common/multi_call_architecture.py`)
```python
class MultiCallArchitecture:
    def plan_architecture(prompt, available_calls, user_input, output_fields):
        # Uses universal prompt template from common/prompts.yaml
        planning_prompt = prompt_manager.format_architecture_planning_prompt(
            available_calls, model, prompt, user_input, output_fields
        )
        plan_json = openai_client.call(planning_prompt)
        return ArchitecturePlan(calls, execution_order, dependencies)
    
    def execute_plan(plan, tier_config, user_input):
        for batch in plan.execution_order:
            results = execute_concurrent_batch(batch, previous_results)
            log_costs_for_batch(results, tier_config)
        return final_summarizer_job_id
```

#### Budget Management (`common/budget_config.py`)
```python
class BudgetConfigManager:
    tiers = [
        TierConfig("basic", $1.00, 1, "gpt-4o-mini"),
        TierConfig("standard", $3.00, 3, "gpt-4o-mini"), 
        TierConfig("premium", $5.00, 5, "gpt-4o-mini")
    ]
```

#### Cost Tracking (`common/cost_tracker.py`)
```python
def log_openai_cost(endpoint, model, tier, job_id, usage, cost, user_input):
    log.info(f"{timestamp} | {endpoint} | {model} | {tier} | {job_id} | ${cost}")
    append_to_file("openai_costs.log", log_entry)
```

## Data Flow

### 1. Configuration Loading
```
agents/business_evaluation.yaml → AgentDefinition
     +
Google Sheets rows 1-3 → SheetSchema  
     ↓
FullAgentConfig (Combined Configuration)
```

### 2. Request Processing
```
User HTTP Request → Azure Function → AnalysisService → Configuration → Validation → Processing
```

### 3. Analysis Execution
```
MultiCallArchitecture.plan_architecture() → ArchitecturePlan
     ↓
MultiCallArchitecture.execute_plan() → Concurrent API calls → Results aggregation
```

### 4. Data Storage
```
User Input → Google Sheets row (job_id, timestamp, input_fields...)
     ↓
Analysis Results → Google Sheets row (...output_fields)
     ↓  
Cost Logging → openai_costs.log
```

## Key File Locations

### Azure Functions (Entry Points)
- `idea-guy/execute_analysis/__init__.py` - Start analysis job
- `idea-guy/process_idea/__init__.py` - Get analysis results
- `idea-guy/get_instructions/__init__.py` - Get user instructions
- `idea-guy/get_pricepoints/__init__.py` - Get budget options
- `idea-guy/read_sheet/__init__.py` - Read Google Sheets data

### Core Business Logic
- `common/agent_service.py` - Main orchestration service
- `common/multi_call_architecture.py` - Multi-call analysis execution
- `common/config/agent_definition.py` - YAML configuration loading
- `common/config/sheet_schema_reader.py` - Dynamic schema parsing
- `common/config/models.py` - Core data models

### Supporting Services
- `common/budget_config.py` - Budget tier management
- `common/cost_tracker.py` - OpenAI cost logging
- `common/utils.py` - OpenAI & Google Sheets client initialization
- `common/http_utils.py` - HTTP request/response utilities

### Configuration
- `agents/business_evaluation.yaml` - Business evaluator agent definition
- Google Sheets rows 1-3 - Dynamic schema definition
- `idea-guy/local.settings.json` - Environment variables

## Testing System

The system includes comprehensive testing protection:

```python
def is_testing_mode():
    return os.getenv('TESTING_MODE') == 'true' or 'pytest' in sys.modules

# When testing:
- OpenAI calls return mock responses
- Google Sheets operations are bypassed  
- No actual costs incurred
- All functionality testable
```

## Error Handling

### Validation Errors
```python
class ValidationError(Exception):
    # Missing required fields
    # Invalid budget tier
    # Malformed input
```

### API Errors
```python
# OpenAI API failures → Fallback strategies
# Google Sheets access issues → Error responses
# JSON parsing failures → Structured error messages
```

## Security & Cost Controls

### API Key Management
- OpenAI API key in environment variables
- Google Sheets service account key file
- Azure Functions authentication

### Cost Protection
- Budget tier limits prevent runaway costs
- Testing mode prevents accidental charges
- Comprehensive cost logging for monitoring
- Per-call cost estimation and tracking

## Extension Points

### Adding New Agent Types
1. Create `agents/{new_agent}.yaml` with configuration
2. Set up Google Sheet with schema in rows 1-3
3. System automatically supports new agent type
4. No code changes required

### Modifying Analysis Logic
- Update prompts in agent YAML configuration
- Modify budget tiers in `BudgetConfigManager`
- Extend multi-call planning strategies
- Add new analysis workflow patterns

This architecture provides a clean separation between configuration, business logic, and infrastructure, making the system highly maintainable and extensible.

## Universal Prompt Configuration System (**NEW**)

### How to Tune the System

#### 🔧 **Tune ALL Agents** (Edit `common/prompts.yaml`)
```yaml
prompts:
  architecture_planning: |
    You are an expert AI architecture planner...
    # Changing this affects EVERY agent type
```

#### 🎯 **Tune ONE Agent** (Edit `agents/business_evaluation.yaml`)  
```yaml
starter_prompt: |
  You are a senior partner at a VC firm...
  # Only affects business evaluation agent

models:
  analysis: "gpt-4o-mini"      # Agent can use different models
  synthesis: "o1-preview"      # Mix and match as needed
```

#### 🔄 **How It Works**
1. **Planning**: Uses common template + agent's output fields dynamically
2. **Analysis**: Combines common template + agent's starter_prompt + dynamic user input
3. **Synthesis**: Uses common template + agent's dynamic output requirements

### Key Benefits
- ✅ **Truly Universal**: No hardcoded business evaluation fields
- ✅ **Easy Tuning**: One file (`common/prompts.yaml`) affects all agents  
- ✅ **Agent Flexibility**: Each agent has its own expertise and models
- ✅ **Dynamic Schema**: Input/output fields come from Google Sheets
- ✅ **Maintainability**: Clear separation between platform and agent logic