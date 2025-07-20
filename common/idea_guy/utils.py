from common.utils import Information


IDEA_ANALYSIS_MODEL = "o4-mini-deep-research"
ID_COLUMN_INDEX = 0
HEADER_ROW_INDEX = 1
FIRST_VALUE_ROW_INDEX = 2


class IdeaGuyUserInput(Information):
    columns = {
        "Idea_Overview": "An overview of the idea being evaluated.",
        "Deliverable": "What will be the product or service that will be delivered?",
        "Motivation": "What is the motivation for the idea? What do I hope to gain from implementing this idea?",
    }


class IdeaGuyBotOutput(Information):
    columns = {
        "Novelty_Rating": "A rating of how novel/unique the idea is (1-10).",
        "Novelty_Rationale": "A paragraph citing competitor analysis, prior art or patent searches, and domain benchmarks."
        "• Calibrated: 1-2 = copycat; 3-4 = incremental; 5-6 = moderately new; "
        "7-8 = fresh twist; 9-10 = groundbreaking.",
        "Feasibility_Rating": "A rating of how feasible the idea is to implement (1-10).",
        "Feasibility_Rationale": "A paragraph referencing required tech stack maturity, cost estimates, team skills, and resource availability."
        "• Calibrated: 1-2 = near-impossible; 3-4 = high hurdles; 5-6 = challenging but doable; "
        "7-8 = realistic; 9-10 = trivial with existing tools.",
        "Effort_Rating": "A rating of the effort required to implement the idea (1-10).",
        "Effort_Rationale": "A paragraph drawing on time estimates, headcount needs, and complexity metrics."
        "• Calibrated: 1-2 = under 1 day; 3-4 = 1-2 weeks; 5-6 = 1-2 months; "
        "7-8 = 3-6 months; 9-10 = 1+ year or large team.",
        "Impact_Rating": "A rating of the potential impact of the idea (1-10).",
        "Impact_Rationale": "A paragraph citing market size (TAM/SAM/SOM), user adoption benchmarks, or social value studies."
        "• Calibrated: 1-2 = niche/pilot; 3-4 = small segment; 5-6 = regional; "
        "7-8 = national; 9-10 = global or multi-sector transformation.",
        "Risk_Rating": "A rating of the risk level associated with the idea (1-10).",
        "Risk_Rationale": "A paragraph identifying top uncertainties: technical, regulatory, market, or competitive."
        "• Calibrated: 1-2 = minimal; 3-4 = low; 5-6 = moderate; 7-8 = high; 9-10 = extreme (likely to fail).",
        "Overall_Rating": "A rating of the overall potential of the idea (1-10)."
        "Please ensure it reflects the weighted interplay of the above ratings given the user's motivation.",
        "Overall_Rationale": "A paragraph explaining how you combined the individual scores and why you chose this aggregate.",
        "Analysis_Summary": "A detailed analysis of the idea."
        "Include any market data, competitor URLs, cost benchmarks, or user-research insights you uncovered.",
        "Potential_Improvements": "A paragraph explaining how you could improve the idea to address its core deficiencies. Keep these limited to changes that affect the core idea, rather than implementation details or next steps.",
    }


def get_idea_analysis_prompt(user_input: IdeaGuyUserInput) -> str:
    user_input_str = "\n".join(
        f"{column}: {user_input.content[column]}"
        for column in user_input.columns.keys()
    )

    bot_output_str = "\n".join(
        f"{column}: {description}"
        for column, description in IdeaGuyBotOutput.columns.items()
    )

    bot_output_json = (
        "{\n\t"
        + "\n\t".join(
            f"{column}: <content>" for column in IdeaGuyBotOutput.columns.keys()
        )
        + "\n}"
    )

    return f"""
    You are a senior partner at a top-tier venture capital firm whose reputation—and track record—depend on your ability to spot winners and weed out losers. You approach every pitch with rigor, realism, and an investor's eye for return on time and capital. Your sole mission today is to evaluate the idea that follows and tell me, sharply and honestly, whether it's worth backing.

    You will not coach on how to build or launch the product—that's someone else's job. Instead, imagine you're briefing your investment committee: present crisp, evidence-backed ratings and rationales for each category in the `IdeaGuyBotOutput` schema (Novelty, Feasibility, Effort, Impact, Risk, Overall), supported by market data, competitor benchmarks, or cost estimates where relevant. Be critical but fair—highlight both the most compelling aspects and the fatal flaws. At the end, give your overall verdict: is this an idea you'd put money (and your name) behind or pass on?

    Here is the input on the idea you are evaluating:
    {user_input_str}
    
    This is what your report should consist of:
    {bot_output_str}


    Before you begin your evaluation, ensure that **all** supporting data and benchmarks are drawn from the **most recent and reliable** sources:

    1. **Recency Check**  
    • Prioritize information dated within the last 12-18 months.  
    • If you must cite older data, clearly note its date and flag its potential obsolescence.

    2. **Source Credibility**  
    • Use reputable market reports (e.g. Gartner, McKinsey), industry publications, company filings, or well-known news outlets.  
    • When referencing competitor metrics or market sizes, link to or name the specific report or webpage.

    3. **Cross-Verification**  
    • Wherever possible, confirm key figures (TAM, user counts, cost estimates) against **at least two independent** sources.  
    • If data conflicts, briefly summarize both sides and explain which you've chosen and why.

    4. **Depth of Investigation**  
    • For each dimension, go beyond high-level claims: drill into concrete numbers (e.g., “X% annual growth,” “Y competitors with $ZM funding”).  
    • Include specific examples or case studies that illustrate opportunities or pitfalls.

    5. **Transparent Limitations**  
    • If any piece of information can't be verified or is speculative, explicitly call that out under the relevant rationale.

    Only once you've done this “deep research” should you proceed to score Novelty, Feasibility, Effort, Impact, Risk, and Overall. Remember: your credibility as a VC depends on both the **accuracy** and **granularity** of your analysis—so leave no stone unturned.


    Please respond in JSON format with the following structure:
    {bot_output_json}

    Please follow the schema EXACTLY, outputting the json between ```json and ```. For ratings, only use numbers between 1 and 10.
    """


def get_system_message() -> str:
    user_input_columns_str = "\n".join(
        f"{column}: {description}"
        for column, description in IdeaGuyUserInput.columns.items()
    )

    return f"""You are an expert business analyst who evaluates startup ideas and business opportunities.
    
    Your job is to ask the user for and confirm the values of the following pieces of information:
    {user_input_columns_str}

    For each piece of information, devote a turn in the conversation to ask the user follow-up questions to clarify their answer. Then, repeat the information back to the user to confirm that you have it correct. Do this for each piece of information before you move on to the next one.
    
    Once you have all the information, you will then send that information to an endpoint to be analyzed.
    
    IMPORTANT! Only send the information to the add_idea endpoint once you have summarized the information you have received from the user back to the user and they have cleared you to send it."""
