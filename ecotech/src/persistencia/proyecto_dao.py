from typing import List, Optional

from src.dominio.empleado import Empleado
from src.dominio.proyecto import Proyecto
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, convertir_fecha, marcador


class ProyectoDAO:
    """
    Data Access Object para Proyecto con manejo seguro de transacciones.
    """

    def guardar(self, proyecto: Proyecto) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(proyecto.fecha_inicio) if proyecto.fecha_inicio else None
        try:
            cursor.execute(
                f"INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES ({p}, {p}, {p})",
                (proyecto.nombre, proyecto.descripcion, fecha_str),
            )
            conexion.commit()
            proyecto.id_proyecto = cursor.lastrowid
            return proyecto.id_proyecto
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar proyecto '{proyecto.nombre}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_proyecto: int) -> Optional[Proyecto]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto WHERE id_proyecto={p}",
                (id_proyecto,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            proy = Proyecto(fila[0], fila[1], fila[2], convertir_fecha(fila[3]))
            proy.empleados_asignados = self.listar_empleados_proyecto(id_proyecto)
            return proy
        except Exception as err:
            raise DAOError(f"Error al buscar proyecto ID {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar(self) -> List[Proyecto]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto ORDER BY id_proyecto"
            )
            proyectos = [
                Proyecto(fila[0], fila[1], fila[2], convertir_fecha(fila[3]))
                for fila in cursor.fetchall()
            ]
            for p_item in proyectos:
                p_item.empleados_asignados = self.listar_empleados_proyecto(p_item.id_proyecto)
            return proyectos
        except Exception as err:
            raise DAOError(f"Error al listar proyectos: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, proyecto: Proyecto) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(proyecto.fecha_inicio) if proyecto.fecha_inicio else None
        try:
            cursor.execute(
                f"UPDATE proyecto SET nombre={p}, descripcion={p}, fecha_inicio={p} WHERE id_proyecto={p}",
                (proyecto.nombre, proyecto.descripcion, fecha_str, proyecto.id_proyecto),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al actualizar proyecto ID {proyecto.id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_proyecto: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM proyecto WHERE id_proyecto = {p}", (id_proyecto,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar proyecto ID {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def asignar_empleado(self, id_proyecto: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"INSERT INTO proyecto_empleado (id_proyecto, id_empleado) VALUES ({p}, {p})",
                (id_proyecto, id_empleado),
            )
            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            return False
        finally:
            cursor.close()
            conexion.close()

    def desasignar_empleado(self, id_proyecto: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"DELETE FROM proyecto_empleado WHERE id_proyecto={p} AND id_empleado={p}",
                (id_proyecto, id_empleado),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al desasignar empleado {id_empleado} de proyecto {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_empleados_proyecto(self, id_proyecto: int) -> List[Empleado]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT e.id_empleado, e.nombre, e.cargo, e.salario, e.direccion, e.telefono, e.correo, e.fecha_inicio_contrato "
                f"FROM empleado e INNER JOIN proyecto_empleado pe ON e.id_empleado = pe.id_empleado "
                f"WHERE pe.id_proyecto = {p} ORDER BY e.nombre",
                (id_proyecto,),
            )
            return [
                Empleado(
                    id_empleado=f[0],
                    nombre=f[1],
                    cargo=f[2],
                    salario=float(f[3]),
                    direccion=f[4] or "",
                    telefono=f[5] or "",
                    correo=f[6] or "",
                    fecha_inicio_contrato=convertir_fecha(f[7]),
                )
                for f in cursor.fetchall()
            ]
        except Exception:
            return []
        finally:
            cursor.close()
            conexion.close()