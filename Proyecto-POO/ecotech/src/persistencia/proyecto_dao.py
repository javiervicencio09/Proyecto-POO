from src.dominio.proyecto import Proyecto
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import convertir_fecha, marcador


class ProyectoDAO:
    def guardar(self, proyecto: Proyecto) -> int:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES ({p}, {p}, {p})",
                        (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio))
            conexion.commit()
            proyecto.id_proyecto = cursor.lastrowid
            return proyecto.id_proyecto
        finally:
            conexion.close()

    def buscar_por_id(self, id_proyecto: int) -> Proyecto | None:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto WHERE id_proyecto={marcador()}",
                        (id_proyecto,))
            fila = cursor.fetchone()
            return Proyecto(fila[0], fila[1], fila[2], convertir_fecha(fila[3])) if fila else None
        finally:
            conexion.close()

    def listar(self) -> list[Proyecto]:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto ORDER BY id_proyecto")
            return [Proyecto(fila[0], fila[1], fila[2], convertir_fecha(fila[3])) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, proyecto: Proyecto) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"UPDATE proyecto SET nombre={p}, descripcion={p}, fecha_inicio={p} WHERE id_proyecto={p}",
                        (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio, proyecto.id_proyecto))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def eliminar(self, id_proyecto: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"DELETE FROM proyecto WHERE id_proyecto={marcador()}", (id_proyecto,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def asignar_empleado(self, id_proyecto: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"INSERT INTO proyecto_empleado (id_proyecto, id_empleado) VALUES ({p}, {p})",
                        (id_proyecto, id_empleado))
            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            return False
        finally:
            conexion.close()

    def desasignar_empleado(self, id_proyecto: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"DELETE FROM proyecto_empleado WHERE id_proyecto={p} AND id_empleado={p}",
                        (id_proyecto, id_empleado))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()