# Universal AI Agent Platform - Implementation Plan

**Created**: 2025-01-28  
**Approach**: Documentation → Tests → System  
**Status**: Ready to Execute

## 🎯 Implementation Strategy

We will follow a **Documentation-First** approach:
1. **Update Documentation** - Get the design crystal clear
2. **Rebuild Tests** - 5 focused tests that define success 
3. **Rebuild System** - Clean implementation guided by tests

## 📚 Phase 1: Documentation (This Phase)

### ✅ COMPLETED
- [x] Created `docs/UNIVERSAL_SYSTEM_DESIGN.md` with complete architecture
- [x] Preserved Azure Functions structure per user feedback
- [x] Defined ruthless deletion and clean implementation strategy

### 🎯 IN PROGRESS  
- [ ] Update `docs/SYSTEM_ARCHITECTURE.md` to reflect new design
- [ ] Update `docs/API.md` to show universal endpoints
- [ ] Update `docs/TESTING.md` for new focused test strategy
- [ ] Delete/update outdated documentation

### Key Documentation Changes
1. **Replace** business-specific examples with universal ones
2. **Emphasize** configuration-over-code approach  
3. **Show** how same endpoints work for any agent type
4. **Document** platform.yaml and new agent format

## 🧪 Phase 2: Rebuild Tests (Next Phase)

### Current Problem: 34 Tests, 9 Failing, Overlapping Concerns

### New Strategy: 5 Focused Tests

```python
# 1. Configuration Loading Test
def test_universal_config_loading():
    """Can we load platform + agent + dynamic schema correctly?"""
    config = UniversalAgentEngine.load_config("business_evaluation")
    assert config.platform_config is not None
    assert config.agent_config is not None  
    assert config.dynamic_schema is not None

# 2. Input Validation Test  
def test_input_validation():
    """Does schema validation work for any agent type?"""
    config = UniversalAgentEngine.load_config("business_evaluation")
    valid_input = {"Idea_Overview": "test", "Business_Model": "test"}
    assert config.validate_input(valid_input) == True
    
    invalid_input = {"wrong_field": "test"}
    assert config.validate_input(invalid_input) == False

# 3. Workflow Engine Test
def test_workflow_execution():
    """Can we plan and execute multi-call analysis?"""
    engine = UniversalAgentEngine()
    job_id = engine.execute_analysis("business_evaluation", test_input, "basic")
    assert job_id is not None
    
# 4. API Integration Test
def test_api_endpoints():
    """Do all Azure Functions work end-to-end?"""
    # Test get_instructions
    instructions = call_azure_function("get_instructions", {"agent": "business_evaluation"})
    assert "collect" in instructions.lower()
    
    # Test get_pricepoints  
    tiers = call_azure_function("get_pricepoints", {})
    assert len(tiers) == 3
    
    # Test execute_analysis
    job = call_azure_function("execute_analysis", {"input": test_input, "tier": "basic"})
    assert "job_id" in job

# 5. Multi-Agent Test
def test_multiple_agent_types():
    """Can we run different agent types through same system?"""
    business_config = UniversalAgentEngine.load_config("business_evaluation")
    # Future: hr_config = UniversalAgentEngine.load_config("hr_analysis")
    
    assert business_config.agent_config.name == "Business Idea Evaluator"
    # assert hr_config.agent_config.name == "HR Analysis Assistant"
```

### Benefits of New Test Strategy
- ✅ **Clear success criteria** - Each test validates one core capability
- ✅ **Fast feedback** - 5 tests run quickly vs 34 slow ones
- ✅ **Universal focus** - Tests ensure system works for ANY agent type
- ✅ **End-to-end coverage** - From config loading to API responses

## 🏗️ Phase 3: Rebuild System (Final Phase)

### Step 1: Create Universal Configuration

**Create `platform.yaml`**:
```yaml
# Universal platform configuration
version: "1.0.0"
description: "Universal AI Agent Platform"

models:
  planning: "gpt-4o-mini"
  analysis: "gpt-4o-mini" 
  synthesis: "gpt-4o-mini"

budget_tiers:
  - name: "basic"
    price: 1.00
    calls: 1
    description: "Single optimized analysis call"
  - name: "standard"  
    price: 3.00
    calls: 3
    description: "Multi-faceted analysis with synthesis"
  - name: "premium"
    price: 5.00
    calls: 5 
    description: "Comprehensive deep-dive analysis"

prompts:
  planning_template: |
    You are an expert AI architecture planner designing optimal execution strategy.
    ANALYSIS TYPE: {analysis_type}
    AVAILABLE CALLS: {calls}
    USER INPUT: {user_input_summary}
    OUTPUT FIELDS: {output_fields}
    
    Design {calls}-call strategy with final summarizer call...
    
  analysis_template: |
    {agent_personality}
    
    ANALYSIS FOCUS: {call_focus}
    USER INPUT: {formatted_user_input}
    
    Provide detailed analysis focusing on: {call_focus}
    
  synthesis_template: |
    Synthesize previous analysis findings into final {analysis_type} analysis.
    
    PREVIOUS FINDINGS: {previous_findings}
    REQUIRED OUTPUT: {json_schema}
    
    Generate complete analysis JSON...
```

### Step 2: Create Universal Engine

**Create `common/engine.py`**:
```python
class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration"""
    
    def __init__(self):
        self.platform_config = self.load_platform_config()
    
    def load_config(self, agent_id: str):
        """Load complete config: platform + agent + dynamic schema"""
        agent_config = self.load_agent_config(agent_id)
        dynamic_schema = self.load_dynamic_schema(agent_config.sheet_url)
        return FullUniversalConfig(self.platform_config, agent_config, dynamic_schema)
    
    def execute_analysis(self, agent_id: str, user_input: dict, tier: str):
        """Universal analysis execution for any agent type"""
        config = self.load_config(agent_id)
        config.validate_input(user_input)
        
        # Plan execution using universal templates
        plan = self.plan_execution(config, tier, user_input)
        
        # Execute using universal workflow  
        job_id = self.execute_plan(config, plan, user_input)
        
        return job_id
```

### Step 3: Update Azure Functions

**Update each Azure Function to use UniversalAgentEngine**:

```python
# idea-guy/get_instructions/__init__.py
def main(req):
    agent_id = req.params.get('agent')  # Required parameter
    engine = UniversalAgentEngine()
    config = engine.load_config(agent_id)
    instructions = config.generate_instructions()
    return func.HttpResponse(instructions)

# idea-guy/get_pricepoints/__init__.py  
def main(req):
    engine = UniversalAgentEngine()
    tiers = engine.platform_config.budget_tiers
    return func.HttpResponse(json.dumps(tiers))

# idea-guy/execute_analysis/__init__.py
def main(req):
    data = json.loads(req.get_body())
    engine = UniversalAgentEngine()
    job_id = engine.execute_analysis(data['agent'], data['input'], data['tier'])
    return func.HttpResponse(json.dumps({"job_id": job_id}))
```

### Step 4: Clean Agent Configuration

**Update `agents/business_evaluation.yaml`**:
```yaml
# Agent-specific configuration only
agent_id: "business_evaluation"
name: "Business Idea Evaluator"
description: "VC-style business idea analysis"
sheet_url: "https://docs.google.com/spreadsheets/d/1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs/"

# Agent's core expertise and personality  
personality: |
  You are a senior partner at a top-tier venture capital firm whose reputation—and track record—depend on your ability to spot winners and weed out losers. You approach every pitch with rigor, realism, and an investor's eye for return on time and capital...

# Optional model overrides (uses platform defaults if omitted)
# models:
#   analysis: "gpt-4o"  # Uncomment if this agent needs different model
```

### Step 5: Ruthless Cleanup

**Delete these files entirely**:
- `common/budget_config.py`
- `common/agent_service.py`  
- 29 of 34 test files (keep only the 5 focused ones)

## 🎯 Success Criteria

### System Works When:
1. ✅ **Configuration loads** - Platform + agent + schema combine correctly
2. ✅ **Validation works** - Input validated against dynamic schema  
3. ✅ **Analysis executes** - Multi-call workflow runs for any agent
4. ✅ **APIs respond** - All Azure Functions work universally
5. ✅ **New agents easy** - Adding HR agent requires only YAML + Sheet

### Business Value Delivered:
- **Maintainability**: Change universal behavior in one place
- **Extensibility**: New agent types in minutes, not days
- **Testability**: 5 focused tests vs 34 overlapping ones
- **Universality**: Same system handles business, HR, legal, medical analysis

## 📋 Next Steps

1. **Complete documentation updates** (current phase)
2. **Write 5 focused tests** that define success
3. **Implement UniversalAgentEngine** guided by tests
4. **Update Azure Functions** to use universal engine  
5. **Test end-to-end** with existing business evaluation
6. **Create second agent type** to prove universality

This plan transforms the system from business-evaluation-specific to truly universal while keeping the clean Azure Functions API structure.