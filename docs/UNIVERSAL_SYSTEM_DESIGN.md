# Universal AI Agent Platform - Complete System Design

**Created**: 2025-01-28  
**Status**: RUTHLESS REDESIGN - No Backwards Compatibility  
**Vision**: Simple, Elegant, Universal

## 🎯 Core Philosophy

**ONE TRUTH**: This system creates AI agents through pure configuration, not code. Adding a new agent type should require ZERO programming - just configuration files.

**THREE PILLARS**:
1. **Universal Templates** - Core prompts work for ANY domain (business, HR, legal, medical, etc.)
2. **Agent Personalities** - Domain expertise through configuration, not hardcoding  
3. **Dynamic Schemas** - Input/output fields defined by users, not developers

## 🏗️ System Architecture

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM LAYER                              │
│  - Universal prompts (planning, analysis, synthesis)           │
│  - Universal budget tiers ($1/$3/$5)                          │  
│  - Universal models (gpt-4o-mini for all functions)           │
│  - Universal workflow engine                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT LAYER                                │
│  - Agent personality (starter_prompt)                          │
│  - Agent name and description                                  │
│  - Optional model overrides                                    │
│  - Google Sheet URL for schema                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   DYNAMIC LAYER                                │
│  - Input fields (what user provides)                           │
│  - Output fields (what analysis generates)                     │
│  - Field descriptions for prompts                              │
│  - All defined in Google Sheets rows 1-3                      │
└─────────────────────────────────────────────────────────────────┘
```

### Single Source of Truth Principle

**PLATFORM CONFIG** (`platform.yaml`):
```yaml
# Universal configuration for ALL agents
models:
  planning: "gpt-4o-mini"
  analysis: "gpt-4o-mini" 
  synthesis: "gpt-4o-mini"

budget_tiers:
  - {name: basic, price: 1.00, calls: 1}
  - {name: standard, price: 3.00, calls: 3}  
  - {name: premium, price: 5.00, calls: 5}

prompts:
  planning_template: |
    Design optimal {calls}-call strategy for {analysis_type}...
  analysis_template: |
    {agent_personality}
    
    ANALYSIS REQUEST: {user_input}
    FOCUS: {call_focus}
  synthesis_template: |
    Synthesize findings into final {analysis_type} analysis...
```

**AGENT CONFIG** (`agents/{name}.yaml`):
```yaml
# Only agent-specific configuration
agent_id: "business_evaluation"
name: "Business Idea Evaluator" 
description: "VC-style business analysis"
sheet_url: "https://docs.google.com/spreadsheets/d/abc123"

# Agent's core expertise and personality
personality: |
  You are a senior partner at a top-tier VC firm...
  
# Optional overrides (uses platform defaults if omitted)
models:
  analysis: "gpt-4o"  # This agent needs better model
```

**DYNAMIC SCHEMA** (Google Sheets rows 1-3):
```
Row 1: user_input | user_input | bot_output | bot_output | bot_output
Row 2: Idea description | Business model | Market analysis | Risk assessment | Overall rating  
Row 3: Idea_Overview | Business_Model | Market_Analysis | Risk_Assessment | Overall_Rating
```

## 🔄 Simplified System Flow

### Clean Azure Functions API

**KEEP EXISTING ENDPOINTS** but make them universal:

```python
# These Azure Functions stay but become universal
GET /api/get_instructions           # Returns instructions for ANY agent type
GET /api/get_pricepoints           # Returns universal budget tiers  
POST /api/execute_analysis         # Starts analysis for ANY agent type
GET /api/process_idea?id={job_id}  # Gets results for ANY agent type
GET /api/read_sheet?id={sheet_id}  # Utility endpoint (unchanged)
```

**Each endpoint becomes agent-agnostic** - they determine agent type from configuration, not hardcoded business logic.

### Core Workflow Engine

```python
class UniversalAgentEngine:
    """Single engine that handles ANY agent type through configuration"""
    
    def analyze(self, agent_id: str, user_input: dict, tier: str):
        # 1. Load configuration (platform + agent + schema)
        config = self.load_config(agent_id)
        
        # 2. Validate input against dynamic schema  
        config.validate_input(user_input)
        
        # 3. Plan execution strategy
        plan = self.plan_analysis(config, tier, user_input)
        
        # 4. Execute multi-call analysis
        results = self.execute_plan(config, plan, user_input)
        
        # 5. Store results and return
        return self.store_and_return(config, results)
```

## 🗂️ Ruthless File Structure

**KILL THESE ENTIRELY**:
- ❌ `common/budget_config.py` - Move to platform.yaml
- ❌ `common/agent_service.py` - Replace with UniversalAgentEngine

**NEW CLEAN STRUCTURE**:
```
platform.yaml                    # Universal configuration
agents/
  business_evaluation.yaml        # Agent-specific config
  hr_analysis.yaml               # Future agent
  product_review.yaml            # Future agent
  
common/
  engine.py                      # UniversalAgentEngine
  config.py                      # Configuration loading  
  workflow.py                    # Multi-call execution
  
idea-guy/                        # Azure Functions (kept)
  get_instructions/              # Universal instructions endpoint
  get_pricepoints/               # Universal budget tiers endpoint
  execute_analysis/              # Universal analysis endpoint
  process_idea/                  # Universal results endpoint
  read_sheet/                    # Utility endpoint (unchanged)
  
tests/
  test_engine.py                 # Core engine tests
  test_config.py                 # Configuration tests
```

## 🎯 Key Design Decisions

### 1. Configuration Over Code
**OLD**: Adding new agent requires Python coding  
**NEW**: Adding new agent requires only YAML file + Google Sheet

### 2. Universal Endpoints  
**OLD**: Azure Functions hardcoded for business evaluation  
**NEW**: Same endpoints work for ANY agent type through configuration

### 3. Universal Templates
**OLD**: Business-specific prompts hardcoded everywhere  
**NEW**: Templates that work for business, HR, legal, medical, etc.

### 4. Schema as Data
**OLD**: Input/output fields hardcoded in Python classes  
**NEW**: Schema defined in Google Sheets, loaded dynamically

### 5. Platform-First Design
**OLD**: Built for business evaluation, extended for other uses  
**NEW**: Built as universal platform from day one

## 📋 Implementation Strategy

### Phase 1: Core Engine (Week 1)
- [ ] Create `platform.yaml` with universal config
- [ ] Build `UniversalAgentEngine` class
- [ ] Implement configuration loading system
- [ ] Create unified API endpoint

### Phase 2: Migration (Week 2)  
- [ ] Migrate business evaluation to new system
- [ ] Update Google Sheets schema
- [ ] Test end-to-end workflow
- [ ] Remove old Azure Functions

### Phase 3: Testing & Polish (Week 3)
- [ ] Comprehensive test suite (10 focused tests, not 34)
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Production deployment

## 🧪 Testing Philosophy

**KILL COMPLEX TESTING**: Instead of 34 overlapping tests, focus on:

1. **Configuration Loading Test** - Can we load platform + agent + schema?
2. **Input Validation Test** - Does schema validation work?
3. **Workflow Engine Test** - Can we plan and execute analysis?
4. **API Integration Test** - Do endpoints work end-to-end?
5. **Multi-Agent Test** - Can we run different agent types?

**5 FOCUSED TESTS > 34 CONFUSED TESTS**

## 🚀 Benefits of New Design

### For Users
- ✅ **Single API** instead of 5 confusing endpoints
- ✅ **Consistent behavior** across all agent types  
- ✅ **Easy customization** through configuration files

### For Developers  
- ✅ **One codebase** handles all agent types
- ✅ **Clear separation** between platform and agent logic
- ✅ **Simple testing** with focused test suite

### For Business
- ✅ **Rapid expansion** - new agent types in hours, not days
- ✅ **Maintainable** - changes affect whole platform or single agent
- ✅ **Scalable** - platform grows without code complexity

## 🔥 Migration Strategy

### Ruthless Deletion List
1. Delete `common/budget_config.py` 
2. Delete `common/agent_service.py`
3. Delete 29 of 34 tests (keep 5 focused ones)
4. Delete hardcoded budget tiers in agent YAML
5. Delete universal prompts from agent YAML

### Clean Implementation
1. Create `platform.yaml` with universal config
2. Create `common/engine.py` with UniversalAgentEngine
3. Update Azure Functions to use UniversalAgentEngine
4. Update `agents/business_evaluation.yaml` to new format
5. Create 5 focused tests

This design eliminates complexity while achieving true universality. Every line of code serves a clear purpose, and adding new agent types becomes trivial.