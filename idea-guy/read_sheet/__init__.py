import azure.functions as func
import datetime
import json
import logging
import os

from common import get_openai_client, get_google_sheets_client, get_spreadsheet

# Initialize clients
spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
client = get_openai_client()
gc = get_google_sheets_client()
spreadsheet = get_spreadsheet(spreadsheet_id, gc)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to read Google Sheets data"""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        result = {}
        for ws in spreadsheet.worksheets():
            result[ws.title] = []
            values = ws.get_all_values()
            column_headers = values[0]

            for row in values[1:]:
                unit = {}
                for i, value in enumerate(row):
                    unit[column_headers[i]] = value
                result[ws.title].append(unit)

        response_data = {"sheet_data": result}

        return func.HttpResponse(
            json.dumps(response_data), mimetype="application/json", status_code=200
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), mimetype="application/json", status_code=500
        )
