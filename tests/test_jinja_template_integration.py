"""Test Jinja2 template integration with ResearchOutput objects."""

import pytest
from common.research_models import ResearchOutput
from common.prompt_manager import prompt_manager


class TestJinjaTemplateIntegration:
    """Test that platform.yaml Jinja2 templates work with ResearchOutput objects."""
    
    def test_synthesis_call_template_renders_research_outputs(self):
        """Test that synthesis_call template can handle List[ResearchOutput]."""
        # Create sample ResearchOutput objects
        research_results = [
            ResearchOutput(
                research_topic="Market size analysis for meal planning apps",
                summary="Large and growing market with significant opportunity",
                key_findings=[
                    "Global meal planning app market valued at $4.6B in 2023",
                    "Expected CAGR of 18.2% through 2030",
                    "72% of users willing to pay for premium features"
                ],
                sources_consulted=["IBISWorld", "Grand View Research"],
                confidence_level="high"
            ),
            ResearchOutput(
                research_topic="Competitive landscape analysis",
                summary="Fragmented market with room for differentiation",
                key_findings=[
                    "Top 3 competitors hold only 35% market share",
                    "Most competitors focus on recipe discovery, not nutrition optimization",
                    "AI-powered personalization is underutilized"
                ],
                sources_consulted=["App Store analysis", "Competitor websites"],
                confidence_level="medium"
            )
        ]
        
        user_input = {
            "Idea_Overview": "AI-powered meal planning app with nutritional optimization",
            "Deliverable": "Mobile application",
            "Motivation": "Help busy professionals eat healthier"
        }
        
        # Mock agent personality and output fields
        agent_personality = "You are a business analyst specializing in mobile app market evaluation."
        
        # Create mock output fields (simplified)
        class MockFieldConfig:
            def __init__(self, name, description):
                self.name = name
                self.description = description
                self.type = "bot output"
                
        output_fields = [
            MockFieldConfig("Novelty_Rating", "Rating of how novel the idea is (1-10)"),
            MockFieldConfig("Market_Analysis", "Analysis of market opportunity")
        ]
        
        # Test template rendering
        try:
            rendered_prompt = prompt_manager.format_synthesis_call_prompt(
                research_results=research_results,
                user_input=user_input,
                agent_personality=agent_personality,
                output_fields=output_fields
            )
            
            # Verify template rendered successfully
            assert isinstance(rendered_prompt, str)
            assert len(rendered_prompt) > 0
            
            # Verify research content was included
            assert "Market size analysis for meal planning apps" in rendered_prompt
            assert "Competitive landscape analysis" in rendered_prompt
            assert "Global meal planning app market valued at $4.6B" in rendered_prompt
            assert "Top 3 competitors hold only 35% market share" in rendered_prompt
            
            # Verify user input was included
            assert "AI-powered meal planning app" in rendered_prompt
            assert "Mobile application" in rendered_prompt
            
            # Verify agent personality was included
            assert "business analyst" in rendered_prompt
            
            # Verify JSON schema structure was included
            assert "Novelty_Rating" in rendered_prompt
            assert "Market_Analysis" in rendered_prompt
            
            # Verify Jinja2 iteration worked (check for multiple research sections)
            research_topic_count = rendered_prompt.count("Research Topic:")
            assert research_topic_count == 2, f"Expected 2 research topics, found {research_topic_count}"
            
            # Verify key findings were properly iterated
            key_findings_count = rendered_prompt.count("Key Findings")
            assert key_findings_count == 2, f"Expected 2 key findings sections, found {key_findings_count}"
            
        except Exception as e:
            pytest.fail(f"Jinja2 template rendering failed: {str(e)}")
    
    def test_synthesis_template_handles_empty_research_results(self):
        """Test template gracefully handles empty research results."""
        research_results = []
        user_input = {"Idea_Overview": "Test idea"}
        agent_personality = "Test agent"
        output_fields = []
        
        # Should not crash with empty research results
        try:
            rendered_prompt = prompt_manager.format_synthesis_call_prompt(
                research_results=research_results,
                user_input=user_input,
                agent_personality=agent_personality,
                output_fields=output_fields
            )
            
            assert isinstance(rendered_prompt, str)
            assert "Test agent" in rendered_prompt
            assert "Test idea" in rendered_prompt
            
        except Exception as e:
            pytest.fail(f"Template should handle empty research results: {str(e)}")
    
    def test_synthesis_template_handles_missing_optional_fields(self):
        """Test template handles ResearchOutput objects with minimal data."""
        # ResearchOutput with only required fields
        research_results = [
            ResearchOutput(
                research_topic="Minimal research topic",
                summary="Basic summary",
                key_findings=["Single finding"]
                # sources_consulted and confidence_level use defaults
            )
        ]
        
        user_input = {"Basic_Input": "Test"}
        agent_personality = "Test agent"
        output_fields = []
        
        try:
            rendered_prompt = prompt_manager.format_synthesis_call_prompt(
                research_results=research_results,
                user_input=user_input,
                agent_personality=agent_personality,
                output_fields=output_fields
            )
            
            assert isinstance(rendered_prompt, str)
            assert "Minimal research topic" in rendered_prompt
            assert "Basic summary" in rendered_prompt
            assert "Single finding" in rendered_prompt
            assert "medium" in rendered_prompt  # Default confidence_level
            
        except Exception as e:
            pytest.fail(f"Template should handle minimal ResearchOutput: {str(e)}")

    def test_synthesis_template_special_characters_handling(self):
        """Test template handles special characters in research data."""
        research_results = [
            ResearchOutput(
                research_topic="Analysis with special chars: & < > \" '",
                summary="Summary with $5.2B revenue & 15% growth",
                key_findings=[
                    "Finding with quotes: \"significant opportunity\"",
                    "Finding with ampersand: R&D investment",
                    "Finding with brackets: <strong>growth</strong>"
                ]
            )
        ]
        
        user_input = {"Test_Input": "Input with & special chars"}
        agent_personality = "Agent with \"quotes\" & ampersands"
        output_fields = []
        
        try:
            rendered_prompt = prompt_manager.format_synthesis_call_prompt(
                research_results=research_results,
                user_input=user_input,
                agent_personality=agent_personality,
                output_fields=output_fields
            )
            
            # Should render without errors
            assert isinstance(rendered_prompt, str)
            assert len(rendered_prompt) > 0
            
        except Exception as e:
            pytest.fail(f"Template should handle special characters: {str(e)}")