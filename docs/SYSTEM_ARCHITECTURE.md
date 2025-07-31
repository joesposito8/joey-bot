# Universal AI Agent Platform - System Architecture

**Last Updated**: 2025-01-30  
**System Status**: RUTHLESS REDESIGN - Documentation Complete, Implementation Ready  
**Recent Changes**: 
- Consolidated platform configuration into platform.yaml (removed prompts.yaml)
- Updated BudgetTierConfig and budget handling to use platform settings
- Fixed test imports and configuration loading
- Added dictionary support to configuration models
<!-- Updated to reflect platform configuration consolidation in commit d1ddb99 -->

## Overview

The Universal AI Agent Platform enables ANY type of AI-powered analysis through pure configuration. The same codebase handles business evaluation, HR analysis, legal review, medical assessment, or any other domain through YAML configuration files.

**Core Principle**: Adding a new agent type requires ZERO code changes - only configuration files.

**Key Features**:
- **Analysis Service**: Single `AnalysisService` handles all agent types through configuration
- **Platform Configuration**: Universal prompts, models, and budget tiers in `common/platform.yaml`
- **Agent Personalities**: Domain expertise through agent-specific YAML files in `agents/`
- **Dynamic Schemas**: Input/output fields defined in Google Sheets by users
- **Clean APIs**: Existing Azure Functions work for ANY agent type (5 endpoints in `idea-guy/`)

## Universal Configuration Architecture

### Four-Layer Configuration System

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTH LAYER                                 │
│  local.settings.json - API Keys & Service Accounts            │
│  - OpenAI API key                                             │
│  - Google Sheets service account                              │
│  - Azure Functions settings                                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
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

### Configuration Files

#### Current System
- 📄 `agents/business_evaluation.yaml` - Agent configuration
- 📄 `idea-guy/local.settings.json` - Environment variables and API keys
- 📄 `.keys/joey-bot-465403-d2eb14543555.json` - Google Sheets service account
- 📄 `platform.yaml` - Universal configuration for ALL agents

### Current File Structure with Exact Locations
<!-- Updated to reflect actual file structure after recent changes -->
```
📁 joey-bot/
├── 📄 PROJECT_VISION.md                    # NEW: Project mission and roadmap  
├── 📄 IMPLEMENTATION_PLAN.md               # NEW: Step-by-step transformation plan
├── 📄 common/platform.yaml                 # CURRENT: Universal configuration
├── 📁 agents/
│   └── 📄 business_evaluation.yaml         # CURRENT: Business agent config (cleaned)
├── 📁 common/                              # Core business logic
│   ├── 📄 agent_service.py                 # CURRENT: Main orchestration service
│   ├── 📄 multi_call_architecture.py       # Workflow execution engine
│   ├── 📄 budget_config.py                 # UPDATED: Uses platform.yaml for budgets
│   ├── 📁 config/                          # Configuration loading system
│   │   ├── 📄 models.py                    # Data models and schemas
│   │   ├── 📄 agent_definition.py          # Agent configuration parsing
│   │   └── 📄 sheet_schema_reader.py       # Google Sheets dynamic schema
│   ├── 📄 cost_tracker.py                  # OpenAI cost logging
│   ├── 📄 utils.py                         # Client initialization
│   └── 📄 http_utils.py                    # HTTP utilities
├── 📁 idea-guy/                            # Azure Functions HTTP endpoints
│   ├── 📁 get_instructions/
│   │   └── 📄 __init__.py                   # Universal instructions endpoint
│   ├── 📁 get_pricepoints/
│   │   └── 📄 __init__.py                   # Universal budget tiers endpoint
│   ├── 📁 execute_analysis/
│   │   └── 📄 __init__.py                   # Universal analysis execution
│   ├── 📁 process_idea/
│   │   └── 📄 __init__.py                   # Universal results retrieval
│   └── 📁 read_sheet/
│       └── 📄 __init__.py                   # Utility endpoint (unchanged)
└── 📁 tests/                               # NEW: 5 focused universal tests
    ├── 📄 test_dynamic_configuration.py    # NEW: Configuration loading tests
    ├── 📄 test_platform_config.py          # NEW: Platform configuration tests
    ├── 📄 test_universal_endpoints.py      # NEW: API integration tests
    └── 📄 test_workflow_engine.py          # NEW: Multi-call workflow tests
```

### Current System Flow
```
User Request → Azure Function → AnalysisService → Configuration Loading → MultiCallArchitecture → OpenAI → Results
             (idea-guy/*.py)   (agent_service.py) (config/models.py)    (multi_call_architecture.py)
```

### Planned Azure Functions Updates
```
GET /api/get_instructions?agent={agent_id}  # Add agent parameter
GET /api/get_pricepoints?agent={agent_id}   # Support multiple agents
POST /api/execute_analysis                  # Add agent_id to request body
GET /api/process_idea?id={job_id}          # Extract agent from job metadata
```

### Configuration System (common/config/models.py)
```python
class FullAgentConfig:
    """Combines agent YAML + Google Sheets schema + universal prompts."""
    
    def get_budget_tiers(self):  # Line 170
        """Load universal budget tiers from platform.yaml"""
        return self._load_from_platform_yaml('budget_tiers')
    
    def get_model(self, model_type: str):  # Line 180
        """Resolve model with agent overrides or platform defaults"""
        return self._get_from_platform_yaml('models', model_type)
```

### Current Core Components

#### A. AnalysisService (common/agent_service.py)
```python
class AnalysisService:
    """Service for managing universal AI agent analysis workflow."""
    
    def __init__(self, spreadsheet_id: str):
        """Initialize with dynamic agent configuration"""
        self.spreadsheet_id = spreadsheet_id
        # Budget management via platform.yaml
    
    @property
    def agent_config(self):
        """Load and cache FullAgentConfig"""
        # Loads platform.yaml + agent YAML + schema
```

#### B. Budget Configuration (common/budget_config.py)
```python
class BudgetConfigManager:
    """Universal budget tier configuration."""
    
    def get_tier_config(self, tier_name: str):
        """Get budget tier configuration from platform.yaml"""
        tiers = self._load_platform_config()
        return BudgetTierConfig.from_dict(
            next(t for t in tiers if t['name'] == tier_name)
        )
```

## Universal Benefits

### For Adding New Agent Types
1. Create `agents/{new_agent}.yaml` with personality
2. Create Google Sheet with schema in rows 1-3  
3. **System automatically works** - no code changes required

### For Tuning System Behavior

#### 🔧 **Tune ALL Agents** (Edit `platform.yaml`)
```yaml
platform:
  models:
    analysis: "gpt-4o-mini"  # Changes model for all agents
  budget_tiers:
    - name: "basic"
      price: 1.00
      calls: 1
```

#### 🎯 **Tune ONE Agent** (Edit `agents/{name}.yaml`)
```yaml
models:
  analysis: "gpt-4o"  # Override just for this agent
starter_prompt: |
  You are a senior partner...  # Agent personality
```

### Architecture Benefits
- ✅ **Zero Code for New Agents**: Pure configuration approach
- ✅ **Universal Maintenance**: Change platform behavior in one place
- ✅ **Agent Flexibility**: Each agent has its own expertise and overrides
- ✅ **Dynamic Schema**: Input/output fields defined by users, not developers
- ✅ **Clean APIs**: Same endpoints work for ANY agent type
- ✅ **Focused Testing**: 5 clear tests instead of 34 overlapping ones

This ruthless redesign achieves true universality while dramatically simplifying the codebase.