# Mobile Banking Transaction Data Warehouse

A Python and PostgreSQL implementation of a star-schema data warehouse for mobile banking transactions. The project extracts a CSV dataset, validates and cleans records, loads dimensions and a fact table, performs dictionary-based reads with `psycopg2.extras.RealDictCursor`, and demonstrates CREATE, READ, UPDATE, and DELETE operations.

## Project structure

```text
retail/
├── data/paysim_sample.csv
├── report/Milestone_2_Report_Template.md
├── screenshots/
├── sql/
│   ├── schema.sql
│   └── analysis.sql
├── src/
│   ├── config.py
│   └── warehouse.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Setup

1. Install PostgreSQL and create a database named `mobile_banking_dw`.
2. Copy `.env.example` to `.env` and enter local credentials.
3. Create a Python environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Run the application:

```powershell
python src\warehouse.py
```

5. Open pgAdmin 4, select the `mobile_banking_dw` database, and verify the tables and rows.

## Database operations

- **CREATE:** Creates the star-schema tables and inserts or upserts source and demonstration records.
- **READ:** Uses `psycopg2.extras.RealDictCursor` so each fetched row is returned as a Python dictionary.
- **UPDATE:** Changes a demonstration fact record's amount and fraud indicators.
- **DELETE:** Removes the selected demonstration record after the CREATE, READ, and UPDATE checks.
- **Other operations:** Extracts and transforms CSV data, removes duplicates, validates types and amounts, and produces transaction summaries.

## Expected evidence

Capture these items for the report:

1. Python code in VS Code.
2. Terminal output from the script.
3. pgAdmin list of created tables.
4. SELECT results for `fact_transactions` and all four dimensions.
5. CREATE, UPDATE, and DELETE results from the terminal.
6. PostgreSQL rows in pgAdmin before and after modifications.

## Security

Never commit `.env` or database passwords. Use `.env.example` for shared documentation.
