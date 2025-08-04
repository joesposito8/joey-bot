"""
Integration tests for Jinja template → LangChain → Parser handoff.
Verifies that the enhanced prompts and ResearchOutput model work end-to-end.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Set testing mode before imports
os.environ["TESTING_MODE"] = "true"
os.environ["IDEA_GUY_SHEET_ID"] = "1bGxOTEPxx3vF3UwPAK7SBUAt1dNqVWAvl3W07Zdj4rs"

from common.research_models import ResearchOutput, get_research_output_parser
from common.prompt_manager import prompt_manager
from common.durable_orchestrator import DurableOrchestrator


class TestTemplateLangChainIntegration:
    """Test complete handoff from Jinja templates through LangChain to parsed results."""
    
    def test_enhanced_research_output_format_instructions_completeness(self):
        """Test that parser format instructions include all enhanced ResearchOutput fields."""
        parser = get_research_output_parser()
        format_instructions = parser.get_format_instructions()
        
        # Verify all required fields are documented
        assert "research_topic" in format_instructions
        assert "summary" in format_instructions  
        assert "key_findings" in format_instructions
        assert "confidence_level" in format_instructions
        
        # Verify new enhanced fields are documented
        assert "supporting_evidence" in format_instructions
        assert "implications" in format_instructions
        assert "limitations" in format_instructions
        assert "sources_consulted" in format_instructions
    
    def test_enhanced_research_output_parser_handles_new_fields(self):
        """Test parser correctly handles enhanced ResearchOutput JSON with new fields."""
        parser = get_research_output_parser()
        
        # Enhanced JSON with all new fields
        enhanced_json = json.dumps({
            "research_topic": "AI market analysis with enhanced data",
            "summary": "Comprehensive analysis with multiple data sources and strategic implications",
            "key_findings": [
                "Market size: $50B with 25% CAGR",
                "Key competitors: OpenAI, Anthropic, Google"
            ],
            "supporting_evidence": [
                "IDC report Q3 2024: AI market valuation",
                "Competitor analysis from TechCrunch",
                "USPTO patent filings data"
            ],
            "implications": [
                "High growth opportunity for new entrants",
                "Need for differentiated positioning",
                "Regulatory compliance will be critical"
            ],
            "sources_consulted": ["IDC", "TechCrunch", "USPTO database"],
            "confidence_level": "high",
            "limitations": "Data limited to publicly available sources, may not reflect private market activity"
        })
        
        result = parser.parse(enhanced_json)
        
        # Verify all fields are correctly parsed
        assert isinstance(result, ResearchOutput)
        assert result.research_topic == "AI market analysis with enhanced data"
        assert len(result.key_findings) == 2
        assert len(result.supporting_evidence) == 3
        assert len(result.implications) == 3
        assert len(result.sources_consulted) == 3
        assert result.limitations != ""
        assert result.confidence_level == "high"
    
    def test_backwards_compatibility_minimal_research_output(self):
        """Test parser handles legacy ResearchOutput JSON with only required fields."""
        parser = get_research_output_parser()
        
        # Minimal JSON (like old system would produce)
        minimal_json = json.dumps({
            "research_topic": "Basic market analysis",
            "summary": "Simple summary",
            "key_findings": ["Finding 1", "Finding 2"]
            # No supporting_evidence, implications, limitations, sources_consulted
        })
        
        result = parser.parse(minimal_json)
        
        # Should work with defaults for new fields
        assert isinstance(result, ResearchOutput)
        assert result.research_topic == "Basic market analysis"
        assert len(result.key_findings) == 2
        assert result.supporting_evidence == []  # Default empty list
        assert result.implications == []  # Default empty list
        assert result.sources_consulted == []  # Default empty list
        assert result.limitations == ""  # Default empty string
        assert result.confidence_level == "medium"  # Default
    
    @pytest.mark.asyncio
    async def test_research_call_template_langchain_parse_integration(self):
        """Test complete flow: format_research_call_prompt → LangChain → parse."""
        # Mock agent config
        mock_config = Mock()
        mock_config.definition.starter_prompt = "You are a business analyst specializing in market research."
        mock_config.get_model.return_value = "gpt-4o-mini"
        
        orchestrator = DurableOrchestrator(mock_config)
        
        # Test data
        research_topic = "Market size analysis for AI-powered meal planning applications"
        user_input = {
            "Idea_Overview": "AI-powered meal planning app with nutritional optimization",
            "Deliverable": "Mobile application for iOS and Android"
        }
        
        # Mock LangChain response with enhanced ResearchOutput format
        mock_langchain_response = Mock()
        mock_langchain_response.content = json.dumps({
            "research_topic": research_topic,
            "summary": "Large and rapidly growing market with significant opportunities for AI-powered personalization in meal planning sector.",
            "key_findings": [
                "Global meal planning app market valued at $4.6B in 2023",
                "Expected CAGR of 18.2% through 2030",
                "72% of users willing to pay for premium AI features",
                "Nutritional optimization is underserved niche"
            ],
            "supporting_evidence": [
                "Grand View Research: Meal Planning App Market Report 2024",
                "App Store analysis: Top 50 meal planning apps revenue data",
                "Consumer survey: 1,200 respondents on AI feature preferences"
            ],
            "implications": [
                "Strong market demand supports premium pricing strategy",
                "AI-powered personalization creates defensible competitive moat",
                "B2C freemium model with premium AI features optimal"
            ],
            "sources_consulted": ["Grand View Research", "App Store Connect", "Consumer survey"],
            "confidence_level": "high",
            "limitations": "Market data primarily from US and Europe, limited insight into Asian markets"
        })
        
        # Test the complete integration
        with patch.object(orchestrator, 'langchain_client') as mock_langchain:
            mock_langchain.ainvoke = AsyncMock(return_value=mock_langchain_response)
            
            # Execute the research call (this tests the complete handoff)
            result = await orchestrator.execute_research_call(research_topic, user_input)
            
            # Verify LangChain was called with properly formatted prompt
            mock_langchain.ainvoke.assert_called_once()
            call_args = mock_langchain.ainvoke.call_args[0][0]  # Get the message list
            prompt_content = call_args[0].content  # Get the HumanMessage content
            
            # Verify prompt formatting worked correctly
            assert research_topic in prompt_content
            assert "AI-powered meal planning app" in prompt_content
            assert "Mobile application" in prompt_content
            assert "business analyst" in prompt_content
            assert "research_topic" in prompt_content  # JSON format instructions included
            assert "supporting_evidence" in prompt_content  # Enhanced fields included
            
            # Verify parsing worked correctly
            assert isinstance(result, ResearchOutput)
            assert result.research_topic == research_topic
            assert len(result.key_findings) == 4
            assert len(result.supporting_evidence) == 3
            assert len(result.implications) == 3
            assert result.confidence_level == "high"
            assert result.limitations != ""
    
    def test_synthesis_template_handles_enhanced_research_output(self):
        """Test synthesis template correctly renders enhanced ResearchOutput objects."""
        # Create enhanced ResearchOutput objects
        research_results = [
            ResearchOutput(
                research_topic="Market size and growth analysis",
                summary="Large addressable market with strong growth trajectory",
                key_findings=[
                    "Market valued at $4.6B in 2023",
                    "18.2% CAGR expected through 2030"
                ],
                supporting_evidence=[
                    "Grand View Research market report",
                    "IBISWorld industry analysis"
                ],
                implications=[
                    "Strong revenue potential for new entrants",
                    "Market timing favorable for launch"
                ],
                sources_consulted=["Grand View Research", "IBISWorld"],
                confidence_level="high",
                limitations="Data focused on US/Europe markets"
            ),
            ResearchOutput(
                research_topic="Competitive landscape assessment", 
                summary="Fragmented market with differentiation opportunities",
                key_findings=[
                    "Top 3 competitors hold 35% market share",
                    "AI personalization underutilized"
                ],
                supporting_evidence=[
                    "App Store competitive analysis",
                    "Feature comparison across 20 apps"
                ],
                implications=[
                    "Room for AI-focused differentiation",
                    "Premium positioning viable"
                ],
                confidence_level="medium",
                limitations="Limited access to private company data"
            )
        ]
        
        user_input = {
            "Idea_Overview": "AI-powered meal planning app",
            "Deliverable": "Mobile application"
        }
        
        agent_personality = "You are a senior business analyst"
        
        # Mock output fields
        class MockFieldConfig:
            def __init__(self, name, description):
                self.name = name
                self.description = description
        
        output_fields = [
            MockFieldConfig("Market_Opportunity", "Assessment of market size and opportunity"),
            MockFieldConfig("Competitive_Position", "Analysis of competitive landscape")
        ]
        
        # Test synthesis template rendering
        rendered_prompt = prompt_manager.format_synthesis_call_prompt(
            research_results=research_results,
            user_input=user_input,
            agent_personality=agent_personality,
            output_fields=output_fields
        )
        
        # Verify all enhanced fields are properly rendered
        assert "Market size and growth analysis" in rendered_prompt
        assert "Competitive landscape assessment" in rendered_prompt
        
        # Verify supporting evidence is rendered
        assert "Grand View Research market report" in rendered_prompt
        assert "App Store competitive analysis" in rendered_prompt
        
        # Verify implications are rendered  
        assert "Strong revenue potential" in rendered_prompt
        assert "Room for AI-focused differentiation" in rendered_prompt
        
        # Verify limitations are rendered
        assert "Data focused on US/Europe markets" in rendered_prompt
        assert "Limited access to private company data" in rendered_prompt
        
        # Verify confidence levels are shown
        assert "high" in rendered_prompt
        assert "medium" in rendered_prompt
    
    def test_format_instructions_match_enhanced_model_schema(self):
        """Test that LangChain format instructions exactly match enhanced ResearchOutput schema."""
        parser = get_research_output_parser()
        format_instructions = parser.get_format_instructions()
        
        # Parse the format instructions to verify they create valid ResearchOutput
        # This tests that the parser's instructions are consistent with the model
        
        # Extract sample JSON from format instructions (parser should provide example)
        assert "research_topic" in format_instructions
        assert "summary" in format_instructions
        assert "key_findings" in format_instructions
        assert "supporting_evidence" in format_instructions
        assert "implications" in format_instructions
        assert "sources_consulted" in format_instructions
        assert "confidence_level" in format_instructions
        assert "limitations" in format_instructions
        
        # Verify that all required fields are marked as required
        # and optional fields are marked as optional
        instructions_lower = format_instructions.lower()
        
        # These should be described as required
        assert any(word in instructions_lower for word in ["required", "must", "mandatory"])
        
        # Check that the model validation and format instructions are aligned
        sample_valid_data = {
            "research_topic": "Test topic",
            "summary": "Test summary", 
            "key_findings": ["Finding 1"],
            "supporting_evidence": [],
            "implications": [],
            "sources_consulted": [],
            "confidence_level": "medium",
            "limitations": ""
        }
        
        # This should parse without errors
        result = ResearchOutput(**sample_valid_data)
        assert isinstance(result, ResearchOutput)


class TestEnhancedPromptsEffectiveness:
    """Test that enhanced prompts actually improve output quality."""
    
    def test_research_planning_prompt_includes_strategic_guidance(self):
        """Test that enhanced research planning prompt provides better guidance."""
        template = prompt_manager.get_prompt_template('research_planning')
        
        # Verify enhanced strategic guidance is present
        assert "research architecture expert" in template.lower()
        assert "complementary coverage" in template.lower()
        assert "progressive depth" in template.lower()
        assert "multiple perspectives" in template.lower()
        assert "evidence variety" in template.lower()
        assert "strategic focus" in template.lower()
    
    def test_research_call_prompt_includes_quality_standards(self):
        """Test that enhanced research call prompt provides better execution guidance."""
        template = prompt_manager.get_prompt_template('research_call')
        
        # Verify enhanced research guidance is present
        assert "research mission" in template.lower()
        assert "research approach" in template.lower()
        assert "quality standards" in template.lower()
        assert "concrete evidence" in template.lower()
        assert "quantitative data" in template.lower()
        assert "case studies" in template.lower()
        assert "verifiable information" in template.lower()
    
    def test_synthesis_prompt_includes_analysis_methodology(self):
        """Test that enhanced synthesis prompt provides better analysis guidance.""" 
        template = prompt_manager.get_prompt_template('synthesis_call')
        
        # Verify enhanced synthesis guidance is present
        assert "definitive analysis" in template.lower()
        assert "synthesis approach" in template.lower()
        assert "patterns and connections" in template.lower()
        assert "weigh evidence quality" in template.lower()
        assert "conflicting findings" in template.lower()
        assert "research-backed insights" in template.lower()