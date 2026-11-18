import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from config import PROJECT_ROOT, get_database_config

DATA_FILE = PROJECT_ROOT / "data" / "paysim_sample.csv"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"
VALID_TYPES = {"CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"}


class TransactionWarehouse:
    def __init__(self):
        self.connection = psycopg2.connect(cursor_factory=RealDictCursor, **get_database_config())

    def close(self):
        if self.connection:
            self.connection.close()

    def create_schema(self):
        with self.connection.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
        self.connection.commit()

    def extract_csv(self, file_path: Path = DATA_FILE):
        with file_path.open("r", newline="", encoding="utf-8") as source:
            return list(csv.DictReader(source))

    def transform(self, records):
        cleaned, rejected = [], []
        seen = set()

        for row in records:
            external_id = str(row.get("step", "")).strip()
            if external_id == "DEMO-CRUD":
                external_id = "DEMO-CRUD-001"

            transaction_type = str(row.get("type", "")).strip().upper()
            sender = str(row.get("nameOrig", "")).strip()
            receiver = str(row.get("nameDest", "")).strip()

            if external_id and external_id != "DEMO-CRUD-001":
                external_id = f"TX-{external_id}-{sender}-{receiver}"

            try:
                amount = Decimal(str(row["amount"]))
                sender_old = Decimal(str(row["oldbalanceOrg"]))
                sender_new = Decimal(str(row["newbalanceOrig"]))
                receiver_old = Decimal(str(row["oldbalanceDest"]))
                receiver_new = Decimal(str(row["newbalanceDest"]))
            except (KeyError, InvalidOperation):
                rejected.append({"record": row, "reason": "Invalid numeric value"})
                continue

            if not external_id or external_id in seen:
                rejected.append({"record": row, "reason": "Missing or duplicate transaction"})
                continue
            if transaction_type not in VALID_TYPES:
                rejected.append({"record": row, "reason": "Invalid transaction type"})
                continue
            if amount < 0 or not sender or not receiver:
                rejected.append({"record": row, "reason": "Invalid amount or account"})
                continue

            seen.add(external_id)
            cleaned.append({
                "external_id": external_id,
                "step": row["step"] if row["step"] != "DEMO-CRUD" else "999",
                "transaction_type": transaction_type,
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "sender_old": sender_old,
                "sender_new": sender_new,
                "receiver_old": receiver_old,
                "receiver_new": receiver_new,
                "is_fraud": str(row["isFraud"]).strip() == "1",
                "is_flagged": str(row["isFlaggedFraud"]).strip() == "1",
                "data_quality_status": "VALID",
            })

        return cleaned, rejected

    def insert_dimension(self, cursor, table, key_column, value_column, values):
        sql = f"INSERT INTO {table} ({value_column}) VALUES %s ON CONFLICT ({value_column}) DO NOTHING"
        execute_values(cursor, sql, [(value,) for value in sorted(set(values))])

    def load(self, cleaned_records):
        with self.connection.cursor() as cursor:
            steps = sorted({int(r["step"]) for r in cleaned_records})
            execute_values(cursor,
                "INSERT INTO dim_time (simulation_step, simulation_hour) VALUES %s "
                "ON CONFLICT (simulation_step) DO NOTHING",
                [(step, step % 24) for step in steps])

            types = {r["transaction_type"] for r in cleaned_records}
            execute_values(cursor,
                "INSERT INTO dim_transaction_type (transaction_type, transaction_category) VALUES %s "
                "ON CONFLICT (transaction_type) DO NOTHING",
                [(t, "Credit" if t == "CASH_IN" else "Debit") for t in sorted(types)])

            senders = {r["sender"] for r in cleaned_records}
            execute_values(cursor,
                "INSERT INTO dim_sender (sender_account, sender_account_class) VALUES %s "
                "ON CONFLICT (sender_account) DO NOTHING",
                [(s, "Customer") for s in sorted(senders)])

            receivers = {r["receiver"] for r in cleaned_records}
            execute_values(cursor,
                "INSERT INTO dim_receiver (receiver_account, receiver_account_class) VALUES %s "
                "ON CONFLICT (receiver_account) DO NOTHING",
                [(r, "Merchant" if r.startswith("M") else "Customer") for r in sorted(receivers)])

            for r in cleaned_records:
                cursor.execute("""
                    INSERT INTO fact_transactions (
                        external_transaction_id, time_key, sender_key, receiver_key,
                        transaction_type_key, amount, sender_old_balance, sender_new_balance,
                        receiver_old_balance, receiver_new_balance, is_fraud,
                        is_flagged_fraud, data_quality_status
                    )
                    SELECT %s, t.time_key, s.sender_key, rcv.receiver_key, tt.transaction_type_key,
                           %s, %s, %s, %s, %s, %s, %s, %s
                    FROM dim_time t
                    JOIN dim_sender s ON s.sender_account = %s
                    JOIN dim_receiver rcv ON rcv.receiver_account = %s
                    JOIN dim_transaction_type tt ON tt.transaction_type = %s
                    WHERE t.simulation_step = %s
                    ON CONFLICT (external_transaction_id) DO UPDATE SET
                        amount = EXCLUDED.amount,
                        is_fraud = EXCLUDED.is_fraud,
                        is_flagged_fraud = EXCLUDED.is_flagged_fraud,
                        data_quality_status = EXCLUDED.data_quality_status,
                        loaded_at = CURRENT_TIMESTAMP
                """, (
                    r["external_id"], r["amount"], r["sender_old"], r["sender_new"],
                    r["receiver_old"], r["receiver_new"], r["is_fraud"], r["is_flagged"],
                    r["data_quality_status"], r["sender"], r["receiver"],
                    r["transaction_type"], int(r["step"])
                ))
        self.connection.commit()

    def create_record(self):
        """Insert a demonstration transaction, then return it as a dictionary."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fact_transactions (
                    external_transaction_id, time_key, sender_key, receiver_key,
                    transaction_type_key, amount, is_fraud, is_flagged_fraud
                )
                SELECT 'CRUD-CREATE-001', t.time_key, s.sender_key, rcv.receiver_key,
                       tt.transaction_type_key, 25.00, FALSE, FALSE
                FROM dim_time t, dim_sender s, dim_receiver rcv, dim_transaction_type tt
                WHERE t.simulation_step = 999
                  AND s.sender_account = 'CDEMO001'
                  AND rcv.receiver_account = 'MDEMO001'
                  AND tt.transaction_type = 'CASH_OUT'
                ON CONFLICT (external_transaction_id) DO UPDATE SET amount = 25.00
                RETURNING external_transaction_id, amount, is_fraud
            """)
            record = cursor.fetchone()
        self.connection.commit()
        return record

    def update_record(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE fact_transactions
                SET amount = 35.00, is_fraud = TRUE, is_flagged_fraud = TRUE,
                    loaded_at = CURRENT_TIMESTAMP
                WHERE external_transaction_id = 'CRUD-CREATE-001'
                RETURNING external_transaction_id, amount, is_fraud, is_flagged_fraud
            """)
            record = cursor.fetchone()
        self.connection.commit()
        return record

    def read_record(self, external_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT external_transaction_id, amount, is_fraud, is_flagged_fraud, data_quality_status
                FROM fact_transactions
                WHERE external_transaction_id = %s
            """, (external_id,))
            return cursor.fetchone()

    def delete_record(self, external_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM fact_transactions
                WHERE external_transaction_id = %s
                RETURNING external_transaction_id
            """, (external_id,))
            record = cursor.fetchone()
        self.connection.commit()
        return record

    def fetch_summary(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT tt.transaction_type,
                       COUNT(*) AS transaction_count,
                       ROUND(SUM(f.amount), 2) AS total_amount,
                       COUNT(*) FILTER (WHERE f.is_fraud) AS fraud_count
                FROM fact_transactions f
                JOIN dim_transaction_type tt USING (transaction_type_key)
                GROUP BY tt.transaction_type
                ORDER BY transaction_count DESC
            """)
            return cursor.fetchall()


def main():
    warehouse = TransactionWarehouse()
    try:
        warehouse.create_schema()
        print("1. Schema created or already available.")

        raw_records = warehouse.extract_csv()
        print(f"2. Extracted {len(raw_records)} source rows.")

        cleaned, rejected = warehouse.transform(raw_records)
        print(f"3. Transformation: {len(cleaned)} valid, {len(rejected)} rejected.")

        warehouse.load(cleaned)
        print("4. Star schema data loaded successfully.")

        created = warehouse.create_record()
        print("5. CREATE result:", dict(created) if created else None)

        updated = warehouse.update_record()
        print("6. UPDATE result:", dict(updated) if updated else None)

        read_back = warehouse.read_record("CRUD-CREATE-001")
        print("7. READ result:", dict(read_back) if read_back else None)

        deleted = warehouse.delete_record("CRUD-CREATE-001")
        print("8. DELETE result:", dict(deleted) if deleted else None)

        print("9. Transaction summary:")
        for row in warehouse.fetch_summary():
            print(dict(row))

    except psycopg2.Error as error:
        warehouse.connection.rollback()
        print(f"Database error: {error}")
        raise
    finally:
        warehouse.close()


if __name__ == "__main__":
    main()
