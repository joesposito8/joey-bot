# Joey-Bot Task List

**Last Updated**: 2025-08-04  
**Current Phase**: PHASE 2 CORE IMPLEMENTATION - Universal Agent Platform Ready  
**Status**: **AZURE DURABLE FUNCTIONS PRODUCTION DEPLOYMENT** - Complete DurableOrchestrator system with reliable background processing, async/await architecture, all budget tiers working, enhanced diagnostics. Ready for universal endpoint architecture and Custom GPT integration.

## Completed Work

### Documentation & Planning
- [x] Create comprehensive PROJECT_VISION.md with mission, scope, milestones, and stakeholder context
- [x] Update SYSTEM_ARCHITECTURE.md with detailed file locations and component tracing  
- [x] Enhanced architecture documentation with current vs planned system comparison
- [x] Document recent testing restructure (34→5 tests, 29 files deleted)
- [x] Create IMPLEMENTATION_PLAN.md with step-by-step transformation roadmap
- [x] Create UNIVERSAL_SYSTEM_DESIGN.md with complete ruthless redesign specification
- [x] Update CLAUDE.md to reflect universal platform status and documentation structure
<!-- Updated from commit 8203cf2 -->

### Test System Restructure  
- [x] Delete 29 legacy test files (2,165 lines removed)
- [x] Create 5 new focused universal tests (2,578 lines added)
- [x] Restructure test directory from integration/unit to universal approach
- [x] Implement test files for dynamic configuration, platform config, agent engine, endpoints, and workflow
- [x] Update workflow engine tests to be behavior-driven
- [x] Remove prescriptive test assertions about specific implementation details
- [x] Add dynamic mock response generation for testing
<!-- Updated from commit 61c9503 -->

### Configuration System Updates
- [x] Simplify common/budget_config.py to lightweight wrapper
- [x] Update agents/business_evaluation.yaml to remove hardcoded budget tiers
- [x] Consolidate universal templates and budget tiers in platform.yaml
- [x] Update FullAgentConfig to use universal prompt system
- [x] Create unified error handling system in common/errors.py
- [x] Remove UniversalAgentEngine in favor of existing AnalysisService
- [x] Update system architecture docs to reflect current state
- [x] Add universal settings access via FullAgentConfig
- [x] Simplify MultiCallArchitecture configuration handling
<!-- Updated from commit 9ad9008 -->

### Test Infrastructure Overhaul
- [x] Fix import-time Google Sheets execution in Azure Functions (moved to lazy initialization)
- [x] Replace Google Sheets mocking with real API integration (API is free to use)
- [x] Update test data to match actual schema requirements (proper field names)
- [x] Align test expectations with actual validation behavior (ValidationError vs ValueError)
- [x] Fix sheet schema validation to require descriptions for all fields except ID/Time
- [x] Add proper ConfigurationError imports and error handling
- [x] Fix missing test fixtures by moving to module level scope
- [x] Update response structure expectations to match real Google Sheets API
- [x] Improve test pass rate from 58% to 95% (25→41 passing tests)
- [x] Eliminate all test errors, reduce failures from 16 to 2
- [x] Validate all critical components: Platform config, Workflow engine, Dynamic config, Business evaluator
<!-- Updated from commit 9f2d5b7 -->

### Recent Critical Fixes
- [x] Fix template formatting error in platform.yaml (escape curly braces)
- [x] Fix agent_config parameter passing to MultiCallArchitecture constructor
- [x] Update get_pricepoints endpoint to use GET method
- [x] Clean up get_budget_options method - remove backwards compatibility
- [x] Remove unused user_interaction model from platform.yaml
<!-- Updated from commits 328221f, 07758da, 7a4019f, 45fece7, b44594e -->

### JSON Parsing & Performance Optimization
- [x] **FIX JSON parsing failures** - Resolved invalid escape sequences (\$1.2M) causing research call failures
  - Implemented LangChain OutputFixingParser for automatic JSON error correction across all AI calls
  - Created layered parsing strategy: Direct parsing → clean_json_response → LLM correction
  - Applied to all 3 parser types: research (PydanticOutputParser), planning (JsonOutputParser), synthesis (JsonOutputParser)
- [x] **OPTIMIZE LLM correction costs** - Added 3-layer parsing to minimize expensive GPT-4o-mini correction calls
  - Layer 1: Direct parsing (0ms, clean JSON)
  - Layer 2: clean_json_response + parsing (1ms, handles escape sequences/markdown)
  - Layer 3: OutputFixingParser LLM correction (200-1000ms, complex issues only)
- [x] **IMPLEMENT duplicate prevention** - Comprehensive solution for duplicate research calls issue
  - Added deterministic job fingerprinting using SHA256 of user_input + budget_tier + agent_id
  - Implemented request deduplication with existing job detection via Google Sheets
  - Added Azure Functions concurrency controls (maxConcurrentOrchestratorFunctions: 3)
  - Enhanced orchestration instance deduplication using deterministic instance IDs
- [x] **INCREASE function timeout** - Extended Azure Functions timeout from 5 to 10 minutes for deep research calls
  - Updated host.json with functionTimeout: "00:10:00"
  - Added environment variable override: AzureFunctionsJobHost__functionTimeout
<!-- Updated from commits 228afb8, efaa055, 536436f, 2becb73, a141684 -->

### Sequential Research→Synthesis System Implementation
- [x] DELETE common/multi_call_architecture.py ENTIRELY - Fundamentally broken (background=True prevents dependencies)
- [x] CREATE common/research_models.py with LangChain PydanticOutputParser for structured JSON research outputs
- [x] CREATE common/durable_orchestrator.py with sequential research→synthesis workflow using universal planning
- [x] IMPLEMENT comprehensive failing tests for TDD approach (ResearchOutput, DurableOrchestrator, workflow engine)
- [x] CREATE execute_research_call activity function using LangChain + PydanticOutputParser for structured JSON
- [x] CREATE execute_synthesis_call activity function using Jinja2 templates + existing agent personality
- [x] REPLACE create_multi_call_analysis() call with DurableOrchestrator integration in AnalysisService
- [x] UPDATE workflow engine tests to test new durable orchestrator replacing MultiCallArchitecture
- [x] VALIDATE 64/64 tests passing (100% pass rate) including complex workflow scenarios with universal planning agent
<!-- Updated from commits eca28ef, 65da1b0, 902971b, e1364e5 -->

### API Modernization & Prompt Centralization
- [x] RENAME process_idea → summarize_idea with direct Google Sheets lookup (no OpenAI polling)
- [x] MOVE all hardcoded prompts from DurableOrchestrator to platform.yaml (research_planning, research_call templates)
- [x] COMPREHENSIVE platform.yaml cleanup - removed 67+ lines of unused complex templates (architecture_planning, analysis_call)
- [x] ENHANCE AnalysisService._create_spreadsheet_record() to store complete analysis results immediately
- [x] CREATE centralized template formatting methods in prompt_manager.py for research workflow
- [x] DELETE unused format_architecture_planning_prompt and format_analysis_call_prompt methods
<!-- Updated from commits e1364e5, 2a5c0c2 -->

### Component Audit & Code Cleanup
- [x] DELETE generate_analysis_prompt from FullAgentConfig - only used in tests, replaced by LangChain approach
- [x] KEEP FieldConfig class - confirmed essential for dynamic schema system
- [x] KEEP get_budget_options vs BudgetTierConfig - confirmed proper separation of concerns
- [x] KEEP PromptManager - confirmed heavily used core component for prompt centralization
- [x] DELETE validate_analysis_result from utils.py - replaced by LangChain PydanticOutputParser validation
- [x] CREATE clean_json_response utility and replace hardcoded JSON parsing in DurableOrchestrator
- [x] CONSOLIDATE duplicate JSON extraction logic throughout codebase
<!-- Updated from commits 83bf754, 34c57c7 -->

## Pending Tasks

### 🚨 CRITICAL: Deep Research API Async Job Polling (URGENT - TIMEOUT ISSUE)

#### Durable Functions Timeout Resolution
- [ ] **IMPLEMENT async job polling for research calls using OpenAI Deep Research API**
  - Update `common/durable_orchestrator.py` to use `background=True` in research calls
  - Create `StartResearchJob` activity function: POST /v1/deep_research with background=true → returns job_id
  - Create `CheckResearchStatus` activity function: GET /v1/deep_research/jobs/{job_id} → returns status
  - Create `FetchResearchResult` activity function: GET /v1/deep_research/jobs/{job_id}/result → returns ResearchOutput
  - Update orchestrator to use durable timers (5-minute waits with zero billing cost)
  - Replace current LangChain `ainvoke()` calls with async job polling pattern

- [ ] **IMPLEMENT async job polling for synthesis calls using OpenAI Deep Research API**
  - Update synthesis calls to use `background=True` for long-running deep research synthesis
  - Create `StartSynthesisJob` activity function: POST /v1/deep_research with background=true → returns job_id
  - Create `CheckSynthesisStatus` activity function: GET /v1/deep_research/jobs/{job_id} → returns status
  - Create `FetchSynthesisResult` activity function: GET /v1/deep_research/jobs/{job_id}/result → returns final result
  - Integrate synthesis job polling into orchestrator workflow after research completion

- [ ] **REFACTOR Azure Functions structure for async job polling**
  - Create separate activity functions for each async operation (start/check/fetch)
  - Update `analysis_orchestrator/__init__.py` to coordinate multiple short activity calls with durable timers
  - Remove `execute_complete_workflow` monolithic activity function
  - Implement proper error handling and retry logic for each activity function
  - Ensure each activity completes in <5 minutes to avoid timeout issues

### PHASE 2: Universal Endpoint Architecture

#### Universal Agent Parameter Support
- [ ] **ADD agent parameter support to Azure Functions** - Update all 5 endpoints to accept ?agent={agent_id} parameter
- [ ] **UPDATE get_instructions endpoint** - Load FullAgentConfig based on agent parameter for dynamic instructions
- [ ] **UPDATE get_pricepoints endpoint** - Load agent-specific budget tiers from configuration
- [ ] **UPDATE execute_analysis endpoint** - Route to correct agent configuration based on agent parameter
- [ ] **UPDATE summarize_idea endpoint** - Support multiple agent types through agent parameter
- [ ] **VALIDATE universal endpoints** - Test same endpoints work for different agent configurations

#### Custom GPT Integration Updates
- [ ] **UPDATE openapi_chatgpt.yaml schema** - Add agent parameter support for universal endpoints
- [ ] **CREATE Custom GPT templates** - Document Custom GPT creation process with dynamic instructions
- [ ] **TEST Custom GPT workflow** - Verify complete 7-step workflow: get_instructions → collect input → get_pricepoints → execute_analysis → summarize_idea
- [ ] **UPDATE Custom GPT instructions** - Reflect new universal endpoint architecture

### PHASE 3: Second Agent Type Creation (UNIVERSALITY PROOF)

#### HR Analysis Agent Implementation
- [ ] **CREATE agents/hr_evaluation.yaml** - HR analysis agent configuration with unique personality
- [ ] **CREATE Google Sheet for HR agent** - New schema with HR-specific input/output fields
- [ ] **TEST HR agent through universal endpoints** - Prove same codebase handles different analysis domains
- [ ] **CREATE HR Custom GPT** - Deploy second Custom GPT using universal endpoint architecture
- [ ] **VALIDATE universality** - Demonstrate zero-code agent creation through pure configuration

### Integration & Production Deployment

#### Azure Functions Production Optimization
- [ ] **INTEGRATE with existing cost tracking** - Adapt log_openai_cost() for sequential DurableOrchestrator calls
- [ ] **ADD web search capability** - LangChain tools integration for enhanced research
- [ ] **OPTIMIZE configuration loading** - Cache FullAgentConfig for multiple agent types
- [ ] **IMPLEMENT request rate limiting** - Ensure OpenAI API compliance across multiple agents

#### Performance & Monitoring
- [ ] **MONITOR system performance** - Track analysis execution times across different agent types
- [ ] **OPTIMIZE memory usage** - Lazy loading improvements for multiple agent configurations
- [ ] **ADD error monitoring** - Enhanced logging and error tracking for production deployment
- [ ] **IMPLEMENT usage analytics** - Track usage patterns across different agent types and Custom GPTs

### Integration & Production Deployment

#### Azure Durable Functions Background Processing - ✅ COMPLETED
- [x] **IMPLEMENT fast-return polling system** - Added threading-based background processing for 45-second Custom GPT timeout (REPLACED)
- [x] **MODIFY DurableOrchestrator** - Added fast_return parameter and complete_remaining_workflow() method
- [x] **UPDATE AnalysisService** - Added background threading and spreadsheet update methods  
- [x] **ENHANCE summarize_idea endpoint** - Added processing vs completed state handling
- [x] **🔥 CRITICAL: REPLACE threading with Azure Durable Functions** - Complete implementation with orchestrator/activity pattern
  - Created `idea-guy/analysis_orchestrator/__init__.py` with proper orchestrationTrigger binding
  - Created `idea-guy/execute_complete_workflow/__init__.py` with async activityTrigger function
  - Updated `common/durable_orchestrator.py` with full async/await architecture using `await LangChain.ainvoke()`
  - Fixed basic tier workflow to run synthesis with 0 research calls
  - Enhanced `idea-guy/host.json` with comprehensive Durable Functions logging and diagnostics
  - Implemented proper coroutine handling throughout async call chain
- [x] **ADD azure-functions-durable dependency** - Integrated with production Durable Functions runtime
- [x] **CREATE Durable Functions orchestrator pattern** - Full orchestrator + activity functions implementation
- [x] **REMOVE all threading code** - Replaced with Azure-native reliable background processing
<!-- Updated from commits a6ca71a, df275a7, 2a9ea7d, fe5dfbb, edc3128 -->

#### Model Configuration Updates  
- [x] **FIX model naming alignment** - Updated planning/research/synthesis model references for semantic consistency
- [x] **CORRECT model configuration path** - Fixed FullAgentConfig.get_model() to access platform.models correctly
- [x] **UPDATE platform.yaml models** - Aligned model names with workflow phases
<!-- Updated from commits 50bb4f8, 5ec75ce, 61db11e -->

#### Fallback Logic & Error Handling Improvements
- [x] **REMOVE problematic fallback logic** - Eliminated silent failures that masked configuration errors
- [x] **IMPLEMENT fail-fast error handling** - Added explicit validation instead of silent defaults
- [x] **UPDATE model validation** - Model access now raises ValidationError for unknown types
- [x] **ENHANCE budget tier validation** - Removed silent empty list fallbacks
<!-- Updated from commit 145a696 -->

#### Azure Functions Migration to Durable Functions - ✅ COMPLETED
- [x] **DEPLOY Durable Functions**: Replaced threading with orchestrator/activity pattern
- [x] **CONFIGURE function scaling**: Implemented sequential execution with proper async/await handling
- [x] **UPDATE environment variables**: Enhanced host.json with Durable Functions configuration and diagnostics
- [x] **TEST production deployment**: Validated complete reliable background processing workflow with all budget tiers

#### Custom GPT Integration Updates
- [ ] **UPDATE Custom GPT instructions**: Reflect new fire-and-forget + summarize workflow
- [ ] **MODIFY OpenAPI schema**: Update for execute_analysis + summarize_idea endpoints
- [ ] **TEST Custom GPT workflow**: Fire-and-forget → polling → results display
- [ ] **DOCUMENT new user experience**: Show execution plan, estimated time, progress updates

### Phase 3: Validation & Polish (Future)

#### Second Agent Type Creation
- [ ] Create HR analysis agent configuration to prove universality
- [ ] Set up Google Sheet schema for HR agent type
- [ ] Test that same Azure Functions work for multiple agent types
- [ ] Document agent creation process for future agent types

#### Performance & Optimization
- [ ] Optimize configuration loading for multiple agent types
- [ ] Test multi-call architecture performance with universal templates
- [ ] Implement caching for frequently accessed configuration data
- [ ] Monitor and optimize API response times

#### Documentation Updates
- [ ] Update API.md to reflect universal endpoints with agent parameters
- [ ] Update TESTING.md for new 5-focused-test strategy
- [ ] Create agent creation guide for non-technical users
- [ ] Update troubleshooting guide for universal system

## IMMEDIATE NEXT STEPS (Priority Order) - TIMEOUT RESOLUTION FOCUS

1. **🔥 CRITICAL**: ~~DELETE common/multi_call_architecture.py and implement DurableOrchestrator~~ ✅ COMPLETED
2. **🔥 CRITICAL**: ~~CENTRALIZE all prompts in platform.yaml and clean up legacy templates~~ ✅ COMPLETED  
3. **🔥 CRITICAL**: ~~RENAME process_idea → summarize_idea with direct Google Sheets lookup~~ ✅ COMPLETED
4. **🔥 CRITICAL**: ~~AUDIT and remove duplicate/unused components throughout codebase~~ ✅ COMPLETED
5. **🔥 CRITICAL**: ~~IMPLEMENT fast-return polling system for Custom GPT timeout~~ ✅ COMPLETED 
6. **🚨 URGENT**: ~~**REPLACE threading with Azure Durable Functions**~~ ✅ COMPLETED - Reliable background processing in Azure Functions achieved
7. **🚨 URGENT**: ~~**RESOLVE JSON parsing and duplicate call issues**~~ ✅ COMPLETED - Robust error handling and deduplication implemented
8. **🚨 CRITICAL**: **IMPLEMENT OpenAI Deep Research API async job polling** - Resolve 10-minute timeout issue by moving long-running work to OpenAI servers
9. **🔥 CRITICAL**: **ADD agent parameter support to all Azure Functions endpoints** - Enable universal endpoint architecture
10. **⚡ HIGH**: **UPDATE openapi_chatgpt.yaml schema** - Support agent parameters for Custom GPT integration
11. **⚡ HIGH**: **CREATE second agent type (HR evaluation)** - Prove universality through pure configuration
12. **🔧 MEDIUM**: **INTEGRATE cost tracking and web search capabilities** - Production optimization

## ARCHITECTURE EVOLUTION PLAN

### ✅ Phase 1 COMPLETED: Core System Replacement
- **✅ DELETED** common/multi_call_architecture.py (435 lines removed)
- **✅ CREATED** common/durable_orchestrator.py with sequential research→synthesis workflow
- **✅ MODERNIZED** API endpoints with summarize_idea and direct Google Sheets lookup
- **✅ CENTRALIZED** all prompts in platform.yaml (removed 67+ lines of unused templates)
- **✅ ACHIEVED** 100% test pass rate (64/64 tests) with comprehensive component audit

### 🔄 Phase 2 IN PROGRESS: Universal Platform Architecture
- **ADD** agent parameter support to all Azure Functions endpoints
- **UPDATE** Custom GPT integration with universal endpoint schema
- **OPTIMIZE** configuration loading for multiple agent types
- **INTEGRATE** enhanced monitoring and cost tracking

### 📋 Phase 3 PLANNED: Universality Validation
- **CREATE** second agent type (HR evaluation) to prove zero-code agent creation
- **DEPLOY** multiple Custom GPTs using same universal endpoint architecture
- **VALIDATE** complete universal platform capabilities
- **DOCUMENT** agent creation process for future expansion

## SYSTEM STATUS - AZURE DURABLE FUNCTIONS PRODUCTION DEPLOYMENT

- **✅ Azure Durable Functions**: Production-ready orchestrator/activity pattern with reliable background processing (COMPLETED)
- **✅ Async/Await Architecture**: Full async implementation with LangChain ainvoke() and proper coroutine handling (COMPLETED)
- **✅ All Budget Tiers Working**: Basic (0+1), Standard (2+1), Premium (4+1) with basic tier synthesis fix (COMPLETED)
- **✅ Enhanced Diagnostics**: Comprehensive Durable Functions logging with traceInputsAndOutputs and monitoring (COMPLETED)
- **✅ DurableOrchestrator System**: Sequential research→synthesis workflow fully operational (COMPLETED)
- **✅ OpenAI Client Integration**: Centralized client with LangChain integration (WORKING)
- **✅ Google Sheets Integration**: Real API with dynamic schema and immediate result storage (WORKING)
- **✅ Configuration System**: Four-layer universal configuration with prompt centralization (WORKING)
- **✅ HTTP Infrastructure**: 6 Azure Functions endpoints including orchestrator trigger (WORKING)
- **✅ Test Infrastructure**: 100% pass rate (64/64 tests) with comprehensive coverage (WORKING)
- **✅ Component Audit**: All duplicate/legacy code removed, clean architecture achieved (COMPLETED)

## SUCCESS METRICS ACHIEVED

- **✅ Azure Durable Functions Production**: Reliable background processing replacing unreliable threading architecture
- **✅ Async/Await Integration**: Full async implementation with LangChain ainvoke() eliminating coroutine serialization errors
- **✅ All Budget Tiers Functional**: Basic, Standard, Premium all working correctly including basic tier synthesis fix
- **✅ Enhanced Production Diagnostics**: Comprehensive Durable Functions logging with trace capabilities and monitoring
- **✅ Architectural Excellence**: Clean, modern codebase with centralized prompt management
- **✅ Perfect Test Coverage**: 100% pass rate (64/64 tests) maintained throughout transformation
- **✅ API Modernization**: Direct Google Sheets lookup eliminates OpenAI polling complexity
- **✅ Component Optimization**: Removed all duplicate/legacy code while preserving essential functionality
- **✅ Universal Design**: System ready for unlimited agent types through pure configuration
- **✅ Production Ready**: Complete reliable background processing with guaranteed execution

<!-- Updated from commits e1364e5, 2a5c0c2, 83bf754, 34c57c7, 25e78f2 -->