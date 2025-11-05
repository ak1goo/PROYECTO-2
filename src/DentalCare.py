import os
import shutil
import sqlite3
import json
import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import list, Dict, Any, Optional


try: 
    from PIL import image
    PIL_AVAILABLE = True
except:
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
    
    