"""Cost tracking system for OpenAI API calls."""
import json
import logging
import os
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from common.http_utils import is_testing_mode


@dataclass
class APICost:
    """Represents the cost of an API call."""
    timestamp: str
    endpoint: str
    model: str
    budget_tier: str
    job_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    user_input_summary: str
    testing_mode: bool
    execution_plan: Optional[Dict[str, Any]] = None  # Store multi-call architecture plan


class CostTracker:
    """Thread-safe cost tracking system for OpenAI API calls."""
    
    def __init__(self, log_file_path: str = "openai_costs.log"):
        """Initialize cost tracker.
        
        Args:
            log_file_path: Path to cost log file
        """
        self.log_file_path = log_file_path
        self._lock = threading.Lock()
    
    def log_api_call(
        self,
        endpoint: str,
        model: str,
        budget_tier: str,
        job_id: str,
        usage_data: Dict[str, Any],
        cost_usd: float,
        user_input: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None,
        execution_plan: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an OpenAI API call with cost information.
        
        Args:
            endpoint: API endpoint called (e.g., 'execute_analysis')
            model: OpenAI model used (e.g., 'gpt-4o-mini')
            budget_tier: Budget tier selected ('basic', 'standard', 'premium')
            job_id: Unique job identifier
            usage_data: Token usage from OpenAI response
            cost_usd: Actual cost in USD
            user_input: User's input data for summary
            additional_context: Optional extra context
        """
        try:
            # Create cost record
            cost_record = APICost(
                timestamp=datetime.utcnow().isoformat() + "Z",
                endpoint=endpoint,
                model=model,
                budget_tier=budget_tier,
                job_id=job_id,
                input_tokens=usage_data.get("prompt_tokens", 0),
                output_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                cost_usd=cost_usd,
                user_input_summary=self._summarize_user_input(user_input),
                testing_mode=is_testing_mode(),
                execution_plan=execution_plan
            )
            
            # Convert to dict for JSON serialization
            record_dict = {
                "timestamp": cost_record.timestamp,
                "endpoint": cost_record.endpoint,
                "model": cost_record.model,
                "budget_tier": cost_record.budget_tier,
                "job_id": cost_record.job_id,
                "tokens": {
                    "input": cost_record.input_tokens,
                    "output": cost_record.output_tokens,
                    "total": cost_record.total_tokens
                },
                "cost_usd": cost_record.cost_usd,
                "user_input_summary": cost_record.user_input_summary,
                "testing_mode": cost_record.testing_mode,
                "execution_plan": cost_record.execution_plan
            }
            
            # Add additional context if provided
            if additional_context:
                record_dict["additional_context"] = additional_context
            
            # Thread-safe file writing
            with self._lock:
                self._write_cost_record(record_dict)
            
            # Also log to application logger
            logging.info(
                f"💰 API Cost Logged: {model} | {budget_tier} | ${cost_usd:.4f} | "
                f"{cost_record.total_tokens} tokens | Job: {job_id[:8]}..."
            )
            
        except Exception as e:
            logging.error(f"Failed to log API cost: {str(e)}", exc_info=True)
    
    def _write_cost_record(self, record: Dict[str, Any]) -> None:
        """Thread-safe writing of cost record to file.
        
        Args:
            record: Cost record dictionary
        """
        # Append as JSON lines format for easy parsing
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\\n")
        except Exception as e:
            logging.error(f"Failed to write cost record to {self.log_file_path}: {str(e)}")
    
    def _summarize_user_input(self, user_input: Dict[str, Any]) -> str:
        """Create a brief summary of user input for logging.
        
        Args:
            user_input: User's input data
            
        Returns:
            Brief summary string
        """
        try:
            idea = user_input.get("Idea_Overview", "")[:100]  # First 100 chars
            if len(user_input.get("Idea_Overview", "")) > 100:
                idea += "..."
            return idea
        except Exception:
            return "Unable to summarize user input"
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get cost summary for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Cost summary dictionary
        """
        try:
            if not os.path.exists(self.log_file_path):
                return {"total_cost": 0, "call_count": 0, "records": []}
            
            records = []
            total_cost = 0.0
            call_count = 0
            
            # Calculate cutoff date
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                        
                        if record_date >= cutoff_date:
                            records.append(record)
                            if not record.get("testing_mode", False):  # Only count real costs
                                total_cost += record.get("cost_usd", 0)
                                call_count += 1
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            return {
                "total_cost_usd": round(total_cost, 4),
                "real_api_calls": call_count,
                "total_records": len(records),
                "days": days,
                "records": records[-10:] if records else []  # Last 10 records
            }
            
        except Exception as e:
            logging.error(f"Failed to get cost summary: {str(e)}")
            return {"error": str(e)}


# Global cost tracker instance
_cost_tracker = None
_tracker_lock = threading.Lock()


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance (singleton pattern).
    
    Returns:
        Global CostTracker instance
    """
    global _cost_tracker
    
    if _cost_tracker is None:
        with _tracker_lock:
            if _cost_tracker is None:
                _cost_tracker = CostTracker()
    
    return _cost_tracker


def log_openai_cost(
    endpoint: str,
    model: str,
    budget_tier: str,
    job_id: str,
    usage_data: Dict[str, Any],
    cost_usd: float,
    user_input: Dict[str, Any],
    execution_plan: Optional[Dict[str, Any]] = None,
    **kwargs
) -> None:
    """Convenience function to log OpenAI API cost.
    
    Args:
        endpoint: API endpoint called
        model: OpenAI model used
        budget_tier: Budget tier selected
        job_id: Unique job identifier
        usage_data: Token usage from OpenAI response
        cost_usd: Actual cost in USD
        user_input: User's input data
        execution_plan: Multi-call architecture execution plan
        **kwargs: Additional context
    """
    tracker = get_cost_tracker()
    tracker.log_api_call(
        endpoint=endpoint,
        model=model,
        budget_tier=budget_tier,
        job_id=job_id,
        usage_data=usage_data,
        cost_usd=cost_usd,
        user_input=user_input,
        additional_context=kwargs if kwargs else None,
        execution_plan=execution_plan
    )


def get_cost_summary(days: int = 30) -> Dict[str, Any]:
    """Get cost summary for the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Cost summary dictionary
    """
    tracker = get_cost_tracker()
    return tracker.get_cost_summary(days)


# OpenAI API pricing (per 1K tokens) - Update these as OpenAI changes pricing
OPENAI_PRICING = {
    "gpt-4o-mini": {
        "input": 0.000150,   # $0.15 per 1K input tokens
        "output": 0.000600   # $0.60 per 1K output tokens
    },
    "o1-mini": {
        "input": 0.003000,   # $3.00 per 1K input tokens
        "output": 0.012000   # $12.00 per 1K output tokens
    },
}


def calculate_cost_from_usage(model: str, usage_data: Dict[str, Any]) -> float:
    """Calculate cost from OpenAI usage data.
    
    Args:
        model: OpenAI model name
        usage_data: Usage data from OpenAI response
        
    Returns:
        Estimated cost in USD
    """
    try:
        if model not in OPENAI_PRICING:
            logging.warning(f"Unknown model {model} for cost calculation")
            return 0.0
        
        pricing = OPENAI_PRICING[model]
        input_tokens = usage_data.get("prompt_tokens", 0)
        output_tokens = usage_data.get("completion_tokens", 0)
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)  # Round to 6 decimal places
        
    except Exception as e:
        logging.error(f"Failed to calculate cost: {str(e)}")
        return 0.0
