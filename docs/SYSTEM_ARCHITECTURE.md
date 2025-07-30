# Universal AI Agent Platform - System Architecture

**Last Updated**: 2025-01-28  
**System Status**: RUTHLESS REDESIGN - Configuration-Driven Universal Platform

## Overview

The Universal AI Agent Platform enables ANY type of AI-powered analysis through pure configuration. The same codebase handles business evaluation, HR analysis, legal review, medical assessment, or any other domain through YAML configuration files.

**Core Principle**: Adding a new agent type requires ZERO code changes - only configuration files.

**Key Features**:
- **Universal Engine**: Single `UniversalAgentEngine` handles all agent types
- **Platform Configuration**: Universal prompts, models, and budget tiers in `platform.yaml`
- **Agent Personalities**: Domain expertise through agent-specific YAML files
- **Dynamic Schemas**: Input/output fields defined in Google Sheets by users
- **Clean APIs**: Existing Azure Functions work for ANY agent type

## Universal Configuration Architecture

### Three-Layer Configuration System

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM LAYER                              │
│  platform.yaml - Universal config for ALL agents              │
│  - Universal prompts (planning, analysis, synthesis)           │
│  - Universal budget tiers ($1/$3/$5)                          │  
│  - Universal models (gpt-4o-mini for all functions)           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT LAYER                                │
│  agents/{name}.yaml - Agent-specific configuration             │
│  - Agent personality and expertise                             │
│  - Agent name and description                                  │
│  - Optional model overrides                                    │
│  - Google Sheet URL for schema                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   DYNAMIC LAYER                                │
│  Google Sheets Rows 1-3 - User-defined schema                  │
│  - Input fields (what user provides)                           │
│  - Output fields (what analysis generates)                     │
│  - Field descriptions for prompts                              │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure
```
platform.yaml                   # Universal configuration for ALL agents
agents/
  business_evaluation.yaml       # Business evaluation agent
  hr_analysis.yaml              # HR analysis agent (future)
  legal_review.yaml             # Legal review agent (future)
common/
  engine.py                     # UniversalAgentEngine
  config.py                     # Configuration loading system
idea-guy/                       # Azure Functions (universal endpoints)
  get_instructions/             # Works for ANY agent type
  get_pricepoints/              # Universal budget tiers
  execute_analysis/             # Universal analysis execution
  process_idea/                 # Universal result retrieval
```

## Universal System Flow

### High-Level Flow
```
User Request → Azure Function → UniversalAgentEngine → Configuration Loading → Analysis Execution → Results
```

### Core Engine Architecture
```python
class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration"""
    
    def load_config(self, agent_id: str):
        """Load complete config: platform + agent + dynamic schema"""
        platform_config = load_yaml("platform.yaml")
        agent_config = load_yaml(f"agents/{agent_id}.yaml") 
        dynamic_schema = parse_google_sheet(agent_config.sheet_url)
        return FullUniversalConfig(platform_config, agent_config, dynamic_schema)
    
    def execute_analysis(self, agent_id: str, user_input: dict, tier: str):
        """Universal analysis execution for any agent type"""
        config = self.load_config(agent_id)
        config.validate_input(user_input)
        
        plan = self.plan_execution(config, tier, user_input)
        job_id = self.execute_plan(config, plan, user_input)
        return job_id
```

### Universal Endpoint Processing

#### A. Get Instructions Endpoint (Universal)
```python
GET /api/get_instructions?agent={agent_id}
│
├─ get_instructions/__init__.py:main()
│  ├─ agent_id = req.params.get('agent')  # Required parameter
│  ├─ engine = UniversalAgentEngine()
│  ├─ config = engine.load_config(agent_id)  # Load platform + agent + schema
│  ├─ instructions = config.generate_instructions()  # Uses dynamic schema
│  └─ Return instructions for ANY agent type
```

#### B. Get Price Points Endpoint (Universal)
```python
GET /api/get_pricepoints
│
├─ get_pricepoints/__init__.py:main()
│  ├─ engine = UniversalAgentEngine()
│  ├─ tiers = engine.platform_config.budget_tiers  # Universal tiers from platform.yaml
│  │  └─ Return [Basic($1, 1 call), Standard($3, 3 calls), Premium($5, 5 calls)]
│  └─ Same budget tiers for ALL agent types
```

#### C. Execute Analysis Endpoint (Universal)
```python
POST /api/execute_analysis
Body: {agent: "business_evaluation", input: {...}, tier: "standard"}
│
├─ execute_analysis/__init__.py:main()
│  ├─ data = json.loads(req.get_body())
│  ├─ engine = UniversalAgentEngine()
│  ├─ job_id = engine.execute_analysis(data['agent'], data['input'], data['tier'])
│  │  ├─ config = engine.load_config(data['agent'])  # Platform + agent + schema
│  │  ├─ config.validate_input(data['input'])        # Dynamic validation
│  │  ├─ plan = engine.plan_execution(config, data['tier'], data['input'])
│  │  │  └─ Uses universal planning template from platform.yaml
│  │  └─ job_id = engine.execute_plan(config, plan, data['input'])
│  │     └─ Universal multi-call workflow engine
│  └─ Return {job_id: job_id}
```

#### D. Process Analysis Results (Universal)
```python
GET /api/process_idea?id={job_id}
│
├─ process_idea/__init__.py:main()
│  ├─ job_id = req.params.get('id')
│  ├─ response = openai_client.responses.retrieve(job_id)
│  ├─ If analysis complete:
│  │  ├─ Extract agent_id from job metadata
│  │  ├─ config = UniversalAgentEngine().load_config(agent_id)
│  │  ├─ results = parse_results(response, config.dynamic_schema)
│  │  ├─ Write results to Google Sheets using dynamic schema
│  │  └─ Return structured results
│  └─ Else return {status: "processing"}
```

## Key System Components

### Universal Configuration Loading
```python
class FullUniversalConfig:
    """Combines platform + agent + dynamic configuration"""
    platform_config: PlatformConfig      # From platform.yaml
    agent_config: AgentConfig            # From agents/{name}.yaml  
    dynamic_schema: DynamicSchema        # From Google Sheets rows 1-3

    def validate_input(self, user_input: dict) -> bool:
        """Validate input against dynamic schema"""
        
    def generate_instructions(self) -> str:
        """Generate user instructions from dynamic schema"""
        
    def get_model(self, model_type: str) -> str:
        """Get model with agent overrides: agent_config.models or platform_config.models"""
```

### Universal Workflow Engine
```python
class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration"""
    
    def load_config(self, agent_id: str) -> FullUniversalConfig:
        """Load complete configuration for any agent"""
        
    def plan_execution(self, config: FullUniversalConfig, tier: str, user_input: dict):
        """Plan multi-call execution using universal templates"""
        
    def execute_plan(self, config: FullUniversalConfig, plan: ExecutionPlan, user_input: dict):
        """Execute analysis plan with universal workflow"""
```

### Configuration Files

**Platform Configuration** (`platform.yaml`):
```yaml
models:
  planning: "gpt-4o-mini"
  analysis: "gpt-4o-mini"
  synthesis: "gpt-4o-mini"

budget_tiers:
  - {name: basic, price: 1.00, calls: 1}
  - {name: standard, price: 3.00, calls: 3}
  - {name: premium, price: 5.00, calls: 5}

prompts:
  planning_template: "Design optimal {calls}-call strategy..."
  analysis_template: "{agent_personality}\nANALYSIS: {user_input}..."
  synthesis_template: "Synthesize findings into {analysis_type}..."
```

**Agent Configuration** (`agents/business_evaluation.yaml`):
```yaml
agent_id: "business_evaluation"
name: "Business Idea Evaluator"
sheet_url: "https://docs.google.com/spreadsheets/d/..."

personality: |
  You are a senior partner at a top-tier VC firm...

# Optional model overrides
models:
  analysis: "gpt-4o"  # This agent uses better model
```

## Universal Data Flow

### 1. Configuration Loading (Universal)
```
platform.yaml → PlatformConfig (models, budget_tiers, prompts)
     +
agents/{agent_id}.yaml → AgentConfig (personality, optional overrides)
     +
Google Sheets rows 1-3 → DynamicSchema (input/output fields)
     ↓
FullUniversalConfig (Complete Configuration)
```

### 2. Request Processing (Any Agent Type)
```
User Request → Azure Function → UniversalAgentEngine → Config Loading → Validation → Analysis
```

### 3. Universal Analysis Execution
```
UniversalAgentEngine.plan_execution() → Uses platform.yaml templates
     ↓
UniversalAgentEngine.execute_plan() → Multi-call workflow → Results
```

### 4. Universal Data Storage
```
User Input → Google Sheets (dynamic schema)
     ↓
Analysis Results → Google Sheets (dynamic output fields)
     ↓  
Cost Logging → openai_costs.log
```

## Key File Locations

### Universal Configuration
- `platform.yaml` - **NEW**: Universal configuration for ALL agents
- `agents/business_evaluation.yaml` - **UPDATED**: Agent-specific configuration only
- `agents/{agent_name}.yaml` - **FUTURE**: Additional agent types

### Azure Functions (Universal Endpoints)
- `idea-guy/get_instructions/__init__.py` - **UPDATED**: Universal instructions for any agent
- `idea-guy/get_pricepoints/__init__.py` - **UPDATED**: Universal budget tiers
- `idea-guy/execute_analysis/__init__.py` - **UPDATED**: Universal analysis execution  
- `idea-guy/process_idea/__init__.py` - **UPDATED**: Universal result retrieval
- `idea-guy/read_sheet/__init__.py` - **UNCHANGED**: Utility endpoint

### Core Universal Engine
- `common/engine.py` - **NEW**: UniversalAgentEngine (replaces agent_service.py)
- `common/config.py` - **NEW**: Universal configuration loading
- `common/workflow.py` - **NEW**: Universal multi-call workflow

### Supporting Services (Kept)
- `common/cost_tracker.py` - OpenAI cost logging
- `common/utils.py` - OpenAI & Google Sheets client initialization  
- `common/http_utils.py` - HTTP request/response utilities

### Deleted Files
- ❌ `common/budget_config.py` - **DELETED**: Moved to platform.yaml
- ❌ `common/agent_service.py` - **DELETED**: Replaced by UniversalAgentEngine

## Universal Testing Strategy

**NEW**: 5 Focused Tests (replacing 34 overlapping tests)

```python
# 1. Configuration Loading Test - Can we load all config layers?
# 2. Input Validation Test - Does dynamic schema validation work?  
# 3. Workflow Engine Test - Can we execute analysis for any agent?
# 4. API Integration Test - Do all endpoints work universally?
# 5. Multi-Agent Test - Can we run different agent types?
```

Testing mode automatically detected:
- Mock OpenAI responses
- Skip Google Sheets operations
- No costs incurred
- Fast test execution

## Universal Benefits

### For Adding New Agent Types
1. Create `agents/{new_agent}.yaml` with personality
2. Create Google Sheet with schema in rows 1-3  
3. **System automatically works** - no code changes required

### For Tuning System Behavior

#### 🔧 **Tune ALL Agents** (Edit `platform.yaml`)
```yaml
prompts:
  planning_template: |
    You are an expert planner...
    # This affects EVERY agent type
```

#### 🎯 **Tune ONE Agent** (Edit `agents/{name}.yaml`)
```yaml
personality: |
  You are a senior partner at a VC firm...
  # Only affects this specific agent

models:
  analysis: "gpt-4o"  # This agent uses better model
```

### Architecture Benefits
- ✅ **Zero Code for New Agents**: Pure configuration approach
- ✅ **Universal Maintenance**: Change platform behavior in one place
- ✅ **Agent Flexibility**: Each agent has its own expertise and overrides
- ✅ **Dynamic Schema**: Input/output fields defined by users, not developers
- ✅ **Clean APIs**: Same endpoints work for ANY agent type
- ✅ **Focused Testing**: 5 clear tests instead of 34 overlapping ones

This ruthless redesign achieves true universality while dramatically simplifying the codebase.