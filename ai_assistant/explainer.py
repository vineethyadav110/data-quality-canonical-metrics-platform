import os
import json

from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv("ai_assistant/.env")


# Read Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not set. "
        "Add it to ai_assistant/.env"
    )


# Initialize Groq client
client = Groq(api_key=api_key)


# Use the same model as the SQL generator
MODEL = "openai/gpt-oss-120b"


EXPLANATION_SYSTEM_PROMPT = """
You are a business analytics assistant.

Your job is to explain database query results clearly
and accurately for a business user.

Rules:

1. Answer the user's original question directly.
2. Use ONLY the provided query result.
3. Do not invent values, trends, causes, or explanations.
4. Do not introduce information that is not present in the result.
5. Preserve dates and numeric values accurately.
6. Use appropriate business formatting:
   - Currency values should use $ and commas.
   - Rates should be expressed as percentages when appropriate.
   - Large counts should use commas.
7. Keep the answer concise, normally 1-3 sentences.
8. If multiple rows are returned, summarize the relevant result clearly.
9. If the result does not contain enough information to answer,
   explicitly say that the available result is insufficient.
"""


def generate_explanation(
    question: str,
    sql: str,
    results: list[dict],
) -> str:
    """
    Convert a SQL query result into a concise business answer.
    """

    # Handle empty results without asking the LLM to guess.
    if not results:
        return (
            "No matching data was found for that question "
            "in the available analytical dataset."
        )

    result_context = json.dumps(
        results,
        indent=2,
        default=str,
    )

    user_prompt = f"""
User question:

{question}

SQL query used:

{sql}

Query result:

{result_context}

Provide the answer to the user's original question
using only the query result above.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": EXPLANATION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    explanation = response.choices[0].message.content.strip()

    return explanation