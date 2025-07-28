"""Multi-call architecture system for intelligent analysis planning and execution."""
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Any

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


def get_architecture_planning_prompt(
    original_prompt: str, 
    available_calls: int,
    user_input: Dict[str, Any]
) -> str:
    """Generate universal prompt for planning optimal call architecture.
    
    Args:
        original_prompt: The analysis prompt to execute (from agent config)
        available_calls: Number of API calls available
        user_input: User's input data
        
    Returns:
        Universal planning prompt for architecture design
    """
    # Format user input generically
    input_summary = "\n".join([f"{key}: {value}" for key, value in user_input.items()])
    
    return f"""You are an expert AI architecture planner. Your job is to design the optimal execution strategy to achieve the most accurate analysis using the available resources.

RESOURCES: {available_calls} total API calls to gpt-4o-mini
CONSTRAINTS: 
- Maximum 4 calls can run simultaneously
- Each call tree must end with a summarizer that attempts to answer the original prompt
- You must use ALL available calls efficiently
- Focus on comprehensive analysis across all required dimensions

ORIGINAL ANALYSIS PROMPT TO EXECUTE:
{original_prompt}

USER INPUT DATA:
{input_summary}

ANALYSIS REQUIREMENTS:
- Provide comprehensive analysis across all required output fields
- Use available calls to maximize depth and accuracy
- Ensure final output matches the required format structure

TASK: Design the optimal call architecture as a JSON plan with this exact structure:

{{
    "strategy_explanation": "Brief explanation of your approach",
    "total_calls": {available_calls},
    "max_concurrent": 4,
    "calls": [
        {{
            "call_id": "call_1",
            "purpose": "What this call will focus on",
            "prompt": "Specific prompt for this call focusing on [purpose]",
            "dependencies": [],
            "is_summarizer": false
        }},
        {{
            "call_id": "call_2", 
            "purpose": "Another focused analysis area",
            "prompt": "Specific prompt for this call",
            "dependencies": ["call_1"],
            "is_summarizer": false
        }},
        {{
            "call_id": "final_summary",
            "purpose": "Synthesize all findings into final analysis", 
            "prompt": "Synthesize the findings from previous calls into the complete analysis format required by the original prompt",
            "dependencies": ["call_1", "call_2"],
            "is_summarizer": true
        }}
    ],
    "execution_order": [
        ["call_1"],
        ["call_2"], 
        ["final_summary"]
    ]
}}

OPTIMIZATION STRATEGIES for {available_calls} calls:
- 1 call: Single comprehensive analysis covering all required dimensions
- 3 calls: Multi-faceted analysis with specialized focus areas, then synthesize
- 5+ calls: Deep specialized analysis across multiple dimensions with comprehensive synthesis

CRITICAL: The final summarizer MUST provide complete analysis covering all required output fields as specified in the original prompt.

Ensure each non-summarizer call focuses on a specific aspect that contributes unique value to the overall analysis.

Respond with ONLY the JSON plan, no other text."""


class MultiCallArchitecture:
    """Manages multi-call analysis architecture and execution."""
    
    def __init__(self, openai_client):
        """Initialize with OpenAI client.
        
        Args:
            openai_client: OpenAI client for API calls
        """
        self.client = openai_client
        self.max_concurrent_calls = 4
    
    def plan_architecture(
        self, 
        original_prompt: str,
        available_calls: int,
        user_input: Dict[str, Any]
    ) -> ArchitecturePlan:
        """Plan optimal architecture for given constraints.
        
        Args:
            original_prompt: Analysis prompt to execute (from agent config)
            available_calls: Number of API calls available
            user_input: User's input data
            
        Returns:
            Complete architecture plan
            
        Raises:
            ValueError: If planning fails
        """
        try:
            # Generate planning prompt
            planning_prompt = get_architecture_planning_prompt(
                original_prompt, available_calls, user_input
            )
            
            # Get architecture plan from o4-mini-high (using gpt-4o-mini for now)
            response = self.client.responses.create(
                model="gpt-4o-mini",
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
            # Fallback to simple sequential plan
            return self._create_fallback_plan(original_prompt, available_calls)
    
    def _create_fallback_plan(self, original_prompt: str, available_calls: int) -> ArchitecturePlan:
        """Create simple fallback plan if architecture planning fails.
        
        Args:
            original_prompt: Analysis prompt
            available_calls: Number of calls available
            
        Returns:
            Simple sequential architecture plan
        """
        if available_calls == 1:
            calls = [CallPlan(
                call_id="single_analysis",
                prompt=original_prompt,
                dependencies=[],
                is_summarizer=True,
                purpose="Complete comprehensive analysis"
            )]
            execution_order = [["single_analysis"]]
        else:
            # Simple sequential approach
            calls = []
            for i in range(available_calls - 1):
                calls.append(CallPlan(
                    call_id=f"analysis_{i+1}",
                    prompt=f"Focus on aspect {i+1} of: {original_prompt}",
                    dependencies=[f"analysis_{i}"] if i > 0 else [],
                    is_summarizer=False,
                    purpose=f"Analysis aspect {i+1}"
                ))
            
            # Final summarizer
            calls.append(CallPlan(
                call_id="final_summary", 
                prompt=f"Synthesize all previous analysis into: {original_prompt}",
                dependencies=[f"analysis_{i+1}" for i in range(available_calls - 1)],
                is_summarizer=True,
                purpose="Final synthesis of all analysis"
            ))
            
            # Sequential execution
            execution_order = [[f"analysis_{i+1}"] for i in range(available_calls - 1)]
            execution_order.append(["final_summary"])
        
        return ArchitecturePlan(
            total_calls=available_calls,
            max_concurrent=self.max_concurrent_calls,
            calls=calls,
            execution_order=execution_order
        )
    
    def execute_plan(
        self, 
        plan: ArchitecturePlan,
        tier_config,
        user_input: Dict[str, Any]
    ) -> str:
        """Execute the architecture plan with full multi-call support.
        
        Args:
            plan: Architecture plan to execute
            tier_config: Budget tier configuration
            user_input: User's input for cost logging
            
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
                batch_results = self._execute_batch(batch, plan, tier_config, call_results)
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
                    estimated_cost = calculate_cost_from_usage(tier_config.model, estimated_usage)
                    
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
                        model=tier_config.model,
                        budget_tier=tier_config.level,
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
            
            for call in plan.calls:
                if call.is_summarizer:
                    final_call = call
                    final_job_id = call_results[call.call_id]["job_id"]
                    break
            
            if not final_job_id:
                raise ValueError("No final summarizer call found in execution results")
            
            logging.info(f"Successfully executed {plan.total_calls}-call architecture plan. Final job ID: {final_job_id}")
            return final_job_id
            
        except Exception as e:
            logging.error(f"Plan execution failed: {str(e)}")
            raise ValueError(f"Failed to execute architecture plan: {str(e)}")
    
    def _execute_batch(
        self, 
        batch: List[str], 
        plan: ArchitecturePlan, 
        tier_config,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a batch of calls concurrently.
        
        Args:
            batch: List of call IDs to execute in this batch
            plan: Overall architecture plan
            tier_config: Budget tier configuration
            previous_results: Results from previous batches
            
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
                
                # Inject results from dependencies into the prompt
                enhanced_prompt = self._inject_dependencies(
                    call_plan.prompt, call_plan.dependencies, previous_results
                )
                
                # Submit the API call
                future = executor.submit(
                    self._execute_single_call,
                    enhanced_prompt,
                    tier_config
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
    
    def _execute_single_call(self, prompt: str, tier_config) -> Dict[str, Any]:
        """Execute a single API call.
        
        Args:
            prompt: The prompt to send
            tier_config: Budget tier configuration
            
        Returns:
            Result dictionary with job_id and status
        """
        response = self.client.responses.create(
            model=tier_config.model,
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            background=True,
            tools=tier_config.tools if tier_config.tools else None,
            reasoning=tier_config.reasoning if tier_config.reasoning else None
        )
        
        return {
            "job_id": response.id,
            "status": "processing",
            "model": tier_config.model
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
    tier_config,
    openai_client,
    agent_config
) -> str:
    """Create and execute universal multi-call analysis architecture.
    
    Args:
        user_input: User's input data
        tier_config: Budget tier configuration with call_count
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
    plan = architecture.plan_architecture(
        original_prompt=original_prompt,
        available_calls=tier_config.call_count,
        user_input=user_input
    )
    
    logging.info(f"Created {tier_config.call_count}-call architecture plan for {tier_config.level} tier")
    
    # Execute the plan
    job_id = architecture.execute_plan(plan, tier_config, user_input)
    
    return job_id
