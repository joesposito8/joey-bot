#!/usr/bin/env python3
"""Test configuration system loading"""

import os
os.environ['TESTING_MODE'] = 'true'
os.environ['IDEA_GUY_SHEET_ID'] = '1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs'

print('=== Testing Configuration System Loading ===')

print('\n1. Testing environment variables...')
print(f'TESTING_MODE: {os.environ.get("TESTING_MODE")}')
print(f'IDEA_GUY_SHEET_ID: {os.environ.get("IDEA_GUY_SHEET_ID")}')
print(f'GOOGLE_SHEETS_KEY_PATH: {bool(os.environ.get("GOOGLE_SHEETS_KEY_PATH"))}')

print('\n2. Testing configuration loading...')
from pathlib import Path
from common.config.agent_definition import AgentDefinition
from common.config.models import FullAgentConfig

# Load business evaluation agent
yaml_path = Path('agents/business_evaluation.yaml')
print(f'Agent YAML exists: {yaml_path.exists()}')

agent_def = AgentDefinition.from_yaml(yaml_path)
print(f'Agent loaded: {agent_def.name}')
print(f'Agent ID: {agent_def.agent_id}')
print(f'Sheet URL configured: {bool(agent_def.sheet_url)}')

print('\n3. Testing Google Sheets integration...')
try:
    config = FullAgentConfig.from_definition(agent_def)
    print(f'Full config created successfully')
    print(f'Input fields: {len(config.schema.input_fields)}')
    print(f'Output fields: {len(config.schema.output_fields)}')
    
    # Show field details
    print('\nInput fields:')
    for field in config.schema.input_fields:
        print(f'  - {field.name}: {field.description}')
    
    print('\nOutput fields:')
    for field in config.schema.output_fields[:3]:  # Show first 3
        print(f'  - {field.name}: {field.description}')
    
except Exception as e:
    print(f'❌ Google Sheets integration failed: {e}')
    print('This might be expected if credentials are not configured')

print('\n4. Testing budget tiers...')
try:
    tiers = config.get_budget_tiers()
    for tier in tiers:
        print(f'  {tier.name}: ${tier.price} ({tier.calls} calls) - {tier.description}')
    print('\n✅ Configuration system test PASSED')
except Exception as e:
    print(f'❌ Budget tiers test failed: {e}')