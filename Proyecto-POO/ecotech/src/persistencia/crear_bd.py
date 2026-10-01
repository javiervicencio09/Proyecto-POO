from src.persistencia.conexion import abrir_conexion


def crear_tablas() -> None:
    conexion = abrir_conexion()
    cursor = conexion.cursor()
    sql = [
        """CREATE TABLE IF NOT EXISTS empleado (
            id_empleado INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(100) NOT NULL,
            cargo VARCHAR(100) NOT NULL, salario DECIMAL(12, 2) NOT NULL,
            direccion VARCHAR(255) NOT NULL DEFAULT '', telefono VARCHAR(30) NOT NULL DEFAULT '',
            correo VARCHAR(150) NOT NULL DEFAULT '', fecha_inicio_contrato DATE NULL
        )""",
        """CREATE TABLE IF NOT EXISTS departamento (
            id_departamento INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(100) NOT NULL,
            gerente VARCHAR(100) NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS proyecto (
            id_proyecto INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(150) NOT NULL,
            descripcion TEXT NOT NULL, fecha_inicio DATE NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS departamento_empleado (
            id_departamento INT NOT NULL, id_empleado INT NOT NULL,
            PRIMARY KEY (id_departamento, id_empleado),
            FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento),
            FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
        )""",
        """CREATE TABLE IF NOT EXISTS proyecto_empleado (
            id_proyecto INT NOT NULL, id_empleado INT NOT NULL,
            PRIMARY KEY (id_proyecto, id_empleado),
            FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto),
            FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
        )""",
    ]

    try:
        for sentencia in sql:
            cursor.execute(sentencia)
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos preparada correctamente.")