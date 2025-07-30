"""Universal budget tier configuration manager."""

from typing import List
from .config.models import BudgetTierConfig, FullAgentConfig, AgentDefinition
from .prompt_manager import prompt_manager


class BudgetConfigManager:
    """Manages budget tiers for all agents using universal configuration."""
    
    def __init__(self):
        """Initialize budget config manager with universal configuration."""
        self._full_config = None
    
    def _get_full_config(self) -> FullAgentConfig:
        """Get FullAgentConfig instance with universal settings."""
        if self._full_config is None:
            # Create universal agent definition
            universal_agent = AgentDefinition(
                agent_id="universal",
                name="Universal Agent",
                sheet_url="",  # Universal config only
                starter_prompt=""  # Universal config only
            )
            # Load universal platform configuration
            self._full_config = FullAgentConfig(universal_agent, None)
        return self._full_config
    
    def get_tier_config(self, tier_name: str) -> BudgetTierConfig:
        """Get configuration for a specific budget tier."""
        config = self._get_full_config()
        tiers = config.get_budget_tiers()
        
        for tier in tiers:
            if tier.name == tier_name:
                return tier
        
        valid_tiers = [tier.name for tier in tiers]
        raise ValueError(f"Invalid budget tier '{tier_name}'. Valid tiers: {valid_tiers}")
    
    def get_all_tiers(self) -> List[BudgetTierConfig]:
        """Get all available budget tier configurations."""
        config = self._get_full_config()
        return config.get_budget_tiers()
    
    def get_tier_names(self) -> List[str]:
        """Get list of available tier names."""
        config = self._get_full_config()
        tiers = config.get_budget_tiers()
        return [tier.name for tier in tiers]