"""Budget tier configuration system for extensible agent framework."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class BudgetTier(Enum):
    """Available budget tiers for analysis."""
    BASIC = "basic"
    STANDARD = "standard" 
    PREMIUM = "premium"


@dataclass
class TierConfig:
    """Configuration for a specific budget tier."""
    level: str
    name: str
    max_cost: float
    estimated_cost: float
    model: str
    description: str
    deliverables: List[str]
    time_estimate: str
    tools: List[Dict[str, str]]
    reasoning: Dict[str, str]
    prompt_template: Optional[str] = None
    call_count: int = 1  # Number of API calls available for this tier


class BudgetConfigManager:
    """Manages budget tier configurations for extensible agent system."""
    
    def __init__(self):
        """Initialize with default agent configurations."""
        # All tiers now use the best prompts, tools, and reasoning available
        # Only cost-affecting factors (model, time limits) vary between tiers
        
        # Standard deliverables for all tiers (best quality output)
        standard_deliverables = [
            "Comprehensive ratings with detailed analysis and specific rationales",
            "Deep competitor research with specific examples and URLs",
            "Market sizing with multiple data sources (TAM/SAM/SOM)",
            "Patent and prior art analysis with specific citations",
            "Regulatory and compliance considerations",
            "Risk assessment with detailed mitigation strategies",
            "Implementation roadmap with timeline suggestions",
            "Cost-benefit analysis with financial projections"
        ]
        
        # Best available tools for all tiers
        premium_tools = [{"type": "web_search_preview"}]
        
        # Best reasoning configuration for all tiers
        premium_reasoning = {"summary": "auto"}
        
        self._configs = {
            BudgetTier.BASIC.value: TierConfig(
                level="basic",
                name="Single-Call Analysis",
                max_cost=1.00,
                estimated_cost=1.00,
                model="gpt-4o-mini",  # All tiers use best model
                description="1 optimized call with intelligent architecture planning",
                deliverables=standard_deliverables,
                time_estimate="5-10 minutes",
                tools=premium_tools,
                reasoning=premium_reasoning,
                prompt_template="multi_call_architecture",
                call_count=1
            ),
            BudgetTier.STANDARD.value: TierConfig(
                level="standard",
                name="Triple-Call Analysis", 
                max_cost=3.00,
                estimated_cost=3.00,
                model="gpt-4o-mini",  # All tiers use best model
                description="3 coordinated calls with intelligent architecture planning",
                deliverables=standard_deliverables,
                time_estimate="15-20 minutes",
                tools=premium_tools,
                reasoning=premium_reasoning,
                prompt_template="multi_call_architecture",
                call_count=3
            ),
            BudgetTier.PREMIUM.value: TierConfig(
                level="premium", 
                name="Five-Call Analysis",
                max_cost=5.00,
                estimated_cost=5.00,
                model="gpt-4o-mini",  # All tiers use best model
                description="5 coordinated calls with intelligent architecture planning",
                deliverables=standard_deliverables,
                time_estimate="20-30 minutes",
                tools=premium_tools,
                reasoning=premium_reasoning,
                prompt_template="multi_call_architecture",
                call_count=5
            )
        }
    
    def get_tier_config(self, tier: str) -> TierConfig:
        """Get configuration for specified tier.
        
        Args:
            tier: Budget tier name
            
        Returns:
            Tier configuration
            
        Raises:
            KeyError: If tier not found
        """
        if tier not in self._configs:
            available = list(self._configs.keys())
            raise KeyError(f"Invalid budget tier '{tier}'. Available: {available}")
        return self._configs[tier]
    
    def get_all_tiers(self) -> List[TierConfig]:
        """Get all available tier configurations.
        
        Returns:
            List of all tier configurations
        """
        return list(self._configs.values())
    
    def get_tier_names(self) -> List[str]:
        """Get all available tier names.
        
        Returns:
            List of tier names
        """
        return list(self._configs.keys())
    
    def add_tier(self, tier_config: TierConfig) -> None:
        """Add new tier configuration (for extensibility).
        
        Args:
            tier_config: New tier configuration to add
        """
        self._configs[tier_config.level] = tier_config
    
    def calculate_pricepoints(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate pricing options for given input.
        
        Args:
            user_input: User's input data
            
        Returns:
            List of pricing options with tier details
        """
        pricepoints = []
        for config in self._configs.values():
            pricepoints.append({
                "level": config.level,
                "name": config.name,
                "max_cost": config.max_cost,
                "estimated_cost": config.estimated_cost,
                "model": config.model,
                "description": config.description,
                "deliverables": config.deliverables,
                "time_estimate": config.time_estimate
            })
        return pricepoints
