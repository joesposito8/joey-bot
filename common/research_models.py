"""
Research data models for LangChain structured output parsing.
Used in the research→synthesis workflow for structured JSON handoff.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_openai import ChatOpenAI
from common.utils import clean_json_response


class ResearchOutput(BaseModel):
    """Enhanced structured output model for research phase of analysis workflow.

    This model defines the JSON structure that research calls must return,
    enabling structured handoff to synthesis phase via LangChain PydanticOutputParser.
    """

    research_topic: str = Field(
        description="The specific research topic or question being investigated"
    )

    summary: str = Field(
        description="Concise 2-3 sentence summary of the most important findings"
    )

    key_findings: List[str] = Field(
        description="Specific findings, insights, or conclusions with supporting evidence",
        min_length=1,
    )

    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Specific data points, statistics, examples, or case studies that support findings",
    )

    implications: List[str] = Field(
        default_factory=list,
        description="What these findings mean for the overall analysis or decision-making",
    )

    sources_consulted: List[str] = Field(
        default_factory=list,
        description="List of sources or search queries used in research (optional)",
    )

    confidence_level: str = Field(
        default="medium", description="Confidence level in findings: low, medium, high"
    )

    limitations: str = Field(
        default="",
        description="Any significant gaps, limitations, or caveats in the research",
    )


# Cache parsers to avoid recreating them
_research_parser = None
_list_parser = None
_dict_parser = None


def _get_fixing_llm():
    """Get LLM for OutputFixingParser with proper API key handling."""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for OutputFixingParser")
    
    return ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        api_key=api_key
    )


class LayeredParser:
    """Parser that tries clean_json_response before falling back to base parser."""
    
    def __init__(self, base_parser):
        self.base_parser = base_parser
    
    def parse(self, text: str):
        # Layer 1: Try direct parsing first
        try:
            return self.base_parser.parse(text)
        except Exception:
            # Layer 2: Try with JSON cleaning
            try:
                cleaned = clean_json_response(text)
                return self.base_parser.parse(cleaned)
            except Exception:
                # Let OutputFixingParser handle it as Layer 3
                raise
    
    def get_format_instructions(self):
        return self.base_parser.get_format_instructions()


def get_research_output_parser() -> OutputFixingParser:
    """Get robust LangChain parser for ResearchOutput model with layered JSON fixing.
    
    Layer 1: Direct parsing
    Layer 2: clean_json_response + parsing  
    Layer 3: OutputFixingParser LLM correction

    Returns:
        OutputFixingParser with built-in preprocessing layers
    """
    global _research_parser
    if _research_parser is None:
        base_parser = PydanticOutputParser(pydantic_object=ResearchOutput)
        layered_parser = LayeredParser(base_parser)
        _research_parser = OutputFixingParser.from_llm(
            parser=layered_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _research_parser


def get_json_list_parser() -> OutputFixingParser:
    """Get robust JSON list parser for research planning topics with layered JSON fixing.
    
    Layer 1: Direct parsing
    Layer 2: clean_json_response + parsing  
    Layer 3: OutputFixingParser LLM correction
    
    Returns:
        OutputFixingParser that handles JSON arrays with preprocessing layers
    """
    global _list_parser
    if _list_parser is None:
        base_parser = JsonOutputParser()
        layered_parser = LayeredParser(base_parser)
        _list_parser = OutputFixingParser.from_llm(
            parser=layered_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _list_parser


def get_json_dict_parser() -> OutputFixingParser:
    """Get robust JSON dict parser for synthesis results with layered JSON fixing.
    
    Layer 1: Direct parsing
    Layer 2: clean_json_response + parsing  
    Layer 3: OutputFixingParser LLM correction
    
    Returns:
        OutputFixingParser that handles JSON objects with preprocessing layers
    """
    global _dict_parser
    if _dict_parser is None:
        base_parser = JsonOutputParser()
        layered_parser = LayeredParser(base_parser)
        _dict_parser = OutputFixingParser.from_llm(
            parser=layered_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _dict_parser
