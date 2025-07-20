"""
Business Evaluation Agent implementation with LangChain workflows.
"""

import json
import logging
from typing import Dict, List, Any

import gspread
from openai import OpenAI

from .base_agent import BaseAgent, SheetSchema
from .budget_tiers import BudgetSystem, BudgetTier, TierLevel, BUSINESS_EVALUATION_TIERS
from .langchain_workflows import BusinessEvaluationChains
from common.idea_guy.utils import IdeaGuyUserInput, IdeaGuyBotOutput


class BusinessEvaluationAgent(BaseAgent):
    """Agent specialized for evaluating business ideas."""
    
    def __init__(self, spreadsheet_id: str, gc: gspread.Client, openai_client: OpenAI):
        # Create schema from existing idea-guy classes
        schema = SheetSchema(
            input_columns=IdeaGuyUserInput.columns,
            output_columns=IdeaGuyBotOutput.columns
        )
        
        super().__init__(spreadsheet_id, gc, openai_client, schema)
        
        # Initialize budget system
        self.budget_system = BudgetSystem()
        self.budget_system.register_agent_tiers("business_evaluation", BUSINESS_EVALUATION_TIERS)
        
        # Initialize LangChain workflows
        self.workflows = BusinessEvaluationChains(openai_client)
    
    def get_budget_options(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return available budget options for business evaluation."""
        tiers = self.budget_system.get_tiers_for_agent("business_evaluation")
        options = []
        
        for tier in tiers:
            estimated_cost = self.budget_system.estimate_cost("business_evaluation", tier.level, user_input)
            option = tier.to_dict()
            option["estimated_cost"] = estimated_cost
            options.append(option)
        
        return options
    
    def execute_workflow(self, record_id: str, user_input: Dict[str, Any], budget_tier: str) -> Dict[str, Any]:
        """Execute business evaluation workflow using LangChain call chains."""
        try:
            # Get the tier configuration
            tier_level = TierLevel(budget_tier.lower())
            tier = self.budget_system.get_tier("business_evaluation", tier_level)
            
            logging.info(f"Executing {tier.name} workflow for record {record_id}")
            
            # Execute appropriate LangChain workflow based on budget tier
            if tier_level == TierLevel.BASIC:
                # $0.20: Context + Deep Research (2 calls)
                return self.workflows.basic_workflow(user_input)
            elif tier_level == TierLevel.STANDARD:
                # $1.00: Planner + 5 Components + Synthesizer (7 calls)
                return self.workflows.standard_workflow(user_input)
            else:  # PREMIUM
                # $2.50: Deep Planning Chain (3) + Components (8) + Multi-Synthesis (3) = 14 calls
                return self.workflows.premium_workflow(user_input)
                
        except Exception as e:
            logging.error(f"Error executing LangChain workflow for record {record_id}: {str(e)}")
            # Return fallback response
            return self._create_fallback_response(f"Workflow execution failed: {str(e)}", tier_level)
    
    def _create_fallback_response(self, error_message: str, tier_level: TierLevel) -> Dict[str, Any]:
        """Create a fallback response when workflow execution fails."""
        tier_info = {
            TierLevel.BASIC: "Context + Deep Research workflow (2 calls)",
            TierLevel.STANDARD: "Planner + Components + Synthesizer workflow (7 calls)",
            TierLevel.PREMIUM: "Deep Planning Chain + Multi-Synthesis workflow (14 calls)"
        }
        
        return {
            field: (
                f"Workflow execution failed for {tier_info[tier_level]}. Error: {error_message[:100]}..."
                if "Rationale" in field or "Summary" in field or "Improvements" in field
                else "3" if "Rating" in field 
                else f"Error in {tier_info[tier_level]}: {error_message[:50]}..."
            )
            for field in IdeaGuyBotOutput.columns.keys()
        }