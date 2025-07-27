"""HTTP utilities for Azure Functions with consistent response formatting."""
import azure.functions as func
import json
import logging
import traceback
import os
from typing import Dict, Any, Optional


def is_testing_mode() -> bool:
    """Check if we're in testing mode to prevent API charges."""
    return (
        os.getenv("TESTING_MODE", "false").lower() == "true" or
        os.getenv("PYTEST_CURRENT_TEST") is not None or
        "test" in os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "").lower()
    )


def build_json_response(
    data: Dict[str, Any], 
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> func.HttpResponse:
    """Build standardized JSON HTTP response.
    
    Args:
        data: Response data dictionary
        status_code: HTTP status code (default: 200)
        headers: Optional HTTP headers
        
    Returns:
        Azure Function HTTP response
    """
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
        
    return func.HttpResponse(
        json.dumps(data),
        status_code=status_code,
        headers=default_headers,
        mimetype="application/json"
    )


def build_error_response(
    message: str, 
    status_code: int = 400,
    error_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    log_level: str = "error",
    include_traceback: bool = False
) -> func.HttpResponse:
    """Build standardized error HTTP response with comprehensive logging.
    
    Args:
        message: Error message for user/ChatGPT bot
        status_code: HTTP status code (default: 400)
        error_type: Optional error type classification
        details: Optional additional error details
        log_level: Logging level (debug, info, warning, error, critical)
        include_traceback: Whether to log full traceback
        
    Returns:
        Azure Function HTTP response with error format
    """
    # Enhanced logging for production debugging
    log_message = f"HTTP {status_code} Error: {message}"
    if error_type:
        log_message += f" (Type: {error_type})"
    if details:
        log_message += f" Details: {details}"
    
    # Log at appropriate level
    logger = logging.getLogger(__name__)
    log_func = getattr(logger, log_level.lower(), logger.error)
    log_func(log_message)
    
    if include_traceback:
        logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # Build user-friendly error response for ChatGPT bot
    error_data = {
        "error": message,
        "status": "error",
        "success": False
    }
    
    if error_type:
        error_data["error_type"] = error_type
    if details:
        error_data["details"] = details
        
    # Add helpful context for ChatGPT bot
    if status_code == 400:
        error_data["suggestion"] = "Please check your request format and required fields"
    elif status_code == 500:
        error_data["suggestion"] = "This is a server error. Please try again or contact support"
    
    # Add testing mode warning if applicable
    if is_testing_mode():
        error_data["testing_mode"] = True
        error_data["note"] = "Running in testing mode - no API charges incurred"
        
    return build_json_response(error_data, status_code)


def log_and_return_error(
    message: str,
    status_code: int = 500,
    error_type: str = "server_error",
    context: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None
) -> func.HttpResponse:
    """Log error comprehensively and return ChatGPT-friendly response.
    
    Args:
        message: User-facing error message
        status_code: HTTP status code
        error_type: Classification of error
        context: Additional context for logging
        exception: Original exception if available
        
    Returns:
        Standardized error response
    """
    # Comprehensive logging for debugging
    log_details = {
        "error_type": error_type,
        "status_code": status_code,
        "message": message,
        "testing_mode": is_testing_mode()
    }
    
    if context:
        log_details["context"] = context
    if exception:
        log_details["exception_type"] = type(exception).__name__
        log_details["exception_message"] = str(exception)
    
    logging.error(f"Error Details: {json.dumps(log_details, indent=2)}")
    
    if exception:
        logging.error(f"Exception traceback: {traceback.format_exc()}")
    
    return build_error_response(
        message=message,
        status_code=status_code,
        error_type=error_type,
        details=context,
        log_level="error",
        include_traceback=True
    )


def validate_json_request(req: func.HttpRequest) -> Dict[str, Any]:
    """Validate and parse JSON request body with detailed error logging.
    
    Args:
        req: Azure Function HTTP request
        
    Returns:
        Parsed JSON data
        
    Raises:
        ValueError: If JSON is invalid or missing
    """
    try:
        req_body = req.get_json()
        if not req_body:
            logging.warning("Received request with empty body")
            raise ValueError("Request body is required. Please provide a JSON object with your request data.")
        
        logging.info(f"Successfully parsed request with keys: {list(req_body.keys())}")
        return req_body
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        raise ValueError(f"Invalid JSON in request body: {str(e)}. Please check your JSON formatting.")
    except Exception as e:
        logging.error(f"Unexpected error parsing request: {str(e)}")
        raise ValueError(f"Failed to parse request: {str(e)}")
