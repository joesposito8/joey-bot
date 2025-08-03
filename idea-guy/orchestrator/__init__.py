import azure.functions as func
import azure.durable_functions as df
import logging
import json
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import build_json_response, build_error_response

# Register functions for Durable Functions runtime
ORCHESTRATOR_FUNCTION_NAME = "analysis_orchestrator"
ACTIVITY_FUNCTION_NAME = "execute_complete_workflow"

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
        workflow_result = yield context.call_activity(ACTIVITY_FUNCTION_NAME, activity_input)
        
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


async def execute_complete_workflow(workflow_input: Dict[str, Any]) -> Dict[str, Any]:
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
        final_result = await orchestrator.complete_remaining_workflow(
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


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    HTTP trigger function that starts the durable orchestration.
    """
    try:
        logging.info(f"[DURABLE-HTTP] Received orchestrator request: {req.method} {req.url}")
        
        # Create durable client using the starter string
        client = df.DurableOrchestrationClient(starter)
        logging.info(f"[DURABLE-HTTP] Created durable client successfully")
        
        # Parse the request body
        try:            
            req_body = req.get_json()
            logging.info(f"[DURABLE-HTTP] Parsed request body: {req_body}")
        except ValueError as e:
            logging.error(f"[DURABLE-HTTP] JSON parsing error: {str(e)}")
            return build_error_response("Invalid JSON in request body", 400)
            
        if not req_body:
            logging.error("[DURABLE-HTTP] Empty request body")
            return build_error_response("Request body is required", 400)
        
        logging.info(f"[DURABLE-HTTP] Starting orchestration with function name: {ORCHESTRATOR_FUNCTION_NAME}")
        logging.info(f"[DURABLE-HTTP] Orchestration input: {json.dumps(req_body, indent=2)}")
        
        # Start the orchestrator
        try:
            instance_id = await client.start_new(ORCHESTRATOR_FUNCTION_NAME, None, req_body)
            logging.info(f"[DURABLE-HTTP] ✅ Successfully started orchestration with instance ID: {instance_id}")
        except Exception as e:
            logging.error(f"[DURABLE-HTTP] ❌ Failed to start orchestration: {str(e)}")
            logging.error(f"[DURABLE-HTTP] Orchestrator function name attempted: {ORCHESTRATOR_FUNCTION_NAME}")
            raise
        
        # Get status check URL for debugging
        base_url = str(req.url).replace('/api/orchestrator', '')
        status_url = f"{base_url}/runtime/webhooks/durabletask/instances/{instance_id}"
        
        logging.info(f"[DURABLE-HTTP] Status check URL: {status_url}")
        
        # Return success response with instance ID and management URLs
        return build_json_response({
            "id": instance_id,
            "statusQueryGetUri": status_url,
            "sendEventPostUri": f"{base_url}/runtime/webhooks/durabletask/instances/{instance_id}/raiseEvent/{{eventName}}",
            "terminatePostUri": f"{base_url}/runtime/webhooks/durabletask/instances/{instance_id}/terminate",
            "message": "Durable orchestration started successfully",
            "orchestrator_function": ORCHESTRATOR_FUNCTION_NAME,
            "activity_function": ACTIVITY_FUNCTION_NAME
        })
        
    except Exception as e:
        logging.error(f"[DURABLE-HTTP] ❌ Failed to start orchestration: {str(e)}")
        logging.error(f"[DURABLE-HTTP] Exception type: {type(e).__name__}")
        import traceback
        logging.error(f"[DURABLE-HTTP] Traceback: {traceback.format_exc()}")
        return build_error_response(f"Failed to start analysis: {str(e)}", 500)

