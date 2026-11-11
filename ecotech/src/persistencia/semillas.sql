-- ==============================================================================
-- ECOTECH SOLUTIONS - DATOS SEMILLA (SEED DATA)
-- Compatible con MySQL 8.x / 9.x (WampServer) y SQLite
-- Modelo Integral Unidad 3 (TI3021 Programación Orientada a Objeto Seguro)
-- ==============================================================================

-- Desactivar verificación de claves foráneas temporalmente durante la carga
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------------------------
-- 1. TABLA: usuario (Contraseñas con Hashing Seguro SHA-256)
-- Claves en texto plano:
-- admin@ecotech.cl        -> Admin2026*
-- gerencia@ecotech.cl     -> Gerente2026*
-- ana.perez@ecotech.cl    -> AnaPerez2026*
-- carlos.ruiz@ecotech.cl  -> CarlosRuiz2026*
-- luis.gomez@ecotech.cl   -> LuisGomez2026*
-- sofia.castro@ecotech.cl -> SofiaCastro2026*
-- ------------------------------------------------------------------------------
INSERT INTO usuario (id_usuario, nombre, correo, contrasena_hash, tipo_usuario) VALUES
(1, 'Administrador General', 'admin@ecotech.cl', '8d90ed647b948fa80c3c9bbf5316c78f151723f52fb9d6101f818af8afff69ec', 'ADMIN'),
(2, 'Gerencia de Operaciones', 'gerencia@ecotech.cl', '50a7c462725fa848d795fefab314ba1a681c2f9d6ad44dbb8a4f08e4860b2eb8', 'ADMIN'),
(3, 'Ana Pérez', 'ana.perez@ecotech.cl', '3cb49a43a0d58beea26e47b355c2d33ce74b966cf17f779183cfbb94966cb17b', 'USUARIO'),
(4, 'Carlos Ruiz', 'carlos.ruiz@ecotech.cl', 'f3555543d81b95388c3f4e1f7d54203e0078103c80cf2e26090a21a5a7ad8a9d', 'USUARIO'),
(5, 'Luis Gómez', 'luis.gomez@ecotech.cl', 'e9dcbe4b11c97a51d279cf48c3b179e830e0bc3021f47f6a7351662fb167664f', 'USUARIO'),
(6, 'Sofía Castro', 'sofia.castro@ecotech.cl', '8495a8966bfcaee09403b22cfc1664e1d1f057885b5df33246ebbb75b11a43a3', 'USUARIO')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- ------------------------------------------------------------------------------
-- 2. TABLA: administrador (Herencia de Usuario)
-- ------------------------------------------------------------------------------
INSERT INTO administrador (id_usuario, nivel_acceso) VALUES
(1, 'SUPERADMIN'),
(2, 'SENIOR')
ON DUPLICATE KEY UPDATE nivel_acceso=VALUES(nivel_acceso);

-- ------------------------------------------------------------------------------
-- 3. TABLA: empleado
-- ------------------------------------------------------------------------------
INSERT INTO empleado (id_empleado, nombre, cargo, salario, direccion, telefono, correo, fecha_inicio_contrato, id_usuario) VALUES
(1, 'Carlos Ruiz', 'Gerente de Operaciones en Terreno', 2800000.00, 'Av. Los Conquistadores 1920, Providencia, Santiago', '+56 9 7123 4567', 'carlos.ruiz@ecotech.cl', '2024-03-01', 4),
(2, 'Ana Pérez', 'Ingeniera Ambiental Senior', 1950000.00, 'Calle Las Araucarias 450, Concepción', '+56 9 8234 5678', 'ana.perez@ecotech.cl', '2024-05-15', 3),
(3, 'Luis Gómez', 'Analista de Datos y Huella de Carbono', 1450000.00, 'Pasaje El Roble 812, Santiago Centro', '+56 9 9345 6789', 'luis.gomez@ecotech.cl', '2024-08-01', 5),
(4, 'Sofía Castro', 'Especialista en Energías Renovables', 1750000.00, 'Av. Del Mar 2200, La Serena', '+56 9 6456 7890', 'sofia.castro@ecotech.cl', '2024-09-10', 6),
(5, 'Matías Valenzuela', 'Técnico de Monitoreo Fotovoltaico', 980000.00, 'Calle Prat 340, Antofagasta', '+56 9 5567 8901', 'matias.valenzuela@ecotech.cl', '2025-01-15', NULL)
ON DUPLICATE KEY UPDATE cargo=VALUES(cargo), salario=VALUES(salario);

-- ------------------------------------------------------------------------------
-- 4. TABLA: departamento
-- ------------------------------------------------------------------------------
INSERT INTO departamento (id_departamento, nombre, gerente, id_gerente) VALUES
(1, 'Ingeniería y Sostenibilidad', 'Ana Pérez', 2),
(2, 'Operaciones en Terreno', 'Carlos Ruiz', 1),
(3, 'Tecnología e Innovación', 'Sofía Castro', 4)
ON DUPLICATE KEY UPDATE gerente=VALUES(gerente), id_gerente=VALUES(id_gerente);

-- ------------------------------------------------------------------------------
-- 5. TABLA: departamento_empleado (Relación M:N)
-- ------------------------------------------------------------------------------
INSERT IGNORE INTO departamento_empleado (id_departamento, id_empleado) VALUES
(1, 2),
(1, 3),
(2, 1),
(2, 5),
(3, 4);

-- ------------------------------------------------------------------------------
-- 6. TABLA: proyecto
-- ------------------------------------------------------------------------------
INSERT INTO proyecto (id_proyecto, nombre, descripcion, fecha_inicio) VALUES
(1, 'Parque Solar Atacama Fase II', 'Despliegue y monitoreo de módulos fotovoltaicos de alta radiación en San Pedro de Atacama.', '2025-02-01'),
(2, 'Monitoreo Huella Hídrica Biobío', 'Sensorización continua y trazabilidad de calidad de agua en la cuenca del Río Biobío.', '2025-04-10'),
(3, 'Auditoría Eficiencia Gran Santiago', 'Optimización de consumo energético y climatización pasiva para edificaciones sostenibles.', '2025-06-01'),
(4, 'Planta Eólica Canela Renovables', 'Mantenimiento predictivo y análisis de generación en parque eólico costero Coquimbo.', '2025-08-15')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- ------------------------------------------------------------------------------
-- 7. TABLA: proyecto_empleado (Relación M:N)
-- ------------------------------------------------------------------------------
INSERT IGNORE INTO proyecto_empleado (id_proyecto, id_empleado) VALUES
(1, 1),
(1, 5),
(2, 2),
(2, 3),
(3, 3),
(3, 4),
(4, 1),
(4, 4);

-- ------------------------------------------------------------------------------
-- 8. TABLA: registro_tiempo
-- ------------------------------------------------------------------------------
INSERT INTO registro_tiempo (id_registro, id_empleado, id_proyecto, fecha, horas, descripcion_tareas) VALUES
(1, 1, 1, '2026-02-10', 8.00, 'Supervisión de montaje y puesta en marcha de inversores solares.'),
(2, 5, 1, '2026-02-10', 7.50, 'Inspección termográfica de celdas fotovoltaicas y cableado de potencia.'),
(3, 2, 2, '2026-02-12', 6.00, 'Recolección de muestras de caudal y calibración de sondas multiparamétricas.'),
(4, 3, 2, '2026-02-12', 5.50, 'Modelamiento estadístico de demanda hídrica y consolidación de métricas.'),
(5, 4, 3, '2026-02-15', 7.00, 'Levantamiento de cargas en subestaciones y diagnóstico lumínico LED.'),
(6, 4, 4, '2026-02-18', 8.00, 'Análisis de telemetría de turbinas y curvas de generación eólica.')
ON DUPLICATE KEY UPDATE horas=VALUES(horas);

-- ------------------------------------------------------------------------------
-- 9. TABLA: informe
-- ------------------------------------------------------------------------------
INSERT INTO informe (id_informe, tipo, fecha_generacion, contenido, creado_por) VALUES
(1, 'Resumen Operativo Trimestral', '2026-02-20', 'Informe consolidado de gestión: 4 proyectos activos en terreno, 42.0 horas registradas, 100% cumplimiento normativo ambiental.', 1),
(2, 'Auditoría de Impacto y Sostenibilidad', '2026-02-25', 'Evaluación técnica de viabilidad climática en zona norte y centro sur. Recomendación de continuidad operacional con alta eficiencia.', 2)
ON DUPLICATE KEY UPDATE contenido=VALUES(contenido);

-- ------------------------------------------------------------------------------
-- 10. TABLA: registro_clima_proyecto (Problemática 1 - APIs Externas)
-- ------------------------------------------------------------------------------
INSERT INTO registro_clima_proyecto (id_registro_clima, id_proyecto, ciudad, temperatura, humedad, estado_clima, recomendacion, fecha_consulta) VALUES
(1, 1, 'Antofagasta, Chile', 21.5, 62.0, 'Despejado / Soleado', 'Condición óptima para trabajo en terreno y generación solar.', '2026-02-10 09:30:00'),
(2, 2, 'Concepción, Chile', 18.2, 74.0, 'Nubosidad Parcial', 'Condición meteorológica favorable para toma de muestras en terreno.', '2026-02-12 11:15:00'),
(3, 3, 'Santiago, Chile', 26.8, 41.0, 'Despejado', 'Jornada calurosa: Hidratación continua para cuadrilla de auditores.', '2026-02-15 14:00:00'),
(4, 4, 'La Serena, Chile', 19.0, 68.0, 'Viento Moderado', 'Condición excelente para generación eólica y mantenimiento.', '2026-02-18 10:45:00')
ON DUPLICATE KEY UPDATE temperatura=VALUES(temperatura);

-- ------------------------------------------------------------------------------
-- 11. TABLA: pago_internacional (Problemática 2 - APIs Externas)
-- ------------------------------------------------------------------------------
INSERT INTO pago_internacional (id_pago, id_empleado, id_proyecto, monto_origen, moneda_origen, monto_convertido, moneda_destino, tipo_cambio, fecha_pago, detalles) VALUES
(1, 1, 1, 2800000.00, 'CLP', 2864.40, 'USD', 0.001023, '2026-02-28 17:00:00', 'Liquidación mensual consultor senior - Parque Solar Atacama'),
(2, 2, 2, 1950000.00, 'CLP', 1842.75, 'EUR', 0.000945, '2026-02-28 17:05:00', 'Compensación asesoría internacional cuencas hídricas'),
(3, 3, 3, 1450000.00, 'CLP', 1483.35, 'USD', 0.001023, '2026-02-28 17:10:00', 'Honorarios análisis huella de carbono reporte corporativo'),
(4, 4, 4, 1750000.00, 'CLP', 1653.75, 'EUR', 0.000945, '2026-02-28 17:15:00', 'Liquidación técnica parque eólico Canela')
ON DUPLICATE KEY UPDATE monto_convertido=VALUES(monto_convertido);

-- Reactivar verificación de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

