"""Punto de entrada del proyecto EcoTech.

Ejecuta un ejemplo simple de creación de empleados, un departamento y un
proyecto para verificar que la estructura del dominio funciona correctamente.
"""
from datetime import date

from src.dominio import Departamento, Empleado, Proyecto


def main() -> None:
    empleado1 = Empleado(1, "Ana Pérez", "Desarrolladora", 1200000)
    empleado2 = Empleado(2, "Luis Gómez", "Analista", 1100000)

    departamento = Departamento(1, "Tecnología", "Carlos Ruiz")
    departamento.agregar_empleado(empleado1)
    departamento.agregar_empleado(empleado2)

    proyecto = Proyecto(1, "Migración a la nube", "Proyecto de modernización de infraestructura", date.today())
    proyecto.asignar_empleado(empleado1)
    proyecto.asignar_empleado(empleado2)

    print(departamento)
    for empleado in departamento.empleados:
        print(f"  {empleado}")

    print(proyecto)
    for empleado in proyecto.empleados_asignados:
        print(f"  {empleado}")


if __name__ == "__main__":
    main()
