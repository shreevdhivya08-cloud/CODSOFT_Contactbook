"""
Database Manager for ContactBook
Handles all SQLite database operations with a clean, modular interface.
"""

import sqlite3
import csv
import os
import re
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Database path (stored next to this file so the app is self-contained)
# ──────────────────────────────────────────────────────────────────────────────
DB_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "contacts.db")


# ──────────────────────────────────────────────────────────────────────────────
# Schema
# ──────────────────────────────────────────────────────────────────────────────
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name   TEXT    NOT NULL,
    phone       TEXT    UNIQUE NOT NULL,
    email       TEXT,
    address     TEXT,
    company     TEXT,
    notes       TEXT,
    favorite    INTEGER DEFAULT 0,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _validate_email(email: str) -> bool:
    """Return True if *email* looks valid (or is empty)."""
    if not email:
        return True
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _row_to_dict(row) -> dict:
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row) if row else {}


# ──────────────────────────────────────────────────────────────────────────────
# Database Manager
# ──────────────────────────────────────────────────────────────────────────────
class DatabaseManager:
    """
    Manages all CRUD operations for the contacts database.

    Usage
    -----
        db = DatabaseManager()
        db.add_contact(full_name="Jane Doe", phone="9876543210")
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """Create the contacts table if it doesn't exist."""
        with self._connect() as conn:
            conn.execute(CREATE_TABLE_SQL)
            conn.commit()

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate_contact(
        self,
        full_name: str,
        phone: str,
        email: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        """Raise ValueError with a human-readable message on invalid data."""
        if not full_name or not full_name.strip():
            raise ValueError("Full name is required.")
        if not phone or not phone.strip():
            raise ValueError("Phone number is required.")
        if not _validate_email(email):
            raise ValueError(f"'{email}' is not a valid email address.")

        # Duplicate phone check
        with self._connect() as conn:
            if exclude_id is not None:
                row = conn.execute(
                    "SELECT id FROM contacts WHERE phone = ? AND id != ?",
                    (phone.strip(), exclude_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id FROM contacts WHERE phone = ?",
                    (phone.strip(),),
                ).fetchone()
            if row:
                raise ValueError(
                    f"Phone number '{phone}' already belongs to another contact."
                )

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add_contact(
        self,
        full_name: str,
        phone: str,
        email: str = "",
        address: str = "",
        company: str = "",
        notes: str = "",
        favorite: bool = False,
    ) -> int:
        """Insert a new contact. Returns the new row id."""
        self._validate_contact(full_name, phone, email)
        now = _now()
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO contacts
                   (full_name, phone, email, address, company, notes, favorite,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    full_name.strip(),
                    phone.strip(),
                    email.strip(),
                    address.strip(),
                    company.strip(),
                    notes.strip(),
                    int(favorite),
                    now,
                    now,
                ),
            )
            conn.commit()
            return cur.lastrowid

    def update_contact(
        self,
        contact_id: int,
        full_name: str,
        phone: str,
        email: str = "",
        address: str = "",
        company: str = "",
        notes: str = "",
        favorite: bool = False,
    ) -> None:
        """Update an existing contact by id."""
        self._validate_contact(full_name, phone, email, exclude_id=contact_id)
        with self._connect() as conn:
            conn.execute(
                """UPDATE contacts
                   SET full_name=?, phone=?, email=?, address=?, company=?,
                       notes=?, favorite=?, updated_at=?
                   WHERE id=?""",
                (
                    full_name.strip(),
                    phone.strip(),
                    email.strip(),
                    address.strip(),
                    company.strip(),
                    notes.strip(),
                    int(favorite),
                    _now(),
                    contact_id,
                ),
            )
            conn.commit()

    def delete_contact(self, contact_id: int) -> None:
        """Delete a contact by id."""
        with self._connect() as conn:
            conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
            conn.commit()

    def toggle_favorite(self, contact_id: int) -> bool:
        """Flip the favorite flag. Returns the new state."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT favorite FROM contacts WHERE id=?", (contact_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"No contact with id={contact_id}.")
            new_val = 0 if row["favorite"] else 1
            conn.execute(
                "UPDATE contacts SET favorite=?, updated_at=? WHERE id=?",
                (new_val, _now(), contact_id),
            )
            conn.commit()
            return bool(new_val)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_all_contacts(self, favorites_only: bool = False) -> list[dict]:
        """Return all contacts, optionally filtered to favorites."""
        with self._connect() as conn:
            if favorites_only:
                rows = conn.execute(
                    "SELECT * FROM contacts WHERE favorite=1 ORDER BY full_name COLLATE NOCASE"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM contacts ORDER BY full_name COLLATE NOCASE"
                ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def search_contacts(self, query: str) -> list[dict]:
        """Full-text search across name, phone, and email."""
        q = f"%{query.strip()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM contacts
                   WHERE full_name LIKE ? OR phone LIKE ? OR email LIKE ?
                   ORDER BY full_name COLLATE NOCASE""",
                (q, q, q),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_contact_by_id(self, contact_id: int) -> dict:
        """Return a single contact dict (empty dict if not found)."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM contacts WHERE id=?", (contact_id,)
            ).fetchone()
        return _row_to_dict(row)

    def get_stats(self) -> dict:
        """Return summary statistics for the dashboard."""
        with self._connect() as conn:
            total     = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            favorites = conn.execute(
                "SELECT COUNT(*) FROM contacts WHERE favorite=1"
            ).fetchone()[0]
            with_email = conn.execute(
                "SELECT COUNT(*) FROM contacts WHERE email != ''"
            ).fetchone()[0]
            companies = conn.execute(
                "SELECT COUNT(DISTINCT company) FROM contacts WHERE company != ''"
            ).fetchone()[0]
        return {
            "total":      total,
            "favorites":  favorites,
            "with_email": with_email,
            "companies":  companies,
        }

    # ── Import / Export ───────────────────────────────────────────────────────

    CSV_FIELDS = [
        "full_name", "phone", "email", "address", "company", "notes", "favorite"
    ]

    def export_to_csv(self, filepath: str) -> int:
        """Export all contacts to a CSV file. Returns the row count."""
        contacts = self.get_all_contacts()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for c in contacts:
                writer.writerow({k: c.get(k, "") for k in self.CSV_FIELDS})
        return len(contacts)

    def import_from_csv(self, filepath: str) -> tuple[int, int]:
        """
        Import contacts from a CSV file.
        Returns (imported_count, skipped_count).
        """
        imported = skipped = 0
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.add_contact(
                        full_name=row.get("full_name", "").strip(),
                        phone=row.get("phone", "").strip(),
                        email=row.get("email", "").strip(),
                        address=row.get("address", "").strip(),
                        company=row.get("company", "").strip(),
                        notes=row.get("notes", "").strip(),
                        favorite=str(row.get("favorite", "0")) in ("1", "True", "true"),
                    )
                    imported += 1
                except (ValueError, sqlite3.IntegrityError):
                    skipped += 1
        return imported, skipped
