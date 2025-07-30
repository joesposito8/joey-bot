"""Budget configuration manager - lightweight wrapper around existing functionality."""

from typing import List
from .config.models import BudgetTierConfig, FullAgentConfig, AgentDefinition
from .prompt_manager import prompt_manager


class BudgetConfigManager:
    """Lightweight wrapper for budget tier access using existing FullAgentConfig."""
    
    def __init__(self):
        """Initialize budget config manager."""
        self._full_config = None
    
    def _get_full_config(self) -> FullAgentConfig:
        """Get FullAgentConfig instance to access budget tiers."""
        if self._full_config is None:
            # Create minimal agent definition for universal access
            mock_agent = AgentDefinition(
                agent_id="universal",
                name="Universal Agent",
                sheet_url="",  # Not needed for budget tier access
                starter_prompt=""  # Not needed for budget tier access
            )
            # Create FullAgentConfig which loads universal config
            self._full_config = FullAgentConfig(mock_agent, None)
        return self._full_config
    
    def get_tier_config(self, tier_name: str) -> BudgetTierConfig:
        """Get configuration for a specific budget tier."""
        config = self._get_full_config()
        tiers = config.get_budget_tiers()
        
        for tier in tiers:
            if tier.name == tier_name:
                # Add backwards compatibility attributes
                tier.model = config.get_model('analysis')
                tier.max_cost = tier.price
                tier.max_calls = tier.calls
                return tier
        
        valid_tiers = [tier.name for tier in tiers]
        raise ValueError(f"Invalid budget tier '{tier_name}'. Valid tiers: {valid_tiers}")
    
    def get_all_tiers(self) -> List[BudgetTierConfig]:
        """Get all available budget tier configurations."""
        config = self._get_full_config()
        tiers = config.get_budget_tiers()
        
        # Add backwards compatibility attributes
        for tier in tiers:
            tier.model = config.get_model('analysis')
            tier.max_cost = tier.price
            tier.max_calls = tier.calls
        
        return tiers
    
    def get_tier_names(self) -> List[str]:
        """Get list of available tier names."""
        config = self._get_full_config()
        tiers = config.get_budget_tiers()
        return [tier.name for tier in tiers]