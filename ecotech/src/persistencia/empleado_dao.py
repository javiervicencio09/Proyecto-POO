from typing import List, Optional

from src.dominio.empleado import Empleado
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, convertir_fecha, marcador


class EmpleadoDAO:
    """
    Data Access Object para Empleado con manejo de transacciones y excepciones seguras.
    """

    def guardar(self, empleado: Empleado) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(empleado.fecha_inicio_contrato) if empleado.fecha_inicio_contrato else None
        try:
            cursor.execute(
                f"INSERT INTO empleado (nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato, id_usuario) "
                f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (
                    empleado.nombre,
                    empleado.cargo,
                    empleado.salario,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.correo,
                    fecha_str,
                    empleado.id_usuario,
                ),
            )
            conexion.commit()
            empleado.id_empleado = cursor.lastrowid
            return empleado.id_empleado
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar empleado '{empleado.nombre}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_empleado: int) -> Optional[Empleado]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_empleado, nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato "
                f"FROM empleado WHERE id_empleado = {p}",
                (id_empleado,),
            )
            fila = cursor.fetchone()
            if fila is None:
                return None
            return Empleado(
                id_empleado=fila[0],
                nombre=fila[1],
                cargo=fila[2],
                salario=float(fila[3]),
                direccion=fila[4] or "",
                telefono=fila[5] or "",
                correo=fila[6] or "",
                fecha_inicio_contrato=convertir_fecha(fila[7]),
            )
        except Exception as err:
            raise DAOError(f"Error al buscar empleado ID {id_empleado}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar(self) -> List[Empleado]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_empleado, nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato "
                "FROM empleado ORDER BY id_empleado"
            )
            resultado = []
            for fila in cursor.fetchall():
                resultado.append(
                    Empleado(
                        id_empleado=fila[0],
                        nombre=fila[1],
                        cargo=fila[2],
                        salario=float(fila[3]),
                        direccion=fila[4] or "",
                        telefono=fila[5] or "",
                        correo=fila[6] or "",
                        fecha_inicio_contrato=convertir_fecha(fila[7]),
                    )
                )
            return resultado
        except Exception as err:
            raise DAOError(f"Error al listar empleados: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, empleado: Empleado) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(empleado.fecha_inicio_contrato) if empleado.fecha_inicio_contrato else None
        try:
            cursor.execute(
                f"UPDATE empleado SET nombre={p}, cargo={p}, salario={p}, "
                f"direccion={p}, telefono={p}, correo={p}, fecha_inicio_contrato={p} "
                f"WHERE id_empleado={p}",
                (
                    empleado.nombre,
                    empleado.cargo,
                    empleado.salario,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.correo,
                    fecha_str,
                    empleado.id_empleado,
                ),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al actualizar empleado ID {empleado.id_empleado}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM empleado WHERE id_empleado = {p}", (id_empleado,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar empleado ID {id_empleado}: {err}") from err
        finally:
            cursor.close()
            conexion.close()