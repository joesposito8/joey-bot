"""
Workflow execution engine for multi-step LLM processing.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class WorkflowStep:
    """Represents a single step in an LLM workflow."""
    
    name: str
    prompt_template: str
    model: str
    depends_on: List[str] = None
    tools: List[Dict[str, Any]] = None
    reasoning: Dict[str, str] = None
    background: bool = False
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.tools is None:
            self.tools = []
        if self.reasoning is None:
            self.reasoning = {}


class WorkflowChain:
    """Manages execution of multi-step LLM workflows."""
    
    def __init__(self, steps: List[WorkflowStep]):
        self.steps = {step.name: step for step in steps}
        self.execution_order = self._calculate_execution_order()
    
    def _calculate_execution_order(self) -> List[str]:
        """Calculate the order of step execution based on dependencies."""
        order = []
        completed = set()
        
        while len(completed) < len(self.steps):
            # Find steps that can be executed (all dependencies completed)
            ready_steps = [
                name for name, step in self.steps.items()
                if name not in completed and all(dep in completed for dep in step.depends_on)
            ]
            
            if not ready_steps:
                raise ValueError("Circular dependency detected in workflow steps")
            
            # Add ready steps to execution order
            order.extend(ready_steps)
            completed.update(ready_steps)
        
        return order
    
    def execute(self, context: Dict[str, Any], openai_client: OpenAI) -> Dict[str, Any]:
        """Execute the entire workflow chain."""
        results = {}
        
        for step_name in self.execution_order:
            step = self.steps[step_name]
            
            try:
                # Prepare context for this step
                step_context = {**context, **results}
                
                # Format the prompt with context
                prompt = step.prompt_template.format(**step_context)
                
                # Execute the step
                step_result = self._execute_step(step, prompt, openai_client)
                results[step_name] = step_result
                
                logging.info(f"Completed workflow step: {step_name}")
                
            except Exception as e:
                logging.error(f"Error in workflow step {step_name}: {str(e)}")
                raise
        
        return results
    
    def _execute_step(self, step: WorkflowStep, prompt: str, openai_client: OpenAI) -> Any:
        """Execute a single workflow step."""
        try:
            messages = [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]
            
            # Prepare API call parameters
            api_params = {
                "model": step.model,
                "input": messages,
            }
            
            # Add tools if specified
            if step.tools:
                api_params["tools"] = step.tools
            
            # Add reasoning if specified
            if step.reasoning:
                api_params["reasoning"] = step.reasoning
            
            # Set background processing if specified
            if step.background:
                api_params["background"] = True
                
            # Make API call
            if step.background:
                response = openai_client.responses.create(**api_params)
                return response.id  # Return job ID for background processing
            else:
                # For non-background calls, we would use regular chat completion
                # This is simplified - actual implementation depends on OpenAI API
                response = openai_client.responses.create(**api_params)
                
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
                
        except Exception as e:
            logging.error(f"Error executing workflow step {step.name}: {str(e)}")
            raise


def create_business_evaluation_workflow(tier_model: str) -> WorkflowChain:
    """Create a workflow chain for business idea evaluation."""
    
    # Basic workflow for all tiers
    steps = [
        WorkflowStep(
            name="evaluate_idea",
            prompt_template="""
            You are a senior partner at a top-tier venture capital firm whose reputation—and track record—depend on your ability to spot winners and weed out losers. You approach every pitch with rigor, realism, and an investor's eye for return on time and capital. Your sole mission today is to evaluate the idea that follows and tell me, sharply and honestly, whether it's worth backing.

            Here is the input on the idea you are evaluating:
            Idea Overview: {Idea_Overview}
            Deliverable: {Deliverable} 
            Motivation: {Motivation}
            
            Provide a comprehensive analysis including:
            - Novelty_Rating (1-10): How novel/unique the idea is
            - Novelty_Rationale: Competitor analysis and domain benchmarks
            - Feasibility_Rating (1-10): How feasible to implement
            - Feasibility_Rationale: Tech stack, costs, skills, resources needed
            - Effort_Rating (1-10): Effort required to implement
            - Effort_Rationale: Time estimates, headcount needs, complexity
            - Impact_Rating (1-10): Potential impact
            - Impact_Rationale: Market size, user adoption, social value
            - Risk_Rating (1-10): Risk level
            - Risk_Rationale: Technical, regulatory, market, competitive risks
            - Overall_Rating (1-10): Overall potential
            - Overall_Rationale: How individual scores combine
            - Analysis_Summary: Detailed analysis with market data and insights
            - Potential_Improvements: How to improve the idea's core deficiencies

            Respond in JSON format with these exact fields.
            """,
            model=tier_model,
            tools=[{"type": "web_search_preview"}] if tier_model in ["o1-mini", "o4-mini-deep-research"] else [],
            reasoning={"summary": "auto"} if tier_model == "o4-mini-deep-research" else {}
        )
    ]
    
    return WorkflowChain(steps)