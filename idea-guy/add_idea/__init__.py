import azure.functions as func
import datetime
import json
import logging
import os

from common import (
    get_openai_client,
    get_google_sheets_client,
    get_spreadsheet,
)
from common.idea_guy import (
    IDEA_ANALYSIS_MODEL,
    IdeaGuyUserInput,
    get_idea_analysis_prompt,
)


spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
client = get_openai_client()
gc = get_google_sheets_client()
spreadsheet = get_spreadsheet(spreadsheet_id, gc)


def start_idea_analysis(user_input: IdeaGuyUserInput) -> str:
    prompt = get_idea_analysis_prompt(user_input)

    try:
        response = client.responses.create(
            model=IDEA_ANALYSIS_MODEL,
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
            ],
            tools=[{"type": "web_search_preview"}],
            reasoning={"summary": "auto"},
            background=True,
        )

        # Extract the response content
        content = response.id
        if content is None:
            raise ValueError(
                "OpenAI returned an empty response. The analysis could not be initiated."
            )

        return content

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {str(e)}")
        raise ValueError(f"Failed to call OpenAI API. Technical details: {str(e)}")


def add_user_input_to_sheet(job_id: str, user_input: IdeaGuyUserInput) -> bool:
    try:
        worksheet = spreadsheet.get_worksheet(0)

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([job_id, current_date, *user_input.content.values()])

        return True

    except Exception as e:
        logging.error(f"Error adding idea to sheet: {str(e)}")
        return False


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse the request body
        req_body = req.get_json()

        if not req_body or any(
            column not in req_body for column in IdeaGuyUserInput.columns.keys()
        ):
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": f"Expected {IdeaGuyUserInput.columns.keys()}, got {list(req_body.keys())}"
                    }
                ),
                mimetype="application/json",
                status_code=400,
            )

        user_input = IdeaGuyUserInput(req_body)

        for column in user_input.columns.keys():
            if not user_input.content[column] or not user_input.content[column].strip():
                return func.HttpResponse(
                    json.dumps({"error": f"{column} cannot be empty"}),
                    mimetype="application/json",
                    status_code=400,
                )

        job_id = start_idea_analysis(user_input)

        # Add to the spreadsheet
        success = add_user_input_to_sheet(job_id, user_input)

        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to add idea to spreadsheet"}),
                mimetype="application/json",
                status_code=500,
            )

        response_data = {
            "message": "Idea analysis started successfully with job id: " + job_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        return func.HttpResponse(
            json.dumps(response_data), mimetype="application/json", status_code=200
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), mimetype="application/json", status_code=500
        )
