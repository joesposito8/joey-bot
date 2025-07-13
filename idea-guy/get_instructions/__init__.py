import azure.functions as func
import json
import logging

from common.idea_guy import get_system_message


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for instructions.')

    try:
        instructions = get_system_message()

        response_data = {
            "instructions": instructions,
        }

        return func.HttpResponse(
            json.dumps(response_data), mimetype="application/json", status_code=200
        )

    except Exception as e:
        logging.error(f"Error retrieving instructions: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to retrieve instructions: {str(e)}"}),
            mimetype="application/json",
            status_code=500,
        )
