"""
Research data models for LangChain structured output parsing.
Used in the research→synthesis workflow for structured JSON handoff.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


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


def get_research_output_parser() -> PydanticOutputParser[ResearchOutput]:
    """Get configured LangChain parser for ResearchOutput model.

    Returns:
        PydanticOutputParser configured for ResearchOutput structured parsing
    """
    return PydanticOutputParser(pydantic_object=ResearchOutput)
