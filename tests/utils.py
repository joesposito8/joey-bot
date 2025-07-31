"""Test utilities for the Universal AI Agent Platform."""
import json
from unittest.mock import Mock
from typing import Dict, Any, Optional

def create_mock_response(content: Dict[str, Any]) -> Mock:
    """Create a mock OpenAI API response with consistent structure.
    
    Args:
        content: Dictionary to be JSON-encoded in the response
        
    Returns:
        Mock response object matching OpenAI API structure
    """
    response = Mock()
    response.output = [Mock()]
    response.output[0].content = [Mock()]
    response.output[0].content[0].text = json.dumps(content)
    return response

def generate_mock_plan(available_calls: int, max_concurrent: Optional[int] = None) -> Dict[str, Any]:
    """Generate a mock multi-call architecture plan.
    
    Args:
        available_calls: Number of API calls to include in plan
        max_concurrent: Maximum concurrent calls (defaults to min(available_calls, 4))
        
    Returns:
        Dictionary containing the mock plan structure
    """
    if max_concurrent is None:
        max_concurrent = min(available_calls, 4)

    # For single call, create minimal viable plan
    if available_calls == 1:
        return {
            "strategy_explanation": "Single-call analysis workflow",
            "total_calls": 1,
            "max_concurrent": 1,
            "calls": [{
                "call_id": "analysis_1",
                "purpose": "Complete analysis and synthesis",
                "prompt": "Analyze and synthesize results",
                "dependencies": [],
                "is_summarizer": True
            }],
            "execution_order": [["analysis_1"]]
        }

    # For multiple calls, create dependency chain with parallel execution
    calls = []
    execution_order = []
    current_batch = []
    
    for i in range(available_calls):
        call_id = f"analysis_{i+1}"
        
        # Last call is always a summarizer
        is_summarizer = (i == available_calls - 1)
        
        # Create dependencies - each call depends on previous batch
        dependencies = []
        if i > 0:
            # Depend on previous batch calls
            prev_batch_start = max(0, i - max_concurrent)
            dependencies = [f"analysis_{j+1}" for j in range(prev_batch_start, i)]
        
        calls.append({
            "call_id": call_id,
            "purpose": f"{'Synthesis' if is_summarizer else 'Analysis'} stage {i+1}",
            "prompt": f"Execute {'synthesis' if is_summarizer else 'analysis'} stage {i+1}",
            "dependencies": dependencies,
            "is_summarizer": is_summarizer
        })
        
        # Add to current batch if space available and dependencies met
        if len(current_batch) < max_concurrent:
            current_batch.append(call_id)
        else:
            execution_order.append(current_batch)
            current_batch = [call_id]
    
    if current_batch:
        execution_order.append(current_batch)

    return {
        "strategy_explanation": f"{available_calls}-call analysis workflow",
        "total_calls": available_calls,
        "max_concurrent": max_concurrent,
        "calls": calls,
        "execution_order": execution_order
    }

def create_mock_openai_client() -> Mock:
    """Create a mock OpenAI client for testing.
    
    Returns:
        Mock client that returns appropriate responses for different calls
    """
    client = Mock()
    
    def mock_create(**kwargs):
        """Dynamic mock response generation based on input."""
        if 'architecture_planning' in kwargs.get('model', ''):
            # Extract available_calls from the prompt
            prompt = kwargs['input'][0]['content'][0]['text']
            available_calls = int(prompt.split('available_calls: ')[1].split('\n')[0])
            return create_mock_response(generate_mock_plan(available_calls))
        else:
            # Analysis/execution response
            return create_mock_response({
                "Analysis_Result": "Mock analysis output",
                "Overall_Rating": "8/10",
                "Key_Insights": ["Mock insight 1", "Mock insight 2"]
            })
    
    client.responses.create.side_effect = mock_create
    return client