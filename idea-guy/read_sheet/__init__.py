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

ID_COLUMN_INDEX = 0
HEADER_ROW_INDEX = 1
FIRST_VALUE_ROW_INDEX = 2


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to read Google Sheets data"""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Check for id query parameter
        id_param = req.params.get('id')

        result = {}
        for ws in spreadsheet.worksheets():
            result[ws.title] = []
            values = ws.get_all_values()

            if not values or len(values) < FIRST_VALUE_ROW_INDEX:
                continue

            column_headers = values[HEADER_ROW_INDEX]

            if id_param:
                found_match = False
                for row in values[FIRST_VALUE_ROW_INDEX:]:
                    if row and len(row) > 0 and row[ID_COLUMN_INDEX] == id_param:
                        unit = {}
                        for i, value in enumerate(row):
                            if i < len(column_headers):
                                unit[column_headers[i]] = value
                        result[ws.title].append(unit)
                        found_match = True
                        break

                if not found_match:
                    return func.HttpResponse(
                        json.dumps(
                            {
                                "error": f"No row found with id '{id_param}' in worksheet '{ws.title}'"
                            }
                        ),
                        mimetype="application/json",
                        status_code=404,
                    )
            else:
                for row in values[FIRST_VALUE_ROW_INDEX:]:
                    unit = {}
                    for i, value in enumerate(row):
                        if i < len(column_headers):
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
