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
        # Check required environment variables
        sheet_id = os.environ.get('IDEA_GUY_SHEET_ID')
        if not sheet_id:
            raise ValueError("IDEA_GUY_SHEET_ID environment variable not set")
        
        logging.info(f"Initializing service with sheet ID: {sheet_id}")
        
        # Initialize service with dynamic configuration
        service = AnalysisService(sheet_id)
        
        # Generate instructions from dynamic agent configuration
        logging.info("Loading agent configuration...")
        config = service.agent_config
        logging.info(f"Agent config loaded: {config.definition.name}")
        
        instructions = config.generate_instructions()
        response_data = {"instructions": instructions}
        
        # Add testing mode info
        if is_testing_mode():
            response_data["testing_mode"] = True
            response_data["note"] = "Running in testing mode - no API charges will occur during analysis"
        
        logging.info(f"Successfully generated dynamic system instructions ({len(instructions)} chars)")
        return build_json_response(response_data)
        
    except Exception as e:
        logging.error(f"Failed to generate instructions: {str(e)}")
        import traceback
        logging.error(f"Full traceback: {traceback.format_exc()}")
        
        return build_error_response(
            message=f"Configuration error: {str(e)}",
            status_code=500,
            error_type="config_error",
            details={"endpoint": "get_instructions", "error": str(e)}
        )
