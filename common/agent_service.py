"""Extensible agent service layer for business analysis workflow."""
import datetime
import json
import logging
import uuid
import os
from typing import Dict, Any, Optional

from common import get_openai_client, get_google_sheets_client, get_spreadsheet
from common.budget_config import BudgetConfigManager, TierConfig
from common.idea_guy.utils import IdeaGuyUserInput, get_idea_analysis_prompt
from common.http_utils import is_testing_mode
from common.cost_tracker import log_openai_cost, calculate_cost_from_usage
from common.multi_call_architecture import create_multi_call_analysis


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class AnalysisService:
    """Service for managing business idea analysis workflow."""
    
    def __init__(self, spreadsheet_id: str):
        """Initialize analysis service.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.spreadsheet_id = spreadsheet_id
        self.budget_manager = BudgetConfigManager()
        self._openai_client = None
        self._sheets_client = None
        self._spreadsheet = None
    
    @property
    def openai_client(self):
        """Lazy-initialized OpenAI client."""
        if self._openai_client is None:
            self._openai_client = get_openai_client()
        return self._openai_client
    
    @property
    def sheets_client(self):
        """Lazy-initialized Google Sheets client."""
        if self._sheets_client is None:
            self._sheets_client = get_google_sheets_client()
        return self._sheets_client
    
    @property
    def spreadsheet(self):
        """Lazy-initialized spreadsheet object."""
        if self._spreadsheet is None:
            self._spreadsheet = get_spreadsheet(self.spreadsheet_id, self.sheets_client)
        return self._spreadsheet
    
    def validate_user_input(self, user_input: Dict[str, Any]) -> None:
        """Validate user input against required schema.
        
        Args:
            user_input: User's input data
            
        Raises:
            ValidationError: If validation fails
        """
        if not user_input:
            raise ValidationError("user_input is required")
        
        required_fields = list(IdeaGuyUserInput.columns.keys())
        missing_fields = [
            field for field in required_fields 
            if field not in user_input or not str(user_input[field]).strip()
        ]
        
        if missing_fields:
            raise ValidationError(
                f"Missing or empty required input fields: {missing_fields}"
            )
    
    def get_budget_options(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get available budget tiers for analysis.
        
        Args:
            user_input: User's input data
            
        Returns:
            Budget options with pricing details
        """
        self.validate_user_input(user_input)
        pricepoints = self.budget_manager.calculate_pricepoints(user_input)
        
        return {
            "agent_type": "business_evaluation",
            "pricepoints": pricepoints,
            "user_input": user_input,
            "message": "Select a budget tier and call /api/execute_analysis to start the analysis",
            "next_endpoint": "/api/execute_analysis",
            "timestamp": datetime.datetime.now().isoformat(),
        }
    
    def create_analysis_job(
        self, 
        user_input: Dict[str, Any], 
        budget_tier: str
    ) -> Dict[str, Any]:
        """Create async analysis job with selected budget tier.
        
        Args:
            user_input: User's input data
            budget_tier: Selected budget tier
            
        Returns:
            Job creation response with job ID
            
        Raises:
            ValidationError: If input validation fails
        """
        logging.info(f"Creating analysis job with tier: {budget_tier}")
        
        # Validate inputs
        self.validate_user_input(user_input)
        tier_config = self.budget_manager.get_tier_config(budget_tier)
        
        # Check for testing mode
        if is_testing_mode():
            logging.warning("Running in testing mode - creating mock job")
            return self._create_mock_job(user_input, budget_tier)
        
        # Create spreadsheet record
        job_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self._create_spreadsheet_record(job_id, timestamp, user_input)
            logging.info(f"Created spreadsheet record with ID: {job_id}")
        except Exception as e:
            logging.error(f"Failed to create spreadsheet record: {str(e)}")
            raise ValidationError(f"Failed to create spreadsheet record: {str(e)}")
        
        # Start multi-call analysis architecture
        try:
            analysis_job_id = create_multi_call_analysis(user_input, tier_config, self.openai_client)
            logging.info(f"Started multi-call analysis job: {analysis_job_id}")
        except Exception as e:
            logging.error(f"Failed to start multi-call analysis: {str(e)}")
            raise ValidationError(f"Failed to start analysis: {str(e)}")
        
        return {
            "job_id": analysis_job_id,
            "status": "processing",
            "agent_type": "business_evaluation",
            "budget_tier": budget_tier,
            "spreadsheet_record_id": job_id,
            "message": f"Analysis started with {budget_tier} tier. Use job_id to poll /api/process_idea",
            "next_endpoint": f"/api/process_idea?id={analysis_job_id}",
            "timestamp": datetime.datetime.now().isoformat(),
        }
    
    def _create_spreadsheet_record(
        self, 
        job_id: str, 
        timestamp: str, 
        user_input: Dict[str, Any]
    ) -> None:
        """Create initial spreadsheet record for job tracking.
        
        Args:
            job_id: Unique job identifier
            timestamp: Creation timestamp
            user_input: User's input data
        """
        try:
            worksheet = self.spreadsheet.get_worksheet(0)
            
            # Create row with job ID, timestamp, and input data
            row_data = [job_id, timestamp]
            
            # Add input column values in schema order
            for column in IdeaGuyUserInput.columns.keys():
                row_data.append(user_input.get(column, ""))
            
            # Add empty output columns (will be filled by process_idea)
            for _ in range(len(IdeaGuyUserInput.columns) + 8):  # Approximate output columns
                row_data.append("")
            
            worksheet.append_row(row_data)
            
        except Exception as e:
            logging.error(f"Error creating spreadsheet record: {str(e)}")
            raise ValidationError(f"Failed to create spreadsheet record: {str(e)}")
    
    
    def _estimate_usage_for_tier(self, tier_config: TierConfig) -> Dict[str, Any]:
        """Estimate token usage based on tier configuration.
        
        All tiers use o4-mini-deep-research with multi-call architecture.
        Usage scales with number of calls available.
        
        Args:
            tier_config: Budget tier configuration
            
        Returns:
            Estimated usage data with prompt_tokens, completion_tokens, total_tokens
        """
        # Base estimate per call for o4-mini-deep-research
        prompt_tokens_per_call = 2500
        completion_tokens_per_call = 4000
        
        # Scale by number of calls in the tier
        total_prompt_tokens = prompt_tokens_per_call * tier_config.call_count
        total_completion_tokens = completion_tokens_per_call * tier_config.call_count
        
        return {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens
        }
    
    def _create_mock_job(
        self, 
        user_input: Dict[str, Any], 
        budget_tier: str
    ) -> Dict[str, Any]:
        """Create mock job for testing mode to prevent API charges.
        
        Args:
            user_input: User's input data
            budget_tier: Selected budget tier
            
        Returns:
            Mock job creation response
        """
        mock_job_id = f"mock_{uuid.uuid4()}"
        
        logging.info(f"Created mock job {mock_job_id} for testing (no API charges)")
        
        return {
            "job_id": mock_job_id,
            "status": "processing",
            "agent_type": "business_evaluation",
            "budget_tier": budget_tier,
            "spreadsheet_record_id": mock_job_id,
            "message": f"[TESTING MODE] Mock analysis started with {budget_tier} tier. No API charges incurred.",
            "next_endpoint": f"/api/process_idea?id={mock_job_id}",
            "timestamp": datetime.datetime.now().isoformat(),
            "testing_mode": True,
            "note": "This is a mock job for testing purposes - no actual analysis will be performed"
        }