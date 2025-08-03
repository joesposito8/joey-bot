import azure.functions as func
import azure.durable_functions as df
import logging
import json
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.http_utils import build_json_response, build_error_response

# Create Durable Functions app
durable_app = df.DFApp()

@durable_app.orchestration_trigger(context_name="context")
def analysis_orchestrator(context: df.DurableOrchestrationContext):
    """
    Durable orchestrator that handles the complete analysis workflow.
    
    This orchestrator:
    1. Receives the analysis job details from the execute_analysis endpoint
    2. Executes the research and synthesis workflow using DurableOrchestrator
    3. Updates the spreadsheet with final results
    4. Returns completion status
    """
    try:
        # Get input data from the orchestrator context
        input_data = context.get_input()
        logging.info(f"Orchestrator started with input: {input_data}")
        
        job_id = input_data.get("job_id")
        user_input = input_data.get("user_input")
        budget_tier = input_data.get("budget_tier")
        spreadsheet_id = input_data.get("spreadsheet_id")
        research_plan = input_data.get("research_plan")
        
        if not all([job_id, user_input, budget_tier, spreadsheet_id, research_plan]):
            raise ValueError("Missing required input data for orchestration")
        
        # Execute the complete workflow using activity function
        workflow_result = yield context.call_activity(
            "execute_complete_workflow",
            {
                "job_id": job_id,
                "user_input": user_input,
                "budget_tier": budget_tier,
                "spreadsheet_id": spreadsheet_id,
                "research_plan": research_plan
            }
        )
        
        logging.info(f"Workflow completed for job {job_id}: {workflow_result.get('status')}")
        return workflow_result
        
    except Exception as e:
        logging.error(f"Orchestrator failed: {str(e)}")
        return {
            "status": "failed", 
            "error": str(e),
            "job_id": input_data.get("job_id") if input_data else None
        }


@durable_app.activity_trigger(input_name="workflow_input")
def execute_complete_workflow(workflow_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that executes the complete research and synthesis workflow.
    
    This function runs the remaining workflow (research + synthesis) that was
    started by the fast-return execute_analysis endpoint.
    """
    try:
        job_id = workflow_input["job_id"]
        user_input = workflow_input["user_input"]
        budget_tier = workflow_input["budget_tier"]
        spreadsheet_id = workflow_input["spreadsheet_id"]
        research_plan = workflow_input["research_plan"]
        
        logging.info(f"Starting complete workflow execution for job: {job_id}")
        
        # Initialize the analysis service
        analysis_service = AnalysisService(spreadsheet_id)
        
        # Get the orchestrator and complete the remaining workflow
        from common.durable_orchestrator import DurableOrchestrator
        orchestrator = DurableOrchestrator(analysis_service.agent_config)
        
        # Execute the remaining workflow (research + synthesis)
        final_result = orchestrator.complete_remaining_workflow(
            job_id, research_plan, user_input
        )
        
        # Update spreadsheet with the final results
        if final_result.get("final_result"):
            analysis_service._update_spreadsheet_record_with_results(
                job_id, final_result["final_result"]
            )
            logging.info(f"Updated spreadsheet with final results for job: {job_id}")
            
            return {
                "status": "completed",
                "job_id": job_id,
                "message": "Analysis completed successfully"
            }
        else:
            logging.error(f"No final result produced for job: {job_id}")
            return {
                "status": "failed",
                "job_id": job_id,
                "error": "No final result produced"
            }
            
    except Exception as e:
        logging.error(f"Complete workflow execution failed: {str(e)}")
        return {
            "status": "failed", 
            "job_id": workflow_input.get("job_id"),
            "error": str(e)
        }


# Export the durable app for Azure Functions to discover
def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    HTTP trigger function that starts the durable orchestration.
    This function is called by the execute_analysis endpoint to start background processing.
    """
    try:
        # Parse the request body
        req_body = req.get_json()
        if not req_body:
            return build_error_response("Request body is required", 400)
        
        # Create durable client
        client = df.DurableOrchestrationClient(starter)
        
        # Start the orchestrator
        instance_id = client.start_new("analysis_orchestrator", None, req_body)
        
        logging.info(f"Started orchestration with instance ID: {instance_id}")
        
        # Return the instance management URLs
        return client.create_check_status_response(req, instance_id)
        
    except Exception as e:
        logging.error(f"Failed to start orchestration: {str(e)}")
        return build_error_response(f"Failed to start analysis: {str(e)}", 500)