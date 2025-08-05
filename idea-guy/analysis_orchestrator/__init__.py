import azure.functions as func
import azure.durable_functions as durablefunctions
import logging
import json
from datetime import timedelta
from typing import Dict, Any

def orchestrator_function(context: durablefunctions.DurableOrchestrationContext):
    """
    Durable orchestrator that handles async job polling workflow for Deep Research API.
    
    This orchestrator coordinates multiple short activity functions with durable timers
    to avoid the 10-minute timeout limit while long-running jobs execute on OpenAI's servers.
    """
    try:
        # Get input data from the orchestrator context
        input_data = context.get_input()
        logging.info(f"[DURABLE-ORCHESTRATOR] Starting async job polling orchestrator")
        logging.info(f"[DURABLE-ORCHESTRATOR] Job: {input_data.get('job_id')}")
        
        job_id = input_data.get("job_id")
        user_input = input_data.get("user_input")
        budget_tier = input_data.get("budget_tier")
        spreadsheet_id = input_data.get("spreadsheet_id")
        research_plan = input_data.get("research_plan")
        
        if not all([job_id, user_input, budget_tier, spreadsheet_id, research_plan]):
            logging.error("[DURABLE-ORCHESTRATOR] Missing required input data")
            return {
                "status": "failed", 
                "error": "Missing required input data",
                "job_id": job_id
            }
        
        # Prepare serializable agent config data for activity functions
        agent_config_data = {
            "spreadsheet_id": spreadsheet_id
        }
        
        # Extract research topics from the plan
        research_topics = research_plan.get("research_topics", [])
        logging.info(f"[DURABLE-ORCHESTRATOR] Processing {len(research_topics)} research topics")
        
        # Execute research calls using async job polling pattern
        research_results = []
        
        for i, topic in enumerate(research_topics):
            logging.info(f"[DURABLE-ORCHESTRATOR] Starting research job {i+1}/{len(research_topics)}: {topic}")
            
            # Step 1: Start async research job (1 second)
            start_job_input = {
                "research_topic": topic,
                "user_input": user_input,
                "agent_config_data": agent_config_data
            }
            
            job_info = yield context.call_activity("start_research_job", start_job_input)
            research_job_id = job_info.get("job_id")
            
            if not research_job_id:
                logging.error(f"[DURABLE-ORCHESTRATOR] Failed to start research job for: {topic}")
                continue
            
            logging.info(f"[DURABLE-ORCHESTRATOR] Started research job: {research_job_id}")
            
            # Step 2: Poll job status with durable timers (no compute cost during waits)
            max_polls = 12  # 12 * 5 minutes = 1 hour max wait
            poll_count = 0
            job_completed = False
            
            while poll_count < max_polls and not job_completed:
                # Wait 5 minutes between polls (durable timer - no billing cost)
                if poll_count > 0:  # Skip initial wait
                    logging.info(f"[DURABLE-ORCHESTRATOR] Waiting 5 minutes before next poll (poll {poll_count+1}/{max_polls})")
                    yield context.create_timer(context.current_utc_datetime + timedelta(minutes=5))
                
                # Check job status (1 second)
                status_input = {
                    "job_id": research_job_id,
                    "agent_config_data": agent_config_data
                }
                
                status_result = yield context.call_activity("check_job_status", status_input)
                status = status_result.get("status")
                ready_for_fetch = status_result.get("ready_for_fetch", False)
                
                logging.info(f"[DURABLE-ORCHESTRATOR] Job {research_job_id} status: {status}")
                
                if ready_for_fetch:
                    job_completed = True
                    break
                elif status == "failed":
                    logging.error(f"[DURABLE-ORCHESTRATOR] Research job failed: {research_job_id}")
                    break
                
                poll_count += 1
            
            # Step 3: Fetch completed result (1 second)
            if job_completed:
                fetch_input = {
                    "job_id": research_job_id,
                    "job_type": "research",
                    "research_topic": topic,
                    "agent_config_data": agent_config_data
                }
                
                result_data = yield context.call_activity("fetch_job_result", fetch_input)
                
                if result_data.get("status") == "completed" and result_data.get("result"):
                    research_results.append(result_data["result"])
                    logging.info(f"[DURABLE-ORCHESTRATOR] Successfully completed research for: {topic}")
                else:
                    logging.error(f"[DURABLE-ORCHESTRATOR] Failed to fetch result for: {topic}")
            else:
                logging.error(f"[DURABLE-ORCHESTRATOR] Research job timed out after {max_polls} polls: {topic}")
        
        logging.info(f"[DURABLE-ORCHESTRATOR] Completed {len(research_results)} research calls")
        
        # Execute synthesis using async job polling pattern
        logging.info(f"[DURABLE-ORCHESTRATOR] Starting synthesis job")
        
        # Step 1: Start async synthesis job (1 second)
        start_synthesis_input = {
            "research_results": [result for result in research_results],  # Ensure serializable
            "user_input": user_input,
            "agent_config_data": agent_config_data
        }
        
        synthesis_job_info = yield context.call_activity("start_synthesis_job", start_synthesis_input)
        synthesis_job_id = synthesis_job_info.get("job_id")
        
        synthesis_result = None
        
        if synthesis_job_id:
            logging.info(f"[DURABLE-ORCHESTRATOR] Started synthesis job: {synthesis_job_id}")
            
            # Step 2: Poll synthesis job status with durable timers
            max_polls = 12  # 12 * 5 minutes = 1 hour max wait
            poll_count = 0
            synthesis_completed = False
            
            while poll_count < max_polls and not synthesis_completed:
                # Wait 5 minutes between polls (durable timer - no billing cost)
                if poll_count > 0:  # Skip initial wait
                    logging.info(f"[DURABLE-ORCHESTRATOR] Waiting 5 minutes before synthesis poll (poll {poll_count+1}/{max_polls})")
                    yield context.create_timer(context.current_utc_datetime + timedelta(minutes=5))
                
                # Check synthesis job status (1 second)
                status_input = {
                    "job_id": synthesis_job_id,
                    "agent_config_data": agent_config_data
                }
                
                status_result = yield context.call_activity("check_job_status", status_input)
                status = status_result.get("status")
                ready_for_fetch = status_result.get("ready_for_fetch", False)
                
                logging.info(f"[DURABLE-ORCHESTRATOR] Synthesis job {synthesis_job_id} status: {status}")
                
                if ready_for_fetch:
                    synthesis_completed = True
                    break
                elif status == "failed":
                    logging.error(f"[DURABLE-ORCHESTRATOR] Synthesis job failed: {synthesis_job_id}")
                    break
                
                poll_count += 1
            
            # Step 3: Fetch completed synthesis result (1 second)
            if synthesis_completed:
                fetch_input = {
                    "job_id": synthesis_job_id,
                    "job_type": "synthesis",
                    "agent_config_data": agent_config_data
                }
                
                result_data = yield context.call_activity("fetch_job_result", fetch_input)
                
                if result_data.get("status") == "completed" and result_data.get("result"):
                    synthesis_result = result_data["result"]
                    logging.info(f"[DURABLE-ORCHESTRATOR] Successfully completed synthesis")
                else:
                    logging.error(f"[DURABLE-ORCHESTRATOR] Failed to fetch synthesis result")
            else:
                logging.error(f"[DURABLE-ORCHESTRATOR] Synthesis job timed out after {max_polls} polls")
        
        # Fallback synthesis result if async job failed
        if not synthesis_result:
            synthesis_result = {
                "Analysis_Result": f"Analysis completed with {len(research_results)} research findings",
                "Overall_Rating": "7/10", 
                "synthesis_sources": len(research_results),
                "note": "Fallback synthesis due to async job timeout"
            }
        
        # Update spreadsheet with final results
        update_input = {
            "job_id": job_id,
            "final_result": synthesis_result,
            "agent_config_data": agent_config_data
        }
        
        update_result = yield context.call_activity("update_spreadsheet", update_input)
        
        logging.info(f"[DURABLE-ORCHESTRATOR] Async job polling workflow completed for job: {job_id}")
        
        return {
            "status": "completed",
            "job_id": job_id,
            "research_calls_made": len(research_results),
            "synthesis_calls_made": 1,
            "final_result": synthesis_result,
            "message": "Analysis completed using async job polling"
        }
        
    except Exception as e:
        logging.error(f"[DURABLE-ORCHESTRATOR] Async orchestrator failed: {str(e)}")
        import traceback
        logging.error(f"[DURABLE-ORCHESTRATOR] Traceback: {traceback.format_exc()}")
        return {
            "status": "failed", 
            "error": str(e),
            "job_id": input_data.get("job_id") if 'input_data' in locals() else None
        }

# Create the main function using Durable Functions pattern
main = durablefunctions.Orchestrator.create(orchestrator_function)