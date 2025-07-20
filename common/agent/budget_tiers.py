"""
Budget tier system for quality-based pricing.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class TierLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"  
    PREMIUM = "premium"


@dataclass
class BudgetTier:
    """Represents a budget tier with associated cost and capabilities."""
    
    level: TierLevel
    name: str
    max_cost: float
    model: str
    description: str
    deliverables: List[str]
    time_estimate: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "level": self.level.value,
            "name": self.name,
            "max_cost": self.max_cost,
            "model": self.model,
            "description": self.description,
            "deliverables": self.deliverables,
            "time_estimate": self.time_estimate
        }


class BudgetSystem:
    """Manages budget tiers and cost estimation for different agent types."""
    
    def __init__(self):
        self.tier_configs = {}
    
    def register_agent_tiers(self, agent_type: str, tiers: List[BudgetTier]):
        """Register budget tiers for a specific agent type."""
        self.tier_configs[agent_type] = {tier.level: tier for tier in tiers}
    
    def get_tiers_for_agent(self, agent_type: str) -> List[BudgetTier]:
        """Get all available tiers for an agent type."""
        if agent_type not in self.tier_configs:
            raise ValueError(f"No tiers configured for agent type: {agent_type}")
        
        return list(self.tier_configs[agent_type].values())
    
    def get_tier(self, agent_type: str, level: TierLevel) -> BudgetTier:
        """Get specific tier for an agent type."""
        if agent_type not in self.tier_configs:
            raise ValueError(f"No tiers configured for agent type: {agent_type}")
        
        if level not in self.tier_configs[agent_type]:
            raise ValueError(f"Tier {level.value} not available for agent type: {agent_type}")
        
        return self.tier_configs[agent_type][level]
    
    def estimate_cost(self, agent_type: str, level: TierLevel, input_data: Dict[str, Any]) -> float:
        """Estimate cost for processing with given tier based on number of o4-mini-deep-research calls."""
        tier = self.get_tier(agent_type, level)
        
        # Cost per o4-mini-deep-research call (approximately $0.10 per call based on usage patterns)
        cost_per_call = 0.10
        
        # Number of calls per tier
        calls_per_tier = {
            TierLevel.BASIC: 2,      # Context + Deep Research
            TierLevel.STANDARD: 7,   # Planner + 5 Components + Synthesizer  
            TierLevel.PREMIUM: 14    # 3 Planner + 8 Components + 3 Synthesizer
        }
        
        num_calls = calls_per_tier.get(level, 2)
        estimated_cost = num_calls * cost_per_call
        
        # Ensure we don't exceed the tier maximum
        final_cost = min(estimated_cost, tier.max_cost)
        return round(final_cost, 2)


# Predefined business evaluation tiers with LangChain call chains
BUSINESS_EVALUATION_TIERS = [
    BudgetTier(
        level=TierLevel.BASIC,
        name="Context + Deep Research", 
        max_cost=0.20,
        model="o4-mini-deep-research",
        description="Context setup + focused deep research (2 calls)",
        deliverables=[
            "Contextual business analysis setup",
            "Deep research on market opportunity",
            "Focused competitor and feasibility analysis",
            "Comprehensive ratings and rationales"
        ],
        time_estimate="8-12 minutes"
    ),
    BudgetTier(
        level=TierLevel.STANDARD,
        name="Planner + Components + Synthesizer",
        max_cost=1.00,
        model="o4-mini-deep-research", 
        description="Multi-agent workflow with specialized components (7 calls)",
        deliverables=[
            "Strategic planning and approach definition",
            "Novelty and innovation analysis",
            "Technical feasibility deep dive",
            "Market impact assessment", 
            "Risk and competitive analysis",
            "Financial and resource requirements",
            "Synthesized comprehensive report"
        ],
        time_estimate="15-25 minutes"
    ),
    BudgetTier(
        level=TierLevel.PREMIUM,
        name="Deep Planning Chain + Components + Multi-Synthesis",
        max_cost=2.50,
        model="o4-mini-deep-research",
        description="Exhaustive multi-stage workflow with iterative refinement (14 calls)",
        deliverables=[
            "Multi-stage strategic planning (3 iterations)",
            "Comprehensive market research (8 specialized analyses)",
            "Cross-validated technical assessment",
            "Investment-grade financial modeling",
            "Risk mitigation strategy development", 
            "Multi-perspective synthesis (3 viewpoints)",
            "Executive summary and actionable recommendations"
        ],
        time_estimate="25-35 minutes"
    )
]