import azure.functions as func
import logging

from common.idea_guy import get_system_message
from common.http_utils import build_json_response, log_and_return_error, is_testing_mode


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get system instructions for ChatGPT bot workflow.
    
    Returns:
        JSON response with system message instructions
    """
    logging.info('Get instructions HTTP trigger function processed a request.')

    try:
        instructions = get_system_message()
        response_data = {"instructions": instructions}
        
        # Add testing mode info to instructions
        if is_testing_mode():
            response_data["testing_mode"] = True
            response_data["note"] = "Running in testing mode - no API charges will occur during analysis"
        
        logging.info("Successfully retrieved system instructions")
        return build_json_response(response_data)
        
    except Exception as e:
        return log_and_return_error(
            message="Failed to retrieve system instructions. Please contact support.",
            status_code=500,
            error_type="instructions_error",
            context={"endpoint": "get_instructions"},
            exception=e
        )
