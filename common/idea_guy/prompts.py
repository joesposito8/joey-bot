"""
Prompts for OpenAI API calls in the idea-guy functions.
"""


def get_idea_analysis_prompt(idea: str) -> str:
    return f"""
    Analyze the following business idea and provide:
    1. A rating from 1-10 (where 10 is excellent)
    2. Detailed notes about the idea's potential, challenges, and recommendations
    
    Idea: {idea}
    
    Please respond in JSON format with the following structure:
    {{
        "rating": <number 1-10>,
        "notes": "<detailed analysis and recommendations>"
    }}
    """


def get_system_message() -> str:
    return "You are an expert business analyst who evaluates startup ideas and business opportunities."
