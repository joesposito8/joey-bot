import azure.functions as func
import azure.durable_functions as df
import logging
import json
from typing import Dict, Any

def main(context: df.DurableOrchestrationContext):
    """
    Durable orchestrator that handles the complete analysis workflow.
    """
    try:
        # Get input data from the orchestrator context
        input_data = context.get_input()
        logging.info(f"[DURABLE-ORCHESTRATOR] Orchestrator started with input: {input_data}")
        
        # Log to Application Insights for tracking
        logging.info(f"[DURABLE-ORCHESTRATOR] Starting orchestration for job: {input_data.get('job_id')}")
        logging.info(f"[DURABLE-ORCHESTRATOR] Orchestration input data: {json.dumps(input_data, indent=2)}")
        
        job_id = input_data.get("job_id")
        user_input = input_data.get("user_input")
        budget_tier = input_data.get("budget_tier")
        spreadsheet_id = input_data.get("spreadsheet_id")
        research_plan = input_data.get("research_plan")
        
        if not all([job_id, user_input, budget_tier, spreadsheet_id, research_plan]):
            logging.error("[DURABLE-ORCHESTRATOR] Missing required input data for orchestration")
            return {
                "status": "failed", 
                "error": "Missing required input data",
                "job_id": job_id
            }
        
        # Execute the complete workflow using activity function
        activity_input = {
            "job_id": job_id,
            "user_input": user_input,
            "budget_tier": budget_tier,
            "spreadsheet_id": spreadsheet_id,
            "research_plan": research_plan
        }
        
        # Call the activity function to do the actual work
        logging.info(f"[DURABLE-ORCHESTRATOR] Calling activity function for job: {job_id}")
        workflow_result = yield context.call_activity("execute_complete_workflow", activity_input)
        
        logging.info(f"[DURABLE-ORCHESTRATOR] Activity function completed for job {job_id}: {workflow_result.get('status')}")
        logging.info(f"[DURABLE-ORCHESTRATOR] Final workflow result: {workflow_result}")
        return workflow_result
        
    except Exception as e:
        logging.error(f"[DURABLE-ORCHESTRATOR] Orchestrator failed: {str(e)}")
        return {
            "status": "failed", 
            "error": str(e),
            "job_id": input_data.get("job_id") if 'input_data' in locals() else None
        }