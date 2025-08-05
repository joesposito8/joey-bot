import azure.functions as func
import logging
from typing import Dict, Any

from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import is_testing_mode

async def main(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that starts an async research job using OpenAI Deep Research API.
    
    Args:
        job_input: Contains research_topic, user_input, agent_config_data
        
    Returns:
        Dict with job_id and status for polling
    """
    try:
        research_topic = job_input["research_topic"]
        user_input = job_input["user_input"]
        agent_config_data = job_input["agent_config_data"]
        
        logging.info(f"[START-RESEARCH-JOB] Starting async research job for topic: {research_topic}")
        
        if is_testing_mode():
            # Return mock job for testing
            import uuid
            mock_job_id = f"test_job_{uuid.uuid4().hex[:8]}"
            logging.info(f"[START-RESEARCH-JOB] Created mock job: {mock_job_id}")
            return {
                "job_id": mock_job_id,
                "status": "started",
                "research_topic": research_topic
            }
        
        # Initialize orchestrator with agent config data
        from common.config import FullAgentConfig
        from common.agent_service import AnalysisService
        
        # Reconstruct agent config from serializable data
        analysis_service = AnalysisService(agent_config_data["spreadsheet_id"])
        orchestrator = DurableOrchestrator(analysis_service.agent_config)
        
        # Start async research job using OpenAI Deep Research API
        job_result = await orchestrator.start_research_job(research_topic, user_input)
        
        logging.info(f"[START-RESEARCH-JOB] Successfully started job: {job_result['job_id']}")
        return job_result
        
    except Exception as e:
        logging.error(f"[START-RESEARCH-JOB] Failed to start research job: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "research_topic": job_input.get("research_topic", "unknown")
        }