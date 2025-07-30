# Joey-Bot Project Documentation Directory

**Last Updated**: 2025-01-28  
**Status**: RUTHLESS REDESIGN - Documentation Complete, Implementation Ready

## Quick Reference

Joey-Bot is transforming into a **Universal AI Agent Platform** where ANY type of analysis (business, HR, legal, medical, etc.) runs through the same codebase via pure configuration. **NEW**: Complete ruthless redesign eliminates hardcoded business logic and achieves true universality.

## 📚 Documentation Structure

### Core Documentation (5 Essential Documents)

1. **[Universal System Design](docs/UNIVERSAL_SYSTEM_DESIGN.md)** 🎯
   - **Purpose**: Complete ruthless redesign specification
   - **Contains**: Configuration-driven architecture, component elimination, implementation strategy
   - **Use When**: Understanding the new universal platform vision

2. **[Implementation Plan](IMPLEMENTATION_PLAN.md)** 📋
   - **Purpose**: Step-by-step transformation roadmap
   - **Contains**: Documentation → Tests → System rebuild strategy
   - **Use When**: Executing the universal platform implementation

3. **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** 🏗️
   - **Purpose**: **UPDATED** - Universal system architecture 
   - **Contains**: UniversalAgentEngine, configuration layers, universal endpoints
   - **Use When**: Understanding how the universal system works internally

4. **[API Reference](docs/API.md)** 🔌
   - **Purpose**: Learn how to use the system's endpoints
   - **Contains**: Complete API documentation, request/response examples, usage patterns
   - **Use When**: Integrating with joey-bot, building clients, or testing endpoints

5. **[Testing Guide](docs/TESTING.md)** 🧪
   - **Purpose**: **TO UPDATE** - New 5-focused-test strategy
   - **Contains**: Universal testing approach, configuration testing, cost protection
   - **Use When**: Testing the universal platform

6. **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** 🔧
   - **Purpose**: Solve common problems and debug issues
   - **Contains**: Common issues, diagnostic tools, error solutions, performance tips
   - **Use When**: Something isn't working or you need to debug problems

## 🚀 Quick Start

### For Users (API Integration)
1. Start with **[API Reference](docs/API.md)** to understand endpoints
2. Use **[Testing Guide](docs/TESTING.md)** to set up safe development environment
3. Reference **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** if issues arise

### For Developers (Code Changes)
1. Read **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** to understand the codebase
2. Use **[Testing Guide](docs/TESTING.md)** for safe development practices
3. Reference **[API Reference](docs/API.md)** to understand expected behavior
4. Use **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** for debugging

## 🎯 Key System Facts

### Current Status
- **RUTHLESS REDESIGN COMPLETE** - Documentation and plan ready for implementation
- **Universal Configuration System** - Platform + Agent + Dynamic schema layers
- **5 Focused Tests** - Replacing 34 overlapping tests with clear success criteria  
- **Zero-Code Agent Creation** - New agent types via YAML + Google Sheet only
- **Business Evaluator** - First agent implementation (currently deployed)
- **Dynamic Configuration** - Agents defined by YAML + Google Sheets schema
- **Azure Functions** - 5 HTTP endpoints for complete analysis workflow
- **Cost Protection** - Testing mode prevents accidental API charges

### Main Components
```
Azure Functions → AnalysisService → MultiCallArchitecture → OpenAI → Google Sheets
```

### Configuration Files
- **`agents/business_evaluation.yaml`** - Agent configuration
- **Google Sheets rows 1-3** - Dynamic schema definition
- **`idea-guy/local.settings.json`** - Environment variables

### Testing
```bash
export TESTING_MODE=true  # Prevents API charges
python -m pytest tests/ -v
```

## 📋 Important Commands

### Development
```bash
# Safe testing (no API charges)
export TESTING_MODE=true
python -m pytest tests/unit/ -v

# Run Azure Functions locally  
cd idea-guy && func start --python

# Check system health
python -c "from common.http_utils import is_testing_mode; print(f'Testing mode: {is_testing_mode()}')"
```

### Production
```bash
# Required environment variables
export OPENAI_API_KEY=sk-your-key
export IDEA_GUY_SHEET_ID=your-sheet-id
export GOOGLE_SHEETS_KEY_PATH=path/to/credentials.json

# Disable testing mode for production
unset TESTING_MODE
```

## 🔍 Finding Information

### "How do I...?"
- **Use the API?** → [API Reference](docs/API.md)
- **Set up testing?** → [Testing Guide](docs/TESTING.md)
- **Understand the code?** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **Fix an error?** → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

### "What does X do?"
- **System components** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **API endpoints** → [API Reference](docs/API.md)
- **Error messages** → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

### "Why isn't X working?"
- **Start here** → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **Check configuration** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **Verify API usage** → [API Reference](docs/API.md)
- **Test safely** → [Testing Guide](docs/TESTING.md)

## 🏗️ Project Structure

```
joey-bot/
├── docs/                          # 📚 All documentation
│   ├── SYSTEM_ARCHITECTURE.md    # 🏗️ Technical implementation
│   ├── API.md                     # 🔌 Endpoint reference  
│   ├── TESTING.md                 # 🧪 Safe development
│   └── TROUBLESHOOTING.md         # 🔧 Problem solving
├── agents/                        # ⚙️ Agent configurations
│   └── business_evaluation.yaml  # Current business evaluator config
├── common/                        # 🧠 Core business logic
│   ├── agent_service.py          # Main orchestration service
│   ├── multi_call_architecture.py # Multi-call analysis execution
│   ├── config/                   # Dynamic configuration system
│   └── ...                       # Supporting services
├── idea-guy/                      # 🌐 Azure Functions (HTTP endpoints)
│   ├── execute_analysis/         # Start analysis
│   ├── process_idea/             # Get results
│   ├── get_instructions/         # Get user instructions
│   └── ...                       # Other endpoints
└── tests/                         # 🧪 Test suites
    ├── unit/                     # Unit tests
    └── integration/              # Integration tests
```

## 🎯 Development Workflow

1. **Always start with testing mode**: `export TESTING_MODE=true`
2. **Read relevant docs** for your task
3. **Make changes** using the architecture guide
4. **Test thoroughly** using the testing guide
5. **Debug issues** using the troubleshooting guide
6. **Verify API behavior** using the API reference

## ⚠️ Important Notes

- **Always use testing mode** during development to prevent API charges
- **Never commit secrets** - all keys should be in environment variables
- **Follow the system architecture** when making code changes
- **Test thoroughly** before deploying to production
- **Check troubleshooting guide** before asking for help

---

**Need help?** Start with the relevant documentation above. Each document is designed to be self-contained and practical for specific use cases.