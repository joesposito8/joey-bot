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
            # Load universal platform configuration from prompt_manager
            config = prompt_manager._load_common_config()
            platform_config = config.get('platform', {})
            budget_tiers = platform_config.get('budget_tiers', [])
            self._full_config = budget_tiers
        return self._full_config
    
    def get_tier_config(self, tier_name: str) -> BudgetTierConfig:
        """Get configuration for a specific budget tier."""
        tiers = self._get_full_config()
        
        for tier_data in tiers:
            if tier_data['name'] == tier_name:
                return BudgetTierConfig.from_dict(tier_data)
        
        valid_tiers = [tier['name'] for tier in tiers]
        raise ValueError(f"Invalid budget tier '{tier_name}'. Valid tiers: {valid_tiers}")
    
    def get_all_tiers(self) -> List[BudgetTierConfig]:
        """Get all available budget tier configurations."""
        return self._get_full_config()
    
    def get_tier_names(self) -> List[str]:
        """Get list of available tier names."""
        tiers = self._get_full_config()
        return [tier['name'] for tier in tiers]