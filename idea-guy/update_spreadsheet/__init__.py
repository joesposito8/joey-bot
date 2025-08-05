import azure.functions as func
import logging
from typing import Dict, Any

from common.agent_service import AnalysisService
from common.http_utils import is_testing_mode

async def main(update_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity function that updates the spreadsheet with final analysis results.
    
    Args:
        update_input: Contains job_id, final_result, agent_config_data
        
    Returns:
        Dict with status and job_id
    """
    try:
        job_id = update_input["job_id"]
        final_result = update_input["final_result"]
        agent_config_data = update_input["agent_config_data"]
        
        logging.info(f"[UPDATE-SPREADSHEET] Updating spreadsheet for job: {job_id}")
        
        if is_testing_mode():
            logging.info(f"[UPDATE-SPREADSHEET] Mock spreadsheet update for job: {job_id}")
            return {
                "status": "completed",
                "job_id": job_id,
                "message": "Mock spreadsheet update completed"
            }
        
        # Initialize analysis service
        analysis_service = AnalysisService(agent_config_data["spreadsheet_id"])
        
        # Update spreadsheet with final results
        analysis_service._update_spreadsheet_record_with_results(job_id, final_result)
        
        logging.info(f"[UPDATE-SPREADSHEET] Successfully updated spreadsheet for job: {job_id}")
        return {
            "status": "completed",
            "job_id": job_id,
            "message": "Spreadsheet updated successfully"
        }
        
    except Exception as e:
        logging.error(f"[UPDATE-SPREADSHEET] Failed to update spreadsheet: {str(e)}")
        return {
            "status": "failed",
            "job_id": update_input.get("job_id", "unknown"),
            "error": str(e)
        }