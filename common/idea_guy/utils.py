from common.utils import Information


class IdeaGuyUserInput(Information):
    columns = ["Idea_Overview", "Deliverable", "Motivation"]


class IdeaGuyBotOutput(Information):
    columns = [
        "Analysis_Summary",
        "Novelty_Rating",
        "Feasibility_Rating",
        "Effort_Rating",
        "Impact_Rating",
        "Risk_Rating",
        "Overall_Rating",
    ]


def get_idea_analysis_prompt(user_input: IdeaGuyUserInput) -> str:
    user_input_str = "\n".join(
        f"{column}: {user_input.content[column]}" for column in user_input.columns
    )

    bot_output_str = (
        "{\n\t"
        + "\n\t".join(f"{column}: <content>" for column in IdeaGuyBotOutput.columns)
        + "\n}"
    )

    return f"""
    Analyze the following business idea and provide:
    1. A rating from 1-10 (where 10 is excellent)
    2. Detailed notes about the idea's potential, challenges, and recommendations
    
    {user_input_str}
    
    Please respond in JSON format with the following structure:
    {bot_output_str}

    All ratings should be a number between 1 and 10, where 10 is the highest rating.
    """


def get_system_message() -> str:
    user_input_columns_str = "\n".join(IdeaGuyUserInput.columns)

    return f"""You are an expert business analyst who evaluates startup ideas and business opportunities.
    
    Your job is to ask the user for and confirm the values of the following pieces of information:
    {user_input_columns_str}

    For each piece of information, devote a turn in the conversation to ask the user follow-up questions to clarify their answer. Then, repeat the information back to the user to confirm that you have it correct. Do this for each piece of information before you move on to the next one.
    
    Once you have all the information, you will then send that information to an endpoint to be analyzed.
    
    IMPORTANT! Only send the information to the add_idea endpoint once you have summarized the information you have received from the user back to the user and they have cleared you to send it."""
