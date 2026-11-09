from datetime import datetime
from typing import Optional

from src.seguridad.validador import sanitizar_texto, validar_codigo_moneda, validar_numero


class PagoInternacional:
    """
    Modela la liquidación o pago a trabajadores en monedas internacionales (Criterio 3.1.1).
    Integra indicadores económicos en tiempo real para calcular montos convertidos con exactitud.
    """

    def __init__(
        self,
        id_pago: Optional[int],
        id_empleado: int,
        id_proyecto: Optional[int],
        monto_origen: float,
        moneda_origen: str,
        monto_convertido: float,
        moneda_destino: str,
        tipo_cambio: float,
        fecha_pago: Optional[str] = None,
        detalles: str = "",
    ) -> None:
        self.id_pago = id_pago
        self.id_empleado = int(validar_numero(id_empleado, "El ID del empleado", minimo=1))
        self.id_proyecto = int(id_proyecto) if id_proyecto is not None else None
        self.monto_origen = validar_numero(monto_origen, "El monto de origen", minimo=0.0)
        self.moneda_origen = validar_codigo_moneda(moneda_origen)
        self.monto_convertido = validar_numero(monto_convertido, "El monto convertido", minimo=0.0)
        self.moneda_destino = validar_codigo_moneda(moneda_destino)
        self.tipo_cambio = validar_numero(tipo_cambio, "El tipo de cambio", minimo=0.000001)
        self.fecha_pago = fecha_pago or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.detalles = sanitizar_texto(detalles, max_longitud=300, permitir_vacio=True)

    def resumen_pago(self) -> str:
        """Retorna un comprobante legible para la liquidación del trabajador."""
        return (
            f"Pago ID: {self.id_pago or 'Pendiente'} | Empleado: {self.id_empleado} | "
            f"Origen: ${self.monto_origen:,.2f} {self.moneda_origen} -> "
            f"Destino: ${self.monto_convertido:,.2f} {self.moneda_destino} "
            f"(Tasa: {self.tipo_cambio:.4f}) | Fecha: {self.fecha_pago}"
        )

    def __str__(self) -> str:
        return self.resumen_pago()

