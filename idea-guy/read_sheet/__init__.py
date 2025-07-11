import azure.functions as func
import datetime
import json
import logging
import os

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

# Google Sheets configuration
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
spreadsheet_id: str = os.getenv("IDEA_GUY_SHEET_ID", "")
creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_SHEETS_KEY_PATH"), scopes=SCOPES
)

# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gc = gspread.authorize(creds)
spreadsheet = gc.open_by_key(spreadsheet_id)


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
