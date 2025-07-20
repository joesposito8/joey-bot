from typing import Dict
import azure.functions as func
import datetime
import json
import logging
import os

from common import get_openai_client, get_google_sheets_client, get_spreadsheet
from common.idea_guy.utils import IdeaGuyUserInput
from common.utils import extract_json_from_text
from common.idea_guy import IdeaGuyBotOutput, ID_COLUMN_INDEX


spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
client = get_openai_client()
gc = get_google_sheets_client()
spreadsheet = get_spreadsheet(spreadsheet_id, gc)


def get_idea_analysis_result(job_id: str) -> Dict[str, str] | None:
    try:
        # Get the response using the job ID
        response = client.responses.retrieve(job_id)

        # Check if the response is ready
        if response.status == "completed":
            # Extract the content from the response
            if hasattr(response, 'output') and response.output:
                # Convert response to string and extract JSON
                response_str = str(response.output[-1].content[0].text)  # type: ignore
                json_result = extract_json_from_text(response_str, IdeaGuyBotOutput())

                if json_result:
                    return json_result
                else:
                    # Return structured raw response if JSON extraction fails
                    return {
                        "raw_response": response_str,
                        "extraction_failed": "True",
                        "validation_failed": "True",
                        "message": "Could not extract or validate structured JSON from response",
                        "expected_fields": ", ".join(
                            list(IdeaGuyBotOutput.columns.keys())
                        ),
                    }
            else:
                raise ValueError("Response completed but no output found")
        elif response.status in ["failed", "cancelled", "incomplete"]:
            error_msg = getattr(response, 'error', 'Unknown error')
            raise ValueError(f"Analysis failed: {error_msg}")
        else:
            # Response is still processing
            return None

    except Exception as e:
        logging.error(f"Error retrieving response {job_id}: {str(e)}")
        raise ValueError(f"Failed to retrieve analysis result: {str(e)}")


def add_bot_output_to_sheet(job_id: str, result: Dict[str, str]):
    try:
        worksheet = spreadsheet.get_worksheet(0)

        cell = worksheet.find(job_id)

        if cell:
            cell_column_index = cell.col - 1
            if cell_column_index == ID_COLUMN_INDEX:
                row_num = cell.row
                start_col = (
                    cell.col + len(IdeaGuyUserInput.columns.keys()) + 2
                )  # + 2 for going to next column over, and timestamp column
                for value in result.values():
                    worksheet.update_cell(row_num, start_col, value)
                    start_col += 1
        else:
            raise ValueError(f"Job ID {job_id} not found in spreadsheet.")
    except Exception as e:
        logging.error(f"Error adding idea to sheet: {str(e)}")
        raise ValueError(f"Failed to add idea to sheet: {str(e)}")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get the job ID from query parameters
        job_id = req.params.get('id')

        if not job_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'id' query parameter"}),
                mimetype="application/json",
                status_code=400,
            )

        # Try to get the analysis result
        result = get_idea_analysis_result(job_id)

        if result is None:
            # Analysis is not ready yet
            response_data = {
                "status": "processing",
                "message": "The idea analysis is still being processed. Please try again later.",
                "job_id": job_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            return func.HttpResponse(
                json.dumps(response_data),
                mimetype="application/json",
                status_code=202,  # Accepted but not completed
            )

        try:
            add_bot_output_to_sheet(job_id, result)
        except ValueError as e:
            logging.error(f"Error adding idea to sheet: {str(e)}")
            return func.HttpResponse(
                json.dumps(
                    {"error": f"Failed to add idea to spreadsheet, because of {e}"}
                ),
                mimetype="application/json",
                status_code=500,
            )

        # Analysis is ready
        response_data = {
            "status": "completed",
            "message": "Idea analysis completed successfully",
            "job_id": job_id,
            **result,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
        )

    except ValueError as e:
        # Handle specific errors like missing job ID, analysis failures, or validation errors
        error_message = str(e)
        if "validation failed" in error_message.lower():
            # For validation errors, provide more detailed information
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": error_message,
                        "type": "validation_error",
                        "expected_fields": list(IdeaGuyBotOutput.columns.keys()),
                    }
                ),
                mimetype="application/json",
                status_code=422,  # Unprocessable Entity for validation errors
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": error_message}),
                mimetype="application/json",
                status_code=400,
            )
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            mimetype="application/json",
            status_code=500,
        )
