from datetime import date
from typing import Any, Dict, Optional


class Informe:
    """
    Representa un informe gerencial o técnico generado en el sistema EcoTech Solutions.
    Permite consolidar información de empleados, proyectos y registros de tiempo.
    """

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
        self.fecha_generacion = fecha_generacion or date.today()
        self.contenido = contenido
        self.creado_por = creado_por

    def generar(self, datos: Optional[Dict[str, Any]] = None) -> str:
        """
        Método definido en el UML (+ generar).
        Genera el cuerpo del informe a partir de un conjunto de datos o resumen.
        """
        encabezado = (
            f"========================================\n"
            f"       INFORME: {self.tipo.upper()}\n"
            f"       Fecha: {self.fecha_generacion}\n"
            f"========================================\n"
        )
        if datos:
            cuerpo = "\n".join(f"- {clave}: {valor}" for clave, valor in datos.items())
        else:
            cuerpo = self.contenido or "Sin datos adicionales."

        self.contenido = f"{encabezado}\n{cuerpo}\n"
        return self.contenido

    def exportar(self, ruta_archivo: Optional[str] = None) -> str:
        """
        Método definido en el UML (+ exportar).
        Exporta el informe a un archivo o retorna el texto estructurado para persistir.
        """
        texto_exportable = self.contenido or self.generar()
        if ruta_archivo:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(texto_exportable)
        return texto_exportable

    def __str__(self) -> str:
        return (
            f"Informe(id={self.id_informe}, tipo='{self.tipo}', "
            f"fecha={self.fecha_generacion}, caracteres={len(self.contenido)})"
        )
