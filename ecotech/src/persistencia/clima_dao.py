import logging
from typing import List, Optional

from src.dominio.registro_clima import RegistroClima
from src.excepciones import DAOError
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import marcador

logger = logging.getLogger("ecotech.persistencia.clima")


class ClimaDAO:
    """
    Data Access Object para la persistencia local de consultas meteorológicas externas (Criterio 3.1.1).
    Permite auditar las decisiones operativas tomadas para cada proyecto y actuar como caché/historial.
    """

    def guardar(self, registro: RegistroClima) -> int:
        """Persiste un registro de clima en la base de datos."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"INSERT INTO registro_clima_proyecto "
                f"(id_proyecto, ciudad, temperatura, humedad, estado_clima, recomendacion, fecha_consulta) "
                f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (
                    registro.id_proyecto,
                    registro.ciudad,
                    registro.temperatura,
                    registro.humedad,
                    registro.estado_clima,
                    registro.recomendacion,
                    registro.fecha_consulta,
                ),
            )
            conexion.commit()
            registro.id_registro_clima = cursor.lastrowid
            return registro.id_registro_clima
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al persistir registro climático para '{registro.ciudad}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_registro_clima: int) -> Optional[RegistroClima]:
        """Obtiene un registro climático por su ID."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_registro_clima, id_proyecto, ciudad, temperatura, humedad, "
                f"estado_clima, recomendacion, fecha_consulta "
                f"FROM registro_clima_proyecto WHERE id_registro_clima = {p}",
                (id_registro_clima,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            return RegistroClima(*fila)
        except Exception as err:
            raise DAOError(f"Error al buscar registro climático ID {id_registro_clima}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_por_proyecto(self, id_proyecto: int) -> List[RegistroClima]:
        """Retorna el historial de mediciones climáticas asociadas a un proyecto."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_registro_clima, id_proyecto, ciudad, temperatura, humedad, "
                f"estado_clima, recomendacion, fecha_consulta "
                f"FROM registro_clima_proyecto WHERE id_proyecto = {p} "
                f"ORDER BY id_registro_clima DESC",
                (id_proyecto,),
            )
            return [RegistroClima(*fila) for fila in cursor.fetchall()]
        except Exception as err:
            raise DAOError(f"Error al listar clima para proyecto ID {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def obtener_ultimo_clima(self, id_proyecto: int) -> Optional[RegistroClima]:
        """Retorna la última medición meteorológica guardada para el proyecto (actúa como caché local)."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_registro_clima, id_proyecto, ciudad, temperatura, humedad, "
                f"estado_clima, recomendacion, fecha_consulta "
                f"FROM registro_clima_proyecto WHERE id_proyecto = {p} "
                f"ORDER BY id_registro_clima DESC LIMIT 1",
                (id_proyecto,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            return RegistroClima(*fila)
        except Exception as err:
            raise DAOError(f"Error al obtener última medición de clima: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_todos(self) -> List[RegistroClima]:
        """Retorna todos los registros meteorológicos almacenados."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "SELECT id_registro_clima, id_proyecto, ciudad, temperatura, humedad, "
                "estado_clima, recomendacion, fecha_consulta "
                "FROM registro_clima_proyecto ORDER BY id_registro_clima DESC"
            )
            return [RegistroClima(*fila) for fila in cursor.fetchall()]
        except Exception as err:
            raise DAOError(f"Error al listar registros climáticos: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_registro_clima: int) -> bool:
        """Elimina un registro meteorológico."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"DELETE FROM registro_clima_proyecto WHERE id_registro_clima = {p}",
                (id_registro_clima,),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar registro climático ID {id_registro_clima}: {err}") from err
        finally:
            cursor.close()
            conexion.close()
