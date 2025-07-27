from typing import Dict
import azure.functions as func
import datetime
import logging
import os

from common import get_openai_client, get_google_sheets_client, get_spreadsheet
from common.agent_service import AnalysisService
from common.utils import extract_json_from_text
from common.http_utils import build_json_response, build_error_response, is_testing_mode, log_and_return_error
from common.cost_tracker import log_openai_cost, calculate_cost_from_usage

ID_COLUMN_INDEX = 0


# Lazy initialization to prevent import-time dependencies
_client = None
_gc = None
_spreadsheet = None


def get_lazy_client():
    """Get lazily initialized OpenAI client."""
    global _client
    if _client is None:
        _client = get_openai_client()
    return _client


def get_lazy_sheets_client():
    """Get lazily initialized Google Sheets client.""" 
    global _gc
    if _gc is None:
        _gc = get_google_sheets_client()
    return _gc


def get_lazy_spreadsheet():
    """Get lazily initialized spreadsheet."""
    global _spreadsheet
    if _spreadsheet is None:
        spreadsheet_id = os.getenv("IDEA_GUY_SHEET_ID", "")
        if not spreadsheet_id:
            raise ValueError("IDEA_GUY_SHEET_ID environment variable is required")
        _spreadsheet = get_spreadsheet(spreadsheet_id, get_lazy_sheets_client())
    return _spreadsheet


def get_idea_analysis_result(job_id: str, service: AnalysisService) -> Dict[str, str] | None:
    try:
        # Get the response using the job ID
        client = get_lazy_client()
        response = client.responses.retrieve(job_id)

        # Check if the response is ready
        if response.status == "completed":
            # Log actual API costs when job completes
            try:
                if hasattr(response, 'usage') and response.usage and not is_testing_mode():
                    # Extract usage data from completed response
                    usage_data = {
                        "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                        "completion_tokens": getattr(response.usage, 'completion_tokens', 0), 
                        "total_tokens": getattr(response.usage, 'total_tokens', 0)
                    }
                    
                    # Calculate actual cost
                    model = getattr(response, 'model', 'unknown')
                    actual_cost = calculate_cost_from_usage(model, usage_data)
                    
                    # Log actual cost (overrides previous estimate)
                    log_openai_cost(
                        endpoint="process_idea_completion",
                        model=model,
                        budget_tier="unknown",  # Would need to pass this from job creation
                        job_id=job_id,
                        usage_data=usage_data,
                        cost_usd=actual_cost,
                        user_input={"summary": "Analysis completion - see execute_analysis for details"},
                        estimated=False,  # This is actual usage
                        completion_status="completed"
                    )
                    
                    logging.info(f"💰 Actual API cost logged for job {job_id}: ${actual_cost:.4f}")
                    
            except Exception as e:
                logging.warning(f"Failed to log actual API cost for job {job_id}: {str(e)}")
            
            # Extract the content from the response with improved error handling
            if hasattr(response, 'output') and response.output and len(response.output) > 0:
                try:
                    # Safely access nested response structure
                    last_output = response.output[-1]
                    logging.info(f"Response output structure - last_output type: {type(last_output)}")
                    
                    if hasattr(last_output, 'content') and last_output.content and len(last_output.content) > 0:
                        first_content = last_output.content[0]
                        logging.info(f"Response content structure - first_content type: {type(first_content)}")
                        
                        if hasattr(first_content, 'text'):
                            response_str = str(first_content.text)
                            logging.info(f"Successfully extracted response text, length: {len(response_str)}")
                            
                            # Extract JSON from the response text using dynamic schema
                            output_fields = [field.name for field in service.agent_config.schema.output_fields]
                            
                            # Create mock object for compatibility with extract_json_from_text
                            class MockOutput:
                                def __init__(self, fields):
                                    self.columns = {field: f"Dynamic field {field}" for field in fields}
                            
                            mock_output = MockOutput(output_fields)
                            json_result = extract_json_from_text(response_str, mock_output)

                            if json_result:
                                return json_result
                            else:
                                # Return structured raw response if JSON extraction fails
                                logging.warning(f"JSON extraction failed for job {job_id}")
                                return {
                                    "raw_response": response_str,
                                    "extraction_failed": "True",
                                    "validation_failed": "True",
                                    "message": "Could not extract or validate structured JSON from response",
                                    "expected_fields": ", ".join(output_fields),
                                }
                        else:
                            raise ValueError(f"Response content missing text attribute. Available attributes: {dir(first_content)}")
                    else:
                        content_info = f"length: {len(last_output.content) if hasattr(last_output, 'content') and last_output.content else 'None'}"
                        raise ValueError(f"Response output missing content array. Content {content_info}")
                except (IndexError, AttributeError) as e:
                    logging.error(f"Response structure access failed for job {job_id}: {str(e)}")
                    logging.error(f"Response output length: {len(response.output) if response.output else 'None'}")
                    if response.output and len(response.output) > 0:
                        logging.error(f"Last output attributes: {dir(response.output[-1])}")
                    raise ValueError(f"Response structure invalid: {str(e)}")
            else:
                output_info = f"length: {len(response.output) if hasattr(response, 'output') and response.output else 'None'}"
                raise ValueError(f"Response completed but no output found. Output {output_info}, has_output_attr: {hasattr(response, 'output')}")
        elif response.status in ["failed", "cancelled", "incomplete"]:
            error_msg = getattr(response, 'error', 'Unknown error')
            raise ValueError(f"Analysis failed: {error_msg}")
        else:
            # Response is still processing
            return None

    except Exception as e:
        logging.error(f"Error retrieving response {job_id}: {str(e)}")
        raise ValueError(f"Failed to retrieve analysis result: {str(e)}")


def add_bot_output_to_sheet(job_id: str, result: Dict[str, str], service: AnalysisService):
    try:
        spreadsheet = get_lazy_spreadsheet()
        worksheet = spreadsheet.get_worksheet(0)

        cell = worksheet.find(job_id)

        if cell:
            cell_column_index = cell.col - 1
            if cell_column_index == ID_COLUMN_INDEX:
                row_num = cell.row
                start_col = (
                    cell.col + len(service.agent_config.schema.input_fields) + 2
                )  # + 2 for going to next column over, and timestamp column
                
                # Write output in schema order
                for field in service.agent_config.schema.output_fields:
                    value = result.get(field.name, "")
                    worksheet.update_cell(row_num, start_col, value)
                    start_col += 1
        else:
            raise ValueError(f"Job ID {job_id} not found in spreadsheet.")
    except Exception as e:
        logging.error(f"Error adding idea to sheet: {str(e)}")
        raise ValueError(f"Failed to add idea to sheet: {str(e)}")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    service = None  # Initialize for error handling scope

    try:
        # Get the job ID from query parameters
        job_id = req.params.get('id')

        if not job_id:
            return log_and_return_error(
                message="Missing 'id' query parameter. Please provide the job ID to check analysis status.",
                status_code=400,
                error_type="missing_job_id",
                context={"endpoint": "process_idea"}
            )

        # Check for mock job (testing mode)
        if job_id.startswith("mock_"):
            logging.info(f"Processing mock job: {job_id}")
            return build_json_response({
                "status": "completed",
                "message": "[TESTING MODE] Mock analysis completed",
                "job_id": job_id,
                "testing_mode": True,
                "note": "This is a mock response for testing - no actual analysis was performed",
                "mock_results": {
                    "Novelty_Rating": "7",
                    "Novelty_Rationale": "Mock analysis - this would contain actual evaluation in production",
                    "Overall_Rating": "7",
                    "Analysis_Summary": "This is a mock analysis result for testing purposes"
                },
                "timestamp": datetime.datetime.now().isoformat(),
            })
        
        # Initialize service with dynamic configuration
        try:
            service = AnalysisService(os.environ['IDEA_GUY_SHEET_ID'])
        except Exception as e:
            return build_error_response(
                message=f"Configuration error: {str(e)}",
                status_code=500,
                error_type="config_error",
                details={"endpoint": "process_idea"}
            )
        
        # Try to get the analysis result
        try:
            result = get_idea_analysis_result(job_id, service)
            logging.info(f"Retrieved analysis result for job {job_id}: {result is not None}")
        except Exception as e:
            return build_error_response(
                message=f"Failed to retrieve analysis result: {str(e)}",
                status_code=500,
                error_type="result_retrieval_error",
                details={"endpoint": "process_idea", "job_id": job_id}
            )

        if result is None:
            # Analysis is not ready yet
            response_data = {
                "status": "processing",
                "message": "The idea analysis is still being processed. Please try again later.",
                "job_id": job_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            
            logging.info(f"Job {job_id} still processing")
            return build_json_response(response_data, 202)

        try:
            add_bot_output_to_sheet(job_id, result, service)
            logging.info(f"Successfully added analysis results to spreadsheet for job {job_id}")
        except ValueError as e:
            return build_error_response(
                message=f"Analysis completed but failed to save to spreadsheet: {str(e)}",
                status_code=500,
                error_type="spreadsheet_save_error",
                details={"endpoint": "process_idea", "job_id": job_id}
            )

        # Analysis is ready
        response_data = {
            "status": "completed",
            "message": "Idea analysis completed successfully",
            "job_id": job_id,
            **result,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        
        logging.info(f"Successfully completed analysis for job {job_id}")
        return build_json_response(response_data)

    except ValueError as e:
        # Handle specific errors like missing job ID, analysis failures, or validation errors
        error_message = str(e)
        if "validation failed" in error_message.lower():
            return log_and_return_error(
                message=f"Analysis output validation failed: {error_message}",
                status_code=422,
                error_type="output_validation_error",
                context={
                    "endpoint": "process_idea",
                    "job_id": job_id,
                    "expected_fields": [field.name for field in service.agent_config.schema.output_fields] if service else "unknown"
                },
                exception=e
            )
        else:
            return log_and_return_error(
                message=error_message,
                status_code=400,
                error_type="processing_error",
                context={"endpoint": "process_idea", "job_id": job_id},
                exception=e
            )
    except Exception as e:
        return log_and_return_error(
            message="An unexpected error occurred while processing your analysis. Please contact support.",
            status_code=500,
            error_type="server_error",
            context={"endpoint": "process_idea", "job_id": job_id},
            exception=e
        )
