# Project Vision

## Mission & Goals

**Primary Mission**: Transform Joey-Bot into a Universal AI Agent Platform where ANY type of analysis (business, HR, legal, medical, technical, etc.) can be deployed through pure configuration, with each agent type accessed via its own dedicated Custom GPT that orchestrates the complete analysis workflow.

**Core Goals**:
- **Zero-Code Agent Creation**: Adding new agent types requires only YAML configuration + Google Sheets schema + Custom GPT setup
- **One Custom GPT per Agent**: Each agent type gets its own Custom GPT with dynamic instructions fetched from `get_instructions` endpoint
- **Universal Architecture**: Single codebase handles all analysis domains through template-driven approach
- **Production Scalability**: Robust Azure Functions infrastructure with intelligent multi-call workflows
- **Cost-Effective Intelligence**: Budget-tiered analysis ($1/$3/$5) with optimized OpenAI usage
- **Developer Experience**: Simple, maintainable system with focused testing and clear documentation

**Success Metrics**:
- Create new agent type configuration in under 30 minutes (YAML + Google Sheet + Azure endpoints)
- Deploy Custom GPT manually in under 10 minutes using OpenAI interface + openapi_chatgpt.yaml schema
- Single platform.yaml change affects all agent types universally
- 5 focused tests replace 34 overlapping tests
- Universal endpoint architecture supports multiple agent types (via agent parameters or separate endpoints)

## Scope & Non-Goals

### In Scope
- **Universal Configuration System**: Platform + Agent + Dynamic schema layers
- **Custom GPT Architecture**: One Custom GPT per agent type with dynamic instruction fetching
- **OpenAPI Integration**: Custom GPTs configured with openapi_chatgpt.yaml schema for endpoint calling
- **Multi-Call Intelligence**: Smart workflow planning for 1/3/5 call budget tiers
- **Current Business Evaluator**: Maintain production functionality during transition
- **Azure Functions Scaling**: Support multiple agent types (via agent parameters or dedicated endpoint sets)
- **Google Sheets Integration**: Dynamic schema definition and data storage per agent type
- **Cost Protection**: Testing mode prevents accidental API charges
- **Comprehensive Documentation**: Architecture, API, testing, troubleshooting guides

### Non-Goals
- **Backwards Compatibility**: Ruthless redesign eliminates legacy hardcoded logic
- **GUI Agent Builder**: Command-line/file-based configuration only
- **Real-time Analysis**: Async workflow with job IDs, not synchronous responses
- **Multi-Tenancy**: Single-tenant system focused on core universality
- **Advanced Workflow Patterns**: No loops, conditionals, or complex orchestration
- **Custom Model Training**: OpenAI API integration only, no model fine-tuning

## Key Milestones

### Phase 1: Universal Foundation (Week 1) ✅ COMPLETE
- [x] **Documentation Complete**: Universal system design, implementation plan, architecture docs
- [x] **Current System Analysis**: Understanding existing business evaluator and Azure Functions
- [x] **Configuration Strategy**: Three-layer system (Platform → Agent → Dynamic)

### Phase 2: Core Implementation (Week 2) 🔄 IN PROGRESS
- [x] **Create `platform.yaml`**: Universal configuration for all agents
- [x] **Enhanced AnalysisService**: Universal agent orchestration (replaced UniversalAgentEngine concept)
- [ ] **Update Azure Functions**: Add agent parameter support for universal endpoints
- [ ] **Custom GPT Integration**: Update openapi_chatgpt.yaml for universal agent support
- [x] **Migrate Business Evaluator**: Convert to new universal format
- [x] **5 Focused Tests**: Replace 34 overlapping tests with clear success criteria

### Phase 3: Validation & Polish (Week 3)
- [ ] **End-to-End Testing**: Verify complete 7-step Custom GPT workflow works universally
- [ ] **Second Agent Type**: Create HR/Legal agent with new Custom GPT to prove universality
- [ ] **Custom GPT Templates**: Document Custom GPT creation process and OpenAPI schema usage
- [ ] **Performance Optimization**: Ensure multi-call architecture scales across multiple Custom GPTs
- [ ] **Production Deployment**: Deploy universal system to Azure with Custom GPT integration
- [ ] **Documentation Updates**: API reference, Custom GPT setup guide, troubleshooting, examples

### Phase 4: Platform Maturity (Month 2)
- [ ] **Agent Marketplace**: Easy discovery and sharing of agent configurations
- [ ] **Advanced Templates**: Reusable workflow patterns for common analysis types
- [ ] **Monitoring & Analytics**: Usage tracking, cost optimization, performance metrics
- [ ] **Enterprise Features**: Teams, permissions, audit logs

## Stakeholder Context

### Primary Users
- **End Users**: Interact with Custom GPTs for specific analysis needs (business evaluation, HR analysis, etc.)
- **AI Agent Creators**: Deploy new analysis types as Custom GPTs without programming
- **Business Analysts**: Use Business Evaluation Custom GPT for VC-quality idea evaluation
- **Domain Experts**: HR, legal, medical professionals using specialized Custom GPTs for analysis
- **Developers**: Platform maintainers and integrators building on joey-bot infrastructure

### User Needs
- **Conversational Interface**: Natural language interaction through Custom GPTs
- **Speed**: New agent types deployed as Custom GPTs in minutes, not days
- **Quality**: Professional-grade analysis with cited sources and detailed rationales  
- **Cost Control**: Predictable pricing with testing mode for safe development
- **Flexibility**: Customizable input/output schemas without code changes
- **Reliability**: Production-ready infrastructure with proper error handling
- **Seamless Experience**: Custom GPT handles all API orchestration transparently

### Technical Stakeholders
- **Platform Team**: Maintains universal engine and Azure Functions infrastructure
- **Agent Creators**: Configure new analysis types through YAML, Google Sheets, and Custom GPT deployment
- **Custom GPT Developers**: Create and configure Custom GPTs using dynamic instructions from joey-bot
- **API Consumers**: Integrate with joey-bot through clean HTTP endpoints (primarily Custom GPTs)
- **System Administrators**: Monitor costs, performance, and system health

### Success Criteria by Stakeholder
- **End Users**: "The Custom GPT understood my request and delivered professional analysis seamlessly"
- **Agent Creators**: "I created a legal document reviewer Custom GPT in 20 minutes"
- **Business Users**: "The analysis quality matches expensive consulting reports"  
- **Custom GPT Developers**: "The dynamic instructions made deployment effortless"
- **Developers**: "The system is simple to understand and test"
- **Operations**: "Costs are predictable and scaling is automatic"

### Current Status Context
Joey-Bot is transitioning from a hardcoded business evaluation tool to a truly universal platform accessed through dedicated Custom GPTs. The architecture is proven, documentation is complete, and implementation is ready to begin. The ruthless redesign will eliminate technical debt while dramatically expanding capabilities.

**Key Architectural Pattern**: Each agent type becomes its own Custom GPT that:
1. Starts with minimal prompt: "call get_instructions to understand what to do"
2. Dynamically fetches agent personality/behavior from `get_instructions` endpoint
3. Uses openapi_chatgpt.yaml schema to call Azure Functions endpoints
4. Orchestrates complete 7-step analysis workflow:
   - Get instructions → Collect user input → Show price options → User selects tier → Execute analysis → Get results → Present results
5. Stores results in agent-specific Google Sheet

**Scaling Requirements**: Each new agent type requires:
- New agent YAML configuration
- New Google Sheet with custom schema
- New Azure Functions endpoints (or universal endpoints with agent parameters)
- New Custom GPT manually created in OpenAI interface

**Key Design Decision**: Prioritize universality over backwards compatibility to achieve the vision of "any agent type through configuration alone, accessible via dedicated Custom GPTs."