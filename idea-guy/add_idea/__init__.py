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
    IdeaGuyBotOutput,
    IdeaGuyUserInput,
    get_idea_analysis_prompt,
)


spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
client = get_openai_client()
gc = get_google_sheets_client()
spreadsheet = get_spreadsheet(spreadsheet_id, gc)


def analyze_idea_with_openai(user_input: IdeaGuyUserInput) -> IdeaGuyBotOutput:
    prompt = get_idea_analysis_prompt(user_input)

    try:
        response = client.chat.completions.create(
            model=IDEA_ANALYSIS_MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        # Extract the response content
        content = response.choices[0].message.content
        if content is None:
            raise ValueError(
                "OpenAI returned an empty response. The analysis could not be completed."
            )

        content = content.strip()

        # Try to parse as JSON
        try:
            result = json.loads(content)
            if any(column not in result for column in IdeaGuyBotOutput.columns.keys()):
                raise ValueError(
                    f"OpenAI response missing required fields. Expected {IdeaGuyBotOutput.columns.keys()} fields. Received: {content}"
                )
            return IdeaGuyBotOutput(data=result)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content and "```" in content:
                try:
                    # Extract content between ```json and ```
                    start = content.find("```json") + 7
                    end = content.rfind("```")
                    if start > 6 and end > start:
                        json_content = content[start:end].strip()
                        result = json.loads(json_content)
                        if any(
                            column not in result
                            for column in IdeaGuyBotOutput.columns.keys()
                        ):
                            raise ValueError(
                                f"OpenAI response missing required fields. Expected {IdeaGuyBotOutput.columns.keys()} fields. Received: {content}"
                            )
                        return IdeaGuyBotOutput(data=result)
                except (json.JSONDecodeError, ValueError):
                    pass

            # If JSON parsing fails, return error with the raw content
            raise ValueError(
                f"OpenAI response was not valid JSON. Could not parse the analysis. Raw response: {content}"
            )

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {str(e)}")
        raise ValueError(f"Failed to call OpenAI API. Technical details: {str(e)}")


def add_idea_to_sheet(
    user_input: IdeaGuyUserInput, bot_output: IdeaGuyBotOutput
) -> bool:
    try:
        # Get the first worksheet (or create one if it doesn't exist)
        worksheet = spreadsheet.get_worksheet(0)

        # Add the new row
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row(
            [current_date, *user_input.content.values(), *bot_output.content.values()]
        )

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

        bot_output = analyze_idea_with_openai(user_input)

        # Check if the analysis failed
        if any(
            bot_output.content[column] is None
            for column in IdeaGuyBotOutput.columns.keys()
        ):
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "Analysis failed, empty fields: "
                        + ", ".join(
                            column
                            for column in IdeaGuyBotOutput.columns.keys()
                            if bot_output.content[column] is None
                        ),
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                ),
                mimetype="application/json",
                status_code=500,
            )

        # Add to the spreadsheet
        success = add_idea_to_sheet(user_input, bot_output)

        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to add idea to spreadsheet"}),
                mimetype="application/json",
                status_code=500,
            )

        response_data = {
            "message": "Idea added successfully",
            **user_input.content,
            **bot_output.content,
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
