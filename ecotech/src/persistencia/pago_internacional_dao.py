import logging
from typing import List, Optional

from src.dominio.pago_internacional import PagoInternacional
from src.excepciones import DAOError
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import marcador

logger = logging.getLogger("ecotech.persistencia.pago_internacional")


class PagoInternacionalDAO:
    """
    Data Access Object para la persistencia local de pagos y liquidaciones
    calculadas con divisas internacionales (Criterio 3.1.1).
    """

    def guardar(self, pago: PagoInternacional) -> int:
        """Persiste una liquidación internacional en la base de datos."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"INSERT INTO pago_internacional "
                f"(id_empleado, id_proyecto, monto_origen, moneda_origen, "
                f"monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles) "
                f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (
                    pago.id_empleado,
                    pago.id_proyecto,
                    pago.monto_origen,
                    pago.moneda_origen,
                    pago.monto_convertido,
                    pago.moneda_destino,
                    pago.tipo_cambio,
                    pago.fecha_pago,
                    pago.detalles,
                ),
            )
            conexion.commit()
            pago.id_pago = cursor.lastrowid
            return pago.id_pago
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar liquidación internacional: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_pago: int) -> Optional[PagoInternacional]:
        """Recupera un pago internacional por su identificador."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_pago, id_empleado, id_proyecto, monto_origen, moneda_origen, "
                f"monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles "
                f"FROM pago_internacional WHERE id_pago = {p}",
                (id_pago,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            return PagoInternacional(*fila)
        except Exception as err:
            raise DAOError(f"Error al buscar pago internacional ID {id_pago}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_por_empleado(self, id_empleado: int) -> List[PagoInternacional]:
        """Obtiene el historial de pagos internacionales de un empleado."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_pago, id_empleado, id_proyecto, monto_origen, moneda_origen, "
                f"monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles "
                f"FROM pago_internacional WHERE id_empleado = {p} ORDER BY id_pago DESC",
                (id_empleado,),
            )
            return [PagoInternacional(*fila) for fila in cursor.fetchall()]
        except Exception as err:
            raise DAOError(f"Error al listar pagos de empleado ID {id_empleado}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_por_proyecto(self, id_proyecto: int) -> List[PagoInternacional]:
        """Obtiene las liquidaciones asociadas a un proyecto internacional específico."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(
                f"SELECT id_pago, id_empleado, id_proyecto, monto_origen, moneda_origen, "
                f"monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles "
                f"FROM pago_internacional WHERE id_proyecto = {p} ORDER BY id_pago DESC",
                (id_proyecto,),
            )
            return [PagoInternacional(*fila) for fila in cursor.fetchall()]
        except Exception as err:
            raise DAOError(f"Error al listar pagos de proyecto ID {id_proyecto}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def listar_todos(self) -> List[PagoInternacional]:
        """Retorna todos los pagos internacionales registrados en el sistema."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "SELECT id_pago, id_empleado, id_proyecto, monto_origen, moneda_origen, "
                "monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles "
                "FROM pago_internacional ORDER BY id_pago DESC"
            )
            return [PagoInternacional(*fila) for fila in cursor.fetchall()]
        except Exception as err:
            raise DAOError(f"Error al listar todos los pagos internacionales: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_pago: int) -> bool:
        """Elimina un pago internacional por su ID."""
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador(conexion)

        try:
            cursor.execute(f"DELETE FROM pago_internacional WHERE id_pago = {p}", (id_pago,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar pago internacional ID {id_pago}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

