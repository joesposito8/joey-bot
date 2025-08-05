"""
Research data models for LangChain structured output parsing.
Used in the research→synthesis workflow for structured JSON handoff.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_openai import ChatOpenAI


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


def get_research_output_parser() -> OutputFixingParser:
    """Get robust LangChain parser for ResearchOutput model with automatic JSON fixing.

    Returns:
        OutputFixingParser that wraps PydanticOutputParser with automatic retry/fix capability
    """
    global _research_parser
    if _research_parser is None:
        base_parser = PydanticOutputParser(pydantic_object=ResearchOutput)
        _research_parser = OutputFixingParser.from_llm(
            parser=base_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _research_parser


def get_json_list_parser() -> OutputFixingParser:
    """Get robust JSON list parser for research planning topics.
    
    Returns:
        OutputFixingParser that handles JSON arrays with automatic error correction
    """
    global _list_parser
    if _list_parser is None:
        base_parser = JsonOutputParser()
        _list_parser = OutputFixingParser.from_llm(
            parser=base_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _list_parser


def get_json_dict_parser() -> OutputFixingParser:
    """Get robust JSON dict parser for synthesis results.
    
    Returns:
        OutputFixingParser that handles JSON objects with automatic error correction
    """
    global _dict_parser
    if _dict_parser is None:
        base_parser = JsonOutputParser()
        _dict_parser = OutputFixingParser.from_llm(
            parser=base_parser,
            llm=_get_fixing_llm(),
            max_retries=2
        )
    return _dict_parser
