import azure.functions as func
import logging
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.durable_orchestrator import DurableOrchestrator

async def main(workflow_input):
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
            logging.info(f"[DURABLE-ACTIVITY] Updated spreadsheet with final results for job: {job_id}")
            
            return {
                "status": "completed",
                "job_id": job_id,
                "message": "Analysis completed successfully"
            }
        else:
            logging.error(f"[DURABLE-ACTIVITY] No final result produced for job: {job_id}")
            return {
                "status": "failed",
                "job_id": job_id,
                "error": "No final result produced"
            }
            
    except Exception as e:
        logging.error(f"[DURABLE-ACTIVITY] Complete workflow execution failed: {str(e)}")
        return {
            "status": "failed", 
            "job_id": workflow_input.get("job_id"),
            "error": str(e)
        }