# Joey-Bot Project Documentation Directory

**Last Updated**: 2025-01-28  
**Status**: RUTHLESS REDESIGN - Documentation Complete, Implementation Ready

## Quick Reference

Joey-Bot is transforming into a **Universal AI Agent Platform** where ANY type of analysis (business, HR, legal, medical, etc.) runs through the same codebase via pure configuration. **NEW**: Complete ruthless redesign eliminates hardcoded business logic and achieves true universality.

## 📚 Documentation Structure

### Core Documentation (3 Essential Documents)

1. **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** 🏗️
   - **Purpose**: Complete technical implementation guide with exact file locations
   - **Contains**: Current vs planned architecture, component tracing, universal system design
   - **Use When**: Understanding how the system works, finding code locations, making changes

2. **[Task List](docs/TASKLIST.md)** 📋
   - **Purpose**: Current implementation roadmap with actionable tasks and priorities
   - **Contains**: Completed work, pending tasks by phase, dependencies, risk mitigation
   - **Use When**: Planning work, tracking progress, understanding what needs to be done

3. **[Developer Guide](docs/DEVELOPER_GUIDE.md)** 🛠️
   - **Purpose**: Everything developers need: API, testing, troubleshooting in one place
   - **Contains**: API reference, testing strategies, debugging, development workflow
   - **Use When**: Developing, testing, debugging, or integrating with joey-bot

## 🚀 Quick Start

### For Users (API Integration)
1. Start with **[Developer Guide](docs/DEVELOPER_GUIDE.md)** to understand endpoints and testing
2. Use testing mode setup to prevent API charges
3. Follow the complete workflow: Instructions → Price Points → Execute → Poll Results

### For Developers (Code Changes)
1. Read **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** to understand the codebase structure
2. Use **[Developer Guide](docs/DEVELOPER_GUIDE.md)** for testing, debugging, and development workflow
3. Check **[Task List](docs/TASKLIST.md)** for current priorities and implementation roadmap
4. Follow **[Project Vision](PROJECT_VISION.md)** for long-term goals and context

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
python -m pytest tests/ -v

# Run Azure Functions locally  
cd idea-guy && func start --python

# Check system health
python -c "from common.http_utils import is_testing_mode; print(f'Testing mode: {is_testing_mode()}')"

# Test specific components
python -m pytest tests/test_platform_config.py -v
python -m pytest tests/test_dynamic_configuration.py -v
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
- **Use the API?** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - API Reference section
- **Set up testing?** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - Testing Guide section
- **Understand the code?** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **Fix an error?** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - Troubleshooting section

### "What does X do?"
- **System components** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **API endpoints** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - API Reference
- **File locations** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md) - Complete File Mapping

### "Why isn't X working?"
- **Start here** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - Troubleshooting Guide
- **Check configuration** → [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- **Development setup** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - Quick Start
- **Test safely** → [Developer Guide](docs/DEVELOPER_GUIDE.md) - Testing Mode

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