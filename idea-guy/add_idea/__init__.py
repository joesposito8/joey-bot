import azure.functions as func
import datetime
import json
import logging
import os

from common import get_openai_client, get_google_sheets_client, get_spreadsheet
from common.idea_guy.prompts import get_idea_analysis_prompt, get_system_message

# Initialize clients
spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
client = get_openai_client()
gc = get_google_sheets_client()
spreadsheet = get_spreadsheet(spreadsheet_id, gc)


def analyze_idea_with_openai(idea: str) -> dict:
    prompt = get_idea_analysis_prompt(idea)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": get_system_message(),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        # Extract the response content
        content = response.choices[0].message.content
        if content is None:
            return {
                "rating": None,
                "notes": "ERROR: OpenAI returned an empty response. The analysis could not be completed.",
            }

        content = content.strip()

        # Try to parse as JSON
        try:
            result = json.loads(content)
            # Validate that the result has the expected structure
            if "rating" not in result or "notes" not in result:
                return {
                    "rating": None,
                    "notes": f"ERROR: OpenAI response missing required fields. Expected 'rating' and 'notes' fields. Received: {content}",
                }
            return result
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
                        if "rating" not in result or "notes" not in result:
                            return {
                                "rating": None,
                                "notes": f"ERROR: OpenAI response missing required fields. Expected 'rating' and 'notes' fields. Received: {content}",
                            }
                        return result
                except (json.JSONDecodeError, ValueError):
                    pass

            # If JSON parsing fails, return error with the raw content
            return {
                "rating": None,
                "notes": f"ERROR: OpenAI response was not valid JSON. Could not parse the analysis. Raw response: {content}",
            }

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {str(e)}")
        return {
            "rating": None,
            "notes": f"ERROR: Failed to call OpenAI API. Technical details: {str(e)}",
        }


def add_idea_to_sheet(idea: str, rating: int, notes: str) -> bool:
    """
    Add the idea and its analysis to the Google Sheet.

    Args:
        idea: The original idea
        rating: The rating from OpenAI
        notes: The analysis notes from OpenAI

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the first worksheet (or create one if it doesn't exist)
        try:
            worksheet = spreadsheet.get_worksheet(0)
        except:
            # Create a new worksheet if none exists
            worksheet = spreadsheet.add_worksheet(title="Ideas", rows=1000, cols=10)
            # Add headers
            worksheet.append_row(
                ["Time", "Description of Idea", "Notes", "Rating (out of 10)"]
            )

        # Add the new row
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([current_date, idea, notes, rating])

        return True

    except Exception as e:
        logging.error(f"Error adding idea to sheet: {str(e)}")
        return False


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to add and analyze ideas"""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse the request body
        req_body = req.get_json()

        if not req_body or 'idea' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'idea' field in request body"}),
                mimetype="application/json",
                status_code=400,
            )

        idea = req_body['idea']

        if not idea or not idea.strip():
            return func.HttpResponse(
                json.dumps({"error": "Idea cannot be empty"}),
                mimetype="application/json",
                status_code=400,
            )

        analysis = analyze_idea_with_openai(idea.strip())
        rating = analysis.get('rating')
        notes = analysis.get('notes', 'No analysis available')

        # Check if the analysis failed
        if rating is None:
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "Idea analysis failed",
                        "details": notes,
                        "idea": idea.strip(),
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                ),
                mimetype="application/json",
                status_code=500,
            )

        # Add to the spreadsheet
        success = add_idea_to_sheet(idea.strip(), rating, notes)

        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to add idea to spreadsheet"}),
                mimetype="application/json",
                status_code=500,
            )

        response_data = {
            "message": "Idea added successfully",
            "idea": idea.strip(),
            "rating": rating,
            "notes": notes,
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
