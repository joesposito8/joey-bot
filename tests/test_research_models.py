#!/usr/bin/env python3
"""
Test ResearchOutput model and LangChain integration.
Tests structured JSON parsing for research→synthesis workflow.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pydantic import ValidationError

# TODO: Import after implementation
try:
    from common.research_models import ResearchOutput, get_research_output_parser
except ImportError:
    ResearchOutput = None
    get_research_output_parser = None


class TestResearchOutput:
    """Test ResearchOutput Pydantic model validation."""
    
    def test_valid_research_output_creation(self):
        """Test ResearchOutput model with valid data."""
        if ResearchOutput is None:
            pytest.skip("ResearchOutput model not implemented yet")
        
        valid_data = {
            "research_topic": "Mobile fitness app market analysis",
            "summary": "Growing market with opportunities in personalized fitness",
            "key_findings": [
                "Market size is $4.4B and growing 14% annually",
                "Personalization is key differentiator",
                "Users want social features"
            ],
            "sources_consulted": ["web search", "market reports"],
            "confidence_level": "high"
        }
        
        # Should create valid ResearchOutput
        research = ResearchOutput(**valid_data)
        assert research.research_topic == valid_data["research_topic"]
        assert research.summary == valid_data["summary"]
        assert len(research.key_findings) == 3
        assert research.confidence_level == "high"
    
    def test_required_fields_validation(self):
        """Test ResearchOutput fails with missing required fields."""
        if ResearchOutput is None:
            pytest.skip("ResearchOutput model not implemented yet")
        
        incomplete_data = {
            "research_topic": "Test topic"
            # Missing summary and key_findings
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ResearchOutput(**incomplete_data)
        
        # Should fail validation for missing required fields
        assert "summary" in str(exc_info.value)
        assert "key_findings" in str(exc_info.value)
    
    def test_empty_key_findings_validation(self):
        """Test ResearchOutput requires at least one key finding."""
        if ResearchOutput is None:
            pytest.skip("ResearchOutput model not implemented yet")
        
        invalid_data = {
            "research_topic": "Test topic",
            "summary": "Test summary",
            "key_findings": []  # Empty list should fail min_items=1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ResearchOutput(**invalid_data)
        
        assert "at least 1 item" in str(exc_info.value)
    
    def test_default_values(self):
        """Test ResearchOutput default values for optional fields."""
        if ResearchOutput is None:
            pytest.skip("ResearchOutput model not implemented yet")
        
        minimal_data = {
            "research_topic": "Test topic",
            "summary": "Test summary",
            "key_findings": ["Finding 1"]
        }
        
        research = ResearchOutput(**minimal_data)
        assert research.sources_consulted == []
        assert research.confidence_level == "medium"


class TestLangChainIntegration:
    """Test LangChain PydanticOutputParser integration."""
    
    def test_get_research_output_parser(self):
        """Test parser factory function returns configured parser."""
        if get_research_output_parser is None:
            pytest.skip("get_research_output_parser not implemented yet")
        
        parser = get_research_output_parser()
        
        # Should return PydanticOutputParser configured for ResearchOutput
        assert hasattr(parser, 'pydantic_object')
        assert parser.pydantic_object == ResearchOutput
    
    def test_parser_format_instructions(self):
        """Test parser generates proper format instructions."""
        if get_research_output_parser is None:
            pytest.skip("get_research_output_parser not implemented yet")
        
        parser = get_research_output_parser()
        instructions = parser.get_format_instructions()
        
        # Should contain JSON schema instructions
        assert "json" in instructions.lower()
        assert "research_topic" in instructions
        assert "key_findings" in instructions
    
    def test_parser_parses_valid_json(self):
        """Test parser correctly parses valid JSON to ResearchOutput."""
        if get_research_output_parser is None:
            pytest.skip("get_research_output_parser not implemented yet")
        
        parser = get_research_output_parser()
        valid_json = json.dumps({
            "research_topic": "AI market analysis",
            "summary": "Rapid growth expected",
            "key_findings": ["$50B market", "25% CAGR"],
            "confidence_level": "high"
        })
        
        result = parser.parse(valid_json)
        
        # Should return ResearchOutput instance
        assert isinstance(result, ResearchOutput)
        assert result.research_topic == "AI market analysis"
        assert len(result.key_findings) == 2
    
    def test_parser_handles_invalid_json(self):
        """Test parser handles malformed JSON gracefully."""
        if get_research_output_parser is None:
            pytest.skip("get_research_output_parser not implemented yet")
        
        parser = get_research_output_parser()
        invalid_json = "{ invalid json structure"
        
        # Should raise appropriate parsing error
        with pytest.raises(Exception):  # TODO: Specify exact exception type
            parser.parse(invalid_json)