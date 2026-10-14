import sqlite3


def create_database():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chemicals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            manufacturer TEXT,
            cas_number TEXT,
            storage_location TEXT,
            quantity REAL,
            unit TEXT,
            sds_reference TEXT
        )
    """)

    connection.commit()
    connection.close()

def save_chemical(
    product_name,
    manufacturer,
    cas_number,
    storage_location,
    quantity,
    unit,
    sds_reference
):
    connection = sqlite3.connect("chemicals.db")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO chemicals (
                product_name, manufacturer, cas_number,
                storage_location, quantity, unit, sds_reference
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_name, manufacturer, cas_number,
            storage_location, quantity, unit, sds_reference
        ))

        chemical_id = cursor.lastrowid

        if quantity > 0:
            cursor.execute("""
                INSERT INTO stock_movements (
                    chemical_id, movement_type, amount,
                    balance_after, reason
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                chemical_id,
                "Opening",
                quantity,
                quantity,
                "Opening quantity at registration"
            ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
    
    

def get_all_chemicals():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            manufacturer,
            cas_number,
            storage_location,
            quantity,
            unit,
            sds_reference
        FROM chemicals
        ORDER BY id DESC
    """)

    chemicals = cursor.fetchall()
    connection.close()
    return chemicals

def get_chemical_by_id(chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            manufacturer,
            cas_number,
            storage_location,
            quantity,
            unit,
            sds_reference
        FROM chemicals
        WHERE id = ?
    """, (chemical_id,))

    chemical = cursor.fetchone()
    connection.close()
    return chemical

def update_chemical(
    chemical_id,
    product_name,
    manufacturer,
    cas_number,
    storage_location,
    sds_reference
):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE chemicals
        SET product_name = ?,
            manufacturer = ?,
            cas_number = ?,
            storage_location = ?,
            sds_reference = ?
            
        WHERE id = ? AND status = 'Active'
    """, (
        product_name,
        manufacturer,
        cas_number,
        storage_location,
        sds_reference,
        chemical_id
    ))

    connection.commit()
    connection.close()

    
def create_sds_table():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_data_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            revision_date TEXT,
            uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            pdf_data BLOB NOT NULL,
            FOREIGN KEY (chemical_id) REFERENCES chemicals(id)
        )
    """)

    connection.commit()
    connection.close()
    
def save_sds(chemical_id, file_name, revision_date, pdf_data):
    if not pdf_data.startswith(b"%PDF-"):
        raise ValueError("The selected file does not appear to be a PDF.")

    if len(pdf_data) > 10 * 1024 * 1024:
        raise ValueError("The PDF must be 10 MB or smaller.")

    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO safety_data_sheets (
            chemical_id,
            file_name,
            revision_date,
            pdf_data
        )
        VALUES (?, ?, ?, ?)
    """, (
        chemical_id,
        file_name,
        revision_date,
        pdf_data
    ))

    connection.commit()
    connection.close()
    
def get_sds_versions(chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, file_name, revision_date, uploaded_at
        FROM safety_data_sheets
        WHERE chemical_id = ?
        ORDER BY revision_date DESC, id DESC
    """, (chemical_id,))

    versions = cursor.fetchall()
    connection.close()
    return versions


def get_sds_file(sds_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT file_name, pdf_data
        FROM safety_data_sheets
        WHERE id = ?
    """, (sds_id,))

    result = cursor.fetchone()
    connection.close()
    return result

def delete_sds(sds_id, chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM safety_data_sheets
        WHERE id = ? AND chemical_id = ?
    """, (sds_id, chemical_id))

    deleted = cursor.rowcount
    connection.commit()
    connection.close()
    return deleted > 0

def create_stock_movements_table():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            balance_after REAL NOT NULL CHECK (balance_after >= 0),
            reason TEXT NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chemical_id) REFERENCES chemicals(id)
        )
    """)

    connection.commit()
    connection.close()
    
def record_stock_movement(chemical_id, movement_type, amount, reason):
    if movement_type not in ("Receive", "Use", "Dispose"):
        raise ValueError("Choose Receive, Use, or Dispose.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if not reason.strip():
        raise ValueError("Enter a reason or reference.")

    connection = sqlite3.connect("chemicals.db")

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT quantity, status FROM chemicals WHERE id = ?",
            (chemical_id,)
        )
        
        
        
        row = cursor.fetchone()

        if row is None:
            raise ValueError("Chemical not found.")

        if row[1] != "Active":
            raise ValueError(
                "Archived chemicals cannot have stock movements."
            )

        current_balance = float(row[0] or 0)
        change = amount if movement_type == "Receive" else -amount
        new_balance = round(current_balance + change, 4)

        if new_balance < 0:
            raise ValueError(
                f"Not enough stock. Available: {current_balance}"
            )

        cursor.execute(
            "UPDATE chemicals SET quantity = ? WHERE id = ?",
            (new_balance, chemical_id)
        )

        cursor.execute("""
            INSERT INTO stock_movements (
                chemical_id,
                movement_type,
                amount,
                balance_after,
                reason
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            chemical_id,
            movement_type,
            amount,
            new_balance,
            reason.strip()
        ))

        connection.commit()
        return new_balance

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def get_stock_movements(chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recorded_at,
            movement_type,
            amount,
            balance_after,
            reason
        FROM stock_movements
        WHERE chemical_id = ?
        ORDER BY id DESC
    """, (chemical_id,))

    movements = cursor.fetchall()
    connection.close()
    return movements

def add_chemical_status_column():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(chemicals)")
    column_names = [column[1] for column in cursor.fetchall()]

    if "status" not in column_names:
        cursor.execute("""
            ALTER TABLE chemicals
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Active'
        """)

    connection.commit()
    connection.close()
    
def archive_chemical(chemical_id):
    connection = sqlite3.connect("chemicals.db")

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT quantity, status FROM chemicals WHERE id = ?",
            (chemical_id,)
        )
        chemical = cursor.fetchone()

        if chemical is None:
            raise ValueError("Chemical not found.")

        if chemical[1] == "Archived":
            raise ValueError("Chemical is already archived.")

        if float(chemical[0] or 0) != 0:
            raise ValueError(
                "Stock balance must be zero before archiving."
            )

        cursor.execute(
            "UPDATE chemicals SET status = 'Archived' WHERE id = ?",
            (chemical_id,)
        )
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def restore_chemical(chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE chemicals
        SET status = 'Active'
        WHERE id = ? AND status = 'Archived'
    """, (chemical_id,))

    restored = cursor.rowcount
    connection.commit()
    connection.close()

    if not restored:
        raise ValueError("Archived chemical not found.")
    
def get_chemicals_with_status():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, product_name, quantity, unit, status
        FROM chemicals
        ORDER BY product_name, id
    """)

    chemicals = cursor.fetchall()
    connection.close()
    return chemicals

def get_active_chemicals():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            manufacturer,
            cas_number,
            storage_location,
            quantity,
            unit,
            sds_reference
        FROM chemicals
        WHERE status = 'Active'
        ORDER BY id DESC
    """)

    chemicals = cursor.fetchall()
    connection.close()
    return chemicals

def add_minimum_stock_column():
    connection = sqlite3.connect("chemicals.db")

    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(chemicals)")
        columns = [column[1] for column in cursor.fetchall()]

        if "minimum_stock" not in columns:
            cursor.execute("""
                ALTER TABLE chemicals
                ADD COLUMN minimum_stock REAL NOT NULL DEFAULT 0
            """)

        connection.commit()
    finally:
        connection.close()
        
def set_minimum_stock(chemical_id, minimum_stock):
    if minimum_stock < 0:
        raise ValueError("Minimum stock cannot be negative.")

    connection = sqlite3.connect("chemicals.db")

    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE chemicals
            SET minimum_stock = ?
            WHERE id = ? AND status = 'Active'
        """, (minimum_stock, chemical_id))

        if cursor.rowcount == 0:
            raise ValueError("Active chemical not found.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
        
def get_minimum_stock(chemical_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT minimum_stock FROM chemicals WHERE id = ?",
        (chemical_id,)
    )
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return float(row[0] or 0)

def add_sds_review_columns():
    connection = sqlite3.connect("chemicals.db")

    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(safety_data_sheets)")
        columns = [column[1] for column in cursor.fetchall()]

        if "last_reviewed_date" not in columns:
            cursor.execute("""
                ALTER TABLE safety_data_sheets
                ADD COLUMN last_reviewed_date TEXT
            """)

        if "review_due_date" not in columns:
            cursor.execute("""
                ALTER TABLE safety_data_sheets
                ADD COLUMN review_due_date TEXT
            """)

        connection.commit()
    finally:
        connection.close()
        
def update_sds_review_dates(sds_id, last_reviewed_date, review_due_date):
    connection = sqlite3.connect("chemicals.db")

    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE safety_data_sheets
            SET last_reviewed_date = ?,
                review_due_date = ?
            WHERE id = ?
        """, (last_reviewed_date, review_due_date, sds_id))

        if cursor.rowcount == 0:
            raise ValueError("SDS version not found.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
        
def get_sds_review_dates(sds_id):
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT last_reviewed_date, review_due_date
        FROM safety_data_sheets
        WHERE id = ?
    """, (sds_id,))

    dates = cursor.fetchone()
    connection.close()
    return dates
def get_sds_review_records():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.chemical_id,
            c.product_name,
            s.file_name,
            s.revision_date,
            s.last_reviewed_date,
            s.review_due_date
        FROM safety_data_sheets AS s
        JOIN chemicals AS c ON c.id = s.chemical_id
        WHERE c.status = 'Active'
          AND s.review_due_date IS NOT NULL
        ORDER BY s.review_due_date
    """)

    records = cursor.fetchall()
    connection.close()
    return records

def get_sds_without_review_date():
    connection = sqlite3.connect("chemicals.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            s.id,
            c.product_name,
            s.file_name,
            s.revision_date,
            s.uploaded_at
        FROM safety_data_sheets AS s
        JOIN chemicals AS c ON c.id = s.chemical_id
        WHERE c.status = 'Active'
          AND s.review_due_date IS NULL
        ORDER BY c.product_name, s.uploaded_at DESC
    """)

    records = cursor.fetchall()
    connection.close()
    return records