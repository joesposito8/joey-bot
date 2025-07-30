# Joey-Bot Universal AI Agent Platform Tests

This directory contains the comprehensive test suite for the Universal AI Agent Platform, designed to test every part of the system without calling OpenAI APIs.

## Architecture Overview

The test suite validates the three-layer Universal System Design:
- **Platform Layer** (`platform.yaml`) - Universal settings, budget tiers, models
- **Agent Layer** (`agents/*.yaml`) - Agent-specific configurations  
- **Dynamic Layer** (Google Sheets) - User-defined schemas and runtime data

## Test Structure (5 Core Tests)

### `test_platform_config.py` - Platform Layer Validation
Tests universal platform configuration and settings:
- ✅ Platform.yaml loading and validation
- ✅ Universal budget tiers ($1/$3/$5 for basic/standard/premium)
- ✅ Model configuration (gpt-4o-mini standard)
- ✅ Universal prompt templates
- ✅ Cost tracking and pricing validation
- ✅ Testing mode environment setup

### `test_universal_agent_engine.py` - Agent Orchestration
Tests the Universal Agent Engine and multi-agent support:
- ✅ Universal agent creation and initialization
- ✅ Multi-agent support and agent type switching
- ✅ Budget tier integration across all agents
- ✅ Shared infrastructure (cost tracking, multi-call architecture)
- ✅ Universal input validation and error handling
- ✅ Performance optimization and memory efficiency

### `test_dynamic_configuration.py` - Configuration Pipeline
Tests the complete YAML → Google Sheets → Runtime configuration:
- ✅ Configuration data models (FieldConfig, SheetSchema, BudgetTierConfig)
- ✅ Google Sheets schema parsing with comprehensive scenarios
- ✅ YAML agent definition loading and validation
- ✅ Full agent configuration combining static + dynamic config
- ✅ Instruction generation and analysis prompt creation
- ✅ End-to-end configuration flow validation

### `test_workflow_engine.py` - Universal Workflow Patterns
Tests the universal Planner → Execution → Synthesizer workflow:
- ✅ Universal workflow planning and execution order
- ✅ Multi-tier workflow scaling (1/3/5 calls for basic/standard/premium)
- ✅ LangChain workflow integration and memory management
- ✅ Parallel execution optimization and result aggregation
- ✅ Advanced workflow patterns and performance monitoring
- ✅ Integration with existing systems (AnalysisService, endpoints)

### `test_universal_endpoints.py` - All Azure Functions
Tests all 5 Azure Function endpoints with any agent type:
- ✅ Universal endpoint architecture and response consistency
- ✅ **get_instructions** - Dynamic instruction generation for any agent
- ✅ **get_pricepoints** - Universal budget tier pricing
- ✅ **execute_analysis** - Analysis execution with comprehensive validation  
- ✅ **process_idea** - Result processing with universal output formats
- ✅ **read_sheet** - Universal sheet access with parameter handling
- ✅ End-to-end ChatGPT bot workflow simulation
- ✅ Comprehensive error handling and performance testing

## Key Testing Features

### 🚫 No OpenAI API Calls
All tests run in `TESTING_MODE=true` to prevent API charges:
- Mock OpenAI client responses for all scenarios
- Comprehensive result simulation without real API calls
- Cost-free validation of all system components

### 🎯 Extraordinarily Comprehensive Coverage
Tests every part of the Universal AI Agent Platform:
- Platform configuration and universal settings
- Agent orchestration and multi-agent support
- Dynamic configuration pipeline (YAML + Sheets)
- Universal workflow patterns and execution
- All Azure Function endpoints with any agent type
- Error handling, performance, and edge cases

### 🔄 Universal Agent Support
Tests work with any agent type through configuration:
- Business evaluation agents
- Technical analysis agents  
- Market research agents
- Any future agent types added via YAML configuration

## Running Tests

```bash
# Run complete comprehensive test suite
python -m pytest tests/ -v

# Run individual test modules
python -m pytest tests/test_platform_config.py -v
python -m pytest tests/test_universal_agent_engine.py -v
python -m pytest tests/test_dynamic_configuration.py -v
python -m pytest tests/test_workflow_engine.py -v
python -m pytest tests/test_universal_endpoints.py -v

# Run with detailed output and timing
python -m pytest tests/ -v -s --tb=short

# Run specific test scenarios
python -m pytest tests/test_universal_endpoints.py::TestEndToEndWorkflow -v
```

## Environment Setup

Required environment variables for testing:
```bash
export TESTING_MODE="true"
export IDEA_GUY_SHEET_ID="test_sheet_id_for_testing"
```

Optional (for real Google Sheets integration tests):
```bash
export GOOGLE_SHEETS_KEY_PATH=".keys/joey-bot-465403-d2eb14543555.json"
export OPENAI_API_KEY="your-api-key-here"
```

## Test Coverage

The comprehensive test suite covers:
- ✅ **Platform Layer** - Universal settings, budget tiers, models
- ✅ **Agent Layer** - YAML configuration loading and validation
- ✅ **Dynamic Layer** - Google Sheets schema parsing and integration
- ✅ **Workflow Engine** - Universal Planner→Execution→Synthesizer patterns  
- ✅ **Azure Functions** - All 5 endpoints with comprehensive scenarios
- ✅ **Error Handling** - Graceful error handling across all components
- ✅ **Performance** - Memory efficiency, response times, concurrency
- ✅ **Integration** - End-to-end workflows and component integration

## Migration from Previous Tests

The new test structure replaces the previous 34 overlapping tests with 5 comprehensive tests:

**Eliminated Tests** (business-specific/duplicated):
- ❌ `test_business_evaluation_yaml.py` - Business-specific
- ❌ `test_business_evaluation_config.py` - Business-specific integration  
- ❌ `test_model_replacement.py` - One-time migration test

**Enhanced Tests** (universal/comprehensive):
- 🔄 `test_agent.py` → `test_universal_agent_engine.py` (universal agent support)
- 🔄 `test_multi_call_architecture.py` → `test_workflow_engine.py` (universal workflows)
- 🔄 `test_chatgpt_flow.py` → `test_universal_endpoints.py` (all endpoints)
- ✅ `test_config_models.py` + `test_sheet_schema_reader.py` + `test_agent_definition.py` + `test_full_agent_config.py` → `test_dynamic_configuration.py` (combined comprehensive testing)

**New Tests**:
- 🆕 `test_platform_config.py` - Universal platform configuration validation

This provides **extraordinarily comprehensive** testing of every system component while eliminating duplication and business-specific constraints.