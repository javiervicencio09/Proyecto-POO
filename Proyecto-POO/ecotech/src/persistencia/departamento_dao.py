from src.dominio.departamento import Departamento
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import marcador


class DepartamentoDAO:
    def guardar(self, departamento: Departamento) -> int:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"INSERT INTO departamento (nombre, gerente) VALUES ({p}, {p})",
                        (departamento.nombre, departamento.gerente))
            conexion.commit()
            departamento.id_departamento = cursor.lastrowid
            return departamento.id_departamento
        finally:
            conexion.close()

    def buscar_por_id(self, id_departamento: int) -> Departamento | None:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT id_departamento, nombre, gerente FROM departamento WHERE id_departamento={marcador()}",
                        (id_departamento,))
            fila = cursor.fetchone()
            return Departamento(*fila) if fila else None
        finally:
            conexion.close()

    def listar(self) -> list[Departamento]:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_departamento, nombre, gerente FROM departamento ORDER BY id_departamento")
            return [Departamento(*fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, departamento: Departamento) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"UPDATE departamento SET nombre={p}, gerente={p} WHERE id_departamento={p}",
                        (departamento.nombre, departamento.gerente, departamento.id_departamento))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def eliminar(self, id_departamento: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"DELETE FROM departamento WHERE id_departamento={marcador()}", (id_departamento,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def agregar_empleado(self, id_departamento: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"INSERT INTO departamento_empleado (id_departamento, id_empleado) VALUES ({p}, {p})",
                        (id_departamento, id_empleado))
            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            return False
        finally:
            conexion.close()

    def eliminar_empleado(self, id_departamento: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            p = marcador()
            cursor.execute(f"DELETE FROM departamento_empleado WHERE id_departamento={p} AND id_empleado={p}",
                        (id_departamento, id_empleado))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()