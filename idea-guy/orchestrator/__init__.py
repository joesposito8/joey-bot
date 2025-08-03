import azure.functions as func
import azure.durable_functions as df
import logging
import json
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import build_json_response, build_error_response

# Register functions for Durable Functions runtime - use directory names as function names
ORCHESTRATOR_FUNCTION_NAME = "analysis_orchestrator"
ACTIVITY_FUNCTION_NAME = "execute_complete_workflow"



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

