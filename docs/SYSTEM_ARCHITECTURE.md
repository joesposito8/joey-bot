# Universal AI Agent Platform - System Architecture

**Last Updated**: 2025-01-30  
**System Status**: RUTHLESS REDESIGN - Documentation Complete, Implementation Ready  
**Recent Changes**: Created PROJECT_VISION.md, added 5 new universal tests, deleted 29 legacy tests <!-- Updated to reflect vision initialization and test restructuring in recent commits -->

## Overview

The Universal AI Agent Platform enables ANY type of AI-powered analysis through pure configuration. The same codebase handles business evaluation, HR analysis, legal review, medical assessment, or any other domain through YAML configuration files.

**Core Principle**: Adding a new agent type requires ZERO code changes - only configuration files.

**Key Features**:
- **Universal Engine**: Single `UniversalAgentEngine` handles all agent types (PLANNED)
- **Platform Configuration**: Universal prompts, models, and budget tiers in `common/prompts.yaml` (CURRENT)
- **Agent Personalities**: Domain expertise through agent-specific YAML files in `agents/`
- **Dynamic Schemas**: Input/output fields defined in Google Sheets by users
- **Clean APIs**: Existing Azure Functions work for ANY agent type (5 endpoints in `idea-guy/`)

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
├── 📄 common/prompts.yaml                  # CURRENT: Universal templates and budget tiers
├── 📁 agents/
│   └── 📄 business_evaluation.yaml         # CURRENT: Business agent config (cleaned)
├── 📁 common/                              # Core business logic
│   ├── 📄 agent_service.py                 # CURRENT: Main orchestration (to be replaced)
│   ├── 📄 multi_call_architecture.py       # Workflow execution engine
│   ├── 📄 budget_config.py                 # UPDATED: Lightweight wrapper (simplified)
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
    ├── 📄 test_universal_agent_engine.py   # NEW: Core engine tests (planned)
    ├── 📄 test_universal_endpoints.py      # NEW: API integration tests
    └── 📄 test_workflow_engine.py          # NEW: Multi-call workflow tests
```

### PLANNED Structure (Post-Implementation)
```
📁 joey-bot/
├── 📄 platform.yaml                       # PLANNED: Universal config for ALL agents
├── 📁 common/
│   ├── 📄 engine.py                        # PLANNED: UniversalAgentEngine
│   ├── 📄 config.py                        # PLANNED: Universal config loading
│   └── 📄 workflow.py                      # PLANNED: Universal multi-call workflow
└── [Other files remain the same]
```

## System Flow - Current vs Planned

### Current System Flow (Transition State)
```
User Request → Azure Function → AnalysisService → Configuration Loading → MultiCallArchitecture → OpenAI → Results
             (idea-guy/*.py)   (agent_service.py)  (config/models.py)    (multi_call_architecture.py)
```

### PLANNED Universal System Flow
```
User Request → Azure Function → UniversalAgentEngine → Configuration Loading → Analysis Execution → Results
             (idea-guy/*.py)   (common/engine.py)    (platform.yaml +     (workflow.py)
                                                     agents/*.yaml +
                                                     Google Sheets)
```

### Current Core Components with File Locations

#### A. AnalysisService (common/agent_service.py:20-200)
```python
class AnalysisService:
    """CURRENT: Service for managing universal AI agent analysis workflow."""
    
    def __init__(self, spreadsheet_id: str):  # Line 23
        """Initialize with dynamic agent configuration from Google Sheets"""
        self.spreadsheet_id = spreadsheet_id
        # Budget management now handled via agent configuration (Line 30)
    
    @property
    def agent_config(self):  # Line 70
        """Load and cache FullAgentConfig from agents/business_evaluation.yaml"""
        # Located at common/agent_service.py:70-85
```

#### B. MultiCallArchitecture (common/multi_call_architecture.py:50-150)
```python
def create_multi_call_analysis(user_input, calls_available, openai_client, agent_config):
    """CURRENT: Creates intelligent multi-call analysis workflow"""
    # Architecture planning using templates from common/prompts.yaml
    # Located at common/multi_call_architecture.py:50
```

#### C. Configuration System (common/config/models.py:1-200)
```python
class FullAgentConfig:  # Line 150
    """CURRENT: Combines agent YAML + Google Sheets schema + universal prompts"""
    
    def get_budget_tiers(self):  # Line 170
        """Load universal budget tiers from common/prompts.yaml"""
    
    def get_model(self, model_type: str):  # Line 180
        """Resolve model with agent overrides or platform defaults"""
```

### PLANNED Core Engine Architecture (To Be Implemented)
```python
# common/engine.py (PLANNED)
class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration"""
    
    def load_config(self, agent_id: str):
        """Load complete config: platform + agent + dynamic schema"""
        platform_config = load_yaml("platform.yaml")  # PLANNED
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

### Current Endpoint Processing with Exact File Locations

#### A. Get Instructions Endpoint (idea-guy/get_instructions/__init__.py)
<!-- Updated to reflect current implementation, not planned universal version -->
```python
GET /api/get_instructions  # Currently no agent parameter required
│
├─ idea-guy/get_instructions/__init__.py:main() (Line 9)
│  ├─ sheet_id = os.environ.get('IDEA_GUY_SHEET_ID')  # Line 19
│  ├─ service = AnalysisService(sheet_id)  # Line 26 - Uses current system
│  ├─ config = service.agent_config  # Line 30 - Loads from agents/business_evaluation.yaml
│  ├─ instructions = config.generate_instructions()  # Line 33 - Uses dynamic schema
│  └─ Return instructions with testing_mode flag (Line 34-42)
│
├─ CURRENT BEHAVIOR: Hardcoded to business_evaluation agent
└─ PLANNED: Add agent parameter for universal support
```

#### B. PLANNED Universal Get Instructions (Future Implementation)
```python
GET /api/get_instructions?agent={agent_id}  # PLANNED parameter
│
├─ idea-guy/get_instructions/__init__.py:main()  # TO BE UPDATED
│  ├─ agent_id = req.params.get('agent')  # PLANNED: Required parameter
│  ├─ engine = UniversalAgentEngine()  # PLANNED: Replace AnalysisService
│  ├─ config = engine.load_config(agent_id)  # PLANNED: Load platform + agent + schema
│  └─ Return instructions for ANY agent type
```

#### B. Get Price Points Endpoint (idea-guy/get_pricepoints/__init__.py)
```python
GET /api/get_pricepoints
│
├─ idea-guy/get_pricepoints/__init__.py:main() (Line 9)
│  ├─ sheet_id = os.environ.get('IDEA_GUY_SHEET_ID')  # Line 19
│  ├─ service = AnalysisService(sheet_id)  # Line 26 - Current system
│  ├─ pricepoints = []  # Line 129 - Generate from agent config
│  ├─ for tier in service.agent_config.get_budget_tiers():  # Line 131
│  │  └─ Loads from common/prompts.yaml budget_tiers (Line 16-55)
│  └─ Return universal budget tiers: [Basic($1), Standard($3), Premium($5)]
│
├─ CURRENT: Uses AnalysisService + FullAgentConfig.get_budget_tiers()
│  └─ Budget tiers loaded from common/prompts.yaml:16-55
└─ PLANNED: Direct access via UniversalAgentEngine.platform_config
```

#### C. Execute Analysis Endpoint (idea-guy/execute_analysis/__init__.py)
```python
POST /api/execute_analysis
Body: {user_input: {...}, budget_tier: "standard"}  # Currently no agent parameter
│
├─ idea-guy/execute_analysis/__init__.py:main() (Line 9)
│  ├─ data = json.loads(req.get_body())  # Line 19
│  ├─ sheet_id = os.environ.get('IDEA_GUY_SHEET_ID')  # Line 22
│  ├─ service = AnalysisService(sheet_id)  # Line 33 - Current system
│  ├─ job_id = service.execute_analysis(
│  │    data['user_input'], data['budget_tier'])  # Line 35-36
│  │  ├─ config = service.agent_config  # Loads agents/business_evaluation.yaml
│  │  ├─ service.validate_input(data['user_input'])  # Line 45 - Dynamic validation
│  │  ├─ tier_config = find_budget_tier(data['budget_tier'])  # Line 174-182
│  │  └─ analysis_job_id = create_multi_call_analysis(
│  │      user_input, tier_config.calls, openai_client, agent_config)  # Line 190
│  │    └─ Located in common/multi_call_architecture.py:50
│  └─ Return {"analysis_job_id": job_id}  # Line 40
│
├─ CURRENT: Hardcoded to business_evaluation agent
└─ PLANNED: Add agent parameter and use UniversalAgentEngine
```

#### D. Process Analysis Results (idea-guy/process_idea/__init__.py)
```python
GET /api/process_idea?id={job_id}
│
├─ idea-guy/process_idea/__init__.py:main() (Line 9)
│  ├─ job_id = req.params.get('id')  # Line 19
│  ├─ sheet_id = os.environ.get('IDEA_GUY_SHEET_ID')  # Line 22
│  ├─ service = AnalysisService(sheet_id)  # Line 33
│  ├─ response = service.openai_client.beta.threads.runs.retrieve(
│  │    thread_id=job_id.split('_')[0], run_id=job_id.split('_')[1])  # Line 35-36
│  ├─ If analysis complete (response.status == 'completed'):  # Line 45
│  │  ├─ extract_content = service.extract_thread_content(job_id)  # Line 47
│  │  ├─ parsed_results = service.parse_analysis_results(extract_content)  # Line 50
│  │  ├─ service.write_to_sheet(user_input, parsed_results)  # Line 55
│  │  │  └─ Uses dynamic schema from Google Sheets rows 1-3
│  │  └─ Return structured results with all analysis fields  # Line 60-70
│  └─ Else return {"status": response.status}  # Line 75
│
├─ CURRENT: Uses AnalysisService with hardcoded business evaluation
└─ PLANNED: Extract agent_id from job metadata for universal support
```

#### E. Read Sheet Utility (idea-guy/read_sheet/__init__.py)
```python
GET /api/read_sheet?id={sheet_id}
│
├─ idea-guy/read_sheet/__init__.py:main() (Line 9)
│  ├─ sheet_id = req.params.get('id') or os.environ.get('IDEA_GUY_SHEET_ID')  # Line 19
│  ├─ sheets_client = get_google_sheets_client()  # Line 26
│  ├─ spreadsheet = get_spreadsheet(sheets_client, sheet_id)  # Line 27
│  └─ Return raw sheet data as JSON  # Line 30-40
│
└─ UNCHANGED: Utility endpoint, no universal modifications needed
```

## Key System Components with File Locations

### Current Configuration System (common/config/models.py)

#### A. FullAgentConfig (common/config/models.py:150-250)
```python
class FullAgentConfig:
    """CURRENT: Combines agent YAML + Google Sheets schema + universal prompts"""
    
    def __init__(self, agent_definition: AgentDefinition, spreadsheet_id: str):  # Line 155
        """Initialize with agent config and sheet ID"""
        self.definition = agent_definition  # From agents/business_evaluation.yaml
        self.spreadsheet_id = spreadsheet_id
        self.schema = None  # Loaded from Google Sheets rows 1-3
        self._prompt_manager = None  # Loads from common/prompts.yaml
    
    def get_budget_tiers(self) -> List[BudgetTierConfig]:  # Line 170
        """Load universal budget tiers from common/prompts.yaml:16-55"""
        return self.prompt_manager.get_budget_tiers()
    
    def get_model(self, model_type: str) -> str:  # Line 180
        """Get model with agent overrides or platform defaults from prompts.yaml:9-13"""
        # Agent overrides from agents/business_evaluation.yaml:42-44 (commented out)
        # Platform defaults from common/prompts.yaml:9-13
        return self.prompt_manager.get_model(model_type, self.definition.models)
    
    def generate_instructions(self) -> str:  # Line 200
        """Generate user instructions from dynamic Google Sheets schema"""
        # Uses schema loaded from Google Sheets rows 1-3
        # Located at common/config/models.py:200-230
```

#### B. AgentDefinition (common/config/agent_definition.py:20-100)
```python
class AgentDefinition:
    """CURRENT: Agent configuration loaded from agents/*.yaml files"""
    
    agent_id: str                       # "business_evaluation"
    name: str                          # "Business Idea Evaluator"
    sheet_url: str                     # Google Sheets URL
    starter_prompt: str                # Agent personality (Line 11-38 in YAML)
    models: Dict[str, str] = None      # Optional model overrides (Line 42-44)
    
    @classmethod
    def from_yaml_file(cls, file_path: str):  # Line 50
        """Load agent definition from agents/business_evaluation.yaml"""
        # Located at common/config/agent_definition.py:50-80
```

#### C. PromptManager (common/prompt_manager.py:20-150)
```python
class PromptManager:
    """CURRENT: Loads universal templates from common/prompts.yaml"""
    
    def __init__(self):  # Line 25
        """Load prompts.yaml with universal templates and budget tiers"""
        self.config = self._load_prompts_config()  # Loads common/prompts.yaml
    
    def get_budget_tiers(self) -> List[BudgetTierConfig]:  # Line 40
        """Return universal budget tiers from common/prompts.yaml:16-55"""
        # Returns: [Basic($1, 1 call), Standard($3, 3 calls), Premium($5, 5 calls)]
    
    def get_prompt_template(self, template_name: str) -> str:  # Line 60
        """Get universal template from common/prompts.yaml:58-165"""
        # Templates: architecture_planning, analysis_call, synthesis_call
```

### PLANNED Universal Configuration (To Be Implemented)
```python
# common/config.py (PLANNED)
class FullUniversalConfig:
    """Combines platform + agent + dynamic configuration"""
    platform_config: PlatformConfig      # From platform.yaml (PLANNED)
    agent_config: AgentConfig            # From agents/{name}.yaml  
    dynamic_schema: DynamicSchema        # From Google Sheets rows 1-3

    def validate_input(self, user_input: dict) -> bool:
        """Validate input against dynamic schema"""
        
    def generate_instructions(self) -> str:
        """Generate user instructions from dynamic schema"""
        
    def get_model(self, model_type: str) -> str:
        """Get model with agent overrides: agent_config.models or platform_config.models"""
```

### Current Workflow Engine (common/multi_call_architecture.py)

#### A. MultiCallArchitecture (common/multi_call_architecture.py:50-200)
```python
def create_multi_call_analysis(user_input, calls_available, openai_client, agent_config):
    """CURRENT: Creates intelligent multi-call analysis workflow"""
    # Line 50: Main entry point for multi-call analysis
    
    # Step 1: Architecture Planning (Line 60-80)
    planning_prompt = agent_config.prompt_manager.get_prompt_template(
        'architecture_planning')  # From common/prompts.yaml:59-126
    
    # Step 2: Execute Planned Calls (Line 100-150)
    for call in architecture_plan.calls:
        if call.get('is_summarizer'):
            # Final synthesis call using common/prompts.yaml:144-165
        else:
            # Individual analysis call using common/prompts.yaml:128-142
    
    # Step 3: Return OpenAI Thread/Run ID (Line 180-200)
    return f"{thread.id}_{run.id}"  # Job ID format
```

#### B. Key Workflow Functions (common/multi_call_architecture.py)
```python
def plan_multi_call_architecture(calls_available, user_input, agent_config):  # Line 20
    """Plan optimal call strategy using architecture_planning template"""
    # Uses common/prompts.yaml:59-126 for planning
    
def execute_analysis_call(call_config, user_input, agent_config):  # Line 120
    """Execute individual analysis call"""
    # Uses common/prompts.yaml:128-142 for analysis_call template
    
def execute_synthesis_call(previous_findings, agent_config):  # Line 140
    """Execute final synthesis call"""
    # Uses common/prompts.yaml:144-165 for synthesis_call template
```

### PLANNED Universal Workflow Engine (To Be Implemented)
```python
# common/engine.py (PLANNED)
class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration"""
    
    def load_config(self, agent_id: str) -> FullUniversalConfig:
        """Load complete configuration for any agent"""
        
    def plan_execution(self, config: FullUniversalConfig, tier: str, user_input: dict):
        """Plan multi-call execution using universal templates"""
        
    def execute_plan(self, config: FullUniversalConfig, plan: ExecutionPlan, user_input: dict):
        """Execute analysis plan with universal workflow"""
```

### Current Configuration Files with Exact Content

#### A. Universal Platform Configuration (common/prompts.yaml:1-166)
<!-- Updated to reflect current implementation using prompts.yaml instead of planned platform.yaml -->
```yaml
# Universal AI Agent Platform - Common Prompts and Models Configuration
platform:
  version: "2.1.0"
  description: "Universal AI Agent Platform shared configuration"

# Models used for different platform functions (Lines 9-13)
models:
  architecture_planning: "gpt-4o-mini"    # Model for planning multi-call architecture
  analysis: "gpt-4o-mini"                 # Model for individual analysis calls
  synthesis: "gpt-4o-mini"                # Model for final synthesis
  user_interaction: "gpt-4o-mini"         # Model for user input processing/validation

# Universal budget tiers - same pricing and capabilities for ALL agents (Lines 16-55)
budget_tiers:
  - name: "basic"
    price: 1.00
    calls: 1
    description: "1 optimized call with intelligent architecture planning"
    time_estimate: "5-10 minutes"
    deliverables: ["Comprehensive analysis with detailed insights..."]  # Lines 23-28
    
  - name: "standard"
    price: 3.00
    calls: 3
    description: "3 coordinated calls with intelligent architecture planning"
    time_estimate: "15-20 minutes"
    deliverables: ["Comprehensive analysis with detailed insights..."]  # Lines 36-41
    
  - name: "premium"
    price: 5.00
    calls: 5
    description: "5 coordinated calls with intelligent architecture planning"
    time_estimate: "20-30 minutes"
    deliverables: ["Comprehensive analysis with detailed insights..."]  # Lines 49-54

# Common prompts used across all agent types (Lines 58-165)
prompts:
  architecture_planning: |  # Lines 59-126
    You are an expert AI architecture planner. Your job is to design the optimal execution strategy...
    
  analysis_call: |  # Lines 128-142
    {starter_prompt}
    SPECIFIC FOCUS: {call_purpose}
    USER INPUT: {formatted_user_input}...
    
  synthesis_call: |  # Lines 144-165
    You are synthesizing findings from multiple specialized analysis calls...
```

#### B. Business Evaluation Agent Configuration (agents/business_evaluation.yaml:1-51)
```yaml
agent_id: "business_evaluation"  # Line 1
name: "Business Idea Evaluator"  # Line 2
description: "Evaluates business ideas for market viability, feasibility, and investment potential using VC-style analysis"  # Line 3
version: "1.0.0"  # Line 4
author: "Joey Bot Platform"  # Line 5

# Google Sheet containing both schema definition (rows 1-3) and data storage
sheet_url: "https://docs.google.com/spreadsheets/d/1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs/"  # Line 8

# Core agent personality and expertise (starter prompt) (Lines 11-38)
starter_prompt: |
  You are a senior partner at a top-tier venture capital firm whose reputation—and track record—depend on your ability to spot winners and weed out losers. You approach every pitch with rigor, realism, and an investor's eye for return on time and capital...
  [38 lines of detailed VC personality and research requirements]

# Budget tiers are now universal - defined in common/prompts.yaml (Lines 39-40)
# All agents use the same pricing structure and capabilities

# Model overrides for this agent (optional - uses platform defaults if not specified) (Lines 42-44)
# models:
#   analysis: "gpt-4o"  # Override if this agent needs a different model

# Workflow configuration (Lines 47-51)
workflow_template: "multi_call_architecture"
tools:
  - type: "web_search_preview"
reasoning:
  summary: "auto"
```

#### C. PLANNED Platform Configuration (platform.yaml - To Be Created)
```yaml
# PLANNED: Universal platform configuration for ALL agents
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

## Complete File Mapping - Current vs Planned
<!-- Updated to show exact current file locations and their planned replacements -->

### Configuration Files

#### Current Configuration System
- 📄 `common/prompts.yaml` **(Lines 1-166)** - Universal templates, models, budget tiers
- 📄 `agents/business_evaluation.yaml` **(Lines 1-51)** - Business agent personality and config
- 📄 `common/config/models.py` **(Lines 1-250)** - Data models and configuration classes
- 📄 `common/config/agent_definition.py` **(Lines 1-100)** - Agent YAML parsing
- 📄 `common/config/sheet_schema_reader.py` **(Lines 1-150)** - Google Sheets schema loading

#### Planned Configuration System
- 📄 `platform.yaml` - **PLANNED**: Universal configuration for ALL agents
- 📄 `agents/business_evaluation.yaml` - **TO UPDATE**: Agent-specific configuration only
- 📄 `agents/{agent_name}.yaml` - **FUTURE**: Additional agent types
- 📄 `common/config.py` - **PLANNED**: Universal configuration loading

### HTTP Endpoints (Azure Functions)

#### Current Azure Functions (idea-guy/)
- 📄 `idea-guy/get_instructions/__init__.py` **(Lines 9-55)** - Instructions for business evaluation
- 📄 `idea-guy/get_pricepoints/__init__.py` **(Lines 9-45)** - Universal budget tiers  
- 📄 `idea-guy/execute_analysis/__init__.py` **(Lines 9-50)** - Analysis execution
- 📄 `idea-guy/process_idea/__init__.py` **(Lines 9-80)** - Result retrieval
- 📄 `idea-guy/read_sheet/__init__.py` **(Lines 9-45)** - **UNCHANGED**: Utility endpoint

#### Planned Azure Functions Updates
- 📄 `idea-guy/get_instructions/__init__.py` - **TO UPDATE**: Add agent parameter for universal support
- 📄 `idea-guy/get_pricepoints/__init__.py` - **TO UPDATE**: Use UniversalAgentEngine
- 📄 `idea-guy/execute_analysis/__init__.py` - **TO UPDATE**: Add agent parameter and universal execution
- 📄 `idea-guy/process_idea/__init__.py` - **TO UPDATE**: Extract agent_id from job metadata

### Core Business Logic

#### Current Core System
- 📄 `common/agent_service.py` **(Lines 20-200)** - **CURRENT**: Main orchestration service
- 📄 `common/multi_call_architecture.py` **(Lines 50-200)** - **CURRENT**: Workflow execution
- 📄 `common/budget_config.py` **(Lines 1-60)** - **SIMPLIFIED**: Lightweight wrapper
- 📄 `common/prompt_manager.py` **(Lines 20-150)** - **CURRENT**: Template loading

#### Planned Core System
- 📄 `common/engine.py` - **PLANNED**: UniversalAgentEngine (replaces agent_service.py)
- 📄 `common/workflow.py` - **PLANNED**: Universal multi-call workflow
- ❌ `common/budget_config.py` - **TO DELETE**: Move functionality to platform.yaml
- ❌ `common/agent_service.py` - **TO DELETE**: Replace with UniversalAgentEngine

### Supporting Services (Unchanged)
- 📄 `common/cost_tracker.py` **(Lines 1-100)** - OpenAI cost logging
- 📄 `common/utils.py` **(Lines 1-150)** - OpenAI & Google Sheets client initialization  
- 📄 `common/http_utils.py` **(Lines 1-80)** - HTTP request/response utilities

### Testing System

#### Current Testing (Recent Major Restructure)
- 📄 `tests/test_dynamic_configuration.py` **(NEW: 548 lines)** - Configuration loading tests
- 📄 `tests/test_platform_config.py` **(NEW: 273 lines)** - Platform configuration tests
- 📄 `tests/test_universal_agent_engine.py` **(NEW: 400 lines)** - Core engine tests
- 📄 `tests/test_universal_endpoints.py` **(NEW: 787 lines)** - API integration tests
- 📄 `tests/test_workflow_engine.py` **(NEW: 570 lines)** - Multi-call workflow tests

#### Deleted Legacy Tests (29 files removed)
- ❌ `tests/integration/test_business_evaluation_config.py` **(DELETED: 240 lines)**
- ❌ `tests/integration/test_chatgpt_flow.py` **(DELETED: 187 lines)**
- ❌ `tests/integration/test_full_agent_config.py` **(DELETED: 106 lines)**
- ❌ `tests/unit/test_agent.py` **(DELETED: 86 lines)**
- ❌ `tests/unit/test_config_models.py` **(DELETED: 144 lines)**
- ❌ *[24 additional test files deleted - see git diff for complete list]*

### Documentation System
- 📄 `PROJECT_VISION.md` **(NEW: 150+ lines)** - Project mission and roadmap
- 📄 `IMPLEMENTATION_PLAN.md` **(NEW: 259 lines)** - Step-by-step transformation plan
- 📄 `docs/UNIVERSAL_SYSTEM_DESIGN.md` **(NEW: 257 lines)** - Complete redesign specification
- 📄 `docs/SYSTEM_ARCHITECTURE.md` **(UPDATED: This file)** - Technical implementation details
- 📄 `CLAUDE.md` **(UPDATED: 43 lines changed)** - Documentation directory and quick reference

## Testing Strategy - Major Restructure Complete
<!-- Updated to reflect recent test file creation and deletion -->

### Recent Testing Overhaul (34 → 5 Tests)
**COMPLETED**: Deleted 29 legacy test files, created 5 new focused universal tests

#### New Universal Test Files (Total: 2,578 lines)
```python
# 1. test_dynamic_configuration.py (548 lines) - Configuration loading tests
class TestDynamicConfiguration:
    def test_load_agent_definition()  # Line 20
    def test_load_google_sheets_schema()  # Line 50
    def test_full_agent_config_creation()  # Line 100
    # Tests: Can we load platform + agent + dynamic schema correctly?

# 2. test_platform_config.py (273 lines) - Platform configuration tests  
class TestPlatformConfig:
    def test_budget_tiers_loading()  # Line 25
    def test_universal_prompts_loading()  # Line 75
    def test_model_configuration()  # Line 125
    # Tests: Do universal templates and budget tiers work?

# 3. test_universal_agent_engine.py (400 lines) - Core engine tests
class TestUniversalAgentEngine:
    def test_engine_initialization()  # Line 30
    def test_config_loading()  # Line 80
    def test_analysis_execution()  # Line 150
    # Tests: Can we execute analysis for any agent type?

# 4. test_universal_endpoints.py (787 lines) - API integration tests
class TestUniversalEndpoints:
    def test_get_instructions_endpoint()  # Line 40
    def test_get_pricepoints_endpoint()  # Line 120
    def test_execute_analysis_endpoint()  # Line 200
    def test_process_idea_endpoint()  # Line 350
    # Tests: Do all Azure Functions work universally?

# 5. test_workflow_engine.py (570 lines) - Multi-call workflow tests
class TestWorkflowEngine:
    def test_architecture_planning()  # Line 50
    def test_multi_call_execution()  # Line 150
    def test_synthesis_generation()  # Line 300
    # Tests: Can we plan and execute multi-call workflows?
```

#### Deleted Legacy Tests (29 files, 2,165 lines removed)
- ❌ **Integration Tests** (8 files deleted):
  - `test_business_evaluation_config.py` (240 lines)
  - `test_chatgpt_flow.py` (187 lines)
  - `test_full_agent_config.py` (106 lines)
  - `test_multi_call_architecture.py` (198 lines)
  - `test_new_analysis.py` (67 lines)
  - `test_process_idea.py` (61 lines)
  - `test_process_idea_endpoint.py` (75 lines)
  - `__init__.py` (1 line)

- ❌ **Unit Tests** (6 files deleted):
  - `test_agent.py` (86 lines)
  - `test_agent_definition.py` (103 lines)
  - `test_business_evaluation_yaml.py` (162 lines)
  - `test_config_models.py` (144 lines)
  - `test_model_replacement.py` (96 lines)
  - `test_sheet_schema_reader.py` (110 lines)
  - `__init__.py` (1 line)

### Current Test Status
⚠️ **IMPORT ERRORS**: New tests have import issues due to missing UniversalAgentEngine class
```bash
# Error in test_workflow_engine.py:13
ImportError: cannot import name 'AnalysisCall' from 'common.multi_call_architecture'
```

### Testing Mode Protection
```python
# common/http_utils.py - Testing mode detection
def is_testing_mode() -> bool:
    return os.environ.get('TESTING_MODE', '').lower() == 'true'

# When TESTING_MODE=true:
# - Mock OpenAI responses (no API charges)
# - Skip Google Sheets operations  
# - Fast test execution
# - No costs incurred
```

### Test Execution Commands
```bash
# Safe testing (no API charges)
export TESTING_MODE=true
python -m pytest tests/ -v

# Check testing mode status
python -c "from common.http_utils import is_testing_mode; print(f'Testing mode: {is_testing_mode()}')"
```

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