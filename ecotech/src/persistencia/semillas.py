"""
Módulo de Datos Semilla (Seeders) para EcoTech Solutions.
Permite poblar automáticamente todas las tablas del modelo de datos
tanto en MySQL (WampServer) como en SQLite (contingencia local),
asegurando consistencia referencial, credenciales seguras y datos
realistas para la evaluación (Unidad 3).
"""

import logging
from typing import Any, Dict, Optional
import sqlite3

from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import marcador
from src.seguridad.validador import hashear_contrasena

logger = logging.getLogger("ecotech.semillas")

# Credenciales de prueba estándar para el sistema:
# admin@ecotech.cl        -> AdminPassword123!
# gerencia@ecotech.cl     -> Gerente2026*
# ana.perez@ecotech.cl    -> AnaPerez2026*
# carlos.ruiz@ecotech.cl  -> CarlosRuiz2026*
# luis.gomez@ecotech.cl   -> LuisGomez2026*
# sofia.castro@ecotech.cl -> SofiaCastro2026*

USUARIOS_SEMILLA = [
    (
        "Administrador General",
        "admin@ecotech.cl",
        hashear_contrasena("AdminPassword123!"),
        "ADMIN",
        "SUPERADMIN",
    ),
    (
        "Gerencia de Operaciones",
        "gerencia@ecotech.cl",
        hashear_contrasena("Gerente2026*"),
        "ADMIN",
        "SENIOR",
    ),
    (
        "Ana Pérez",
        "ana.perez@ecotech.cl",
        hashear_contrasena("AnaPerez2026*"),
        "USUARIO",
        None,
    ),
    (
        "Carlos Ruiz",
        "carlos.ruiz@ecotech.cl",
        hashear_contrasena("CarlosRuiz2026*"),
        "USUARIO",
        None,
    ),
    (
        "Luis Gómez",
        "luis.gomez@ecotech.cl",
        hashear_contrasena("LuisGomez2026*"),
        "USUARIO",
        None,
    ),
    (
        "Sofía Castro",
        "sofia.castro@ecotech.cl",
        hashear_contrasena("SofiaCastro2026*"),
        "USUARIO",
        None,
    ),
]

EMPLEADOS_SEMILLA = [
    {
        "nombre": "Carlos Ruiz",
        "cargo": "Gerente de Operaciones en Terreno",
        "salario": 2800000.0,
        "direccion": "Av. Los Conquistadores 1920, Providencia, Santiago",
        "telefono": "+56 9 7123 4567",
        "correo": "carlos.ruiz@ecotech.cl",
        "fecha_inicio_contrato": "2024-03-01",
        "correo_usuario": "carlos.ruiz@ecotech.cl",
    },
    {
        "nombre": "Ana Pérez",
        "cargo": "Ingeniera Ambiental Senior",
        "salario": 1950000.0,
        "direccion": "Calle Las Araucarias 450, Concepción",
        "telefono": "+56 9 8234 5678",
        "correo": "ana.perez@ecotech.cl",
        "fecha_inicio_contrato": "2024-05-15",
        "correo_usuario": "ana.perez@ecotech.cl",
    },
    {
        "nombre": "Luis Gómez",
        "cargo": "Analista de Datos y Huella de Carbono",
        "salario": 1450000.0,
        "direccion": "Pasaje El Roble 812, Santiago Centro",
        "telefono": "+56 9 9345 6789",
        "correo": "luis.gomez@ecotech.cl",
        "fecha_inicio_contrato": "2024-08-01",
        "correo_usuario": "luis.gomez@ecotech.cl",
    },
    {
        "nombre": "Sofía Castro",
        "cargo": "Especialista en Energías Renovables",
        "salario": 1750000.0,
        "direccion": "Av. Del Mar 2200, La Serena",
        "telefono": "+56 9 6456 7890",
        "correo": "sofia.castro@ecotech.cl",
        "fecha_inicio_contrato": "2024-09-10",
        "correo_usuario": "sofia.castro@ecotech.cl",
    },
    {
        "nombre": "Matías Valenzuela",
        "cargo": "Técnico de Monitoreo Fotovoltaico",
        "salario": 980000.0,
        "direccion": "Calle Prat 340, Antofagasta",
        "telefono": "+56 9 5567 8901",
        "correo": "matias.valenzuela@ecotech.cl",
        "fecha_inicio_contrato": "2025-01-15",
        "correo_usuario": None,
    },
]

DEPARTAMENTOS_SEMILLA = [
    {
        "nombre": "Ingeniería y Sostenibilidad",
        "gerente": "Ana Pérez",
        "correo_gerente": "ana.perez@ecotech.cl",
        "empleados": ["ana.perez@ecotech.cl", "luis.gomez@ecotech.cl"],
    },
    {
        "nombre": "Operaciones en Terreno",
        "gerente": "Carlos Ruiz",
        "correo_gerente": "carlos.ruiz@ecotech.cl",
        "empleados": ["carlos.ruiz@ecotech.cl", "matias.valenzuela@ecotech.cl"],
    },
    {
        "nombre": "Tecnología e Innovación",
        "gerente": "Sofía Castro",
        "correo_gerente": "sofia.castro@ecotech.cl",
        "empleados": ["sofia.castro@ecotech.cl"],
    },
]

PROYECTOS_SEMILLA = [
    {
        "nombre": "Parque Solar Atacama Fase II",
        "descripcion": "Despliegue y monitoreo de módulos fotovoltaicos de alta radiación en San Pedro de Atacama.",
        "fecha_inicio": "2025-02-01",
        "empleados": ["carlos.ruiz@ecotech.cl", "matias.valenzuela@ecotech.cl"],
    },
    {
        "nombre": "Monitoreo Huella Hídrica Biobío",
        "descripcion": "Sensorización continua y trazabilidad de calidad de agua en la cuenca del Río Biobío.",
        "fecha_inicio": "2025-04-10",
        "empleados": ["ana.perez@ecotech.cl", "luis.gomez@ecotech.cl"],
    },
    {
        "nombre": "Auditoría Eficiencia Gran Santiago",
        "descripcion": "Optimización de consumo energético y climatización pasiva para edificaciones sostenibles.",
        "fecha_inicio": "2025-06-01",
        "empleados": ["luis.gomez@ecotech.cl", "sofia.castro@ecotech.cl"],
    },
    {
        "nombre": "Planta Eólica Canela Renovables",
        "descripcion": "Mantenimiento predictivo y análisis de generación en parque eólico costero Coquimbo.",
        "fecha_inicio": "2025-08-15",
        "empleados": ["carlos.ruiz@ecotech.cl", "sofia.castro@ecotech.cl"],
    },
]

REGISTROS_TIEMPO_SEMILLA = [
    {
        "correo_empleado": "carlos.ruiz@ecotech.cl",
        "nombre_proyecto": "Parque Solar Atacama Fase II",
        "fecha": "2026-02-10",
        "horas": 8.0,
        "descripcion": "Supervisión de montaje y puesta en marcha de inversores solares.",
    },
    {
        "correo_empleado": "matias.valenzuela@ecotech.cl",
        "nombre_proyecto": "Parque Solar Atacama Fase II",
        "fecha": "2026-02-10",
        "horas": 7.5,
        "descripcion": "Inspección termográfica de celdas fotovoltaicas y cableado de potencia.",
    },
    {
        "correo_empleado": "ana.perez@ecotech.cl",
        "nombre_proyecto": "Monitoreo Huella Hídrica Biobío",
        "fecha": "2026-02-12",
        "horas": 6.0,
        "descripcion": "Recolección de muestras de caudal y calibración de sondas multiparamétricas.",
    },
    {
        "correo_empleado": "luis.gomez@ecotech.cl",
        "nombre_proyecto": "Monitoreo Huella Hídrica Biobío",
        "fecha": "2026-02-12",
        "horas": 5.5,
        "descripcion": "Modelamiento estadístico de demanda hídrica y consolidación de métricas.",
    },
    {
        "correo_empleado": "sofia.castro@ecotech.cl",
        "nombre_proyecto": "Auditoría Eficiencia Gran Santiago",
        "fecha": "2026-02-15",
        "horas": 7.0,
        "descripcion": "Levantamiento de cargas en subestaciones y diagnóstico lumínico LED.",
    },
    {
        "correo_empleado": "sofia.castro@ecotech.cl",
        "nombre_proyecto": "Planta Eólica Canela Renovables",
        "fecha": "2026-02-18",
        "horas": 8.0,
        "descripcion": "Análisis de telemetría de turbinas y curvas de generación eólica.",
    },
]

INFORMES_SEMILLA = [
    {
        "tipo": "Resumen Operativo Trimestral",
        "fecha_generacion": "2026-02-20",
        "contenido": "Informe consolidado de gestión: 4 proyectos activos en terreno, 42.0 horas registradas, 100% cumplimiento normativo ambiental.",
        "correo_creador": "admin@ecotech.cl",
    },
    {
        "tipo": "Auditoría de Impacto y Sostenibilidad",
        "fecha_generacion": "2026-02-25",
        "contenido": "Evaluación técnica de viabilidad climática en zona norte y centro sur. Recomendación de continuidad operacional con alta eficiencia.",
        "correo_creador": "gerencia@ecotech.cl",
    },
]

CLIMA_SEMILLA = [
    {
        "nombre_proyecto": "Parque Solar Atacama Fase II",
        "ciudad": "Antofagasta, Chile",
        "temperatura": 21.5,
        "humedad": 62.0,
        "estado_clima": "Despejado / Soleado",
        "recomendacion": "Condición óptima para trabajo en terreno y generación solar.",
        "fecha_consulta": "2026-02-10 09:30:00",
    },
    {
        "nombre_proyecto": "Monitoreo Huella Hídrica Biobío",
        "ciudad": "Concepción, Chile",
        "temperatura": 18.2,
        "humedad": 74.0,
        "estado_clima": "Nubosidad Parcial",
        "recomendacion": "Condición meteorológica favorable para toma de muestras en terreno.",
        "fecha_consulta": "2026-02-12 11:15:00",
    },
    {
        "nombre_proyecto": "Auditoría Eficiencia Gran Santiago",
        "ciudad": "Santiago, Chile",
        "temperatura": 26.8,
        "humedad": 41.0,
        "estado_clima": "Despejado",
        "recomendacion": "Jornada calurosa: Hidratación continua para cuadrilla de auditores.",
        "fecha_consulta": "2026-02-15 14:00:00",
    },
    {
        "nombre_proyecto": "Planta Eólica Canela Renovables",
        "ciudad": "La Serena, Chile",
        "temperatura": 19.0,
        "humedad": 68.0,
        "estado_clima": "Viento Moderado",
        "recomendacion": "Condición excelente para generación eólica y mantenimiento.",
        "fecha_consulta": "2026-02-18 10:45:00",
    },
]

PAGOS_SEMILLA = [
    {
        "correo_empleado": "carlos.ruiz@ecotech.cl",
        "nombre_proyecto": "Parque Solar Atacama Fase II",
        "monto_origen": 2800000.0,
        "moneda_origen": "CLP",
        "monto_convertido": 2864.40,
        "moneda_destino": "USD",
        "tipo_cambio": 0.001023,
        "fecha_pago": "2026-02-28 17:00:00",
        "detalles": "Liquidación mensual consultor senior - Parque Solar Atacama",
    },
    {
        "correo_empleado": "ana.perez@ecotech.cl",
        "nombre_proyecto": "Monitoreo Huella Hídrica Biobío",
        "monto_origen": 1950000.0,
        "moneda_origen": "CLP",
        "monto_convertido": 1842.75,
        "moneda_destino": "EUR",
        "tipo_cambio": 0.000945,
        "fecha_pago": "2026-02-28 17:05:00",
        "detalles": "Compensación asesoría internacional cuencas hídricas",
    },
    {
        "correo_empleado": "luis.gomez@ecotech.cl",
        "nombre_proyecto": "Auditoría Eficiencia Gran Santiago",
        "monto_origen": 1450000.0,
        "moneda_origen": "CLP",
        "monto_convertido": 1483.35,
        "moneda_destino": "USD",
        "tipo_cambio": 0.001023,
        "fecha_pago": "2026-02-28 17:10:00",
        "detalles": "Honorarios análisis huella de carbono reporte corporativo",
    },
    {
        "correo_empleado": "sofia.castro@ecotech.cl",
        "nombre_proyecto": "Planta Eólica Canela Renovables",
        "monto_origen": 1750000.0,
        "moneda_origen": "CLP",
        "monto_convertido": 1653.75,
        "moneda_destino": "EUR",
        "tipo_cambio": 0.000945,
        "fecha_pago": "2026-02-28 17:15:00",
        "detalles": "Liquidación técnica parque eólico Canela",
    },
]


def poblar_semillas(conexion: Optional[Any] = None, forzar: bool = False) -> Dict[str, Any]:
    """
    Inserta el conjunto de datos semilla completo en la base de datos configurada.
    Es compatible con MySQL y SQLite, respetando integridad referencial y claves foráneas.
    Si forzar=False y ya existen usuarios, no duplica registros existentes.
    """
    cerrar_al_terminar = False
    if conexion is None:
        conexion = abrir_conexion()
        cerrar_al_terminar = True

    cursor = conexion.cursor()
    p = marcador(conexion)
    conteo = {
        "usuarios": 0,
        "empleados": 0,
        "departamentos": 0,
        "proyectos": 0,
        "registros_tiempo": 0,
        "informes": 0,
        "clima": 0,
        "pagos": 0,
    }

    try:
        # Verificar si la base de datos ya contiene datos
        cursor.execute("SELECT count(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]

        if total_usuarios > 0 and not forzar:
            logger.info("La base de datos ya contiene información (%d usuarios). Omitiendo semillas automáticas.", total_usuarios)
            return {"estado": "omitido", "mensaje": "Base de datos con registros existentes.", "conteo": conteo}

        # 1. Poblar Usuarios y Administradores
        mapa_usuarios = {}  # correo -> id_usuario
        for nombre, correo, clave_hash, tipo, nivel_admin in USUARIOS_SEMILLA:
            cursor.execute(f"SELECT id_usuario FROM usuario WHERE correo = {p}", (correo,))
            row = cursor.fetchone()
            if row:
                u_id = row[0]
            else:
                cursor.execute(
                    f"INSERT INTO usuario (nombre, correo, contrasena_hash, tipo_usuario) VALUES ({p}, {p}, {p}, {p})",
                    (nombre, correo, clave_hash, tipo),
                )
                u_id = cursor.lastrowid
                conteo["usuarios"] += 1

            mapa_usuarios[correo] = u_id

            if nivel_admin:
                cursor.execute(f"SELECT id_usuario FROM administrador WHERE id_usuario = {p}", (u_id,))
                if not cursor.fetchone():
                    cursor.execute(
                        f"INSERT INTO administrador (id_usuario, nivel_acceso) VALUES ({p}, {p})",
                        (u_id, nivel_admin),
                    )

        # 2. Poblar Empleados
        mapa_empleados = {}  # correo -> id_empleado
        for emp in EMPLEADOS_SEMILLA:
            cursor.execute(f"SELECT id_empleado FROM empleado WHERE correo = {p}", (emp["correo"],))
            row = cursor.fetchone()
            if row:
                emp_id = row[0]
            else:
                id_u = mapa_usuarios.get(emp["correo_usuario"])
                cursor.execute(
                    f"INSERT INTO empleado (nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato, id_usuario) "
                    f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                    (
                        emp["nombre"],
                        emp["cargo"],
                        emp["salario"],
                        emp["direccion"],
                        emp["telefono"],
                        emp["correo"],
                        emp["fecha_inicio_contrato"],
                        id_u,
                    ),
                )
                emp_id = cursor.lastrowid
                conteo["empleados"] += 1

            mapa_empleados[emp["correo"]] = emp_id

        # 3. Poblar Departamentos y asignaciones
        mapa_deptos = {}  # nombre -> id_departamento
        for dep in DEPARTAMENTOS_SEMILLA:
            cursor.execute(f"SELECT id_departamento FROM departamento WHERE nombre = {p}", (dep["nombre"],))
            row = cursor.fetchone()
            if row:
                dep_id = row[0]
            else:
                id_gerente = mapa_empleados.get(dep["correo_gerente"])
                cursor.execute(
                    f"INSERT INTO departamento (nombre, gerente, id_gerente) VALUES ({p}, {p}, {p})",
                    (dep["nombre"], dep["gerente"], id_gerente),
                )
                dep_id = cursor.lastrowid
                conteo["departamentos"] += 1

            mapa_deptos[dep["nombre"]] = dep_id

            # Asignar empleados al departamento
            for emp_correo in dep["empleados"]:
                emp_id = mapa_empleados.get(emp_correo)
                if emp_id:
                    cursor.execute(
                        f"SELECT count(*) FROM departamento_empleado WHERE id_departamento = {p} AND id_empleado = {p}",
                        (dep_id, emp_id),
                    )
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            f"INSERT INTO departamento_empleado (id_departamento, id_empleado) VALUES ({p}, {p})",
                            (dep_id, emp_id),
                        )

        # 4. Poblar Proyectos y asignaciones
        mapa_proyectos = {}  # nombre -> id_proyecto
        for proy in PROYECTOS_SEMILLA:
            cursor.execute(f"SELECT id_proyecto FROM proyecto WHERE nombre = {p}", (proy["nombre"],))
            row = cursor.fetchone()
            if row:
                proy_id = row[0]
            else:
                cursor.execute(
                    f"INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES ({p}, {p}, {p})",
                    (proy["nombre"], proy["descripcion"], proy["fecha_inicio"]),
                )
                proy_id = cursor.lastrowid
                conteo["proyectos"] += 1

            mapa_proyectos[proy["nombre"]] = proy_id

            # Asignar empleados al proyecto
            for emp_correo in proy["empleados"]:
                emp_id = mapa_empleados.get(emp_correo)
                if emp_id:
                    cursor.execute(
                        f"SELECT count(*) FROM proyecto_empleado WHERE id_proyecto = {p} AND id_empleado = {p}",
                        (proy_id, emp_id),
                    )
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            f"INSERT INTO proyecto_empleado (id_proyecto, id_empleado) VALUES ({p}, {p})",
                            (proy_id, emp_id),
                        )

        # 5. Poblar Registro de Tiempos
        for reg in REGISTROS_TIEMPO_SEMILLA:
            emp_id = mapa_empleados.get(reg["correo_empleado"])
            proy_id = mapa_proyectos.get(reg["nombre_proyecto"])
            if emp_id and proy_id:
                cursor.execute(
                    f"SELECT count(*) FROM registro_tiempo WHERE id_empleado = {p} AND id_proyecto = {p} AND fecha = {p}",
                    (emp_id, proy_id, reg["fecha"]),
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        f"INSERT INTO registro_tiempo (id_empleado, id_proyecto, fecha, horas, descripcion_tareas) "
                        f"VALUES ({p}, {p}, {p}, {p}, {p})",
                        (emp_id, proy_id, reg["fecha"], reg["horas"], reg["descripcion"]),
                    )
                    conteo["registros_tiempo"] += 1

        # 6. Poblar Informes
        for inf in INFORMES_SEMILLA:
            u_id = mapa_usuarios.get(inf["correo_creador"])
            cursor.execute(f"SELECT count(*) FROM informe WHERE tipo = {p} AND fecha_generacion = {p}", (inf["tipo"], inf["fecha_generacion"]))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    f"INSERT INTO informe (tipo, fecha_generacion, contenido, creado_por) VALUES ({p}, {p}, {p}, {p})",
                    (inf["tipo"], inf["fecha_generacion"], inf["contenido"], u_id),
                )
                conteo["informes"] += 1

        # 7. Poblar Mediciones de Clima
        for clim in CLIMA_SEMILLA:
            proy_id = mapa_proyectos.get(clim["nombre_proyecto"])
            cursor.execute(
                f"SELECT count(*) FROM registro_clima_proyecto WHERE ciudad = {p} AND fecha_consulta = {p}",
                (clim["ciudad"], clim["fecha_consulta"]),
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    f"INSERT INTO registro_clima_proyecto (id_proyecto, ciudad, temperatura, humedad, estado_clima, recomendacion, fecha_consulta) "
                    f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})",
                    (
                        proy_id,
                        clim["ciudad"],
                        clim["temperatura"],
                        clim["humedad"],
                        clim["estado_clima"],
                        clim["recomendacion"],
                        clim["fecha_consulta"],
                    ),
                )
                conteo["clima"] += 1

        # 8. Poblar Pagos Internacionales
        for pago in PAGOS_SEMILLA:
            emp_id = mapa_empleados.get(pago["correo_empleado"])
            proy_id = mapa_proyectos.get(pago["nombre_proyecto"])
            if emp_id:
                cursor.execute(
                    f"SELECT count(*) FROM pago_internacional WHERE id_empleado = {p} AND fecha_pago = {p}",
                    (emp_id, pago["fecha_pago"]),
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        f"INSERT INTO pago_internacional (id_empleado, id_proyecto, monto_origen, moneda_origen, monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles) "
                        f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                        (
                            emp_id,
                            proy_id,
                            pago["monto_origen"],
                            pago["moneda_origen"],
                            pago["monto_convertido"],
                            pago["moneda_destino"],
                            pago["tipo_cambio"],
                            pago["fecha_pago"],
                            pago["detalles"],
                        ),
                    )
                    conteo["pagos"] += 1

        conexion.commit()
        logger.info("Datos semilla insertados correctamente: %s", conteo)
        return {"estado": "exito", "mensaje": "Datos semilla insertados satisfactoriamente.", "conteo": conteo}

    except Exception as err:
        conexion.rollback()
        logger.error("Error al poblar datos semilla: %s", err)
        raise RuntimeError(f"Falla al insertar semillas: {err}") from err
    finally:
        cursor.close()
        if cerrar_al_terminar:
            conexion.close()


def insertar_semillas_si_vacia(conexion: Optional[Any] = None) -> bool:
    """Función de conveniencia para auto-insertar semillas al inicializar tablas si no hay datos."""
    resultado = poblar_semillas(conexion=conexion, forzar=False)
    return resultado.get("estado") == "exito"


if __name__ == "__main__":
    import sys
    forzar = "--forzar" in sys.argv or "-f" in sys.argv
    conn = abrir_conexion()
    motor = "SQLite" if isinstance(conn, sqlite3.Connection) else "MySQL (WampServer)"
    print(f"\n============================================================")
    print(f"     POBLADOR DE DATOS SEMILLA - ECOTECH SOLUTIONS")
    print(f"     Motor de Base de Datos: {motor}")
    print(f"============================================================")
    res = poblar_semillas(conexion=conn, forzar=forzar)
    conn.close()

    if res["estado"] == "exito":
        print("\n[OK] Datos semilla insertados exitosamente:")
        c = res["conteo"]
        print(f" - Usuarios:           {c['usuarios']}")
        print(f" - Empleados:          {c['empleados']}")
        print(f" - Departamentos:      {c['departamentos']}")
        print(f" - Proyectos:          {c['proyectos']}")
        print(f" - Registros de tiempo:{c['registros_tiempo']}")
        print(f" - Informes:           {c['informes']}")
        print(f" - Mediciones clima:   {c['clima']}")
        print(f" - Pagos en divisas:   {c['pagos']}")
    else:
        print(f"\n[INFO] {res['mensaje']}")
        print("Para forzar la re-inserción de registros, use: python -m src.persistencia.semillas --forzar")
