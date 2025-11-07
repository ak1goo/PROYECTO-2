# utils/helpers.py

from datetime import datetime
import json

def validar_fecha(fecha_str):
    
    try:
        datetime.fromisoformat(fecha_str)
        return True
    except Exception:
        return False

def validar_numero(valor):
    
    try:
        float(valor)
        return True
    except ValueError:
        return False

def exportar_json(pacientes, citas, archivo="clinic_export.json"):
    
    data = {
        "pacientes": [p.__dict__ for p in pacientes],
        "citas": citas
    }
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nDatos exportados correctamente a {archivo}\n")
