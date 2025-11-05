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



