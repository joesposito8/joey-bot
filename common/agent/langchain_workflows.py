"""
LangChain-based workflows for business evaluation with budget-optimized call chains.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableSequence
from openai import OpenAI


class BusinessEvaluationChains:
    """LangChain workflows for business evaluation with different budget tiers."""
    
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client
        
        # Initialize LangChain LLM for o4-mini-deep-research
        # Note: We'll use the OpenAI client directly since o4-mini-deep-research 
        # may not be directly supported in LangChain yet
        
    def _make_deep_research_call(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Make a single o4-mini-deep-research call with proper formatting."""
        try:
            messages = [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]
            
            response = self.openai_client.responses.create(
                model="o4-mini-deep-research",
                input=messages,
                tools=[{"type": "web_search_preview"}],
                reasoning={"summary": "auto"}
            )
            
            # Extract response content
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logging.error(f"Error in deep research call: {str(e)}")
            raise
    
    def basic_workflow(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        $0.20 Budget: Context Agent + Deep Research Call (2 calls total)
        """
        logging.info("Starting Basic Workflow: Context + Deep Research (2 calls)")
        
        try:
            # Call 1: Context Setup Agent
            context_prompt = f"""
            You are a business analysis context agent. Your job is to set up the analytical framework 
            and identify the key areas that need deep research for this business idea.
            
            Business Idea Details:
            - Overview: {user_input['Idea_Overview']}
            - Deliverable: {user_input['Deliverable']}
            - Motivation: {user_input['Motivation']}
            
            Please provide:
            1. A structured analysis framework for this type of business
            2. Key research questions that need investigation
            3. Critical success factors to evaluate
            4. Potential market segments and competitive landscape overview
            5. Initial hypothesis about feasibility and market opportunity
            
            Format your response as a comprehensive setup that will guide the deep research phase.
            """
            
            context_result = self._make_deep_research_call(context_prompt)
            
            # Call 2: Deep Research Agent using context
            research_prompt = f"""
            You are a senior business analyst conducting deep research. Based on the context setup below, 
            provide a comprehensive analysis with specific ratings and detailed research.
            
            CONTEXT FROM SETUP AGENT:
            {context_result}
            
            BUSINESS IDEA TO ANALYZE:
            - Overview: {user_input['Idea_Overview']}
            - Deliverable: {user_input['Deliverable']}
            - Motivation: {user_input['Motivation']}
            
            Conduct deep research and provide detailed analysis in this EXACT JSON format:
            {{
                "Novelty_Rating": <1-10 integer>,
                "Novelty_Rationale": "<detailed analysis with market comparisons and prior art research>",
                "Feasibility_Rating": <1-10 integer>,
                "Feasibility_Rationale": "<technical feasibility analysis with cost estimates and resource requirements>",
                "Effort_Rating": <1-10 integer>,
                "Effort_Rationale": "<development effort analysis with timeline and team size estimates>",
                "Impact_Rating": <1-10 integer>,
                "Impact_Rationale": "<market impact analysis with TAM/SAM/SOM and adoption projections>",
                "Risk_Rating": <1-10 integer>,
                "Risk_Rationale": "<comprehensive risk analysis covering technical, market, regulatory, and competitive risks>",
                "Overall_Rating": <1-10 integer>,
                "Overall_Rationale": "<synthesis of all factors with weighted reasoning>",
                "Analysis_Summary": "<comprehensive market research summary with specific data points, competitor analysis, and strategic insights>",
                "Potential_Improvements": "<specific actionable recommendations to strengthen the core idea>"
            }}
            
            Ensure all ratings are integers 1-10 and all text fields contain detailed, research-backed analysis.
            """
            
            research_result = self._make_deep_research_call(research_prompt)
            
            # Parse the JSON response
            return self._parse_analysis_result(research_result, fallback_context=context_result)
            
        except Exception as e:
            logging.error(f"Error in basic workflow: {str(e)}")
            raise
    
    def standard_workflow(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        $1.00 Budget: Planner + 5 Components + Synthesizer (7 calls total)
        """
        logging.info("Starting Standard Workflow: Planner + Components + Synthesizer (7 calls)")
        
        try:
            # Call 1: Strategic Planner Agent
            planner_prompt = f"""
            You are a strategic planning agent for business analysis. Create a comprehensive analysis 
            plan for this business idea and identify the specific research components needed.
            
            Business Idea:
            - Overview: {user_input['Idea_Overview']}
            - Deliverable: {user_input['Deliverable']}
            - Motivation: {user_input['Motivation']}
            
            Create a detailed analysis plan covering:
            1. Market analysis strategy
            2. Technical feasibility assessment plan
            3. Competitive analysis approach
            4. Financial and resource evaluation framework
            5. Risk assessment methodology
            6. Success metrics and benchmarks to research
            
            Provide specific research questions and methodologies for each component.
            """
            
            plan_result = self._make_deep_research_call(planner_prompt)
            
            # Calls 2-6: Specialized Component Agents
            components = []
            
            # Component 1: Novelty & Innovation Analysis
            novelty_prompt = f"""
            You are a novelty and innovation analysis specialist. Based on the strategic plan:
            
            STRATEGIC PLAN:
            {plan_result}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Conduct deep research on novelty and innovation aspects. Provide:
            - Novelty_Rating (1-10)
            - Novelty_Rationale with competitor analysis, prior art research, and innovation benchmarks
            
            Focus on differentiation, IP landscape, and innovation positioning.
            """
            components.append(("novelty", self._make_deep_research_call(novelty_prompt)))
            
            # Component 2: Technical Feasibility Deep Dive
            feasibility_prompt = f"""
            You are a technical feasibility specialist. Based on the strategic plan:
            
            STRATEGIC PLAN:
            {plan_result}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Conduct deep technical feasibility research. Provide:
            - Feasibility_Rating (1-10)
            - Feasibility_Rationale with technology stack analysis, development complexity, and resource requirements
            
            Focus on technical risks, development timeline, and required expertise.
            """
            components.append(("feasibility", self._make_deep_research_call(feasibility_prompt)))
            
            # Component 3: Market Impact Assessment
            impact_prompt = f"""
            You are a market impact analyst. Based on the strategic plan:
            
            STRATEGIC PLAN:
            {plan_result}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Conduct deep market impact research. Provide:
            - Impact_Rating (1-10)
            - Impact_Rationale with TAM/SAM/SOM analysis, user adoption projections, and market dynamics
            
            Focus on market size, growth potential, and adoption barriers.
            """
            components.append(("impact", self._make_deep_research_call(impact_prompt)))
            
            # Component 4: Risk & Competitive Analysis
            risk_prompt = f"""
            You are a risk and competitive analysis specialist. Based on the strategic plan:
            
            STRATEGIC PLAN:
            {plan_result}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Conduct deep risk and competitive research. Provide:
            - Risk_Rating (1-10)
            - Risk_Rationale covering technical, market, regulatory, and competitive risks
            
            Focus on threat assessment and mitigation strategies.
            """
            components.append(("risk", self._make_deep_research_call(risk_prompt)))
            
            # Component 5: Effort & Resource Analysis
            effort_prompt = f"""
            You are an effort and resource analysis specialist. Based on the strategic plan:
            
            STRATEGIC PLAN:
            {plan_result}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Conduct deep effort and resource research. Provide:
            - Effort_Rating (1-10)
            - Effort_Rationale with timeline estimates, team size requirements, and cost projections
            
            Focus on development effort, operational complexity, and resource optimization.
            """
            components.append(("effort", self._make_deep_research_call(effort_prompt)))
            
            # Call 7: Synthesizer Agent
            synthesizer_prompt = f"""
            You are a synthesis agent that combines all component analyses into a comprehensive evaluation.
            
            STRATEGIC PLAN:
            {plan_result}
            
            COMPONENT ANALYSES:
            {self._format_components(components)}
            
            ORIGINAL BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Synthesize all analyses into the final JSON format:
            {{
                "Novelty_Rating": <extract from novelty analysis>,
                "Novelty_Rationale": "<synthesized novelty analysis>",
                "Feasibility_Rating": <extract from feasibility analysis>,
                "Feasibility_Rationale": "<synthesized feasibility analysis>",
                "Effort_Rating": <extract from effort analysis>,
                "Effort_Rationale": "<synthesized effort analysis>",
                "Impact_Rating": <extract from impact analysis>,
                "Impact_Rationale": "<synthesized impact analysis>",
                "Risk_Rating": <extract from risk analysis>,
                "Risk_Rationale": "<synthesized risk analysis>",
                "Overall_Rating": <calculated overall rating 1-10>,
                "Overall_Rationale": "<comprehensive synthesis explaining the overall assessment>",
                "Analysis_Summary": "<comprehensive summary integrating all component insights>",
                "Potential_Improvements": "<actionable recommendations based on all analyses>"
            }}
            
            Ensure all ratings are integers and provide comprehensive synthesis of the specialized analyses.
            """
            
            synthesis_result = self._make_deep_research_call(synthesizer_prompt)
            
            return self._parse_analysis_result(synthesis_result, fallback_context=plan_result)
            
        except Exception as e:
            logging.error(f"Error in standard workflow: {str(e)}")
            raise
    
    def premium_workflow(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        $2.50 Budget: Deep Planning Chain (3) + Components (8) + Multi-Synthesis (3) = 14 calls total
        """
        logging.info("Starting Premium Workflow: Deep Planning + Components + Multi-Synthesis (14 calls)")
        
        try:
            # Calls 1-3: Deep Planning Chain
            planning_results = []
            
            # Planning Call 1: Market Intelligence
            market_intel_prompt = f"""
            You are a market intelligence strategist. Conduct deep market research planning for:
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Develop comprehensive market intelligence strategy covering:
            1. Competitive landscape mapping methodology
            2. Market sizing and segmentation approach
            3. Customer development and validation framework
            4. Industry trend analysis plan
            5. Regulatory and compliance research approach
            
            Provide detailed research methodologies and specific data sources to investigate.
            """
            planning_results.append(("market_intelligence", self._make_deep_research_call(market_intel_prompt)))
            
            # Planning Call 2: Technical Architecture Planning
            tech_planning_prompt = f"""
            You are a technical architecture strategist. Based on the market intelligence:
            
            MARKET INTELLIGENCE:
            {planning_results[0][1]}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Develop comprehensive technical planning covering:
            1. Technology stack evaluation framework
            2. Scalability and performance requirements analysis
            3. Integration and API strategy planning
            4. Security and compliance technical requirements
            5. Development methodology and timeline planning
            
            Focus on technical feasibility and implementation strategy.
            """
            planning_results.append(("technical_planning", self._make_deep_research_call(tech_planning_prompt)))
            
            # Planning Call 3: Business Model Strategy
            business_model_prompt = f"""
            You are a business model strategist. Based on previous planning:
            
            MARKET INTELLIGENCE:
            {planning_results[0][1]}
            
            TECHNICAL PLANNING:
            {planning_results[1][1]}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Develop comprehensive business model strategy covering:
            1. Revenue model optimization
            2. Customer acquisition and retention strategy
            3. Partnership and distribution planning
            4. Financial modeling and unit economics
            5. Risk mitigation and contingency planning
            
            Integrate market and technical insights into business viability assessment.
            """
            planning_results.append(("business_model", self._make_deep_research_call(business_model_prompt)))
            
            # Calls 4-11: Enhanced Component Analysis (8 specialized components)
            component_results = []
            
            component_specs = [
                ("novelty_deep", "Deep Novelty & IP Analysis", "patent landscape, innovation benchmarks, differentiation analysis"),
                ("feasibility_deep", "Technical Feasibility Deep Dive", "architecture analysis, scalability assessment, technical risks"),
                ("market_deep", "Market Opportunity Analysis", "TAM/SAM/SOM, customer segmentation, adoption modeling"),
                ("competitive_deep", "Competitive Intelligence", "competitor SWOT, market positioning, competitive advantages"),
                ("financial_deep", "Financial Modeling", "unit economics, funding requirements, financial projections"),
                ("regulatory_deep", "Regulatory & Compliance", "legal requirements, compliance costs, regulatory risks"),
                ("operational_deep", "Operational Analysis", "resource requirements, operational complexity, scalability"),
                ("strategic_deep", "Strategic Positioning", "market entry strategy, strategic partnerships, growth vectors")
            ]
            
            for comp_id, comp_name, comp_focus in component_specs:
                component_prompt = f"""
                You are a {comp_name} specialist. Based on the comprehensive planning:
                
                PLANNING CONTEXT:
                {self._format_planning_results(planning_results)}
                
                BUSINESS IDEA:
                {self._format_user_input(user_input)}
                
                Conduct deep analysis focusing on: {comp_focus}
                
                Provide comprehensive research findings and specific recommendations for this domain.
                Include quantitative data, benchmarks, and actionable insights.
                """
                component_results.append((comp_id, self._make_deep_research_call(component_prompt)))
            
            # Calls 12-14: Multi-Perspective Synthesis (3 synthesis calls)
            synthesis_results = []
            
            # Synthesis 1: Investment Perspective
            investment_synthesis_prompt = f"""
            You are an investment analyst synthesizing from an investor perspective.
            
            PLANNING CONTEXT:
            {self._format_planning_results(planning_results)}
            
            COMPONENT ANALYSES:
            {self._format_component_results(component_results)}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Provide investment-focused analysis with specific ratings and rationales focusing on:
            - Investment attractiveness and ROI potential
            - Market opportunity and scalability
            - Risk assessment and mitigation
            - Competitive positioning and moats
            """
            synthesis_results.append(("investment", self._make_deep_research_call(investment_synthesis_prompt)))
            
            # Synthesis 2: Operational Perspective
            operational_synthesis_prompt = f"""
            You are an operational strategist synthesizing from an execution perspective.
            
            PLANNING CONTEXT:
            {self._format_planning_results(planning_results)}
            
            COMPONENT ANALYSES:
            {self._format_component_results(component_results)}
            
            INVESTMENT PERSPECTIVE:
            {synthesis_results[0][1]}
            
            BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Provide operation-focused analysis covering:
            - Implementation feasibility and execution complexity
            - Resource requirements and operational challenges
            - Timeline and milestone planning
            - Success metrics and KPIs
            """
            synthesis_results.append(("operational", self._make_deep_research_call(operational_synthesis_prompt)))
            
            # Synthesis 3: Final Integration
            final_synthesis_prompt = f"""
            You are a senior business strategist providing the final integrated analysis.
            
            COMPREHENSIVE RESEARCH CONTEXT:
            
            Planning Results:
            {self._format_planning_results(planning_results)}
            
            Component Analyses:
            {self._format_component_results(component_results)}
            
            Investment Perspective:
            {synthesis_results[0][1]}
            
            Operational Perspective:
            {synthesis_results[1][1]}
            
            ORIGINAL BUSINESS IDEA:
            {self._format_user_input(user_input)}
            
            Synthesize ALL analyses into the final comprehensive JSON format:
            {{
                "Novelty_Rating": <1-10 integer based on integrated analysis>,
                "Novelty_Rationale": "<comprehensive novelty analysis integrating all perspectives>",
                "Feasibility_Rating": <1-10 integer based on integrated analysis>,
                "Feasibility_Rationale": "<comprehensive feasibility analysis>",
                "Effort_Rating": <1-10 integer based on integrated analysis>,
                "Effort_Rationale": "<comprehensive effort analysis>",
                "Impact_Rating": <1-10 integer based on integrated analysis>,
                "Impact_Rationale": "<comprehensive impact analysis>",
                "Risk_Rating": <1-10 integer based on integrated analysis>,
                "Risk_Rationale": "<comprehensive risk analysis>",
                "Overall_Rating": <1-10 integer reflecting overall assessment>,
                "Overall_Rationale": "<executive summary integrating investment and operational perspectives>",
                "Analysis_Summary": "<comprehensive analysis summary with key findings from all 14 research calls>",
                "Potential_Improvements": "<strategic recommendations based on comprehensive multi-perspective analysis>"
            }}
            
            This is the culmination of 14 specialized research calls. Ensure the analysis reflects the depth and breadth of investigation.
            """
            
            final_result = self._make_deep_research_call(final_synthesis_prompt)
            
            return self._parse_analysis_result(
                final_result, 
                fallback_context=self._create_premium_fallback_context(planning_results, component_results, synthesis_results)
            )
            
        except Exception as e:
            logging.error(f"Error in premium workflow: {str(e)}")
            raise
    
    def _format_user_input(self, user_input: Dict[str, Any]) -> str:
        """Format user input for prompts."""
        return f"""
        Overview: {user_input['Idea_Overview']}
        Deliverable: {user_input['Deliverable']}
        Motivation: {user_input['Motivation']}
        """
    
    def _format_components(self, components: List[tuple]) -> str:
        """Format component results for synthesis."""
        formatted = ""
        for comp_type, result in components:
            formatted += f"\n{comp_type.upper()} ANALYSIS:\n{result}\n"
        return formatted
    
    def _format_planning_results(self, planning_results: List[tuple]) -> str:
        """Format planning results."""
        formatted = ""
        for plan_type, result in planning_results:
            formatted += f"\n{plan_type.upper()}:\n{result}\n"
        return formatted
    
    def _format_component_results(self, component_results: List[tuple]) -> str:
        """Format component analysis results."""
        formatted = ""
        for comp_id, result in component_results:
            formatted += f"\n{comp_id.upper()}:\n{result}\n"
        return formatted
    
    def _create_premium_fallback_context(self, planning_results, component_results, synthesis_results) -> str:
        """Create fallback context for premium workflow."""
        return f"""
        PREMIUM WORKFLOW CONTEXT:
        Planning: {len(planning_results)} strategic planning calls
        Components: {len(component_results)} specialized analysis calls  
        Synthesis: {len(synthesis_results)} perspective synthesis calls
        Total Research Depth: 14 specialized research calls completed
        """
    
    def _parse_analysis_result(self, result: str, fallback_context: str = "") -> Dict[str, Any]:
        """Parse the JSON result from analysis, with fallback handling."""
        from common.idea_guy.utils import IdeaGuyBotOutput
        
        # Try to extract JSON from the response
        try:
            # Look for JSON between ```json and ``` markers
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_content = result[json_start:json_end].strip()
            elif "{" in result and "}" in result:
                # Try to extract JSON from the response
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_content = result[json_start:json_end]
            else:
                json_content = result
            
            parsed_result = json.loads(json_content)
            
            # Ensure all required fields are present
            for field in IdeaGuyBotOutput.columns.keys():
                if field not in parsed_result:
                    parsed_result[field] = f"Analysis component missing for {field}"
            
            return parsed_result
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse JSON result: {e}")
            
            # Create fallback response with error context
            return {
                field: f"Analysis parsing failed: {str(e)[:100]}..." if "Rationale" in field or "Summary" in field or "Improvements" in field
                else "5" if "Rating" in field else f"Error: {str(e)[:50]}..."
                for field in IdeaGuyBotOutput.columns.keys()
            }