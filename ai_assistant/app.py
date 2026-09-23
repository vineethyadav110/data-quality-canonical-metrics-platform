import time

from ai_assistant.sql_generator import (
    generate_sql,
    normalize_question,
)
from ai_assistant.sql_validator import validate_sql
from ai_assistant.database.adapter import (
    execute_query,
    get_database_dialect,
)
from ai_assistant.database.audit import (
    initialize_audit_table,
    create_request_id,
    save_audit_record,
)
from ai_assistant.explainer import generate_explanation


MODEL = "openai/gpt-oss-120b"
DATABASE_DIALECT = get_database_dialect()


def print_results(results):
    if not results:
        print("\nNo rows returned.")
        return

    print("\nQuery Results:")
    print("-" * 80)

    columns = list(results[0].keys())
    print(" | ".join(columns))
    print("-" * 80)

    for row in results:
        print(
            " | ".join(
                str(row.get(column, ""))
                for column in columns
            )
        )

    print("-" * 80)


def save_request_audit(
    request_id,
    question,
    normalized_question,
    generated_sql,
    validation_status,
    validation_message,
    execution_status,
    execution_error,
    row_count,
    execution_time_ms,
    answer,
):
    save_audit_record(
        request_id=request_id,
        question=question,
        normalized_question=normalized_question,
        generated_sql=generated_sql,
        validation_status=validation_status,
        validation_message=validation_message,
        execution_status=execution_status,
        execution_error=execution_error,
        row_count=row_count,
        execution_time_ms=execution_time_ms,
        answer=answer,
        model=MODEL,
        database_dialect=DATABASE_DIALECT,
    )


def ask(question: str):
    request_id = create_request_id()
    normalized_question = normalize_question(question)

    generated_sql = None
    validation_status = None
    validation_message = None
    execution_status = None
    execution_error = None
    row_count = None
    execution_time_ms = None
    answer = None

    print("\n" + "=" * 80)
    print(f"Request ID: {request_id}")
    print(f"Database: {DATABASE_DIALECT}")
    print(f"LLM: Groq Cloud / {MODEL}")
    print(f"Question: {question}")
    print("=" * 80)

    try:
        generated_sql = generate_sql(question)
    except Exception as error:
        execution_status = "SQL_GENERATION_FAILED"
        execution_error = str(error)

        print(f"\nSQL generation failed: {error}")

        save_request_audit(
            request_id,
            question,
            normalized_question,
            generated_sql,
            validation_status,
            validation_message,
            execution_status,
            execution_error,
            row_count,
            execution_time_ms,
            answer,
        )
        return

    print("\nGenerated SQL:")
    print("-" * 80)
    print(generated_sql)
    print("-" * 80)

    try:
        is_valid, validation_message = validate_sql(generated_sql)
    except Exception as error:
        validation_status = "FAILED"
        validation_message = str(error)
        execution_status = "VALIDATION_FAILED"
        execution_error = str(error)

        print(f"\nSQL validation failed: {error}")

        save_request_audit(
            request_id,
            question,
            normalized_question,
            generated_sql,
            validation_status,
            validation_message,
            execution_status,
            execution_error,
            row_count,
            execution_time_ms,
            answer,
        )
        return

    validation_status = "PASSED" if is_valid else "FAILED"

    print(f"\nSQL Validation: {validation_message}")

    if not is_valid:
        execution_status = "VALIDATION_FAILED"

        save_request_audit(
            request_id,
            question,
            normalized_question,
            generated_sql,
            validation_status,
            validation_message,
            execution_status,
            execution_error,
            row_count,
            execution_time_ms,
            answer,
        )

        print("\nQuery rejected for safety.")
        return

    execution_start = time.perf_counter()

    try:
        results = execute_query(generated_sql)

        execution_time_ms = round(
            (time.perf_counter() - execution_start) * 1000,
            2,
        )

        row_count = len(results)
        execution_status = "SUCCESS"

    except Exception as error:
        execution_time_ms = round(
            (time.perf_counter() - execution_start) * 1000,
            2,
        )

        execution_status = "EXECUTION_FAILED"
        execution_error = str(error)

        print(f"\nDatabase execution failed: {error}")

        save_request_audit(
            request_id,
            question,
            normalized_question,
            generated_sql,
            validation_status,
            validation_message,
            execution_status,
            execution_error,
            row_count,
            execution_time_ms,
            answer,
        )
        return

    print_results(results)

    try:
        answer = generate_explanation(
            question=question,
            sql=generated_sql,
            results=results,
        )
    except Exception as error:
        execution_status = "EXPLANATION_FAILED"
        execution_error = str(error)

        print(f"\nExplanation generation failed: {error}")
        print(
            "\nThe query executed successfully, "
            "but the explanation layer failed."
        )

        save_request_audit(
            request_id,
            question,
            normalized_question,
            generated_sql,
            validation_status,
            validation_message,
            execution_status,
            execution_error,
            row_count,
            execution_time_ms,
            answer,
        )
        return

    print("\nAssistant Answer:")
    print("-" * 80)
    print(answer)
    print("-" * 80)

    save_request_audit(
        request_id,
        question,
        normalized_question,
        generated_sql,
        validation_status,
        validation_message,
        execution_status,
        execution_error,
        row_count,
        execution_time_ms,
        answer,
    )

    print(f"\nAudit record saved: {request_id}")


def main():
    initialize_audit_table()

    print("=" * 80)
    print("AI Analytics Assistant")
    print("=" * 80)
    print(f"Database dialect: {DATABASE_DIALECT}")
    print(f"LLM provider: Groq Cloud")
    print(f"LLM model: {MODEL}")

    print(
        """
Ask natural-language questions about the analytics dataset.

Examples:
  - How many trips were completed on 2026-09-17?
  - What was the completion rate on 2026-09-18?
  - Show total revenue by date.
  - What was the average trip distance on 2026-09-17?
  - Show active vehicles by date.

Type 'exit' or 'quit' to stop.
"""
    )

    while True:
        try:
            question = input("\nAsk a question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting assistant.")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("\nGoodbye.")
            break

        ask(question)


if __name__ == "__main__":
    main()
