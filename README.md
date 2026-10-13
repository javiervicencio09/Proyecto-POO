# Sistema de Gestion - EcoTech Solutions

**Asignatura:** Programacion Orientada a Objeto Seguro (TI3021)  
**Evaluacion:** Evaluacion Sumativa 2 (ES2)  
**Institucion:** INACAP  

---

## 1. Descripcion General
Sistema de gestion empresarial orientado a objetos desarrollado en Python para la empresa ficticia **EcoTech Solutions**. El software permite gestionar empleados, departamentos, proyectos, asignacion de personal, registro de horas trabajadas, reportes ejecutivos y autenticacion segura de usuarios y administradores con conexion directa a base de datos relacional (MySQL en WampServer o SQLite).

---

## 2. Requisitos Previos
* **Python 3.10** o superior.
* **WampServer** (con el servicio MySQL activo en el puerto 3306 o 3307).

---

## 3. Instalacion y Puesta en Marcha

### Paso 1: Clonar o posicionarse en la carpeta del proyecto
Abrir una terminal en la raiz o en la carpeta `ecotech/`:
```powershell
cd ecotech
```

### Paso 2: Crear y activar el entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Paso 3: Instalar dependencias
```powershell
pip install -r requirements.txt
```

### Paso 4: Configuracion de Base de Datos (.env)
Copiar el archivo de plantilla `.env.example` a `.env`:
```powershell
Copy-Item .env.example .env
```
Para conectar a WampServer, verificar que `.env` contenga:
```env
DB_ENGINE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=ecotech
```
*(Nota: Si no se configura MySQL, el sistema funciona de manera local con SQLite por defecto).*

---

## 4. Ejecucion de la Aplicacion

### Modo Interactivo (Menu CRUD por Consola):
```powershell
python main.py
```
Desplegara el menu principal interactivo:
* `[1] Gestion de Empleados`: Registrar, listar, buscar, modificar salario y eliminar.
* `[2] Gestion de Departamentos`: Crear, listar, asociar gerente y asignar empleados.
* `[3] Gestion de Proyectos`: Crear, listar, consultar personal y horas acumuladas.
* `[4] Registro de Horas y Tiempos`: Cargar trazabilidad de horas por empleado y proyecto.
* `[5] Informes y Reportes`: Generar resumen general y exportar a archivo `.txt`.
* `[6] Usuarios y Autenticacion Segura`: Alta de usuarios/administradores y prueba de credenciales (SHA-256).
* `[0] Salir del Sistema`.

### Modo Demostracion Rapida:
```powershell
python main.py --demo
```

---

## 5. Ejecucion de Pruebas Automatizadas
Para verificar la integridad de la logica orientada a objetos y la persistencia:
```powershell
python -m unittest discover -s tests
```

---

## 6. Estructura Arquitectonica
* `src/dominio/`: Modelos de negocio (Usuario, Administrador, Empleado, Departamento, Proyecto, RegistroDeTiempo, Informe) con encapsulamiento y herencia.
* `src/persistencia/`: Manejo de conexion multimotor, migraciones DDL (`crear_bd.py`) y Data Access Objects (DAOs) con control de transacciones y rollback.
* `src/servicios/`: Logica de control y menu interactivo CLI con validacion de entradas.
* `docs/`: Diagrama UML (`uml_grupal.png`).

## Diagrama de Clases (UML)
![Diagrama UML EcoTech](diagrama_uml.jpeg)
