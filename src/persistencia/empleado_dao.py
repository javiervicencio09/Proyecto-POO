from typing import List, Optional

from src.dominio.empleado import Empleado
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import (
    convertir_fecha,
    exigir_guardado,
    exigir_nuevo,
    fecha_a_texto,
    sesion_bd,
)

# Empleado hereda de Usuario: sus datos están repartidos en usuario (nombre, correo, hash) y empleado.
_SELECT = (
    "SELECT u.id_usuario, u.nombre, e.cargo, e.salario, e.direccion, e.telefono, "
    "u.correo, e.fecha_inicio_contrato, u.contrasena_hash "
    "FROM empleado e INNER JOIN usuario u ON u.id_usuario = e.id_usuario"
)


class EmpleadoDAO:
    """Persistencia de Empleado (tablas usuario + empleado). Un solo punto que sabe armar un Empleado."""

    @staticmethod
    def _fila_a_empleado(fila) -> Empleado:
        """Única función que transforma una fila en Empleado (la reutilizan los demás DAO)."""
        return Empleado(
            id_empleado=fila[0],
            nombre=fila[1],
            cargo=fila[2],
            salario=float(fila[3]),  # MySQL entrega Decimal
            direccion=fila[4] or "",
            telefono=fila[5] or "",
            correo=fila[6] or "",
            fecha_inicio_contrato=convertir_fecha(fila[7]),
            contrasena_hash=fila[8] or "",
        )

    @staticmethod
    def insertar(empleado: Empleado) -> Empleado:
        """Guarda el empleado y le asigna el id generado por la BD (id_empleado == id_usuario)."""
        exigir_nuevo(empleado.id_empleado, "El empleado")
        p = marcador_sql()

        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO usuario (nombre, correo, contrasena_hash, tipo_usuario) VALUES ({p}, {p}, {p}, 'EMPLEADO')",
                (empleado.nombre, empleado.correo or None, empleado.contrasena_hash),
            )
            nuevo_id = cursor.lastrowid
            cursor.execute(
                f"INSERT INTO empleado (id_usuario, cargo, salario, direccion, telefono, fecha_inicio_contrato) "
                f"VALUES ({p}, {p}, {p}, {p}, {p}, {p})",
                (
                    nuevo_id,
                    empleado.cargo,
                    empleado.salario,
                    empleado.direccion,
                    empleado.telefono,
                    fecha_a_texto(empleado.fecha_inicio_contrato),
                ),
            )
        empleado.id_empleado = nuevo_id  # solo después del COMMIT
        return empleado

    @staticmethod
    def buscar_por_id(id_empleado: int) -> Optional[Empleado]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE e.id_usuario = {p}", (id_empleado,))
            fila = cursor.fetchone()
        return EmpleadoDAO._fila_a_empleado(fila) if fila else None

    @staticmethod
    def buscar_por_correo(correo: str) -> Optional[Empleado]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE u.correo = {p}", (correo.strip().lower(),))
            fila = cursor.fetchone()
        return EmpleadoDAO._fila_a_empleado(fila) if fila else None

    @staticmethod
    def listar() -> List[Empleado]:
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY e.id_usuario")
            filas = cursor.fetchall()
        return [EmpleadoDAO._fila_a_empleado(fila) for fila in filas]

    @staticmethod
    def listar_por_departamento(id_departamento: int) -> List[Empleado]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE e.id_departamento = {p} ORDER BY u.nombre", (id_departamento,))
            filas = cursor.fetchall()
        return [EmpleadoDAO._fila_a_empleado(fila) for fila in filas]

    @staticmethod
    def listar_por_proyecto(id_proyecto: int) -> List[Empleado]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"{_SELECT} INNER JOIN proyecto_empleado pe ON pe.id_empleado = e.id_usuario "
                f"WHERE pe.id_proyecto = {p} ORDER BY u.nombre",
                (id_proyecto,),
            )
            filas = cursor.fetchall()
        return [EmpleadoDAO._fila_a_empleado(fila) for fila in filas]

    @staticmethod
    def actualizar(empleado: Empleado) -> bool:
        """True si se actualizó; False si no existe un empleado con ese id."""
        exigir_guardado(empleado.id_empleado, "El empleado")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE empleado SET cargo = {p}, salario = {p}, direccion = {p}, telefono = {p}, "
                f"fecha_inicio_contrato = {p} WHERE id_usuario = {p}",
                (
                    empleado.cargo,
                    empleado.salario,
                    empleado.direccion,
                    empleado.telefono,
                    fecha_a_texto(empleado.fecha_inicio_contrato),
                    empleado.id_empleado,
                ),
            )
            actualizado = cursor.rowcount > 0
            if actualizado:
                cursor.execute(
                    f"UPDATE usuario SET nombre = {p}, correo = {p}, contrasena_hash = {p} WHERE id_usuario = {p}",
                    (empleado.nombre, empleado.correo or None, empleado.contrasena_hash, empleado.id_empleado),
                )
        return actualizado

    @staticmethod
    def eliminar(id_empleado: int) -> bool:
        """
        True si se eliminó; False si no existía. Se borra la fila de usuario y la BD elimina en cascada
        los datos del empleado, sus asignaciones y sus registros de tiempo; si era gerente, el
        departamento queda sin gerente.
        """
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"DELETE FROM usuario WHERE id_usuario = {p} AND tipo_usuario = 'EMPLEADO'", (id_empleado,))
            return cursor.rowcount > 0
