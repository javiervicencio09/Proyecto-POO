"""
Crea las tablas del modelo UML de EcoTech (SQLite o MySQL, según DB_ENGINE).

Cómo se traduce el UML a tablas:
  Usuario <|-- Administrador / Empleado  -> herencia con una tabla hija que comparte la clave
                                            (id_usuario es PK y FK de la hija; por eso id_empleado == id_usuario)
  Departamento 1 ◇── 0..* Empleado       -> empleado.id_departamento (FK en el lado "muchos")
  Departamento 1 ◇── 0..1 Empleado       -> departamento.id_gerente  (FK, puede ser NULL)
  Empleado 0..* ── 0..* Proyecto         -> tabla intermedia proyecto_empleado
  Empleado 1 ── 0..* RegistroDeTiempo    -> registro_tiempo.id_empleado
  Proyecto 1 ── 0..* RegistroDeTiempo    -> registro_tiempo.id_proyecto
  Administrador "genera" Informe         -> informe.creado_por (FK a usuario)

Ejecutar desde la raíz del proyecto:  python -m src.persistencia.crear_bd
"""
from src.persistencia.conexion import obtener_motor
from src.persistencia.dao_util import sesion_bd

TABLAS_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        contrasena_hash TEXT NOT NULL DEFAULT '',
        tipo_usuario TEXT NOT NULL DEFAULT 'USUARIO'
            CHECK (tipo_usuario IN ('USUARIO', 'ADMIN', 'EMPLEADO'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS administrador (
        id_usuario INTEGER PRIMARY KEY,
        nivel_acceso TEXT NOT NULL DEFAULT 'ADMIN',
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS departamento (
        id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        id_gerente INTEGER,
        FOREIGN KEY (id_gerente) REFERENCES empleado(id_usuario) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS empleado (
        id_usuario INTEGER PRIMARY KEY,
        cargo TEXT NOT NULL,
        salario REAL NOT NULL CHECK (salario >= 0),
        direccion TEXT NOT NULL DEFAULT '',
        telefono TEXT NOT NULL DEFAULT '',
        fecha_inicio_contrato TEXT,
        id_departamento INTEGER,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
        FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS proyecto (
        id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        fecha_inicio TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS proyecto_empleado (
        id_proyecto INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        PRIMARY KEY (id_proyecto, id_empleado),
        FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id_usuario) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_tiempo (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_empleado INTEGER NOT NULL,
        id_proyecto INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
        descripcion_tareas TEXT NOT NULL,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id_usuario) ON DELETE CASCADE,
        FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS informe (
        id_informe INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        fecha_generacion TEXT NOT NULL,
        contenido TEXT NOT NULL,
        creado_por INTEGER,
        FOREIGN KEY (creado_por) REFERENCES usuario(id_usuario) ON DELETE SET NULL
    )
    """,
]

TABLAS_MYSQL = [
    """
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INT PRIMARY KEY AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        correo VARCHAR(150) NOT NULL UNIQUE,
        contrasena_hash VARCHAR(255) NOT NULL DEFAULT '',
        tipo_usuario VARCHAR(20) NOT NULL DEFAULT 'USUARIO',
        CHECK (tipo_usuario IN ('USUARIO', 'ADMIN', 'EMPLEADO'))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS administrador (
        id_usuario INT PRIMARY KEY,
        nivel_acceso VARCHAR(50) NOT NULL DEFAULT 'ADMIN',
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS departamento (
        id_departamento INT PRIMARY KEY AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        id_gerente INT NULL,
        FOREIGN KEY (id_gerente) REFERENCES empleado(id_usuario) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS empleado (
        id_usuario INT PRIMARY KEY,
        cargo VARCHAR(100) NOT NULL,
        salario DECIMAL(12, 2) NOT NULL CHECK (salario >= 0),
        direccion VARCHAR(255) NOT NULL DEFAULT '',
        telefono VARCHAR(30) NOT NULL DEFAULT '',
        fecha_inicio_contrato DATE NULL,
        id_departamento INT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
        FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS proyecto (
        id_proyecto INT PRIMARY KEY AUTO_INCREMENT,
        nombre VARCHAR(150) NOT NULL,
        descripcion VARCHAR(500) NOT NULL,
        fecha_inicio DATE NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS proyecto_empleado (
        id_proyecto INT NOT NULL,
        id_empleado INT NOT NULL,
        PRIMARY KEY (id_proyecto, id_empleado),
        FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id_usuario) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_tiempo (
        id_registro INT PRIMARY KEY AUTO_INCREMENT,
        id_empleado INT NOT NULL,
        id_proyecto INT NOT NULL,
        fecha DATE NOT NULL,
        horas DECIMAL(5, 2) NOT NULL CHECK (horas > 0 AND horas <= 24),
        descripcion_tareas VARCHAR(500) NOT NULL,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id_usuario) ON DELETE CASCADE,
        FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS informe (
        id_informe INT PRIMARY KEY AUTO_INCREMENT,
        tipo VARCHAR(100) NOT NULL,
        fecha_generacion DATE NOT NULL,
        contenido TEXT NOT NULL,
        creado_por INT NULL,
        FOREIGN KEY (creado_por) REFERENCES usuario(id_usuario) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]


def crear_tablas() -> None:
    """
    Crea las tablas si no existen (se puede ejecutar varias veces sin riesgo).
    departamento y empleado se referencian entre sí (gerente / pertenece a); en MySQL se desactiva
    un momento la revisión de claves foráneas solo para poder crear ambas tablas.
    """
    es_mysql = obtener_motor() == "mysql"
    with sesion_bd() as cursor:
        if es_mysql:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for sentencia in (TABLAS_MYSQL if es_mysql else TABLAS_SQLITE):
            cursor.execute(sentencia)
        if es_mysql:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos preparada correctamente.")
