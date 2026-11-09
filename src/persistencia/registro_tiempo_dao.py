from typing import List, Optional

from src.dominio.registro_tiempo import RegistroDeTiempo
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import (
    convertir_fecha,
    exigir_guardado,
    exigir_nuevo,
    fecha_a_texto,
    sesion_bd,
)

_SELECT = (
    "SELECT id_registro, fecha, horas, descripcion_tareas, id_empleado, id_proyecto FROM registro_tiempo"
)


class RegistroTiempoDAO:
    """
    Persistencia de RegistroDeTiempo. Cada registro pertenece a un empleado (id_empleado) y a un
    proyecto (id_proyecto): ambas claves son obligatorias y la BD comprueba que existan.
    """

    @staticmethod
    def _fila_a_registro(fila) -> RegistroDeTiempo:
        return RegistroDeTiempo(
            id_registro=fila[0],
            fecha=convertir_fecha(fila[1]),
            horas=float(fila[2]),  # MySQL entrega Decimal
            descripcion_tareas=fila[3],
            id_empleado=fila[4],
            id_proyecto=fila[5],
        )

    @staticmethod
    def insertar(registro: RegistroDeTiempo) -> RegistroDeTiempo:
        exigir_nuevo(registro.id_registro, "El registro de tiempo")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO registro_tiempo (id_empleado, id_proyecto, fecha, horas, descripcion_tareas) "
                f"VALUES ({p}, {p}, {p}, {p}, {p})",
                (
                    registro.id_empleado,
                    registro.id_proyecto,
                    fecha_a_texto(registro.fecha),
                    registro.horas,
                    registro.descripcion_tareas,
                ),
            )
            nuevo_id = cursor.lastrowid
        registro.id_registro = nuevo_id
        return registro

    @staticmethod
    def buscar_por_id(id_registro: int) -> Optional[RegistroDeTiempo]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE id_registro = {p}", (id_registro,))
            fila = cursor.fetchone()
        return RegistroTiempoDAO._fila_a_registro(fila) if fila else None

    @staticmethod
    def listar() -> List[RegistroDeTiempo]:
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY fecha DESC, id_registro DESC")
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def listar_por_empleado(id_empleado: int) -> List[RegistroDeTiempo]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"{_SELECT} WHERE id_empleado = {p} ORDER BY fecha DESC, id_registro DESC", (id_empleado,)
            )
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def listar_por_proyecto(id_proyecto: int) -> List[RegistroDeTiempo]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"{_SELECT} WHERE id_proyecto = {p} ORDER BY fecha DESC, id_registro DESC", (id_proyecto,)
            )
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def total_horas_proyecto(id_proyecto: int) -> float:
        """Usa el método del dominio calcular_horas_totales() sobre los registros del proyecto."""
        return RegistroDeTiempo.calcular_horas_totales(RegistroTiempoDAO.listar_por_proyecto(id_proyecto))

    @staticmethod
    def actualizar(registro: RegistroDeTiempo) -> bool:
        """Modifica fecha, horas y descripción (el empleado y el proyecto no cambian)."""
        exigir_guardado(registro.id_registro, "El registro de tiempo")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE registro_tiempo SET fecha = {p}, horas = {p}, descripcion_tareas = {p} "
                f"WHERE id_registro = {p}",
                (fecha_a_texto(registro.fecha), registro.horas, registro.descripcion_tareas, registro.id_registro),
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(id_registro: int) -> bool:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"DELETE FROM registro_tiempo WHERE id_registro = {p}", (id_registro,))
            return cursor.rowcount > 0
