import azure.functions as func
import logging
import os

from common.http_utils import (
    build_json_response, build_error_response, validate_json_request, 
    log_and_return_error, is_testing_mode
)
from common.agent_service import AnalysisService, ValidationError


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get budget pricing options for business idea analysis.
    
    Args:
        req: HTTP request with user_input in JSON body
        
    Returns:
        JSON response with available budget tiers and pricing
    """
    logging.info('Get pricepoints HTTP trigger function processed a request.')

    try:
        # Parse and validate request
        req_body = validate_json_request(req)
        user_input = req_body.get("user_input", {})
        
        # Get spreadsheet ID from request or environment
        spreadsheet_id = req_body.get(
            "spreadsheet_id", 
            os.getenv("IDEA_GUY_SHEET_ID", "")
        )
        
        if not spreadsheet_id:
            return build_error_response(
                "Spreadsheet ID is required (in request or IDEA_GUY_SHEET_ID env var)",
                400
            )
        
        # Initialize analysis service with dynamic configuration and get budget options
        analysis_service = AnalysisService(spreadsheet_id)
        response_data = analysis_service.get_budget_options(user_input)
        
        # Add testing mode indicator to response
        if is_testing_mode():
            response_data["testing_mode"] = True
            response_data["note"] = "Running in testing mode - no API charges will occur"
        
        logging.info(f"Successfully returned {len(response_data.get('pricepoints', []))} pricing options")
        return build_json_response(response_data)
        
    except ValueError as e:
        return log_and_return_error(
            message=str(e),
            status_code=400,
            error_type="validation_error",
            context={"endpoint": "get_pricepoints", "request_keys": list(req_body.keys()) if 'req_body' in locals() else []},
            exception=e
        )
    except ValidationError as e:
        return log_and_return_error(
            message=f"Input validation failed: {str(e)}",
            status_code=400,
            error_type="input_validation_error",
            context={"endpoint": "get_pricepoints"},
            exception=e
        )
    except Exception as e:
        # Check if this is a configuration error
        if "agent_config" in str(e) or "configuration" in str(e).lower():
            return build_error_response(
                message=f"Configuration error: {str(e)}",
                status_code=500,
                error_type="config_error",
                details={"endpoint": "get_pricepoints"}
            )
        
        return log_and_return_error(
            message="An unexpected error occurred while getting pricing options. Please contact support if this persists.",
            status_code=500,
            error_type="server_error",
            context={"endpoint": "get_pricepoints"},
            exception=e
        )
