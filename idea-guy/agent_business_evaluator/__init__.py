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
from common.agent import BusinessEvaluationAgent, TierLevel


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Business Evaluation Agent HTTP trigger function processed a request.')

    try:
        # Parse the request body
        req_body = req.get_json()

        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                mimetype="application/json",
                status_code=400,
            )

        # Check if this is a budget options request or execution request
        action = req_body.get("action", "get_budget_options")
        
        # Initialize the agent
        spreadsheet_id = os.getenv("IDEA_GUY_SHEET_ID", "")
        if not spreadsheet_id:
            return func.HttpResponse(
                json.dumps({"error": "IDEA_GUY_SHEET_ID environment variable not set"}),
                mimetype="application/json",
                status_code=500,
            )
        
        client = get_openai_client()
        gc = get_google_sheets_client()
        
        agent = BusinessEvaluationAgent(spreadsheet_id, gc, client)
        
        if action == "get_budget_options":
            # Return budget options for the given input
            user_input = req_body.get("user_input", {})
            
            if not user_input:
                return func.HttpResponse(
                    json.dumps({"error": "user_input is required for budget options"}),
                    mimetype="application/json",
                    status_code=400,
                )
            
            # Validate user input has required fields
            required_fields = ["Idea_Overview", "Deliverable", "Motivation"]
            missing_fields = [field for field in required_fields if field not in user_input or not user_input[field].strip()]
            
            if missing_fields:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing or empty required fields: {missing_fields}"}),
                    mimetype="application/json",
                    status_code=400,
                )
            
            try:
                budget_options = agent.get_budget_options(user_input)
                
                response_data = {
                    "action": "budget_options",
                    "budget_options": budget_options,
                    "user_input": user_input,
                    "message": "Select a budget tier and call again with action='execute' to process the idea",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                
                return func.HttpResponse(
                    json.dumps(response_data), 
                    mimetype="application/json", 
                    status_code=200
                )
                
            except Exception as e:
                logging.error(f"Error getting budget options: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Failed to get budget options: {str(e)}"}),
                    mimetype="application/json",
                    status_code=500,
                )
        
        elif action == "execute":
            # Execute the analysis with selected budget tier
            user_input = req_body.get("user_input", {})
            budget_tier = req_body.get("budget_tier", "")
            
            if not user_input or not budget_tier:
                return func.HttpResponse(
                    json.dumps({"error": "user_input and budget_tier are required for execution"}),
                    mimetype="application/json",
                    status_code=400,
                )
            
            # Validate budget tier
            valid_tiers = [tier.value for tier in TierLevel]
            if budget_tier not in valid_tiers:
                return func.HttpResponse(
                    json.dumps({"error": f"Invalid budget_tier. Must be one of: {valid_tiers}"}),
                    mimetype="application/json",
                    status_code=400,
                )
            
            # Validate user input has required fields
            required_fields = ["Idea_Overview", "Deliverable", "Motivation"]
            missing_fields = [field for field in required_fields if field not in user_input or not user_input[field].strip()]
            
            if missing_fields:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing or empty required fields: {missing_fields}"}),
                    mimetype="application/json",
                    status_code=400,
                )
            
            try:
                # Execute the complete workflow
                result = agent.process_request(user_input, budget_tier)
                
                response_data = {
                    "action": "execute",
                    "message": "Business idea analysis completed successfully",
                    "budget_tier": budget_tier,
                    "result": result,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                
                return func.HttpResponse(
                    json.dumps(response_data), 
                    mimetype="application/json", 
                    status_code=200
                )
                
            except Exception as e:
                logging.error(f"Error executing analysis: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Failed to execute analysis: {str(e)}"}),
                    mimetype="application/json",
                    status_code=500,
                )
        
        else:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid action '{action}'. Must be 'get_budget_options' or 'execute'"}),
                mimetype="application/json",
                status_code=400,
            )

    except json.JSONDecodeError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            mimetype="application/json",
            status_code=400,
        )
    except Exception as e:
        logging.error(f"Unexpected error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}), 
            mimetype="application/json", 
            status_code=500
        )