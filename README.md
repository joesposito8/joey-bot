# Joey-Bot: Universal AI Agent Platform

**A configurable, extensible platform for deploying intelligent AI agents through Azure Functions with dynamic multi-call analysis workflows.**

---

## 🎯 What is Joey-Bot?

Joey-Bot is a **Universal AI Agent Platform** that makes it easy to create and deploy specialized AI agents without writing custom code. Instead of building separate systems for different AI use cases, joey-bot provides a unified architecture where agents are defined through configuration files and can be deployed instantly.

### Current Implementation: Business Idea Evaluator
The platform currently powers a sophisticated **business idea evaluation agent** that provides VC-quality analysis of startup concepts with multiple budget tiers and intelligent multi-call workflows.

### Future Potential: Any AI Agent Type
The universal architecture can support any type of AI agent through simple configuration:
- **Technical Architecture Advisor** - System design recommendations
- **Market Research Analyst** - Competitive analysis and market sizing  
- **Legal Document Reviewer** - Contract analysis and risk assessment
- **Content Strategy Planner** - Editorial calendars and content optimization
- **Financial Analysis Agent** - Investment analysis and projections

---

## ✨ Key Features

### 🔧 **Universal Architecture**
- **Configuration-Driven**: Create new agents via YAML files + Google Sheets schema
- **No Code Required**: Deploy new agent types without writing custom logic
- **Dynamic Workflows**: Intelligent multi-call analysis strategies optimized per budget tier

### 🚀 **Production Ready**
- **Azure Functions**: Serverless HTTP endpoints with automatic scaling
- **Cost Protection**: Testing mode prevents accidental API charges during development
- **Multi-Call Intelligence**: Advanced planning algorithms optimize OpenAI usage
- **Google Sheets Integration**: Automatic data storage and schema management

### 💰 **Budget-Aware Analysis**
- **Basic Tier ($1)**: Quick analysis with 1 OpenAI call
- **Standard Tier ($3)**: Detailed analysis with 3 strategic calls  
- **Premium Tier ($5)**: Comprehensive analysis with 5 specialized calls

### 🧪 **Developer Friendly**  
- **Testing Mode**: Zero-cost development with mock responses
- **Comprehensive Documentation**: Architecture guides, API reference, troubleshooting
- **Clean Codebase**: Well-structured, maintainable, fully tested

---

## 🏗️ How It Works

### High-Level Architecture
```
HTTP Request → Azure Functions → Agent Configuration → Multi-Call Planner → OpenAI → Results → Google Sheets
```

### Agent Configuration System
```yaml
# agents/business_evaluation.yaml
agent_id: "business_evaluation"
name: "Business Idea Evaluator"
sheet_url: "https://docs.google.com/spreadsheets/d/YOUR_SHEET/edit"
starter_prompt: |
  You are a senior partner at a top-tier VC firm...
budget_tiers:
  - name: "basic"
    price: 1.00
    calls: 1
```

### Dynamic Schema (Google Sheets)
```
Row 1: | ID | Time | user input    | user input   | bot output     |
Row 2: | ID | Time | Business idea | What you'll  | How novel is   |
Row 3: | ID | Time | Idea_Overview | Deliverable  | Novelty_Rating |
```

The system automatically reads this schema and generates:
- User input validation
- API endpoint documentation  
- Analysis prompts
- Output formatting

---

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/joey-bot.git
cd joey-bot

# Install dependencies
pip install -r requirements.txt

# Enable safe testing mode (no API charges)
export TESTING_MODE=true
```

### 2. Test the API
```bash
# Start Azure Functions locally
cd idea-guy && func start --python

# Test the business evaluator
curl "http://localhost:7071/api/get_instructions"
```

### 3. Try the Complete Workflow
```python
import requests

# Get analysis options
response = requests.post("http://localhost:7071/api/get_pricepoints", 
    json={"user_input": {
        "Idea_Overview": "AI-powered meal planning app",
        "Deliverable": "Mobile app with personalized recipes", 
        "Motivation": "Help people eat healthier"
    }})

# Start analysis
job = requests.post("http://localhost:7071/api/execute_analysis",
    json={
        "user_input": response.json()["user_input"],
        "budget_tier": "standard"
    })

# Check results (immediate in testing mode)
result = requests.get(f"http://localhost:7071/api/process_idea?id={job.json()['job_id']}")
print(f"Analysis: {result.json()['Analysis_Summary']}")
```

---

## 🎨 Creating New Agent Types

### 1. Define Your Agent
```yaml
# agents/tech_advisor.yaml
agent_id: "tech_advisor"
name: "Technical Architecture Advisor"
sheet_url: "https://docs.google.com/spreadsheets/d/YOUR_NEW_SHEET"
starter_prompt: |
  You are a senior software architect with 15 years of experience...
budget_tiers:
  - name: "quick"
    price: 0.50
    calls: 1
  - name: "detailed" 
    price: 2.00
    calls: 4
```

### 2. Set Up Google Sheet Schema
```
Row 1: | ID | Time | user input      | user input        | bot output         |
Row 2: | ID | Time | System requirements | Scale needs    | Recommended stack  |
Row 3: | ID | Time | Requirements    | Scale_Level       | Tech_Stack         |
```

### 3. Deploy
The system automatically discovers and supports your new agent type. No code changes required!

---

## 📊 Current Agent: Business Evaluator

The platform's first agent is a sophisticated business idea evaluator that provides VC-quality analysis:

### Input Fields
- **Idea Overview**: Brief description of the business concept
- **Deliverable**: What specific product or service will be built  
- **Motivation**: Why this idea should exist and what problem it solves

### Analysis Output
- **Novelty Rating**: How unique and innovative the idea is (1-10)
- **Feasibility Rating**: How realistic implementation would be (1-10) 
- **Effort Rating**: Required resources and complexity (1-10)
- **Impact Rating**: Potential market impact and value (1-10)
- **Risk Rating**: Business and execution risks (1-10)
- **Overall Rating**: Comprehensive evaluation (1-10)
- **Analysis Summary**: Detailed written assessment
- **Potential Improvements**: Specific recommendations for enhancement

### Multi-Call Intelligence
The system uses different analysis strategies based on budget tier:
- **Basic**: Single comprehensive call covering all dimensions
- **Standard**: Market research → Competitive analysis → Synthesis
- **Premium**: Market sizing → Technical feasibility → Competition → Risk assessment → Strategic synthesis

---

## 🛠️ Technical Architecture

### Core Components
- **`common/agent_service.py`** - Main orchestration service
- **`common/multi_call_architecture.py`** - Intelligent workflow planning
- **`common/config/`** - Dynamic configuration system
- **`idea-guy/`** - Azure Functions HTTP endpoints

### Extension Points
- **Agent Definitions**: YAML configuration files
- **Schema Management**: Google Sheets rows 1-3
- **Budget Tiers**: Configurable pricing and call strategies
- **Workflow Templates**: Reusable analysis patterns

---

## 📚 Documentation

For detailed technical information:

- **[CLAUDE.md](CLAUDE.md)** - Documentation directory and quick reference
- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** - Technical implementation details
- **[API Reference](docs/API.md)** - Complete endpoint documentation
- **[Testing Guide](docs/TESTING.md)** - Development and testing practices
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🚧 Development Status

### ✅ Current Features
- Universal AI Agent Platform architecture
- Business idea evaluation agent (production ready)
- Azure Functions deployment 
- Multi-call intelligent workflows
- Budget tier management
- Cost protection and testing mode
- Comprehensive documentation

### 🎯 Potential Extensions
- Multiple agent types running concurrently
- Agent marketplace and discovery system
- Advanced workflow patterns (loops, conditionals)
- Integration with external APIs and tools
- GUI for agent creation and management
- Enterprise features (teams, permissions, analytics)

---

## 🤝 Contributing

1. **Enable Testing Mode**: Always develop with `TESTING_MODE=true` to prevent API charges
2. **Follow Architecture**: Use the configuration system for new agents, not hardcoded logic  
3. **Test Thoroughly**: Run the comprehensive test suite before submitting changes
4. **Update Documentation**: Keep docs current with any architectural changes

### Development Workflow
```bash
# Safe development setup
export TESTING_MODE=true
python -m pytest tests/ -v

# Test Azure Functions locally
cd idea-guy && func start --python

# Create new agent type
cp agents/business_evaluation.yaml agents/your_agent.yaml
# Edit configuration and Google Sheet schema
# System automatically supports new agent!
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🌟 Why Joey-Bot?

Traditional AI agent development requires:
- ❌ Custom codebases for each agent type
- ❌ Separate infrastructure and deployment
- ❌ Complex integration and maintenance
- ❌ Duplicate error handling and testing

Joey-Bot provides:
- ✅ **Universal platform** - One system, infinite agent types
- ✅ **Configuration-driven** - No code required for new agents
- ✅ **Production-ready** - Robust, tested, scalable infrastructure
- ✅ **Cost-efficient** - Intelligent multi-call optimization
- ✅ **Developer-friendly** - Comprehensive testing and documentation

**Build AI agents in minutes, not months.**