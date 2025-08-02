from typing import Dict
import azure.functions as func
import datetime
import json
import logging
import os

from common import get_google_sheets_client, get_spreadsheet
from common.agent_service import AnalysisService
from common.http_utils import build_json_response, build_error_response, is_testing_mode, log_and_return_error

ID_COLUMN_INDEX = 0
TIME_COLUMN_INDEX = 1
RESEARCH_PLAN_COLUMN_INDEX = 2


# Lazy initialization to prevent import-time dependencies
_gc = None
_spreadsheet = None


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


def get_analysis_result_from_spreadsheet(job_id: str, service: AnalysisService) -> Dict[str, str] | None:
    """Get completed analysis results from Google Sheets.
    
    Since DurableOrchestrator executes synchronously, results are directly written
    to the spreadsheet. No OpenAI polling is needed.
    
    Args:
        job_id: Job identifier to find in spreadsheet
        service: AnalysisService for schema information
        
    Returns:
        Analysis results dictionary or None if not found/incomplete
    """
    try:
        spreadsheet = get_lazy_spreadsheet()
        worksheet = spreadsheet.get_worksheet(0)

        # Find the job ID in the spreadsheet
        cell = worksheet.find(job_id)
        
        if not cell:
            logging.warning(f"Job ID {job_id} not found in spreadsheet")
            return None
            
        # Ensure the job ID is in the ID column
        if cell.col - 1 != ID_COLUMN_INDEX:
            logging.warning(f"Job ID {job_id} found in wrong column (expected column {ID_COLUMN_INDEX + 1})")
            return None
        
        row_num = cell.row
        
        # Read the entire row to get all data
        row_values = worksheet.row_values(row_num)
        
        if len(row_values) < 3:  # Need at least ID, Time, Research_Plan
            logging.warning(f"Row {row_num} has insufficient data: {len(row_values)} columns")
            return None
        
        # Calculate column positions based on schema
        # Structure: [ID, Time, Research_Plan, ...input_fields, ...output_fields]
        input_fields_count = len(service.agent_config.schema.input_fields)
        output_start_col_0based = 3 + input_fields_count  # 0-based index where output fields start
        output_fields_count = len(service.agent_config.schema.output_fields)
        
        # Check if we have enough columns for output fields
        if len(row_values) < output_start_col_0based + output_fields_count:
            logging.info(f"Analysis not complete yet - missing output data. Row has {len(row_values)} columns, need {output_start_col_0based + output_fields_count}")
            return None
        
        # Extract output field values
        result = {}
        for i, field in enumerate(service.agent_config.schema.output_fields):
            col_index = output_start_col_0based + i  # 0-based indexing
            if col_index < len(row_values):
                value = row_values[col_index].strip()
                if value:  # Only include non-empty values
                    result[field.name] = value
                else:
                    logging.info(f"Output field {field.name} is empty - analysis may not be complete")
                    return None
            else:
                logging.info(f"Output field {field.name} missing - analysis not complete")
                return None
        
        # If we have all output fields populated, analysis is complete
        if len(result) == len(service.agent_config.schema.output_fields):
            logging.info(f"Found complete analysis results for job {job_id}")
            
            # Also extract research plan if available
            if len(row_values) > RESEARCH_PLAN_COLUMN_INDEX:
                research_plan_str = row_values[RESEARCH_PLAN_COLUMN_INDEX].strip()
                if research_plan_str:
                    try:
                        research_plan = json.loads(research_plan_str)
                        result["research_plan"] = research_plan
                    except json.JSONDecodeError:
                        logging.warning(f"Could not parse research plan JSON for job {job_id}")
            
            return result
        else:
            logging.info(f"Analysis incomplete - only {len(result)} of {len(service.agent_config.schema.output_fields)} output fields populated")
            return None
            
    except Exception as e:
        logging.error(f"Error reading analysis results from spreadsheet for job {job_id}: {str(e)}")
        raise ValueError(f"Failed to read analysis results: {str(e)}")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    service = None  # Initialize for error handling scope

    try:
        # Get the job ID from query parameters
        job_id = req.params.get('id')

        if not job_id:
            return log_and_return_error(
                message="Missing 'id' query parameter. Please provide the job ID to get analysis results.",
                status_code=400,
                error_type="missing_job_id",
                context={"endpoint": "summarize_idea"}
            )

        # Check for mock job (testing mode)
        if job_id.startswith("mock_"):
            logging.info(f"Processing mock job: {job_id}")
            
            # Initialize service to get dynamic output fields
            try:
                service = AnalysisService(os.environ['IDEA_GUY_SHEET_ID'])
                output_fields = [field.name for field in service.agent_config.schema.output_fields]
                
                # Generate mock results for all output fields dynamically
                mock_results = {}
                for field in output_fields:
                    if "rating" in field.lower():
                        mock_results[field] = "7"
                    else:
                        mock_results[field] = f"Mock analysis for {field} - this would contain actual evaluation in production"
                
                # Add mock research plan
                mock_results["research_plan"] = {
                    "tier": "standard",
                    "total_calls": 3,
                    "research_calls": 2,
                    "synthesis_calls": 1,
                    "research_topics": [
                        f"Market analysis for {field}" for field in output_fields[:2]
                    ]
                }
                
            except Exception as e:
                logging.warning(f"Could not generate dynamic mock results: {e}")
                # Fallback to generic mock
                mock_results = {
                    "mock_field": "Mock analysis - actual fields determined by agent configuration",
                    "research_plan": {"tier": "basic", "total_calls": 1}
                }
            
            return build_json_response({
                "status": "completed",
                "message": "[TESTING MODE] Mock analysis completed",
                "job_id": job_id,
                "testing_mode": True,
                "note": "This is a mock response for testing - no actual analysis was performed",
                **mock_results,  # Spread dynamic mock results
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
                details={"endpoint": "summarize_idea"}
            )
        
        # Try to get the analysis result from spreadsheet
        try:
            result = get_analysis_result_from_spreadsheet(job_id, service)
            logging.info(f"Retrieved analysis result for job {job_id}: {result is not None}")
        except Exception as e:
            return build_error_response(
                message=f"Failed to retrieve analysis result: {str(e)}",
                status_code=500,
                error_type="result_retrieval_error",
                details={"endpoint": "summarize_idea", "job_id": job_id}
            )

        if result is None:
            # Analysis is not ready yet or job not found
            response_data = {
                "status": "processing",
                "message": "The analysis is still being processed or job ID not found. Please try again later.",
                "job_id": job_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            
            logging.info(f"Job {job_id} not ready or not found")
            return build_json_response(response_data, 202)

        # Analysis is ready
        response_data = {
            "status": "completed",
            "message": "Analysis completed successfully",
            "job_id": job_id,
            **result,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        
        logging.info(f"Successfully retrieved completed analysis for job {job_id}")
        return build_json_response(response_data)

    except ValueError as e:
        # Handle specific errors like missing job ID or analysis failures
        return log_and_return_error(
            message=str(e),
            status_code=400,
            error_type="processing_error",
            context={"endpoint": "summarize_idea", "job_id": job_id},
            exception=e
        )
    except Exception as e:
        return log_and_return_error(
            message="An unexpected error occurred while retrieving your analysis. Please contact support.",
            status_code=500,
            error_type="server_error",
            context={"endpoint": "summarize_idea", "job_id": job_id},
            exception=e
        )