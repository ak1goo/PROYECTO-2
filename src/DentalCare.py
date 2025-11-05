import os
import shutil
import sqlite3
import json
import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

DB_FILE = "clinic.db"
PHOTOS_DIR = "fotos_pacientes"


#-----Mod

@dataclass

class Patient:
    patient_id: int
    name: str
    age: int
    phone: str
    address: str = ""
    photo_path: str = ""
    treatments: list[Dict[str, Any]] = field(default_factory=list)

    def __repr__(self):
        return f"[{self.patient_id}] {self.name} ({self.age} - {self.phone})"
    
@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    date: str
    service: str
    price: float
    attended: int = 0

    def __repr__(self):
        return f"[{self.appointment_id}] P{self.patient_id} - {self.service} @ {self.date} - Q{self.price} - Attended:{self.attended}"
    
#-----AUX
class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    def push(self, data):
        n = Node(data); n.next = self.head; self.head = n
    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out[::-1]
    
class Stack:
    def __init__(self): self._data = []
    def push(self, x): self._data.append(x)
    def pop(self): return self._data.pop() if self._data else None
    def is_empty(self): return len(self._data) == 0

class Queue: 
    def __init__(self): self._data = []
    def enqueue(self, x): self._data.append(x)
    def dequeue(self): return self._data.pop(0) if self._data else None
    def is_empty(self): return len(self._data) == 0

# ---- SQL 
def ensure_db_and_tables():
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
        c.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                date TEXT,
                service TEXT,
                price REAL,
                attended INTEGER DEFAULT 0,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        """)
        conn.commit()   

#----sistema
class ClinicSystemSQL:
    def __init__(self):
        ensure_db_and_tables()
        os.makedirs(PHOTOS_DIR, exist_ok=True)

        self.patients: List[Patient] = []
        self.appointments: List[Appointment] = []
        self.patient_hash: Dict[int, Patient] = {}
        self.history = LinkedList()
        self.undo_stack = Stack()
        self.waiting_queue = Queue()

        self.load_from_db()

#---db
def load_from_db(self):
        self.patients.clear()
        self.appointments.clear()
        self.patient_hash.clear()
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            for row in c.execute("SELECT id, name, age, phone, address, photo_path FROM patients"):
                p = Patient(row[0], row[1], row[2], row[3], row[4] or "", row[5] or "")
                
                self.patients.append(p)
                self.patient_hash[p.patient_id] = p
            for row in c.execute("SELECT id, patient_id, date, service, price, attended FROM appointments"):
                a = Appointment(row[0], row[1], row[2], row[3], row[4], row[5])
                self.appointments.append(a)

