# Mobile Banking Transaction Data Warehouse
## Milestone 2: PostgreSQL Connectivity and Database Operations

**Student Name:** ____________________  
**Project Title:** Design and Implementation of a Mobile Banking Transaction Data Warehouse Using Python, PostgreSQL, and Star Schema  
**Date:** ____________________  

## 1. Project Purpose

This milestone implements the PostgreSQL database component of the mobile banking transaction data warehouse. The project uses Python and `psycopg2` to create a star schema, extract and transform PaySim-style CSV records, load the warehouse, and demonstrate CREATE, READ, UPDATE, and DELETE operations.

## 2. Database and Environment

- Database management system: PostgreSQL
- Database client: pgAdmin 4
- Database name: `mobile_banking_dw`
- Python library: `psycopg2-binary`
- Cursor: `psycopg2.extras.RealDictCursor`
- Source format: CSV

## 3. Star Schema Implementation

### 3.1 Dimension tables

- `dim_time`: simulation step and simulation hour
- `dim_transaction_type`: transaction type and category
- `dim_sender`: originating account
- `dim_receiver`: destination account

### 3.2 Fact table

- `fact_transactions`: one row per individual transaction
- Measures: amount and sender/receiver balances
- Indicators: `is_fraud` and `is_flagged_fraud`
- Foreign keys: time, sender, receiver, and transaction type

**Evidence:** Insert screenshot of the pgAdmin table list and star schema relationships.

## 4. ETL Process

### 4.1 Extract

The Python application reads `data/paysim_sample.csv` using Python's CSV library.

### 4.2 Transform

The transformation process:

- creates unique transaction identifiers;
- converts numeric fields to `Decimal` values;
- removes duplicate external transaction identifiers;
- validates transaction types, account fields, and negative amounts;
- separates rejected records from valid records.

### 4.3 Load

Valid records are inserted or updated in the fact and dimension tables. The load is committed only after all statements complete successfully.

**Evidence:** Insert screenshot of the terminal showing extracted, valid, rejected, and loaded results.

## 5. Database Operations

### 5.1 Create

`CREATE TABLE IF NOT EXISTS` statements create the warehouse tables without deleting existing data. The script also inserts demonstration and source records using parameterized SQL.

**Evidence:** Insert pgAdmin screenshot showing `dim_*` and `fact_transactions` tables.

### 5.2 Read

The script returns query results using `RealDictCursor`, and converts each returned row to a dictionary for display.

**Evidence:** Insert terminal screenshot showing dictionary-based read output.

### 5.3 Update

The script updates `CRUD-CREATE-001` by setting:

- amount to `35.00`;
- `is_fraud` to `TRUE`;
- `is_flagged_fraud` to `TRUE`.

**Evidence:** Insert terminal and pgAdmin update screenshots.

### 5.4 Delete

The script deletes the selected demonstration record `CRUD-CREATE-001` and returns the deleted identifier.

**Evidence:** Insert terminal and pgAdmin delete verification screenshots.

## 6. SQL Analysis

The following analysis queries are available in `sql/analysis.sql`:

- total number and value of transactions by type;
- average amount by type;
- fraudulent transaction counts by type;
- top senders by transaction value.

**Evidence:** Insert screenshot of one or more SELECT query results from pgAdmin.

## 7. Data Quality and Error Handling

- duplicate transaction identifiers are rejected;
- invalid numerical values are separated as rejected records;
- unsupported transaction types are rejected;
- negative amounts and blank accounts are rejected;
- database errors trigger `rollback()`;
- database and cursor resources are closed in `finally` logic.

## 8. Verification Checklist

- [ ] PostgreSQL database and pgAdmin are running.
- [ ] `.env` contains local credentials only.
- [ ] `pip install -r requirements.txt` completed successfully.
- [ ] `python src/warehouse.py` completed successfully.
- [ ] Star-schema tables are visible in pgAdmin.
- [ ] CREATE operation was displayed.
- [ ] READ operation returned a dictionary.
- [ ] UPDATE operation was verified.
- [ ] DELETE operation was verified.
- [ ] Analysis query results were captured.
- [ ] Screenshots are added to this report and the `screenshots` folder.

## 9. Source Code Location

- Python application: `src/warehouse.py`
- Database configuration: `src/config.py`
- Schema: `sql/schema.sql`
- Analysis queries: `sql/analysis.sql`
- Sample source data: `data/paysim_sample.csv`
- Setup instructions: `README.md`

## 10. Conclusion

This milestone successfully establishes PostgreSQL connectivity and implements practical database operations for the mobile banking data warehouse. The implementation follows star-schema modelling, applies ETL validation rules, and demonstrates safe transaction handling with commit and rollback behaviour.
