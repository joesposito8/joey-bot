import azure.functions as func
import logging
from typing import Dict, Any

from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import is_testing_mode
from common.agent_service import AnalysisService

async def main(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that checks the status of an async job using OpenAI Deep Research API.
    
    Args:
        job_input: Contains job_id and agent_config_data
        
    Returns:
        Dict with job_id, status ('running', 'succeeded', 'failed'), and optional result data
    """
    try:
        job_id = job_input["job_id"]
        agent_config_data = job_input["agent_config_data"]
        
        logging.info(f"[CHECK-JOB-STATUS] Checking status for job: {job_id}")
        
        if is_testing_mode():
            # Mock job status - simulate completion after a few checks
            import random
            if random.random() < 0.7:  # 70% chance of completion
                logging.info(f"[CHECK-JOB-STATUS] Mock job completed: {job_id}")
                return {
                    "job_id": job_id,
                    "status": "succeeded",
                    "ready_for_fetch": True
                }
            else:
                logging.info(f"[CHECK-JOB-STATUS] Mock job still running: {job_id}")
                return {
                    "job_id": job_id,
                    "status": "running",
                    "ready_for_fetch": False
                }
        
        # Initialize orchestrator with agent config data
        analysis_service = AnalysisService(agent_config_data["spreadsheet_id"])
        orchestrator = DurableOrchestrator(analysis_service.agent_config)
        
        # Check job status using OpenAI Deep Research API
        status_result = await orchestrator.check_job_status(job_id)
        
        logging.info(f"[CHECK-JOB-STATUS] Job {job_id} status: {status_result['status']}")
        return status_result
        
    except Exception as e:
        logging.error(f"[CHECK-JOB-STATUS] Failed to check job status: {str(e)}")
        return {
            "job_id": job_input.get("job_id", "unknown"),
            "status": "failed",
            "error": str(e),
            "ready_for_fetch": False
        }