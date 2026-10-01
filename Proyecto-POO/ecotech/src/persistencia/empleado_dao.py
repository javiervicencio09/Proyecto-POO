from src.dominio.empleado import Empleado
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import convertir_fecha, marcador


class EmpleadoDAO:
    def guardar(self, empleado: Empleado) -> int:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            parametro = marcador()
            cursor.execute(
                "INSERT INTO empleado (nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato) "
                f"VALUES ({parametro}, {parametro}, {parametro}, {parametro}, {parametro}, {parametro}, {parametro})",
                (empleado.nombre, empleado.cargo, empleado.salario, empleado.direccion,
                empleado.telefono, empleado.correo, empleado.fecha_inicio_contrato),
            )
            conexion.commit()
            empleado.id_empleado = cursor.lastrowid
            return empleado.id_empleado
        finally:
            conexion.close()

    def buscar_por_id(self, id_empleado: int) -> Empleado | None:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT * FROM empleado WHERE id_empleado = {marcador()}", (id_empleado,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            fila = (*fila[:7], convertir_fecha(fila[7]))
            return Empleado(*fila)
        finally:
            conexion.close()

    def listar(self) -> list[Empleado]:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM empleado ORDER BY id_empleado")
            return [Empleado(*fila[:7], convertir_fecha(fila[7])) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, empleado: Empleado) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            parametro = marcador()
            cursor.execute(
                f"UPDATE empleado SET nombre={parametro}, cargo={parametro}, salario={parametro}, "
                f"direccion={parametro}, telefono={parametro}, correo={parametro}, fecha_inicio_contrato={parametro} "
                f"WHERE id_empleado={parametro}",
                (empleado.nombre, empleado.cargo, empleado.salario, empleado.direccion,
                empleado.telefono, empleado.correo, empleado.fecha_inicio_contrato, empleado.id_empleado),
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def eliminar(self, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"DELETE FROM empleado WHERE id_empleado = {marcador()}", (id_empleado,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()