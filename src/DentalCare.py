#!/usr/bin/env python3
"""
Sistema de Clínica Odontológica Dental Care
"""

import os, sys
import sqlite3
import json

#Inicio de sesion

PIN_CLINICA = "admin123"

def iniciar_sesion():
    print("\n---SISTEMA DENTAL CARE---")
    print("Acceso Restringido - Ingrese el pin de la clinica\n")

    intentos = 3
    while intentos > 0:
        pin = input("Ingrese el PIN:").strip()
        if pin == PIN_CLINICA:
            print("\n Acceso concedido. Bienvenid@ al sistema Dental Care\n")
            return True
        else:
            intentos -= 1
            print(f"PIN incorrecto. Intentos restantes: {intentos}\n")

    print("Acceso denegado. Saliendo del sistema.")
    exit()


from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any

#datos
sys.path.append(os.path.join(os.path.dirname(__file__), "Classes"))

from Classes.ClassNode import Node
from Classes.ClassLinkedList import LinkedList
from Classes.ClassStack import Stack
from Classes.ClassQueue import Queue




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

from utils.algorithms import bubble_sort, selection_sort, busqueda_binaria
from utils.helpers import validar_fecha, validar_numero, exportar_json

DB_FILE = "clinic.db"

#FUNCIONES DE CITAS
def ensure_appointments_table():
    with sqlite3.connect(DB_FILE) as conn:
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

def create_appointment(patient_id, date, service, price):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO appointments (patient_id, date, service, price) VALUES (?, ?, ?, ?)",
                  (patient_id, date, service, price))
        conn.commit()
        print("Cita creada correctamente.")

def list_appointments():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        for row in c.execute("SELECT id, patient_id, date, service, price, attended FROM appointments"):
            print(row)

def mark_appointment_attended(aid):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE appointments SET attended = 1 WHERE id = ?", (aid,))
        conn.commit()
        print("Cita marcada como atendida.")

def cancel_appointment(aid):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM appointments WHERE id = ?", (aid,))
        conn.commit()
        print("Cita cancelada.")


# MENÚ PRINCIPAL
def main():
    iniciar_sesion()
    ensure_appointments_table()
    while True:
        print("\n---DENTAL CARE - SISTEMA DE CLÍNICA---")
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
        print("14) Buscar paciente (búsqueda binaria por ID)")
        print("15) Salir")
        op = input("\nSeleccione una opción: ")

        if op == "1":
            name = input("Nombre: ")
            age = int(input("Edad: "))
            phone = input("Teléfono: ")
            address = input("Dirección: ")
            photo = input("Ruta de foto (opcional): ") or None
            p = create_patient_db(name, age, phone, address, photo)
            print(f"Paciente {p.name} agregado con ID {p.patient_id}.")

        elif op == "2":
            patients = load_all_patients_from_db()
            for p in patients:
                print(f"{p.patient_id:3} | {p.name:20} | {p.age} años | Tel: {p.phone}")

        elif op == "3":
            pid = int(input("ID del paciente: "))
            p = get_patient_by_id(pid)
            if p:
                print(f"\n--- DETALLES ---\nID: {p.patient_id}\nNombre: {p.name}\nEdad: {p.age}\nTeléfono: {p.phone}\nDirección: {p.address}\n")
            else:
                print("Paciente no encontrado.")

        elif op == "4":
            pid = int(input("ID a actualizar: "))
            name = input("Nuevo nombre (Enter para dejar igual): ") or None
            age = input("Nueva edad: ") or None
            phone = input("Nuevo teléfono: ") or None
            addr = input("Nueva dirección: ") or None
            photo = input("Nueva foto (opcional): ") or None
            ok = update_patient_db(pid,
                                   name=name,
                                   age=int(age) if age else None,
                                   phone=phone,
                                   address=addr,
                                   photo_source_path=photo)
            print("Actualizado correctamente." if ok else "No se pudo actualizar.")

        elif op == "5":
            pid = int(input("ID a eliminar: "))
            if delete_patient_db(pid):
                print("Paciente eliminado.")
            else:
                print("No se encontró ese ID.")

        elif op == "6":
            pid = int(input("ID del paciente: "))
            date = input("Fecha (YYYY-MM-DD HH:MM): ")
            if not validar_fecha(date):
                print("Formato incorrecto.")
                continue
            service = input("Servicio: ")
            price = input("Precio: ")
            if not validar_numero(price):
                print("Precio inválido.")
                continue
            create_appointment(pid, date, service, float(price))

        elif op == "7":
            list_appointments()

        elif op == "8":
            aid = int(input("ID de la cita a marcar: "))
            mark_appointment_attended(aid)

        elif op == "9":
            aid = int(input("ID de la cita a cancelar: "))
            cancel_appointment(aid)

        elif op == "10":
            name = input("Nombre a buscar: ")
            res = search_patients_by_name(name)
            for p in res:
                print(f"{p.patient_id} | {p.name} | {p.age} años")

        elif op == "11":
            patients = load_all_patients_from_db()
            with sqlite3.connect(DB_FILE) as conn:
                citas = list(conn.execute("SELECT * FROM appointments"))
            exportar_json(patients, citas)

        elif op == "12":
            patients = load_all_patients_from_db()
            patients = bubble_sort(patients, key=lambda x: x.name.lower())
            for p in patients:
                print(f"{p.patient_id} | {p.name}")

        elif op == "13":
            patients = load_all_patients_from_db()
            patients = selection_sort(patients, key=lambda x: x.patient_id)
            for p in patients:
                print(f"{p.patient_id} | {p.name}")

        elif op == "14":
            pid = int(input("ID del paciente a buscar: "))
            patients = load_all_patients_from_db()
            patients.sort(key=lambda x: x.patient_id)
            result = busqueda_binaria(patients, key=lambda x: x.patient_id, valor=pid)
            print(f"Encontrado: {result.name}" if result else "No se encontró ese paciente.")

        elif op == "15":
            print("Saliendo de DentalCare")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()