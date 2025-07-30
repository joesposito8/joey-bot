"""Universal Agent Engine for handling any agent type through configuration."""

from typing import Dict, Any, List
import yaml
import json
from pathlib import Path

from .config.models import AgentDefinition, FullAgentConfig, SheetSchema
from .errors import ValidationError, AnalysisError, SchemaError
from .prompt_manager import prompt_manager
from . import get_openai_client, get_google_sheets_client


class UniversalAgentEngine:
    """Single engine handles ANY agent type through configuration."""
    
    def __init__(self):
        """Initialize with universal platform configuration."""
        self._platform_config = None
        self._agent_configs = {}  # Cache agent configs
        
    def load_agent(self, agent_id: str) -> FullAgentConfig:
        """Load agent config from YAML + dynamic schema.
        
        Args:
            agent_id: Identifier for agent (e.g., "business_evaluation")
            
        Returns:
            Complete agent configuration
            
        Raises:
            ValidationError: If agent config is invalid
            SchemaError: If schema cannot be loaded
        """
        # Return cached config if available
        if agent_id in self._agent_configs:
            return self._agent_configs[agent_id]
            
        # Find agent YAML file
        yaml_path = Path("agents") / f"{agent_id}.yaml"
        if not yaml_path.exists():
            raise ValidationError(f"Agent definition not found: {yaml_path}")
            
        # Load agent definition
        agent_def = AgentDefinition.from_yaml(yaml_path)
        
        try:
            # Get service account path from local.settings.json
            settings_path = Path("idea-guy/local.settings.json")
            if not settings_path.exists():
                raise ConfigurationError("local.settings.json not found")
                
            with open(settings_path) as f:
                settings = json.load(f)
                
            key_path = settings["Values"]["GOOGLE_SHEETS_KEY_PATH"]
            
            # Initialize sheets client with service account
            sheets_client = get_google_sheets_client(key_path=key_path)
            # Load complete config including schema
            config = FullAgentConfig.from_definition(agent_def, sheets_client)
            
            # Cache for reuse
            self._agent_configs[agent_id] = config
            return config
            
        except Exception as e:
            raise SchemaError(f"Failed to load schema for {agent_id}: {str(e)}")
    
    def execute_analysis(
        self,
        agent_id: str,
        user_input: Dict[str, Any],
        budget_tier: str
    ) -> Dict[str, Any]:
        """Execute analysis for any agent type.
        
        Args:
            agent_id: Agent identifier
            user_input: User's input data
            budget_tier: Selected budget tier
            
        Returns:
            Analysis results
            
        Raises:
            ValidationError: If input validation fails
            AnalysisError: If analysis execution fails
        """
        # Load agent configuration
        agent = self.load_agent(agent_id)
        
        # Validate user input
        if not agent.schema.validate_input(user_input):
            raise ValidationError("Invalid or missing input fields")
            
        # Get budget tier configuration
        tier = None
        for t in agent.get_budget_tiers():
            if t.name == budget_tier:
                tier = t
                break
        if not tier:
            raise ValidationError(f"Invalid budget tier: {budget_tier}")
            
        try:
            # Create execution plan
            plan = self._plan_execution(agent, tier, user_input)
            
            # Execute plan using OpenAI
            client = get_openai_client()
            result = self._execute_plan(agent, plan, client)
            
            return result
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {str(e)}")
            
    def _plan_execution(
        self,
        agent: FullAgentConfig,
        tier: Any,  # TODO: Add proper type hint after implementing plan types
        user_input: Dict[str, Any]
    ) -> Any:
        """Plan multi-call execution based on budget tier.
        
        Args:
            agent: Agent configuration
            tier: Budget tier configuration
            user_input: User's input data
            
        Returns:
            Execution plan
        """
        # TODO: Implement execution planning
        raise NotImplementedError
            
    def _execute_plan(
        self,
        agent: FullAgentConfig,
        plan: Any,  # TODO: Add proper type hint after implementing plan types
        openai_client: Any
    ) -> Dict[str, Any]:
        """Execute analysis plan.
        
        Args:
            agent: Agent configuration
            plan: Execution plan
            openai_client: OpenAI client
            
        Returns:
            Analysis results
        """
        # TODO: Implement plan execution
        raise NotImplementedError