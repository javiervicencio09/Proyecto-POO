# Sistema de Gestion - EcoTech Solutions

**Asignatura:** Programacion Orientada a Objeto Seguro (TI3021)  
**Evaluacion:** Evaluacion Sumativa 2 (ES2)  
**Institucion:** INACAP  

---

## 1. Descripcion General
Sistema de gestion empresarial orientado a objetos desarrollado en Python para la empresa ficticia **EcoTech Solutions**. El software permite gestionar empleados, departamentos, proyectos, asignacion de personal, registro de horas trabajadas, reportes ejecutivos y autenticacion segura de usuarios y administradores con conexion directa a base de datos relacional (MySQL en WampServer o SQLite).

---

## 2. Requisitos Previos
* **Python 3.10** o superior instalado en el sistema.
* **Git for Windows (Git Bash)** instalado.
* *(Opcional)* **WampServer** (con el servicio MySQL activo en el puerto 3306 o 3307) si se desea persistencia en MySQL.

---

## 3. Guia de Instalacion y Puesta en Marcha en Git Bash

Sigue estos pasos en tu terminal **Git Bash**:

### Paso 1: Abrir Git Bash y ubicarse en la raiz del proyecto
Navega a la carpeta principal del proyecto:
```bash
cd "/c/Users/javie/OneDrive/Escritorio/Poo/Proyecto-POO"
```
> **Nota:** Puedes comprobar que estas en el directorio correcto ejecutando `pwd` y verificando que veas archivos como `main.py` y `requirements.txt`.

### Paso 2: Crear el entorno virtual
Crea un entorno virtual aislado llamado `venv`:
```bash
python -m venv venv
```
*(Si en tu sistema el comando principal es el lanzador de Python para Windows, tambien puedes usar: `py -m venv venv`)*.

### Paso 3: Activar el entorno virtual
En Git Bash, la activacion del entorno se realiza con el comando `source`:
```bash
source venv/Scripts/activate
```
> **Confirmacion visual:** Una vez ejecutado, observaras el prefijo `(venv)` al inicio de tu prompt en la terminal, lo que indica que el entorno esta activo.

### Paso 4: Instalar las dependencias
Instala las librerias requeridas (`PyMySQL` y `python-dotenv`) ejecutando:
```bash
pip install -r requirements.txt
```

### Paso 5: Configuracion de Base de Datos (.env)
El proyecto incluye un archivo de plantilla en `ecotech/.env.example`. Si aun no existe el archivo `.env`, copialo con:
```bash
cp ecotech/.env.example ecotech/.env
```

Para conectar a **WampServer (MySQL)**, confirma que el archivo `ecotech/.env` contenga:
```env
DB_ENGINE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=ecotech
```
> **Nota importante:** Si no cuentas con WampServer o MySQL encendido, el sistema cambiara de forma automatica a **SQLite local** (`ecotech.db`) sin interrumpir la ejecucion.

---

## 4. Ejecucion de la Aplicacion

Con el entorno virtual activado `(venv)`, ejecuta la aplicacion desde la raiz:

### Modo Interactivo (Menu Principal por Consola):
```bash
python main.py
```
Desplegara el menu interactivo del sistema:
* `[1] Gestion de Empleados`: Registrar, listar, buscar, modificar salario y eliminar.
* `[2] Gestion de Departamentos`: Crear, listar, asociar gerente y asignar empleados.
* `[3] Gestion de Proyectos`: Crear, listar, consultar personal y horas acumuladas.
* `[4] Registro de Horas y Tiempos`: Cargar trazabilidad de horas por empleado y proyecto.
* `[5] Informes y Reportes`: Generar resumen general y exportar a archivo `.txt`.
* `[6] Usuarios y Autenticacion Segura`: Alta de usuarios/administradores y prueba de credenciales (SHA-256).
* `[0] Salir del Sistema`.

### Modo Demostracion Rapida:
Para ejecutar un flujo de demostracion automatizado:
```bash
python main.py --demo
```

### Desactivar el Entorno Virtual:
Cuando finalices tu sesion de trabajo, desactiva el entorno con:
```bash
deactivate
```

---

## 5. Ejecucion de Pruebas Automatizadas (Unit Tests)

Para correr la suite de pruebas unitarias que validan la logica de negocio y persistencia:
```bash
cd ecotech
python -m unittest discover -s tests
cd ..
```

---

## 6. Estructura Arquitectonica
* `src/dominio/`: Modelos de negocio (Usuario, Administrador, Empleado, Departamento, Proyecto, RegistroDeTiempo, Informe) con encapsulamiento y herencia.
* `src/persistencia/`: Manejo de conexion multimotor, migraciones DDL (`crear_bd.py`) y Data Access Objects (DAOs) con control de transacciones y rollback.
* `src/servicios/`: Logica de control y menu interactivo CLI con validacion de entradas.
* `docs/`: Diagrama UML (`uml_grupal.png`).

