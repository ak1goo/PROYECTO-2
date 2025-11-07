#!/usr/bin/env python3
"""
Sistema de Clínica Odontológica 
"""

import os, sys
import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any

# FUNC
from pacientes_sql import (
    Patient,
    create_patient_db,
    load_all_patients_from_db,
    get_patient_by_id,
    update_patient_db,
    delete_patient_db,
    search_patients_by_name
)

#Sistema de inicio de sesión 
usuariosValidos = {
    "admin": {
        "password": "admin123",
         "rol": "Doctora" 
         },
    "recepcionista": {
        "password": "recep2025",
         "rol": "Recepcionista"}
}

def iniciar_sesion():
    print(" === Sistema Dental Care === ")
    print("Inicio de sesión ")

    intentos = 3
    while intentos > 0:
        usuario = input("Usuario: ").strip()
        contraseña = input("Contraseña: ").strip()

        if usuario in usuariosValidos and usuariosValidos[usuario]["password"] == contraseña:
            print(f"Bienvenido/a, {usuario} {usuariosValidos[usuario]['rol']}")
            return usuario, usuariosValidos[usuario]['rol']
        else:
            intentos -= 1
            print(f"Credenciales incorrectas. Te quedan {intentos} intentos.")
#DATOS
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    def push(self, data):
        n = Node(data)
        n.next = self.head
        self.head = n
    def to_list(self):
        cur = self.head
        res = []
        while cur:
            res.append(cur.data)
            cur = cur.next
        return res[::-1]

class Stack:
    def __init__(self): self._data = []
    def push(self, x): self._data.append(x)
    def pop(self): return self._data.pop() if self._data else None

class Queue:
    def __init__(self): self._data = []
    def enqueue(self, x): self._data.append(x)
    def dequeue(self): return self._data.pop(0) if self._data else None

# MODELOS
@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    date: str
    service: str
    price: float
    attended: int = 0

# SYSTEM
class ClinicSystem:
    def __init__(self):
        self.history = LinkedList()
        self.undo_stack = Stack()
        self.waiting_queue = Queue()
        self.patients: List[Patient] = load_all_patients_from_db()
        self.patient_hash: Dict[int, Patient] = {p.patient_id: p for p in self.patients}
        self.appointments: List[Appointment] = []
        self.ensure_appointments_table()

    def ensure_appointments_table(self):
        with sqlite3.connect("clinic.db") as conn:
            c = conn.cursor()
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

    # --------- Métodos de Ordenamiento ---------
    def bubble_sort_patients_by_name(self):
        n = len(self.patients)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.patients[j].name > self.patients[j + 1].name:
                    self.patients[j], self.patients[j + 1] = self.patients[j + 1], self.patients[j]

    def quick_sort_patients_by_id(self):
        def partition(arr, low, high):
            pivot = arr[high].patient_id
            i = low - 1
            
            for j in range(low, high):
                if arr[j].patient_id <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def quick_sort_helper(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                quick_sort_helper(arr, low, pi - 1)
                quick_sort_helper(arr, pi + 1, high)

        quick_sort_helper(self.patients, 0, len(self.patients) - 1)

    def list_patients_ordered(self, order_type="name"):
        if order_type == "name":
            self.bubble_sort_patients_by_name()
            print("Pacientes ordenados por nombre:")
        elif order_type == "id":
            self.quick_sort_patients_by_id()
            print("Pacientes ordenados por ID:")
        
        for p in self.patients:
            print(p)

    # --------- Citas 
    def create_appointment(self, patient_id: int, date_str: str, service: str, price: float):
        try:
            if patient_id not in self.patient_hash:
                raise ValueError("Error: El paciente no existe en el sistema.")
            date_formats = ["%Y-%m-%d %H:%M", "%Y/%m/%d", "%Y-%m-%d"]
            parsed = None
            used_fmt = None
            for fmt in date_formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    used_fmt = fmt
                    break
                except ValueError:
                    continue
            if not parsed:
                raise ValueError("Error: Formato de fecha incorrecto. Use 'YYYY-MM-DD HH:MM' o 'YYYY/MM/DD'")

            date_str = parsed.strftime("%Y-%m-%d %H:%M")
            
            if price < 0:
                raise ValueError("Error: El precio no puede ser negativo.")
            
            if not service.strip():
                raise ValueError("Error: El servicio no puede estar vacío.")

            with sqlite3.connect("clinic.db") as conn:
                c = conn.cursor()
                c.execute("INSERT INTO appointments (patient_id, date, service, price) VALUES (?, ?, ?, ?)",
                          (patient_id, date_str, service, price))
                conn.commit()
                appointment_id = c.lastrowid
                
                appt = Appointment(appointment_id, patient_id, date_str, service, price)
                self.appointments.append(appt)
                print(f"Cita creada exitosamente con ID {appointment_id}")
                return appt

        except sqlite3.Error as e:
            print(f"Error de base de datos: {str(e)}")
            return None
        except ValueError as e:
            print(str(e))
            return None
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return None

    def list_appointments(self):
        try:
            with sqlite3.connect("clinic.db") as conn:
                c = conn.cursor()
                c.execute("SELECT id, patient_id, date, service, price, attended FROM appointments ORDER BY date")
                appointments = c.fetchall()
                
                if not appointments:
                    print("No hay citas registradas en el sistema.")
                    return
                
                print("\nLista de citas:")
                print("ID | Paciente ID | Fecha | Servicio | Precio | Atendida")
                print("-" * 60)
                for row in appointments:
                    print(f"{row[0]:2d} | {row[1]:10d} | {row[2]} | {row[3]:8s} | ${row[4]:6.2f} | {'Sí' if row[5] else 'No'}")
                
        except sqlite3.Error as e:
            print(f"Error al acceder a la base de datos: {str(e)}")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")

    def mark_attended(self, appointment_id: int):
        try:
            with sqlite3.connect("clinic.db") as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM appointments WHERE id = ?", (appointment_id,))
                if not c.fetchone():
                    raise ValueError(f"Error: La cita con ID {appointment_id} no existe en el sistema.")
                

                c.execute("SELECT attended FROM appointments WHERE id = ?", (appointment_id,))
                row = c.fetchone()
                if row and row[0] == 1:
                    raise ValueError(f"Error: La cita con ID {appointment_id} ya está marcada como atendida.")
                
                c.execute("UPDATE appointments SET attended = 1 WHERE id = ?", (appointment_id,))
                if c.rowcount == 0:
                    raise ValueError(f"Error: No se pudo marcar la cita como atendida.")
                
                conn.commit()
                print("Cita marcada como atendida exitosamente.")
                
        except sqlite3.Error as e:
            print(f"Error de base de datos: {str(e)}")
        except ValueError as e:
            print(str(e))
        except Exception as e:
            print(f"Error inesperado: {str(e)}")

    def cancel_appointment(self, appointment_id: int):
        try:
            with sqlite3.connect("clinic.db") as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM appointments WHERE id = ?", (appointment_id,))
                if not c.fetchone():
                    raise ValueError(f"Error: La cita con ID {appointment_id} no existe en el sistema.")
                
                c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                if c.rowcount == 0:
                    raise ValueError(f"Error: No se pudo eliminar la cita con ID {appointment_id}.")
                conn.commit()
                print("Cita cancelada exitosamente.")
        except sqlite3.Error as e:
            print(f"Error de base de datos: {str(e)}")
        except ValueError as e:
            print(str(e))
        except Exception as e:
            print(f"Error inesperado: {str(e)}")

    # --------- Exportar datos ---------
    def export_data_json(self):
        try:
            if not self.patients and not self.appointments:
                raise ValueError("No hay datos para exportar. El sistema está vacío.")
            
            data = {
                "patients": [p.__dict__ for p in self.patients],
                "appointments": [a.__dict__ for a in self.appointments]
            }
            
            try:
                with open("clinic_export.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("Datos exportados exitosamente a clinic_export.json")
            except IOError as e:
                raise IOError(f"Error al escribir el archivo: {str(e)}")
                
        except ValueError as e:
            print(str(e))
        except IOError as e:
            print(str(e))
        except Exception as e:
            print(f"Error inesperado al exportar datos: {str(e)}")

# ------------------ Menú interactivo ------------------
def main_menu():
    sys = ClinicSystem()
    while True:
        print("\n=== Menú Clínica Dental ===")
        print("1) Agregar paciente")
        print("2) Listar pacientes")
        print("3) Ver detalles de paciente")
        print("4) Actualizar paciente")
        print("5) Eliminar paciente")
        print("6) Crear cita")
        print("7) Listar citas")
        print("8) Marcar cita como atendida")
        print("9) Cancelar cita")
        print("10) Buscar paciente por nombre")
        print("11) Exportar datos a JSON")
        print("12) Listar pacientes ordenados por nombre")
        print("13) Listar pacientes ordenados por ID")
        print("14) Salir")
        op = input("Elige opción: ").strip()

        if op == "1":
            name = input("Nombre: ")
            age = int(input("Edad: "))
            phone = input("Teléfono: ")
            address = input("Dirección: ")
            photo = input("Ruta de foto: ").strip() or None
            p = create_patient_db(name, age, phone, address, photo)
            sys.patients.append(p)
            sys.patient_hash[p.patient_id] = p

        elif op == "2":
            for p in sys.patients:
                print(p)

        elif op == "3":
            pid = int(input("ID paciente: "))
            p = get_patient_by_id(pid)
            if not p:
                print("Paciente no encontrado.")
            else:
                print(f"\nID: {p.patient_id}")
                print(f"Nombre: {p.name}")
                print(f"Edad: {p.age}")
                print(f"Teléfono: {p.phone}")
                print(f"Dirección: {p.address}")
                print(f"Foto: {p.photo_path or 'Sin foto'}")

        elif op == "4":
            pid = int(input("ID paciente a actualizar: "))
            name = input("Nuevo nombre (enter para no cambiar): ").strip() or None
            age_in = input("Nueva edad (enter para no cambiar): ").strip()
            age = int(age_in) if age_in else None
            phone = input("Nuevo teléfono: ").strip() or None
            address = input("Nueva dirección: ").strip() or None
            photo = input("Nueva ruta de foto (dejar vacío si no): ").strip() or None
            p = update_patient_db(pid, name, age, phone, address, photo)
            if p:
                print("Paciente actualizado.")
            else:
                print("Paciente no encontrado.")

        elif op == "5":
            pid = int(input("ID paciente a eliminar: "))
            if delete_patient_db(pid):
                sys.patients = [x for x in sys.patients if x.patient_id != pid]
                print("Paciente eliminado.")
            else:
                print("Paciente no encontrado.")

        elif op == "6":
            try:
                pid = int(input("ID paciente: "))
            except ValueError:
                print("ID de paciente inválido. Debe ser un número.")
                continue
            date = input("Fecha y hora (YYYY-MM-DD HH:MM) o fecha (YYYY/MM/DD): ")
            service = input("Servicio: ")
            try:
                price = float(input("Precio: "))
            except ValueError:
                print("Precio inválido. Debe ser un número.")
                continue
            sys.create_appointment(pid, date, service, price)

        elif op == "7":
            sys.list_appointments()

        elif op == "8":
            aid = int(input("ID cita: "))
            sys.mark_attended(aid)

        elif op == "9":
            aid = int(input("ID cita a cancelar: "))
            sys.cancel_appointment(aid)

        elif op == "10":
            q = input("Buscar nombre: ").strip()
            res = search_patients_by_name(q)
            for p in res:
                print(p)

        elif op == "11":
            sys.export_data_json()

        elif op == "12":
            sys.list_patients_ordered("name")

        elif op == "13":
            sys.list_patients_ordered("id")

        elif op == "14":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main_menu()