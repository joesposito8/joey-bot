import azure.functions as func
import logging
from typing import Dict, Any, List

from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import is_testing_mode
from common.research_models import ResearchOutput

async def main(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that starts an async synthesis job using OpenAI Deep Research API.
    
    Args:
        job_input: Contains research_results, user_input, agent_config_data
        
    Returns:
        Dict with job_id and status for polling
    """
    try:
        research_results_data = job_input["research_results"]
        user_input = job_input["user_input"]
        agent_config_data = job_input["agent_config_data"]
        
        logging.info(f"[START-SYNTHESIS-JOB] Starting async synthesis job with {len(research_results_data)} research results")
        
        if is_testing_mode():
            # Return mock job for testing
            import uuid
            mock_job_id = f"test_synthesis_{uuid.uuid4().hex[:8]}"
            logging.info(f"[START-SYNTHESIS-JOB] Created mock synthesis job: {mock_job_id}")
            return {
                "job_id": mock_job_id,
                "status": "started"
            }
        
        # Initialize orchestrator with agent config data
        from common.agent_service import AnalysisService
        
        # Reconstruct agent config from serializable data
        analysis_service = AnalysisService(agent_config_data["spreadsheet_id"])
        orchestrator = DurableOrchestrator(analysis_service.agent_config)
        
        # Convert research results data back to ResearchOutput objects
        research_results = []
        for result_data in research_results_data:
            if isinstance(result_data, dict):
                research_result = ResearchOutput(**result_data)
                research_results.append(research_result)
            else:
                research_results.append(result_data)  # Already a ResearchOutput object
        
        # Start async synthesis job using OpenAI Deep Research API
        job_result = await orchestrator.start_synthesis_job(research_results, user_input)
        
        logging.info(f"[START-SYNTHESIS-JOB] Successfully started synthesis job: {job_result['job_id']}")
        return job_result
        
    except Exception as e:
        logging.error(f"[START-SYNTHESIS-JOB] Failed to start synthesis job: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }