from datetime import datetime

class Cita:
    def __init__(self, paciente, fecha, hora, servicio):
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora
        self.servicio = servicio

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.paciente} ({self.servicio})"

citas = []

def registrar_cita():
    paciente = input("Nombre del paciente: ")
    fecha = input("Fecha (dd/mm/aaaa): ")
    hora = input("Hora (hh:mm): ")
    servicio = input("Servicio odontológico: ")

    cita = Cita(paciente, fecha, hora, servicio)
    citas.append(cita)
    print("Cita registrada correctamente.")

def mostrar_citas():
    if not citas:
        print("No hay citas registradas.")
        return
    print("Citas programadas:")
    for c in citas:
        print("-", c)
    print()

def buscar_cita_binaria(nombre):
  
    ordenar_citas_bubble()

    izq, der = 0, len(citas) - 1
    while izq <= der:
        medio = (izq + der) // 2
        if citas[medio].paciente.lower() == nombre.lower():
            print("🔍 Cita encontrada:", citas[medio])
            return
        elif citas[medio].paciente.lower() < nombre.lower():
            izq = medio + 1
        else:
            der = medio - 1
    print("No se encontró cita para ese paciente.\n")

def ordenar_citas_bubble():
    n = len(citas)
    for i in range(n):
        for j in range(0, n - i - 1):
            if citas[j].paciente.lower() > citas[j + 1].paciente.lower():
                citas[j], citas[j + 1] = citas[j + 1], citas[j]