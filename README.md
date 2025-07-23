# Joey Bot - Extensible Business Analysis Agent

An Azure Function App that provides extensible business idea evaluation with budget-aware analysis tiers and ChatGPT bot integration.

## 🚀 Quick Start

### Prerequisites
- Azure Functions Core Tools
- Python 3.10+
- Google Sheets API credentials
- OpenAI API key

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
IDEA_GUY_SHEET_ID=your_google_sheets_id
GOOGLE_SHEETS_KEY_PATH=path/to/service_account.json
TESTING_MODE=false  # Set to 'true' for development/testing
```

### Installation
```bash
pip install -r requirements.txt
func start  # Run locally
```

## 📋 API Endpoints

### ChatGPT Bot Workflow
1. **GET `/api/get_instructions`** - Get bot workflow instructions
2. **POST `/api/get_pricepoints`** - Get budget options ($0.20, $1.00, $2.50)
3. **POST `/api/execute_analysis`** - Start analysis with selected tier
4. **GET `/api/process_idea?id={job_id}`** - Poll for results

### Legacy Endpoints
- **GET `/api/read_sheet`** - Read spreadsheet data
- **GET `/api/process_idea`** - Process analysis results

## 🎯 Budget Tiers

| Tier | Cost | Model | Features |
|------|------|-------|----------|
| Basic | $0.20 | gpt-4o-mini | Quick ratings & rationales |
| Standard | $1.00 | o1-mini | Market research & analysis |
| Premium | $2.50 | o4-mini-deep-research | Comprehensive research |

## 🧪 Testing Mode

**Enable testing mode to prevent API charges:**
```bash
export TESTING_MODE=true
```

**Features:**
- Creates mock jobs with fake results
- No OpenAI API calls or spreadsheet modifications
- All responses include `"testing_mode": true`
- Perfect for development and CI/CD

## 🔧 Development

### Running Tests
```bash
python test_simple_endpoint.py    # Core functionality tests
python test_chatgpt_flow.py       # End-to-end workflow tests
```

### Adding New Agent Types
1. Create new tier configuration in `common/budget_config.py`
2. Add agent schema in `common/agent/`
3. Register with `BudgetConfigManager.add_tier()`

## 📊 Monitoring & Debugging

### Error Handling
All errors include:
- Clear user-facing messages for ChatGPT bot
- Detailed logging context for debugging
- Error type classification
- Actionable suggestions

### Log Analysis
```bash
# Production logs include full context:
{
  "error_type": "validation_error",
  "endpoint": "execute_analysis", 
  "budget_tier": "premium",
  "exception_type": "ValidationError",
  "testing_mode": false
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ChatGPT Bot   │────│  Azure Functions │────│   OpenAI API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │  Google Sheets   │
                       └──────────────────┘
```

### Components
- **AnalysisService**: Core business logic with lazy initialization
- **BudgetConfigManager**: Extensible tier configuration system
- **HTTP Utils**: Standardized error handling and testing protection
- **Agent Framework**: Schema validation and workflow management

## 📚 Documentation

- [API Reference](docs/API.md)
- [ChatGPT Integration](docs/CHATGPT_INTEGRATION.md)
- [Testing Guide](docs/TESTING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Set `TESTING_MODE=true` for development
2. Run tests before submitting PRs
3. Follow existing error handling patterns
4. Add budget tiers via configuration, not code changes

## 📞 Support

Check the logs for detailed error context. All errors include:
- Error type and endpoint information
- Full stack traces in production
- Actionable suggestions for users