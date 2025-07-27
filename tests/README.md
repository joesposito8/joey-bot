# Joey-Bot Tests

This directory contains the test suite for the joey-bot system.

## Structure

### `unit/`
Unit tests for individual components and modules:
- `test_agent.py` - Core agent functionality
- `test_langchain_workflows.py` - LangChain workflow components  
- `test_model_replacement.py` - Model configuration validation

### `integration/`
Integration tests for end-to-end workflows:
- `test_agent_endpoint.py` - Agent HTTP endpoints
- `test_chatgpt_flow.py` - ChatGPT integration flow
- `test_multi_call_architecture.py` - Multi-call analysis workflows
- `test_new_analysis.py` - Full analysis creation flow
- `test_process_idea_endpoint.py` - Idea processing endpoints

### `debug/`
Debug utilities and temporary debugging tools:
- `debug_job_response.py` - Debug OpenAI job responses
- `debug_spreadsheet.py` - Debug Google Sheets integration

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests only  
python -m pytest tests/integration/

# Run specific test file
python -m pytest tests/unit/test_agent.py

# Run with verbose output
python -m pytest tests/ -v
```

## Environment Setup

Integration tests require environment variables:
- `OPENAI_API_KEY` - OpenAI API key
- `GOOGLE_SHEETS_KEY_PATH` - Path to Google Sheets service account key
- `IDEA_GUY_SHEET_ID` - Google Sheets spreadsheet ID

These can be set from `idea-guy/local.settings.json` or as environment variables.