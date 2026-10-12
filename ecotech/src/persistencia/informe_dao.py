from typing import List, Optional

from src.dominio.informe import Informe
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, convertir_fecha, marcador


class InformeDAO:
    """
    Data Access Object para la persistencia de Informes generados en el sistema.
    """

    def guardar(self, informe: Informe) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        fecha_str = str(informe.fecha_generacion) if informe.fecha_generacion else None
        try:
            cursor.execute(
                f"INSERT INTO informe (tipo, fecha_generacion, contenido, creado_por) "
                f"VALUES ({p}, {p}, {p}, {p})",
                (informe.tipo, fecha_str, informe.contenido, informe.creado_por),
            )
            conexion.commit()
            informe.id_informe = cursor.lastrowid
            return informe.id_informe
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar informe '{informe.tipo}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_informe: int) -> Optional[Informe]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT id_informe, tipo, fecha_generacion, contenido, creado_por "
                f"FROM informe WHERE id_informe = {p}",
                (id_informe,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            id_inf, tipo, fecha, contenido, creador = fila
            return Informe(id_inf, tipo, convertir_fecha(fecha), contenido, creador)
        except Exception as err:
            raise DAOError(f"Error al buscar informe ID {id_informe}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar(self) -> List[Informe]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_informe, tipo, fecha_generacion, contenido, creado_por "
                "FROM informe ORDER BY id_informe DESC"
            )
            return [
                Informe(
                    f[0],
                    f[1],
                    convertir_fecha(f[2]),
                    f[3],
                    f[4],
                )
                for f in cursor.fetchall()
            ]
        except Exception as err:
            raise DAOError(f"Error al listar informes: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_informe: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM informe WHERE id_informe = {p}", (id_informe,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar informe ID {id_informe}: {err}") from err
        finally:
            cursor.close()
            conexion.close()
