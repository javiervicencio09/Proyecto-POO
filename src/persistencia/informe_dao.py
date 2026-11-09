from typing import List, Optional

from src.dominio.informe import Informe
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import (
    convertir_fecha,
    exigir_guardado,
    exigir_nuevo,
    fecha_a_texto,
    sesion_bd,
)

_SELECT = "SELECT id_informe, tipo, fecha_generacion, contenido, creado_por FROM informe"


class InformeDAO:
    """Persistencia de Informe. creado_por es el id del Administrador que lo generó (relación 'genera')."""

    @staticmethod
    def _fila_a_informe(fila) -> Informe:
        return Informe(fila[0], fila[1], convertir_fecha(fila[2]), fila[3] or "", fila[4])

    @staticmethod
    def insertar(informe: Informe) -> Informe:
        exigir_nuevo(informe.id_informe, "El informe")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO informe (tipo, fecha_generacion, contenido, creado_por) VALUES ({p}, {p}, {p}, {p})",
                (informe.tipo, fecha_a_texto(informe.fecha_generacion), informe.contenido, informe.creado_por),
            )
            nuevo_id = cursor.lastrowid
        informe.id_informe = nuevo_id
        return informe

    @staticmethod
    def buscar_por_id(id_informe: int) -> Optional[Informe]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE id_informe = {p}", (id_informe,))
            fila = cursor.fetchone()
        return InformeDAO._fila_a_informe(fila) if fila else None

    @staticmethod
    def listar() -> List[Informe]:
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY id_informe DESC")
            filas = cursor.fetchall()
        return [InformeDAO._fila_a_informe(fila) for fila in filas]

    @staticmethod
    def actualizar(informe: Informe) -> bool:
        exigir_guardado(informe.id_informe, "El informe")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE informe SET tipo = {p}, fecha_generacion = {p}, contenido = {p} WHERE id_informe = {p}",
                (informe.tipo, fecha_a_texto(informe.fecha_generacion), informe.contenido, informe.id_informe),
            )
            return cursor.rowcount > 0

    @staticmethod
    def eliminar(id_informe: int) -> bool:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"DELETE FROM informe WHERE id_informe = {p}", (id_informe,))
            return cursor.rowcount > 0
