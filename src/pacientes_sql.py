import os
import shutil
import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

DB_FILE = "clinic.db"
PHOTOS_DIR = "fotos_pacientes"

@dataclass
class Patient:
    patient_id: int
    name: str
    age: int
    phone: str
    address: str = ""
    photo_path: str = ""
    treatments: List[Dict[str, Any]] = field(default_factory=list)

def ensure_patients_table():
    """Crea la tabla patients si no existe."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                phone TEXT,
                address TEXT,
                photo_path TEXT
            )
        """)
        conn.commit()
    os.makedirs(PHOTOS_DIR, exist_ok=True)

def create_patient_db(name: str, age: int, phone: str, address: str = "", photo_source_path: Optional[str] = None) -> Patient:
    
    ensure_patients_table()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO patients (name, age, phone, address, photo_path) VALUES (?, ?, ?, ?, ?)",
                  (name, age, phone, address, ""))
        pid = c.lastrowid
        conn.commit()

    photo_dest = ""
    if photo_source_path:
        if os.path.exists(photo_source_path):
            ext = os.path.splitext(photo_source_path)[1]
            photo_dest = os.path.join(PHOTOS_DIR, f"patient_{pid}{ext}")
            try:
                shutil.copyfile(photo_source_path, photo_dest)
            except Exception:
                photo_dest = ""
        else:
            photo_dest = ""

    if photo_dest:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("UPDATE patients SET photo_path = ? WHERE id = ?", (photo_dest, pid))
            conn.commit()

    p = Patient(pid, name, age, phone, address, photo_dest)
    return p

def load_all_patients_from_db() -> List[Patient]:
    """Carga todos los pacientes y devuelve una lista de objetos Patient."""
    ensure_patients_table()
    out = []
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        for row in c.execute("SELECT id, name, age, phone, address, photo_path FROM patients"):
            p = Patient(row[0], row[1], row[2], row[3], row[4] or "", row[5] or "")
            out.append(p)
    return out

def get_patient_by_id(pid: int) -> Optional[Patient]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, age, phone, address, photo_path FROM patients WHERE id = ?", (pid,))
        row = c.fetchone()
        if not row:
            return None
        return Patient(row[0], row[1], row[2], row[3], row[4] or "", row[5] or "")

def update_patient_db(pid: int, name: Optional[str] = None, age: Optional[int] = None,
                      phone: Optional[str] = None, address: Optional[str] = None,
                      photo_source_path: Optional[str] = None) -> Optional[Patient]:

    p = get_patient_by_id(pid)
    if not p:
        return None

    sets = []
    vals = []
    if name is not None:
        sets.append("name = ?"); vals.append(name)
    if age is not None:
        sets.append("age = ?"); vals.append(age)
    if phone is not None:
        sets.append("phone = ?"); vals.append(phone)
    if address is not None:
        sets.append("address = ?"); vals.append(address)

    photo_dest = None
    if photo_source_path:
        if os.path.exists(photo_source_path):
            ext = os.path.splitext(photo_source_path)[1]
            photo_dest = os.path.join(PHOTOS_DIR, f"patient_{pid}{ext}")
            try:
                shutil.copyfile(photo_source_path, photo_dest)
            except Exception:
                photo_dest = None
        else:
            photo_dest = None
        if photo_dest:
            sets.append("photo_path = ?"); vals.append(photo_dest)

    if sets:
        vals.append(pid)
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(f"UPDATE patients SET {', '.join(sets)} WHERE id = ?", tuple(vals))
            conn.commit()

    return get_patient_by_id(pid)

def delete_patient_db(pid: int) -> bool:
    """Elimina paciente y devuelve True si existía."""
    p = get_patient_by_id(pid)
    if not p:
        return False
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM patients WHERE id = ?", (pid,))
        conn.commit()

    if p.photo_path and os.path.exists(p.photo_path):
        try:
            os.remove(p.photo_path)
        except Exception:
            pass
    return True

def search_patients_by_name(q: str) -> List[Patient]:
    """Busca por LIKE en DB (más eficiente que cargar todo y filtrar)."""
    ensure_patients_table()
    out = []
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, age, phone, address, photo_path FROM patients WHERE name LIKE ?", (f"%{q}%",))
        for row in c.fetchall():
            out.append(Patient(row[0], row[1], row[2], row[3], row[4] or "", row[5] or ""))
    return out
