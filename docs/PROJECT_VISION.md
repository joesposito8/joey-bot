# Project Vision

## Mission & Goals

**Primary Mission**: Transform Joey-Bot into a Universal AI Agent Platform where ANY type of analysis (business, HR, legal, medical, technical, etc.) can be deployed through pure configuration, not code.

**Core Goals**:
- **Zero-Code Agent Creation**: Adding new agent types requires only YAML configuration + Google Sheets schema
- **Universal Architecture**: Single codebase handles all analysis domains through template-driven approach
- **Production Scalability**: Robust Azure Functions infrastructure with intelligent multi-call workflows
- **Cost-Effective Intelligence**: Budget-tiered analysis ($1/$3/$5) with optimized OpenAI usage
- **Developer Experience**: Simple, maintainable system with focused testing and clear documentation

**Success Metrics**:
- Create new agent type in under 30 minutes (YAML + Google Sheet only)
- Single platform.yaml change affects all agent types universally
- 5 focused tests replace 34 overlapping tests
- Same Azure Functions endpoints work for any agent type

## Scope & Non-Goals

### In Scope
- **Universal Configuration System**: Platform + Agent + Dynamic schema layers
- **Multi-Call Intelligence**: Smart workflow planning for 1/3/5 call budget tiers
- **Current Business Evaluator**: Maintain production functionality during transition
- **Azure Functions API**: Keep existing 5-endpoint structure but make universal
- **Google Sheets Integration**: Dynamic schema definition and data storage
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
- [ ] **Create `platform.yaml`**: Universal configuration for all agents
- [ ] **Build UniversalAgentEngine**: Single engine replacing agent_service.py
- [ ] **Update Azure Functions**: Make endpoints work for any agent type
- [ ] **Migrate Business Evaluator**: Convert to new universal format
- [ ] **5 Focused Tests**: Replace 34 overlapping tests with clear success criteria

### Phase 3: Validation & Polish (Week 3)
- [ ] **End-to-End Testing**: Verify complete workflow works universally
- [ ] **Second Agent Type**: Create HR/Legal agent to prove universality
- [ ] **Performance Optimization**: Ensure multi-call architecture scales
- [ ] **Production Deployment**: Deploy universal system to Azure
- [ ] **Documentation Updates**: API reference, troubleshooting, examples

### Phase 4: Platform Maturity (Month 2)
- [ ] **Agent Marketplace**: Easy discovery and sharing of agent configurations
- [ ] **Advanced Templates**: Reusable workflow patterns for common analysis types
- [ ] **Monitoring & Analytics**: Usage tracking, cost optimization, performance metrics
- [ ] **Enterprise Features**: Teams, permissions, audit logs

## Stakeholder Context

### Primary Users
- **AI Agent Creators**: Need to deploy new analysis types without programming
- **Business Analysts**: Require VC-quality business idea evaluation (current user base)
- **Domain Experts**: HR, legal, medical professionals wanting AI-powered analysis tools
- **Developers**: Platform maintainers and integrators building on joey-bot

### User Needs
- **Speed**: New agent types deployed in minutes, not days
- **Quality**: Professional-grade analysis with cited sources and detailed rationales  
- **Cost Control**: Predictable pricing with testing mode for safe development
- **Flexibility**: Customizable input/output schemas without code changes
- **Reliability**: Production-ready infrastructure with proper error handling

### Technical Stakeholders
- **Platform Team**: Maintains universal engine and Azure Functions infrastructure
- **Agent Creators**: Configure new analysis types through YAML and Google Sheets
- **API Consumers**: Integrate with joey-bot through clean HTTP endpoints
- **System Administrators**: Monitor costs, performance, and system health

### Success Criteria by Stakeholder
- **Agent Creators**: "I created a legal document reviewer in 20 minutes"
- **Business Users**: "The analysis quality matches expensive consulting reports"  
- **Developers**: "The system is simple to understand and test"
- **Operations**: "Costs are predictable and scaling is automatic"

### Current Status Context
Joey-Bot is transitioning from a hardcoded business evaluation tool to a truly universal platform. The architecture is proven, documentation is complete, and implementation is ready to begin. The ruthless redesign will eliminate technical debt while dramatically expanding capabilities.

**Key Decision**: Prioritize universality over backwards compatibility to achieve the vision of "any agent type through configuration alone."