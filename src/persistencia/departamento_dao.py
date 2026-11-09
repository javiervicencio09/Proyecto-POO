from typing import List, Optional

from src.dominio.departamento import Departamento
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import DAOError, exigir_guardado, exigir_nuevo, sesion_bd
from src.persistencia.empleado_dao import EmpleadoDAO


class DepartamentoDAO:
    """
    Persistencia de Departamento. Relaciones del UML:
      - empleados (1 a 0..*): columna empleado.id_departamento
      - gerente   (1 a 0..1): columna departamento.id_gerente
    """

    @staticmethod
    def _id_gerente(departamento: Departamento) -> Optional[int]:
        """Id del gerente (columna id_gerente). La BD solo guarda un Empleado ya registrado, o NULL."""
        gerente = departamento.gerente
        if gerente is None:
            return None
        if gerente.id_empleado is None:
            raise DAOError("El gerente debe ser un empleado ya registrado en la base de datos.")
        return gerente.id_empleado

    @staticmethod
    def _armar(fila) -> Departamento:
        """Reconstruye el Departamento con su gerente y sus empleados (consultas aparte, ya cerrada la anterior)."""
        id_departamento, nombre, id_gerente = fila
        gerente = EmpleadoDAO.buscar_por_id(id_gerente) if id_gerente is not None else None
        empleados = EmpleadoDAO.listar_por_departamento(id_departamento)
        return Departamento(id_departamento, nombre, gerente, empleados)

    @staticmethod
    def insertar(departamento: Departamento) -> Departamento:
        exigir_nuevo(departamento.id_departamento, "El departamento")
        id_gerente = DepartamentoDAO._id_gerente(departamento)
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO departamento (nombre, id_gerente) VALUES ({p}, {p})",
                (departamento.nombre, id_gerente),
            )
            nuevo_id = cursor.lastrowid
        departamento.id_departamento = nuevo_id
        return departamento

    @staticmethod
    def buscar_por_id(id_departamento: int) -> Optional[Departamento]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"SELECT id_departamento, nombre, id_gerente FROM departamento WHERE id_departamento = {p}",
                (id_departamento,),
            )
            fila = cursor.fetchone()
        return DepartamentoDAO._armar(fila) if fila else None

    @staticmethod
    def listar() -> List[Departamento]:
        with sesion_bd() as cursor:
            cursor.execute("SELECT id_departamento, nombre, id_gerente FROM departamento ORDER BY id_departamento")
            filas = cursor.fetchall()
        return [DepartamentoDAO._armar(fila) for fila in filas]

    @staticmethod
    def actualizar(departamento: Departamento) -> bool:
        """Actualiza nombre y gerente. True si existía; False si no."""
        exigir_guardado(departamento.id_departamento, "El departamento")
        id_gerente = DepartamentoDAO._id_gerente(departamento)
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE departamento SET nombre = {p}, id_gerente = {p} WHERE id_departamento = {p}",
                (departamento.nombre, id_gerente, departamento.id_departamento),
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(id_departamento: int) -> bool:
        """True si se eliminó. Sus empleados no se borran: quedan sin departamento."""
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"DELETE FROM departamento WHERE id_departamento = {p}", (id_departamento,))
            return cursor.rowcount > 0

    @staticmethod
    def agregar_empleado(id_departamento: int, id_empleado: int) -> bool:
        """
        Persistencia del método UML agregar_empleado(). Un empleado pertenece a un solo departamento,
        así que si estaba en otro se traslada. False si el empleado no existe;
        si el departamento no existe la BD rechaza la operación (DAOIntegridadError).
        """
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE empleado SET id_departamento = {p} WHERE id_usuario = {p}",
                (id_departamento, id_empleado),
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar_empleado(id_departamento: int, id_empleado: int) -> bool:
        """Persistencia de eliminar_empleado(): True si el empleado pertenecía a ese departamento."""
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE empleado SET id_departamento = NULL WHERE id_usuario = {p} AND id_departamento = {p}",
                (id_empleado, id_departamento),
            )
            return cursor.rowcount > 0
