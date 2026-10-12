from typing import List, Optional

from src.dominio.registro_tiempo import RegistroDeTiempo
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, convertir_fecha, marcador


class RegistroTiempoDAO:
    """
    Data Access Object para la persistencia de registros de tiempo trabajados.
    Permite trazabilidad por empleado y proyecto según diagrama UML.
    """

    def guardar(self, registro: RegistroDeTiempo) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(registro.fecha) if registro.fecha else None
        try:
            cursor.execute(
                f"INSERT INTO registro_tiempo (id_empleado, id_proyecto, fecha, horas, descripcion_tareas) "
                f"VALUES ({p}, {p}, {p}, {p}, {p})",
                (
                    registro.id_empleado,
                    registro.id_proyecto,
                    fecha_str,
                    registro.horas,
                    registro.descripcion_tareas,
                ),
            )
            conexion.commit()
            registro.id_registro = cursor.lastrowid
            return registro.id_registro
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar registro de tiempo: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_registro: int) -> Optional[RegistroDeTiempo]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_registro, fecha, horas, descripcion_tareas, id_empleado, id_proyecto "
                f"FROM registro_tiempo WHERE id_registro = {p}",
                (id_registro,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            id_reg, fecha, horas, desc, emp_id, proy_id = fila
            return RegistroDeTiempo(
                id_reg,
                convertir_fecha(fecha),
                float(horas),
                desc,
                emp_id,
                proy_id,
            )
        except Exception as err:
            raise DAOError(f"Error al buscar registro de tiempo ID {id_registro}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar(self) -> List[RegistroDeTiempo]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_registro, fecha, horas, descripcion_tareas, id_empleado, id_proyecto "
                "FROM registro_tiempo ORDER BY fecha DESC, id_registro DESC"
            )
            return [
                RegistroDeTiempo(
                    f[0],
                    convertir_fecha(f[1]),
                    float(f[2]),
                    f[3],
                    f[4],
                    f[5],
                )
                for f in cursor.fetchall()
            ]
        except Exception as err:
            raise DAOError(f"Error al listar registros de tiempo: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_por_empleado(self, id_empleado: int) -> List[RegistroDeTiempo]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_registro, fecha, horas, descripcion_tareas, id_empleado, id_proyecto "
                f"FROM registro_tiempo WHERE id_empleado = {p} ORDER BY fecha DESC",
                (id_empleado,),
            )
            return [
                RegistroDeTiempo(
                    f[0],
                    convertir_fecha(f[1]),
                    float(f[2]),
                    f[3],
                    f[4],
                    f[5],
                )
                for f in cursor.fetchall()
            ]
        except Exception as err:
            raise DAOError(f"Error al listar tiempos del empleado ID {id_empleado}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_por_proyecto(self, id_proyecto: int) -> List[RegistroDeTiempo]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_registro, fecha, horas, descripcion_tareas, id_empleado, id_proyecto "
                f"FROM registro_tiempo WHERE id_proyecto = {p} ORDER BY fecha DESC",
                (id_proyecto,),
            )
            return [
                RegistroDeTiempo(
                    f[0],
                    convertir_fecha(f[1]),
                    float(f[2]),
                    f[3],
                    f[4],
                    f[5],
                )
                for f in cursor.fetchall()
            ]
        except Exception as err:
            raise DAOError(f"Error al listar tiempos del proyecto ID {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def total_horas_proyecto(self, id_proyecto: int) -> float:
        registros = self.listar_por_proyecto(id_proyecto)
        return RegistroDeTiempo.calcularHorasTotales(registros)

    def eliminar(self, id_registro: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM registro_tiempo WHERE id_registro = {p}", (id_registro,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar registro de tiempo ID {id_registro}: {err}") from err
        finally:
            cursor.close()
            conexion.close()
