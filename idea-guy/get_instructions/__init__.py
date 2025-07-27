import azure.functions as func
import logging
import os

from common.agent_service import AnalysisService
from common.http_utils import build_json_response, build_error_response, is_testing_mode


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get dynamic system instructions generated from agent configuration.
    
    Returns:
        JSON response with dynamically generated instructions
    """
    logging.info('Get instructions HTTP trigger function processed a request.')

    try:
        # Initialize service with dynamic configuration
        service = AnalysisService(os.environ['IDEA_GUY_SHEET_ID'])
        
        # Generate instructions from dynamic agent configuration
        instructions = service.agent_config.generate_instructions()
        response_data = {"instructions": instructions}
        
        # Add testing mode info
        if is_testing_mode():
            response_data["testing_mode"] = True
            response_data["note"] = "Running in testing mode - no API charges will occur during analysis"
        
        logging.info("Successfully generated dynamic system instructions")
        return build_json_response(response_data)
        
    except Exception as e:
        logging.error(f"Failed to generate instructions: {str(e)}")
        return build_error_response(
            message="Failed to retrieve system instructions. Please contact support.",
            status_code=500,
            error_type="config_error",
            details={"endpoint": "get_instructions", "error": str(e)}
        )
