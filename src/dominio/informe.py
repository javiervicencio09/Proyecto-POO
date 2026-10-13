from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from .validaciones import validar_fecha, validar_texto


class Informe:
    """Informe generado por un Administrador (relación "genera"); creado_por es el id de ese administrador."""

    def __init__(
        self,
        id_informe: Optional[int],
        tipo: str,
        fecha_generacion: Optional[date] = None,
        contenido: str = "",
        creado_por: Optional[int] = None,
    ) -> None:
        self.id_informe = id_informe
        self.tipo = tipo
        self.fecha_generacion = validar_fecha(fecha_generacion, "La fecha del informe", opcional=True) or date.today()
        self.contenido = contenido
        self.creado_por = creado_por

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        self._tipo = validar_texto(valor, "El tipo de informe", 100)

    @property
    def creado_por(self) -> Optional[int]:
        return self._creado_por

    @creado_por.setter
    def creado_por(self, valor: Optional[int]) -> None:
        if valor is not None and (isinstance(valor, bool) or not isinstance(valor, int)):
            raise ValueError("creado_por debe ser el id numérico de un administrador.")
        self._creado_por = valor

    def generar(self, datos: Dict[str, Any]) -> None:
        """UML: generar(datos: dict) void. Deja el texto del informe en self.contenido."""
        encabezado = (
            "========================================\n"
            f"       INFORME: {self.tipo.upper()}\n"
            f"       Fecha: {self.fecha_generacion}\n"
            "========================================\n"
        )
        cuerpo = "\n".join(f"- {clave}: {valor}" for clave, valor in datos.items())
        self.contenido = f"{encabezado}\n{cuerpo}\n"

    def exportar(self, ruta: str) -> None:
        """UML: exportar(ruta: string) void. Escribe el contenido en un archivo de texto."""
        if not self.contenido:
            raise ValueError("El informe no tiene contenido generado para exportar.")
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as archivo:
            archivo.write(self.contenido)

    def __str__(self) -> str:
        return f"Informe(id={self.id_informe}, tipo='{self.tipo}', fecha={self.fecha_generacion}, creado_por={self.creado_por})"
