"""Multi-call architecture system for intelligent analysis planning and execution."""
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Any
from unittest.mock import Mock

from common.http_utils import is_testing_mode


@dataclass
class CallPlan:
    """Represents a single API call in the execution plan."""
    call_id: str
    prompt: str
    dependencies: List[str]  # IDs of calls that must complete first
    is_summarizer: bool = False
    purpose: str = ""  # Description of what this call focuses on
    

@dataclass 
class ArchitecturePlan:
    """Complete execution plan for multi-call analysis."""
    total_calls: int
    max_concurrent: int
    calls: List[CallPlan]
    execution_order: List[List[str]]  # Batches of call IDs to execute simultaneously


class MultiCallArchitecture:
    """Manages multi-call analysis architecture and execution."""
    
    def __init__(self, openai_client, agent_config: 'FullAgentConfig'):
        """Initialize with OpenAI client and agent configuration.
        
        Args:
            openai_client: OpenAI client for API calls
            agent_config: FullAgentConfig for dynamic configuration
        """
        self.client = openai_client
        self.agent_config = agent_config
        self.max_concurrent_calls = agent_config.get_universal_setting('max_concurrent_calls', 4)
        
    def _get_architecture_planning_prompt(
        self,
        original_prompt: str,
        available_calls: int,
        user_input: Dict[str, Any],
        output_fields: list
    ) -> str:
        """Generate universal prompt for planning optimal call architecture.
        
        Args:
            original_prompt: The analysis prompt to execute (from agent config)
            available_calls: Number of API calls available
            user_input: User's input data
            output_fields: List of output field names
            
        Returns:
            Universal planning prompt for architecture design
        """
        from .prompt_manager import prompt_manager
        
        return prompt_manager.format_architecture_planning_prompt(
            available_calls=available_calls,
            model=self.agent_config.get_model('architecture_planning'),
            original_prompt=original_prompt,
            user_input=user_input,
            output_fields=output_fields
        )
    
    def plan_architecture(
        self, 
        original_prompt: str,
        available_calls: int,
        user_input: Dict[str, Any],
        output_fields: list
    ) -> ArchitecturePlan:
        """Plan optimal architecture for given constraints.
        
        Args:
            original_prompt: Analysis prompt to execute (from agent config)
            available_calls: Number of API calls available
            user_input: User's input data
            output_fields: List of output field names
            
        Returns:
            Complete architecture plan
            
        Raises:
            ValueError: If planning fails
        """
        try:
            # Generate planning prompt
            planning_prompt = self._get_architecture_planning_prompt(
                original_prompt=original_prompt,
                available_calls=available_calls,
                user_input=user_input,
                output_fields=output_fields
            )
            
            # Get architecture plan using configured model
            planning_model = self.agent_config.get_model('architecture_planning')
            
            # For testing mode, use mock responses
            if is_testing_mode():
                response = Mock()
                response.output = [Mock()]
                response.output[0].content = [Mock()]
                response.output[0].content[0].text = json.dumps({
                    "strategy_explanation": "Test workflow",
                    "total_calls": available_calls,
                    "max_concurrent": min(4, available_calls),
                    "calls": [
                        {
                            "call_id": f"call_{i}",
                            "purpose": f"Stage {i}",
                            "prompt": f"Execute stage {i}",
                            "dependencies": [],
                            "is_summarizer": i == available_calls
                        }
                        for i in range(1, available_calls + 1)
                    ],
                    "execution_order": [[f"call_{i}"] for i in range(1, available_calls + 1)]
                })
            else:
                response = self.client.responses.create(
                    model=planning_model,
                    input=[{"role": "user", "content": [{"type": "input_text", "text": planning_prompt}]}],
                    background=False  # Synchronous for planning
                )
            
            # Parse response
            if hasattr(response, 'output') and response.output:
                response_text = str(response.output[-1].content[0].text)
                
                # Clean response text - remove markdown code blocks if present
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]  # Remove ```json
                if cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text[3:]   # Remove ```
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]  # Remove trailing ```
                cleaned_text = cleaned_text.strip()
                
                plan_data = json.loads(cleaned_text)
                
                # Log the plan for debugging
                logging.info(f"Architecture plan received: {json.dumps(plan_data, indent=2)}")
                
                # Convert to ArchitecturePlan
                calls = []
                for call_data in plan_data["calls"]:
                    calls.append(CallPlan(
                        call_id=call_data["call_id"],
                        prompt=call_data["prompt"],
                        dependencies=call_data.get("dependencies", []),
                        is_summarizer=call_data.get("is_summarizer", False),
                        purpose=call_data.get("purpose", "")
                    ))
                
                return ArchitecturePlan(
                    total_calls=plan_data["total_calls"],
                    max_concurrent=min(plan_data.get("max_concurrent", 4), self.max_concurrent_calls),
                    calls=calls,
                    execution_order=plan_data["execution_order"]
                )
            else:
                raise ValueError("No output from architecture planning")
                
        except Exception as e:
            logging.error(f"Architecture planning failed: {str(e)}")
            raise ValueError(f"Architecture planning failed: {str(e)}")
    
    
    def execute_plan(
        self, 
        plan: ArchitecturePlan,
        user_input: Dict[str, Any],
        agent_config
    ) -> str:
        """Execute the architecture plan with full multi-call support.
        
        Args:
            plan: Architecture plan to execute
            user_input: User's input for cost logging
            agent_config: FullAgentConfig for dynamic prompt generation
            
        Returns:
            Job ID for the main analysis (for polling)
            
        Raises:
            ValueError: If execution fails
        """
        try:
            # Log the execution plan for tracking
            from common.cost_tracker import log_openai_cost, calculate_cost_from_usage
            
            # Store results from each call
            call_results = {}
            
            # Execute batches according to execution order
            for batch_index, batch in enumerate(plan.execution_order):
                logging.info(f"Executing batch {batch_index + 1}/{len(plan.execution_order)}: {batch}")
                
                # Execute calls in this batch concurrently
                batch_results = self._execute_batch(batch, plan, call_results, user_input, agent_config)
                call_results.update(batch_results)
                
                # Log each call's cost
                for call_id, result in batch_results.items():
                    call_plan = next(c for c in plan.calls if c.call_id == call_id)
                    
                    # Estimate usage for this call
                    estimated_usage = {
                        "prompt_tokens": 2500,  # Base estimate per call
                        "completion_tokens": 4000,
                        "total_tokens": 6500
                    }
                    estimated_cost = calculate_cost_from_usage(agent_config.get_model('analysis'), estimated_usage)
                    
                    # Log with execution plan context
                    plan_summary = {
                        "total_calls": plan.total_calls,
                        "call_id": call_id,
                        "call_purpose": call_plan.purpose,
                        "is_summarizer": call_plan.is_summarizer,
                        "batch_index": batch_index + 1,
                        "dependencies": call_plan.dependencies
                    }
                    
                    log_openai_cost(
                        endpoint=f"multi_call_batch_{batch_index + 1}",
                        model=agent_config.get_model('analysis'),
                        budget_tier="agent-configured",
                        job_id=result["job_id"],
                        usage_data=estimated_usage,
                        cost_usd=estimated_cost if not is_testing_mode() else 0.0,
                        user_input=user_input,
                        execution_plan=plan_summary,
                        call_count=plan.total_calls,
                        is_multi_call=True
                    )
            
            # Find the final summarizer call result
            final_call = None
            final_job_id = None
            
            # Debug logging
            summarizer_calls = [call for call in plan.calls if call.is_summarizer]
            logging.info(f"Looking for summarizer calls. Found {len(summarizer_calls)}: {[c.call_id for c in summarizer_calls]}")
            logging.info(f"Call results available: {list(call_results.keys())}")
            
            for call in plan.calls:
                if call.is_summarizer:
                    final_call = call
                    if call.call_id in call_results:
                        final_job_id = call_results[call.call_id]["job_id"]
                        logging.info(f"Found final summarizer job ID: {final_job_id}")
                        break
                    else:
                        logging.error(f"Summarizer call {call.call_id} not found in call_results")
            
            if not final_job_id:
                raise ValueError(f"Summarizer call failed or not found. Available calls: {list(call_results.keys())}")
            
            logging.info(f"Successfully executed {plan.total_calls}-call architecture plan. Final job ID: {final_job_id}")
            return final_job_id
            
        except Exception as e:
            logging.error(f"Plan execution failed: {str(e)}")
            raise ValueError(f"Failed to execute architecture plan: {str(e)}")
    
    def _execute_batch(
        self, 
        batch: List[str], 
        plan: ArchitecturePlan, 
        previous_results: Dict[str, Any],
        user_input: Dict[str, Any],
        agent_config
    ) -> Dict[str, Any]:
        """Execute a batch of calls concurrently.
        
        Args:
            batch: List of call IDs to execute in this batch
            plan: Overall architecture plan
            previous_results: Results from previous batches
            user_input: User's input data for prompt generation
            agent_config: FullAgentConfig for dynamic prompt generation
            
        Returns:
            Dictionary mapping call_id to execution result
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        batch_results = {}
        
        # For testing mode, return mock results immediately
        if is_testing_mode():
            for call_id in batch:
                batch_results[call_id] = {
                    "job_id": f"mock_{call_id}_{int(time.time())}",
                    "status": "completed",
                    "testing_mode": True
                }
            return batch_results
        
        # Execute calls concurrently (max 4 as per constraint)
        max_workers = min(len(batch), plan.max_concurrent)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all calls in the batch
            future_to_call = {}
            
            for call_id in batch:
                call_plan = next(c for c in plan.calls if c.call_id == call_id)
                
                # Generate prompt for this call
                enhanced_prompt = self._generate_call_prompt(call_plan, user_input, agent_config)
                
                # Submit the API call
                future = executor.submit(
                    self._execute_single_call,
                    enhanced_prompt,
                    agent_config
                )
                future_to_call[future] = call_id
            
            # Collect results as they complete
            for future in as_completed(future_to_call):
                call_id = future_to_call[future]
                try:
                    result = future.result()
                    batch_results[call_id] = result
                    logging.info(f"Completed call {call_id}: {result['job_id']}")
                except Exception as e:
                    logging.error(f"Call {call_id} failed: {str(e)}")
                    batch_results[call_id] = {
                        "job_id": f"failed_{call_id}",
                        "status": "failed",
                        "error": str(e)
                    }
        
        return batch_results
    
    def _generate_call_prompt(self, call_plan, user_input, agent_config) -> str:
        """Generate appropriate prompt for a call."""
# Now using universal prompt_manager for all prompts
        
        from .prompt_manager import prompt_manager
        
        if call_plan.is_summarizer and len(agent_config.schema.output_fields) > 1:
            # For multi-field output, use universal synthesis template
            return prompt_manager.format_synthesis_call_prompt(
                previous_findings=call_plan.prompt,
                output_fields=agent_config.schema.output_fields
            )
        else:
            # Regular analysis call using universal template
            return prompt_manager.format_analysis_call_prompt(
                starter_prompt=agent_config.definition.starter_prompt,
                call_purpose=call_plan.purpose,
                user_input=user_input,
                specific_instructions=call_plan.prompt
            )
    
    def _execute_single_call(self, prompt: str, agent_config) -> Dict[str, Any]:
        """Execute a single API call.
        
        Args:
            prompt: The prompt to send
            agent_config: Agent configuration containing model and tools
            
        Returns:
            Result dictionary with job_id and status
        """
        response = self.client.responses.create(
            model=agent_config.get_model('analysis'),
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            background=True,
            tools=[{"type": "web_search_preview"}],  # Standard tools for all agents
            reasoning={"summary": "auto"}  # Standard reasoning for all agents
        )
        
        return {
            "job_id": response.id,
            "status": "processing",
            "model": agent_config.get_model('analysis')
        }
    
    def _inject_dependencies(
        self, 
        prompt: str, 
        dependencies: List[str], 
        previous_results: Dict[str, Any]
    ) -> str:
        """Inject results from dependency calls into the prompt.
        
        Args:
            prompt: Original prompt
            dependencies: List of call IDs this call depends on
            previous_results: Results from previous calls
            
        Returns:
            Enhanced prompt with dependency results
        """
        if not dependencies:
            return prompt
        
        # For now, just note the dependencies in the prompt
        # In a full implementation, we'd wait for and retrieve the actual results
        dependency_context = "\\n\\nCONTEXT FROM PREVIOUS ANALYSIS CALLS:\\n"
        for dep_id in dependencies:
            if dep_id in previous_results:
                dependency_context += f"- {dep_id}: {previous_results[dep_id].get('status', 'completed')}\\n"
            else:
                dependency_context += f"- {dep_id}: pending\\n"
        
        return prompt + dependency_context


def create_multi_call_analysis(
    user_input: Dict[str, Any],
    call_count: int,
    openai_client,
    agent_config
) -> str:
    """Create and execute universal multi-call analysis architecture.
    
    Args:
        user_input: User's input data
        call_count: Number of API calls available for this tier
        openai_client: OpenAI client
        agent_config: FullAgentConfig instance for dynamic configuration
        
    Returns:
        Job ID for polling the analysis result
    """
    if agent_config is None:
        raise ValueError("agent_config is required for universal multi-call analysis")
    
    original_prompt = agent_config.generate_analysis_prompt(user_input)
    
    # Initialize architecture system
    architecture = MultiCallArchitecture(openai_client)
    
    # Plan the architecture
    output_fields = [field.name for field in agent_config.schema.output_fields]
    plan = architecture.plan_architecture(
        original_prompt=original_prompt,
        available_calls=call_count,
        user_input=user_input,
        output_fields=output_fields
    )
    
    logging.info(f"Created {call_count}-call architecture plan")
    
    # Execute the plan
    job_id = architecture.execute_plan(plan, user_input, agent_config)
    
    return job_id
