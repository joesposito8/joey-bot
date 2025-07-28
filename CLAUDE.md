# Joey-Bot Project Documentation Directory

**Last Updated**: 2025-01-28  
**Status**: Universal AI Agent Platform with Universal Prompt Configuration System

## Quick Reference

Joey-Bot is a Universal AI Agent Platform that provides AI-powered analysis through Azure Functions with Google Sheets storage and OpenAI multi-call architecture. **NEW**: Features universal prompt templates that work with any agent type while allowing agent-specific customization.

## 📚 Documentation Structure

### Core Documentation (4 Essential Documents)

1. **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** 🏗️
   - **Purpose**: Understand how the system works internally
   - **Contains**: Semi-pseudocode system flow, component relationships, data flow
   - **Use When**: You need to modify code, debug issues, or understand the technical implementation

2. **[API Reference](docs/API.md)** 🔌
   - **Purpose**: Learn how to use the system's endpoints
   - **Contains**: Complete API documentation, request/response examples, usage patterns
   - **Use When**: Integrating with joey-bot, building clients, or testing endpoints

3. **[Testing Guide](docs/TESTING.md)** 🧪
   - **Purpose**: Test safely without incurring API charges
   - **Contains**: Testing mode setup, test suites, development workflow, cost protection
   - **Use When**: Developing, testing, or debugging the system

4. **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** 🔧
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

### Current Architecture
- **Universal AI Agent Platform** - Configurable for multiple agent types
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