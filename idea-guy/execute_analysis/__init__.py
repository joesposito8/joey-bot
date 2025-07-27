import azure.functions as func
import logging
import os

from common.http_utils import (
    build_json_response, build_error_response, validate_json_request,
    log_and_return_error, is_testing_mode
)
from common.agent_service import AnalysisService, ValidationError


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Execute business idea analysis with selected budget tier.
    
    Args:
        req: HTTP request with user_input and budget_tier in JSON body
        
    Returns:
        JSON response with job ID for polling analysis status
    """
    logging.info('Execute analysis HTTP trigger function processed a request.')

    try:
        # Parse and validate request
        req_body = validate_json_request(req)
        user_input = req_body.get("user_input", {})
        budget_tier = req_body.get("budget_tier", "")
        
        if not budget_tier:
            return build_error_response("budget_tier is required", 400)
        
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
        
        # Initialize analysis service and create job
        analysis_service = AnalysisService(spreadsheet_id)
        response_data = analysis_service.create_analysis_job(user_input, budget_tier)
        
        # Log successful job creation
        logging.info(f"Successfully created analysis job: {response_data.get('job_id')}")
        
        return build_json_response(response_data)
        
    except ValueError as e:
        return log_and_return_error(
            message=str(e),
            status_code=400,
            error_type="validation_error",
            context={
                "endpoint": "execute_analysis",
                "budget_tier": req_body.get("budget_tier") if 'req_body' in locals() else None,
                "user_input_keys": list(req_body.get("user_input", {}).keys()) if 'req_body' in locals() else []
            },
            exception=e
        )
    except ValidationError as e:
        return log_and_return_error(
            message=f"Analysis setup failed: {str(e)}",
            status_code=400,
            error_type="analysis_validation_error",
            context={
                "endpoint": "execute_analysis",
                "budget_tier": req_body.get("budget_tier") if 'req_body' in locals() else None
            },
            exception=e
        )
    except KeyError as e:
        return log_and_return_error(
            message=f"Invalid budget tier selected: {str(e)}. Available tiers: basic, standard, premium",
            status_code=400,
            error_type="invalid_budget_tier",
            context={
                "endpoint": "execute_analysis",
                "requested_tier": req_body.get("budget_tier") if 'req_body' in locals() else None
            },
            exception=e
        )
    except Exception as e:
        # Check if this is a configuration error
        if "agent_config" in str(e) or "configuration" in str(e).lower():
            return build_error_response(
                message=f"Configuration error: {str(e)}",
                status_code=500,
                error_type="config_error",
                details={"endpoint": "execute_analysis"}
            )
        
        return log_and_return_error(
            message="Failed to start analysis. Please check your input and try again, or contact support if this persists.",
            status_code=500,
            error_type="analysis_start_error",
            context={"endpoint": "execute_analysis"},
            exception=e
        )