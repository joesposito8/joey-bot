import azure.functions as func
import logging
from typing import Dict, Any

from common.durable_orchestrator import DurableOrchestrator
from common.http_utils import is_testing_mode
from common.research_models import ResearchOutput
from common.agent_service import AnalysisService

async def main(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that fetches the result of a completed async job using OpenAI Deep Research API.
    
    Args:
        job_input: Contains job_id, job_type ('research' or 'synthesis'), and agent_config_data
        
    Returns:
        Dict with job_id, status, and result data (ResearchOutput for research, dict for synthesis)
    """
    try:
        job_id = job_input["job_id"]
        job_type = job_input.get("job_type", "research")
        agent_config_data = job_input["agent_config_data"]
        research_topic = job_input.get("research_topic", "unknown")
        
        logging.info(f"[FETCH-JOB-RESULT] Fetching {job_type} result for job: {job_id}")
        
        if is_testing_mode():
            # Return mock result based on job type
            if job_type == "research":
                mock_result = {
                    "job_id": job_id,
                    "status": "completed",
                    "result": {
                        "research_topic": research_topic,
                        "summary": f"Mock research summary for {research_topic}",
                        "key_findings": [
                            f"Mock finding 1 for {research_topic}",
                            f"Mock finding 2 for {research_topic}",
                        ],
                        "sources_consulted": ["mock search", "test data"],
                        "confidence_level": "medium",
                        "supporting_evidence": [f"Mock evidence for {research_topic}"],
                        "implications": [f"Mock implication for {research_topic}"],
                        "limitations": "Mock limitations for testing"
                    }
                }
            else:  # synthesis
                mock_result = {
                    "job_id": job_id,
                    "status": "completed",
                    "result": {
                        "Analysis_Result": "Mock synthesis combining all research results",
                        "Overall_Rating": "8/10",
                        "synthesis_sources": 0
                    }
                }
            
            logging.info(f"[FETCH-JOB-RESULT] Mock {job_type} result completed: {job_id}")
            return mock_result
        
        # Initialize orchestrator with agent config data
        analysis_service = AnalysisService(agent_config_data["spreadsheet_id"])
        orchestrator = DurableOrchestrator(analysis_service.agent_config)
        
        # Fetch job result using OpenAI Deep Research API
        if job_type == "research":
            result = await orchestrator.fetch_research_result(job_id, research_topic)
        else:  # synthesis
            result = await orchestrator.fetch_synthesis_result(job_id)
        
        logging.info(f"[FETCH-JOB-RESULT] Successfully fetched {job_type} result for job: {job_id}")
        return {
            "job_id": job_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logging.error(f"[FETCH-JOB-RESULT] Failed to fetch job result: {str(e)}")
        return {
            "job_id": job_input.get("job_id", "unknown"),
            "status": "failed",
            "error": str(e),
            "result": None
        }