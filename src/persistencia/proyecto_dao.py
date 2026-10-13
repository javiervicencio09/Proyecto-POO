from typing import List, Optional

from src.dominio.proyecto import Proyecto
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import (
    convertir_fecha,
    exigir_guardado,
    exigir_nuevo,
    fecha_a_texto,
    sesion_bd,
)
from src.persistencia.empleado_dao import EmpleadoDAO

_SELECT = "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto"


class ProyectoDAO:
    """Persistencia de Proyecto. La relación 'asignado a' (0..* a 0..*) usa la tabla proyecto_empleado."""

    @staticmethod
    def _fila_a_proyecto(fila) -> Proyecto:
        """Reconstruye el Proyecto y carga sus empleados asignados."""
        proyecto = Proyecto(fila[0], fila[1], fila[2], convertir_fecha(fila[3]))
        proyecto.empleados_asignados = EmpleadoDAO.listar_por_proyecto(proyecto.id_proyecto)
        return proyecto

    @staticmethod
    def insertar(proyecto: Proyecto) -> Proyecto:
        exigir_nuevo(proyecto.id_proyecto, "El proyecto")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES ({p}, {p}, {p})",
                (proyecto.nombre, proyecto.descripcion, fecha_a_texto(proyecto.fecha_inicio)),
            )
            nuevo_id = cursor.lastrowid
        proyecto.id_proyecto = nuevo_id
        return proyecto

    @staticmethod
    def buscar_por_id(id_proyecto: int) -> Optional[Proyecto]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE id_proyecto = {p}", (id_proyecto,))
            fila = cursor.fetchone()
        return ProyectoDAO._fila_a_proyecto(fila) if fila else None

    @staticmethod
    def listar() -> List[Proyecto]:
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY id_proyecto")
            filas = cursor.fetchall()
        return [ProyectoDAO._fila_a_proyecto(fila) for fila in filas]

    @staticmethod
    def actualizar(proyecto: Proyecto) -> bool:
        exigir_guardado(proyecto.id_proyecto, "El proyecto")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE proyecto SET nombre = {p}, descripcion = {p}, fecha_inicio = {p} WHERE id_proyecto = {p}",
                (proyecto.nombre, proyecto.descripcion, fecha_a_texto(proyecto.fecha_inicio), proyecto.id_proyecto),
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(id_proyecto: int) -> bool:
        """True si se eliminó. También se eliminan sus asignaciones y registros de tiempo (cascada)."""
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"DELETE FROM proyecto WHERE id_proyecto = {p}", (id_proyecto,))
            return cursor.rowcount > 0

    @staticmethod
    def asignar_empleado(id_proyecto: int, id_empleado: int) -> bool:
        """
        Persistencia de asignar_empleado(). True si se asignó; False si ya estaba asignado.
        Si el proyecto o el empleado no existen, la BD lo rechaza (DAOIntegridadError).
        """
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"SELECT 1 FROM proyecto_empleado WHERE id_proyecto = {p} AND id_empleado = {p}",
                (id_proyecto, id_empleado),
            )
            if cursor.fetchone() is not None:
                return False
            cursor.execute(
                f"INSERT INTO proyecto_empleado (id_proyecto, id_empleado) VALUES ({p}, {p})",
                (id_proyecto, id_empleado),
            )
            return True

    @staticmethod
    def desasignar_empleado(id_proyecto: int, id_empleado: int) -> bool:
        """Persistencia de desasignar_empleado(): True si la asignación existía."""
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"DELETE FROM proyecto_empleado WHERE id_proyecto = {p} AND id_empleado = {p}",
                (id_proyecto, id_empleado),
            )
            return cursor.rowcount > 0
