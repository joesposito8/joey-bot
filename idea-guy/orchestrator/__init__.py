import azure.functions as func
import azure.durable_functions as df
import logging
import json
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import build_json_response, build_error_response

# Create Durable Functions app
app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.orchestration_trigger(context_name="context")
def analysis_orchestrator(context: df.DurableOrchestrationContext):
    """
    Durable orchestrator that handles the complete analysis workflow.
    """
    try:
        # Get input data from the orchestrator context
        input_data = context.get_input()
        logging.info(f"[DURABLE-ORCHESTRATOR] Orchestrator started with input: {input_data}")
        
        # Log to Application Insights for tracking
        import json
        logging.info(f"[DURABLE-ORCHESTRATOR] Starting orchestration for job: {input_data.get('job_id')}")
        logging.info(f"[DURABLE-ORCHESTRATOR] Orchestration input data: {json.dumps(input_data, indent=2)}")
        
        job_id = input_data.get("job_id")
        user_input = input_data.get("user_input")
        budget_tier = input_data.get("budget_tier")
        spreadsheet_id = input_data.get("spreadsheet_id")
        research_plan = input_data.get("research_plan")
        
        if not all([job_id, user_input, budget_tier, spreadsheet_id, research_plan]):
            logging.error("Missing required input data for orchestration")
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
        logging.error(f"Orchestrator failed: {str(e)}")
        return {
            "status": "failed", 
            "error": str(e),
            "job_id": input_data.get("job_id") if 'input_data' in locals() else None
        }


@app.activity_trigger(input_name="workflow_input")
def execute_complete_workflow(workflow_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that executes the complete research and synthesis workflow.
    """
    try:
        job_id = workflow_input["job_id"]
        user_input = workflow_input["user_input"]
        budget_tier = workflow_input["budget_tier"]
        spreadsheet_id = workflow_input["spreadsheet_id"]
        research_plan = workflow_input["research_plan"]
        
        logging.info(f"[DURABLE-ACTIVITY] Starting complete workflow execution for job: {job_id}")
        logging.info(f"[DURABLE-ACTIVITY] Activity received input: {workflow_input}")
        
        # Initialize the analysis service
        analysis_service = AnalysisService(spreadsheet_id)
        
        # Get the orchestrator and complete the remaining workflow
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


@app.route(route="orchestrator", auth_level=func.AuthLevel.ANONYMOUS)
@app.durable_client_input(client_name="client")
def orchestrator_http_start(req: func.HttpRequest, client) -> func.HttpResponse:
    """
    HTTP trigger function that starts the durable orchestration.
    """
    try:
        # Parse the request body
        try:
            req_body = req.get_json()
        except ValueError:
            return build_error_response("Invalid JSON in request body", 400)
            
        if not req_body:
            return build_error_response("Request body is required", 400)
        
        # Start the orchestrator
        instance_id = client.start_new("analysis_orchestrator", None, req_body)
        
        logging.info(f"Started orchestration with instance ID: {instance_id}")
        
        # Return the instance management URLs
        return client.create_check_status_response(req, instance_id)
        
    except Exception as e:
        logging.error(f"Failed to start orchestration: {str(e)}")
        return build_error_response(f"Failed to start analysis: {str(e)}", 500)

