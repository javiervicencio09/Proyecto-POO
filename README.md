# Sistema de Gestión - EcoTech Solutions

**Asignatura:** Programación Orientada a Objeto Seguro (TI3021)  
**Evaluación:** Evaluación Sumativa 3 (ES3) - Consumo de Servicios Externos y Seguridad en Python  
**Institución:** INACAP  
**Estudiante:** Javier Vicencio Zamora  

---

## 1. Descripción General
Sistema de gestión empresarial orientado a objetos desarrollado en Python para **EcoTech Solutions**. El sistema administra empleados, departamentos, proyectos, registros de horas y emisión de informes, e integra capacidades críticas de la **Unidad 3**:
1. **Planificación Operativa y Clima (API Externa)**: Consulta de variables meteorológicas en tiempo real (temperatura, humedad, condición del cielo, viento) mediante **Open-Meteo** (o **OpenWeatherMap**) para anticipar retrasos y determinar la viabilidad operativa de faenas sostenibles en terreno (paneles solares, aerogeneradores).
2. **Gestión de Pagos Internacionales en Divisas (API Externa)**: Consulta de indicadores económicos en tiempo real mediante **Mindicador.cl** (Banco Central de Chile) con contingencia automática a **Open Exchange Rates Global API** para liquidar sueldos a trabajadores en monedas extranjeras (USD, EUR, UF, etc.).
3. **Persistencia Local de APIs**: Almacenamiento auditable de consultas climáticas y comprobantes de liquidación en base de datos relacional (SQLite y MySQL en WampServer).
4. **Seguridad y Control de Acceso**:
   - **Login Gatekeeper obligatorio** antes de acceder al sistema, con bloqueo preventivo tras 3 intentos fallidos para mitigar ataques de fuerza bruta (Criterio 3.1.2).
   - Contraseñas con **hash seguro SHA-256** y comparación en tiempo constante mediante `hmac.compare_digest` para neutralizar ataques de tiempo (Timing Attacks).
   - Validación y sanitización estricta de entradas (prevención de Inyección SQL, XSS, Path Traversal y valores especiales `NaN`/`Infinito`).
   - Manejo seguro de llaves de API en archivo `.env` excluido del control de versiones (`.gitignore`).
5. **Estabilidad y Manejo Robusto de Excepciones (Criterio 3.1.3)**:
   - Timeouts explícitos (`API_TIMEOUT=5.0`) en todas las peticiones HTTP.
   - Jerarquía formal de excepciones en `src/excepciones.py`.
   - Mensajes de error controlados al usuario final que impiden la fuga de información sensible.
   - **Alta disponibilidad (Fallback)**: Si MySQL está inactivo, el sistema conmuta automáticamente a **SQLite local**; si Mindicador sufre caídas de red, conmuta a la API internacional de divisas.

---

## 2. Requisitos Previos
* **Python 3.10** o superior instalado en el sistema.
* **Git for Windows (Git Bash)** instalado.
* Conexión a Internet (para el consumo de servicios web en tiempo real).
* *(Opcional)* **WampServer / MySQL** (puerto 3306): Si no está activo, el sistema conmuta transparentemente a **SQLite local** (`ecotech.db`).

---

## 3. Guía de Instalación y Puesta en Marcha

Sigue estos pasos en tu terminal (**Git Bash** o **PowerShell**):

### Paso 1: Ubicarse en la raíz del proyecto
```bash
cd "/c/Users/javie/OneDrive/Escritorio/Poo/Proyecto-POO"
```

### Paso 2: Activar el entorno virtual existente
```bash
# En Git Bash:
source venv/Scripts/activate

# En PowerShell:
.\venv\Scripts\Activate.ps1
```
*(Verificarás el prefijo `(venv)` al inicio de la línea de comandos)*.

### Paso 3: Instalar o verificar dependencias
```bash
pip install -r requirements.txt
```
*(Librerías oficiales: `requests>=2.31.0`, `PyMySQL==1.1.1`, `python-dotenv==1.0.1`)*.

### Paso 4: Configuración de Variables de Entorno (`.env`)
El proyecto incluye la plantilla documentada en `ecotech/.env.example`. Para configurar el archivo activo:
```bash
cp ecotech/.env.example ecotech/.env
```
Parámetros clave configurados en `ecotech/.env`:
* `DB_ENGINE`: `sqlite` o `mysql`.
* `WEATHER_API_PROVIDER`: `open-meteo` (proveedor oficial gratuito sin clave obligatoria) o `openweathermap`.
* `WEATHER_API_KEY`: Llave opcional para OpenWeatherMap.
* `EXCHANGE_API_PROVIDER`: `mindicador` (Banco Central de Chile) con contingencia a `open.er-api.com`.
* `API_TIMEOUT`: `5.0` segundos de tiempo límite por solicitud HTTP.
* `MAX_LOGIN_INTENTOS`: `3` intentos máximos de autenticación.

---

## 4. Ejecución del Sistema

Con el entorno virtual activado `(venv)`:

### A. Modo Interactivo (Menú Principal por Consola):
```bash
python main.py
```
1. **Inicio de Sesión Requerido (Gatekeeper)**:
   - **Usuario Administrador inicial:** `admin@ecotech.cl`
   - **Contraseña:** `Admin2026*`
2. **Menú de Opciones:**
   - `[1] Gestión de Empleados`: Alta, listado, salarios, búsqueda y liquidaciones en divisas.
   - `[2] Gestión de Departamentos`: Creación, asignación de gerentes y personal.
   - `[3] Gestión de Proyectos`: Asignación de personal, horas acumuladas y clima operativo.
   - `[4] Registro de Horas y Tiempos`: Carga y trazabilidad de horas por proyecto.
   - `[5] Informes y Reportes`: Generación y exportación segura a `.txt`.
   - `[6] Planificación Operativa y Clima de Proyectos (API Externa)`: Consulta meteorológica en tiempo real y recomendación técnica para proyectos sostenibles.
   - `[7] Gestión de Pagos Internacionales en Divisas (API Externa)`: Cotización en vivo y liquidación convertida.
   - `[8] Usuarios y Control de Acceso`: Gestión de credenciales y auditoría de accesos.
   - `[0] Cerrar Sesión y Salir`.

### B. Modo Demostración Rápida (Validación Automática):
Permite validar en pocos segundos todas las inserciones, relaciones de base de datos y el consumo en vivo de las APIs externas:
```bash
python main.py --demo
```

### C. Carga y Población de Datos Semilla:
Permite poblar automáticamente todas las 11 tablas del modelo UML con datos realistas (usuarios, empleados, departamentos, proyectos, horas, mediciones climáticas y liquidaciones en divisas):
```bash
python main.py --seed
```
O ejecutando el módulo de persistencia:
```bash
cd ecotech
python -m src.persistencia.semillas --forzar
cd ..
```
*(También se dispone del script SQL estándar en `ecotech/src/persistencia/semillas.sql` para importación directa en phpMyAdmin).*

---

## 5. Ejecución de la Suite de Pruebas Automatizadas

El proyecto incluye **29 pruebas unitarias automatizadas** que validan la lógica de negocio, la persistencia, el consumo de servicios web con `unittest.mock`, el manejo de errores de red (timeouts, caídas de conexión) y los mecanismos de seguridad:

```bash
cd ecotech
python -m unittest discover -s tests
cd ..
```
**Resultado esperado:**
```text
Ran 29 tests in ~1.2s
OK
```

---

## 6. Documentación Adicional
* **Informe Técnico de Seguridad y Auditoría de IA (Criterio 3.1.4):**  
  Consulte el documento [`ecotech/docs/INFORME_SEGURIDAD_IA.md`](ecotech/docs/INFORME_SEGURIDAD_IA.md) para revisar la bitácora de prompts, vulnerabilidades detectadas en código generado por IA y justificación técnica de las decisiones adoptadas.
* **Diagrama de Clases UML:**  
  Ubicado en `ecotech/docs/uml_grupal.png`.
