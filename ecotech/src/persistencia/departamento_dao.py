from typing import List, Optional

from src.dominio.departamento import Departamento
from src.dominio.empleado import Empleado
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, convertir_fecha, marcador


class DepartamentoDAO:
    """
    Data Access Object para Departamento con manejo de integridad transaccional.
    """

    def guardar(self, departamento: Departamento) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        id_gerente = (
            departamento.gerente.id_empleado
            if isinstance(departamento.gerente, Empleado)
            else None
        )
        try:
            cursor.execute(
                f"INSERT INTO departamento (nombre, gerente, id_gerente) VALUES ({p}, {p}, {p})",
                (departamento.nombre, departamento.gerente_nombre, id_gerente),
            )
            conexion.commit()
            departamento.id_departamento = cursor.lastrowid
            return departamento.id_departamento
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar departamento '{departamento.nombre}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_departamento: int) -> Optional[Departamento]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_departamento, nombre, gerente FROM departamento WHERE id_departamento={p}",
                (id_departamento,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            depto = Departamento(fila[0], fila[1], fila[2])
            depto.empleados = self.listar_empleados_departamento(id_departamento)
            return depto
        except Exception as err:
            raise DAOError(f"Error al buscar departamento ID {id_departamento}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar(self) -> List[Departamento]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_departamento, nombre, gerente FROM departamento ORDER BY id_departamento")
            deptos = [Departamento(*fila) for fila in cursor.fetchall()]
            for depto in deptos:
                depto.empleados = self.listar_empleados_departamento(depto.id_departamento)
            return deptos
        except Exception as err:
            raise DAOError(f"Error al listar departamentos: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, departamento: Departamento) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        id_gerente = (
            departamento.gerente.id_empleado
            if isinstance(departamento.gerente, Empleado)
            else None
        )
        try:
            cursor.execute(
                f"UPDATE departamento SET nombre={p}, gerente={p}, id_gerente={p} WHERE id_departamento={p}",
                (departamento.nombre, departamento.gerente_nombre, id_gerente, departamento.id_departamento),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al actualizar departamento ID {departamento.id_departamento}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_departamento: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM departamento WHERE id_departamento={p}", (id_departamento,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar departamento ID {id_departamento}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def agregar_empleado(self, id_departamento: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"INSERT INTO departamento_empleado (id_departamento, id_empleado) VALUES ({p}, {p})",
                (id_departamento, id_empleado),
            )
            conexion.commit()
            return True
        except Exception as err:
            conexion.rollback()
            # Si ya está asociado, no es un fallo fatal
            return False
        finally:
            cursor.close()
            conexion.close()

    def eliminar_empleado(self, id_departamento: int, id_empleado: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"DELETE FROM departamento_empleado WHERE id_departamento={p} AND id_empleado={p}",
                (id_departamento, id_empleado),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al desvincular empleado {id_empleado} de departamento {id_departamento}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_empleados_departamento(self, id_departamento: int) -> List[Empleado]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT e.id_empleado, e.nombre, e.cargo, e.salario, e.direccion, e.telefono, e.correo, e.fecha_inicio_contrato "
                f"FROM empleado e INNER JOIN departamento_empleado de ON e.id_empleado = de.id_empleado "
                f"WHERE de.id_departamento = {p} ORDER BY e.nombre",
                (id_departamento,),
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