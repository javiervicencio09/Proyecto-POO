import logging
from src.persistencia.conexion import abrir_conexion, obtener_motor

logger = logging.getLogger(__name__)


def crear_tablas() -> None:
    """
    Crea todas las tablas requeridas por el diagrama de clases UML (EcoTech Solutions)
    tanto para SQLite como para MySQL (WampServer), asegurando integridad referencial
    y compatibilidad con esquemas previos.
    """
    conexion = abrir_conexion()
    cursor = conexion.cursor()
    motor = obtener_motor()

    if motor == "sqlite":
        sentencias = [
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                contrasena_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'USUARIO'
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS administrador (
                id_usuario INTEGER PRIMARY KEY,
                nivel_acceso TEXT NOT NULL DEFAULT 'ADMIN',
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cargo TEXT NOT NULL,
                salario REAL NOT NULL,
                direccion TEXT NOT NULL DEFAULT '',
                telefono TEXT NOT NULL DEFAULT '',
                correo TEXT NOT NULL DEFAULT '',
                fecha_inicio_contrato TEXT,
                id_usuario INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS departamento (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                gerente TEXT NOT NULL,
                id_gerente INTEGER,
                FOREIGN KEY (id_gerente) REFERENCES empleado(id_empleado) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto (
                id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS departamento_empleado (
                id_departamento INTEGER NOT NULL,
                id_empleado INTEGER NOT NULL,
                PRIMARY KEY (id_departamento, id_empleado),
                FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE CASCADE,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto_empleado (
                id_proyecto INTEGER NOT NULL,
                id_empleado INTEGER NOT NULL,
                PRIMARY KEY (id_proyecto, id_empleado),
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                horas REAL NOT NULL,
                descripcion_tareas TEXT NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS informe (
                id_informe INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                fecha_generacion TEXT NOT NULL,
                contenido TEXT NOT NULL,
                creado_por INTEGER,
                FOREIGN KEY (creado_por) REFERENCES usuario(id_usuario) ON DELETE SET NULL
            );
            """,
        ]
    else:
        sentencias = [
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(150) NOT NULL UNIQUE,
                contrasena_hash VARCHAR(255) NOT NULL,
                tipo_usuario VARCHAR(20) NOT NULL DEFAULT 'USUARIO'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS administrador (
                id_usuario INT PRIMARY KEY,
                nivel_acceso VARCHAR(50) NOT NULL DEFAULT 'ADMIN',
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                cargo VARCHAR(100) NOT NULL,
                salario DECIMAL(12, 2) NOT NULL,
                direccion VARCHAR(255) NOT NULL DEFAULT '',
                telefono VARCHAR(30) NOT NULL DEFAULT '',
                correo VARCHAR(150) NOT NULL DEFAULT '',
                fecha_inicio_contrato DATE NULL,
                id_usuario INT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS departamento (
                id_departamento INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                gerente VARCHAR(100) NOT NULL,
                id_gerente INT NULL,
                FOREIGN KEY (id_gerente) REFERENCES empleado(id_empleado) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto (
                id_proyecto INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(150) NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_inicio DATE NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS departamento_empleado (
                id_departamento INT NOT NULL,
                id_empleado INT NOT NULL,
                PRIMARY KEY (id_departamento, id_empleado),
                FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE CASCADE,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto_empleado (
                id_proyecto INT NOT NULL,
                id_empleado INT NOT NULL,
                PRIMARY KEY (id_proyecto, id_empleado),
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id_registro INT PRIMARY KEY AUTO_INCREMENT,
                id_empleado INT NOT NULL,
                id_proyecto INT NOT NULL,
                fecha DATE NOT NULL,
                horas DECIMAL(5, 2) NOT NULL,
                descripcion_tareas TEXT NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS informe (
                id_informe INT PRIMARY KEY AUTO_INCREMENT,
                tipo VARCHAR(100) NOT NULL,
                fecha_generacion DATE NOT NULL,
                contenido TEXT NOT NULL,
                creado_por INT NULL,
                FOREIGN KEY (creado_por) REFERENCES usuario(id_usuario) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        ]

    try:
        for sql in sentencias:
            cursor.execute(sql)

        # Migración automática si la tabla empleado o departamento ya existían sin nuevas columnas
        if motor == "sqlite":
            cursor.execute("PRAGMA table_info(empleado);")
            columnas_empleado = [col[1] for col in cursor.fetchall()]
            if "id_usuario" not in columnas_empleado:
                cursor.execute("ALTER TABLE empleado ADD COLUMN id_usuario INTEGER;")

            cursor.execute("PRAGMA table_info(departamento);")
            columnas_depto = [col[1] for col in cursor.fetchall()]
            if "id_gerente" not in columnas_depto:
                cursor.execute("ALTER TABLE departamento ADD COLUMN id_gerente INTEGER;")

        conexion.commit()
    except Exception as err:
        conexion.rollback()
        raise RuntimeError(f"Error al inicializar las tablas de la base de datos: {err}") from err
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos preparada correctamente con el modelo UML completo.")