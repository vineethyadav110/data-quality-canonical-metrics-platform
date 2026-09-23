import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from ai_assistant.schema_context import (
    METRIC_DEFINITIONS,
    DIMENSION_DEFINITIONS,
)
from ai_assistant.prompts import SYSTEM_PROMPT
from ai_assistant.database.adapter import get_active_dialect

DATABASE_DIALECT = get_active_dialect()

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv("ai_assistant/.env")

# ---------------------------------------------------------
# Groq API configuration
# ---------------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to ai_assistant/.env")

client = Groq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"

# ---------------------------------------------------------
# Database Dialect Configuration
# ---------------------------------------------------------
DATABASE_DIALECT = "sqlite"


def normalize_question(question: str) -> str:
    """
    Normalize user-entered natural-language questions
    before sending them to the LLM.
    Removes trailing question marks.
    """
    if not isinstance(question, str):
        raise TypeError("Question must be a string.")
    cleaned = question.strip()
    cleaned = re.sub(r"[?？]+$", "", cleaned).strip()
    return cleaned


def generate_sql(question: str) -> str:
    """
    Convert a natural-language analytics question
    into a read-only SQL query using the approved semantic layer.
    """
    clean_question = normalize_question(question)
    if not clean_question:
        raise ValueError("Question cannot be empty.")

    schema_context = json.dumps(
        {
            "metrics": METRIC_DEFINITIONS,
            "dimensions": DIMENSION_DEFINITIONS,
        },
        indent=2,
    )

    user_prompt = f"""
Database dialect: {DATABASE_DIALECT}

Available canonical metrics and dimensions:
{schema_context}

Rules for query generation:
- Use the approved canonical metric tables.
- Approved dimensions may be used for filtering, grouping, and ordering.
- Use trip_date to answer questions about specific trip dates.
- Use pipeline_date for data-quality pipeline dates.
- Generate SQL compatible with {DATABASE_DIALECT}.
- Dates must use YYYY-MM-DD string literals such as '2026-09-17'.
- Do NOT use DATE 'YYYY-MM-DD' syntax.
- Do NOT use SQL parameter placeholders such as '?'.
- Do not invent tables or columns.
- Use only read-only SELECT queries.

User question:
{clean_question}

Return ONLY the SQL query.
Do not include markdown fences.
Do not include explanations.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    # Remove accidental markdown formatting
    sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```\s*", "", sql)
    sql = re.sub(r"\s*```$", "", sql)

    return sql.strip()