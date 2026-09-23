# Data Quality & Canonical Metrics Platform with AI Analytics Assistant

An end-to-end analytics engineering platform that transforms operational data into trusted canonical metrics through automated data-quality validation, quarantine, remediation, analytics modeling, and BI reporting.

The platform also includes an AI Analytics Assistant that converts natural-language business questions into governed, read-only SQL and explains query results for business users.

## Project Overview

Operational analytics often requires more than simply loading data into a warehouse.

Data must be:

* validated before reaching analytical models
* monitored for quality failures
* quarantined when records cannot be safely processed
* remediated when deterministic corrections are possible
* transformed into consistent business metrics
* exposed through trusted BI dashboards
* made accessible to business users without requiring SQL expertise

This project implements that workflow as a production-style analytics engineering platform.

## System Architecture

<img width="336" height="821" alt="Platform_architecture" src="https://github.com/user-attachments/assets/82cccd4f-7e87-4ca9-b097-dc4645240f01" />

```text
Raw Data
   |
   v
Staging Models
   |
   v
Data Quality Validation
   |
   +--------------------+
   |                    |
   v                    v
Clean Records       Failed Records
   |                    |
   v                    v
Analytics Models    Quarantine
   |                    |
   v                    v
Canonical Metrics   Remediation
   |                    |
   +----------+---------+
              |
              v
          Power BI
              |
              v
      AI Analytics Assistant
              |
              v
          Groq Cloud
              |
              v
       SQL Generation
              |
              v
       SQL Validation
              |
              v
      Read-Only Execution
              |
              v
        Result Explanation
              |
              v
          Audit Log
```


## Key Capabilities

### 1. Data Quality Pipeline

The analytics pipeline validates operational trip data before it reaches analytical models.

Validation rules include:

* missing trip identifiers
* duplicate trip identifiers
* missing vehicle identifiers
* negative distance
* negative fare
* invalid duration
* invalid timestamp sequences
* invalid delivery statuses

Records that fail validation are separated from the clean analytical dataset.

### 2. Quarantine and Remediation

The platform distinguishes between:

**Automatically correctable issues**

Examples include:

* whitespace normalization
* case normalization
* deterministic status corrections such as `completeed` → `completed`

**Issues requiring investigation**

Examples include:

* negative distance
* negative fare
* missing vehicle
* impossible timestamps
* duplicate records

Remediation activity is logged so that corrections remain traceable.

### 3. Canonical Metrics

The platform defines reusable analytical metrics rather than allowing every dashboard or analyst to calculate business logic independently.

Examples include:

* Total Trips
* Completed Trips
* Cancelled Trips
* Completion Rate
* Average Duration
* Average Distance
* Total Distance
* Total Revenue
* Revenue per Mile
* Active Vehicles
* Quality Failure Rate

Metric definitions are maintained as governed analytical metadata.

### 4. BI Reporting

Power BI provides an operations and data-quality view containing:

* total trips
* completion rate
* revenue
* active vehicles
* daily trip trends
* completion-rate trends
* revenue trends
* quality failure rate
* failed-record counts
* failure reasons
* remediation information
* pipeline execution status

<img width="1071" height="620" alt="PowerBI_dashboard" src="https://github.com/user-attachments/assets/66d1c517-70d0-4407-90c4-8debf256b1c0" />

<img width="1091" height="687" alt="PowerBi_dashboard2" src="https://github.com/user-attachments/assets/2a382adb-61e8-4690-8a01-a33977fd42e8" />

### 5. AI Analytics Assistant

Users can ask questions in natural language, for example:

> What were total trips on September 17?

The assistant performs:

```text
Natural Language Question
        ↓
Canonical Metric Context
        ↓
Groq LLM
        ↓
SQL Generation
        ↓
SQL Validation
        ↓
Read-Only Execution
        ↓
Query Result
        ↓
Business Explanation
```

<img width="820" height="696" alt="digital_assistant_demo" src="https://github.com/user-attachments/assets/7b7e494e-b542-4fa1-8f55-615790384798" />

The assistant is constrained to approved canonical metrics and dimensions.

### 6. SQL Safety

Generated SQL is validated before execution.

The validation layer checks for:

* single-statement execution
* read-only query behavior
* approved tables
* approved columns
* forbidden SQL operations
* SQL parameter placeholders
* unauthorized data access patterns

The application does not directly execute arbitrary LLM-generated SQL.

### 7. Query Auditability

AI requests are recorded in an audit table containing information such as:

* request ID
* original question
* normalized question
* generated SQL
* validation status
* validation message
* execution status
* execution errors
* row count
* execution time
* generated answer
* model
* database dialect
* timestamp

This provides traceability for AI-assisted analytics requests.

## Technology Stack

* Python
* SQL
* dbt
* Apache Airflow
* SQLite
* Snowflake connector
* Power BI
* Groq Cloud
* SQLGlot

## Database Architecture

The analytical warehouse is organized around the following logical layers:

```text
RAW
  ↓
STAGING
  ↓
QUALITY
  ↓
ANALYTICS
```

Key analytical objects include:

* `RAW_TRIPS`
* `DQ_FAILED_RECORDS`
* `DQ_REMEDIATION_LOG`
* `FCT_TRIPS`
* `FCT_TRIP_METRICS`
* `DATA_QUALITY_METRICS`
* `PIPELINE_RUN_AUDIT`

## Runtime Architecture

The project supports a local SQLite runtime for reproducible development and demonstration.

A Snowflake database adapter is included for cloud warehouse execution.

This separation keeps the application architecture independent of a single database implementation.

```text
Application
    |
    v
Database Adapter
    |
    +------ SQLite
    |
    +------ Snowflake
```

## Example Questions

The AI assistant can answer questions such as:

```text
What were total trips on 2026-09-17?

What was the completion rate on 2026-09-18?

Which day had the highest total revenue?

Show total trips and completion rate by trip date.
```

## Engineering Principles Demonstrated

This project focuses on several analytics engineering principles:

* trusted canonical metrics
* data-quality-first modeling
* separation of raw, quality, and analytical layers
* deterministic remediation
* auditability
* reusable metric definitions
* controlled AI-generated SQL
* read-only analytical execution
* database abstraction
* BI-ready analytical models
* reproducible local development

## Project Structure

```text
data-quality-canonical-metrics-platform/
│
├── airflow/
│   └── dags/
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── quality/
│   │   └── analytics/
│   ├── tests/
│   └── dbt_project.yml
│
├── ai_assistant/
│   ├── app.py
│   ├── sql_generator.py
│   ├── sql_validator.py
│   ├── schema_context.py
│   ├── prompts.py
│   ├── explainer.py
│   └── database/
│       ├── local.py
│       ├── setup_local.py
│       ├── adapter.py
│       ├── audit.py
│       └── snowflake.py
│
├── docs/
│   └── canonical_metrics.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Running the AI Assistant

Create the environment configuration locally:

```text
GROQ_API_KEY=<your key>
DATABASE_DIALECT=sqlite
```

Do not commit credentials or `.env` files.

Initialize the local analytical database:

```bash
python ai_assistant/database/setup_local.py
```

Run the assistant:

```bash
python -m ai_assistant.app
```

The assistant will generate SQL, validate the query, execute it against the analytical dataset, explain the result, and record the request in the audit log.

## Portfolio Focus

This project demonstrates the intersection of:

**Analytics Engineering + Data Quality + BI + AI-assisted Analytics**

The architecture is intentionally designed around governed analytical data rather than treating the LLM as the source of truth.

The LLM generates and explains queries, while canonical metric definitions, SQL validation, and the analytical data layer provide the control framework.
