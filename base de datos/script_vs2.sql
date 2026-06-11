CREATE DATABASE bd_paella;
USE bd_paella;

-- =====================================================
-- ROLES Y AUTENTICACIÓN
-- =====================================================

CREATE TABLE roles (
    id_role_pk   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(20) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE usuarios_auth (
    id_auth_pk       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario   VARCHAR(50) UNIQUE NOT NULL,
    contrasena_hash  VARCHAR(255) NOT NULL,
    correo           VARCHAR(40) NULL,
    id_role_fk       INT NOT NULL,
    activo           TINYINT(1) DEFAULT 1,
    requiere_cambio_pw TINYINT(1) DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auth_role FOREIGN KEY (id_role_fk) REFERENCES roles(id_role_pk)
);
SELECT * FROM usuarios_auth;
SELECT * FROM roles;

-- =====================================================
-- PERSONAS: EMPLEADOS Y CLIENTES
-- =====================================================

CREATE TABLE empleados (
    id_empleado_pk INT AUTO_INCREMENT PRIMARY KEY,
    foto_empleado VARCHAR(255) NOT NULL,
    nom_empleado VARCHAR(50) NOT NULL,
    apellido_empleado VARCHAR(50) NOT NULL,
    fecha_naci_empleado DATE NOT NULL,
    tipo_doc ENUM('Cédula de Ciudadanía', 'Cédula de Extranjería', 'Pasaporte', 'Tarjeta de Identidad') NOT NULL,
    num_doc VARCHAR(12) NOT NULL UNIQUE,
    tel_empleado VARCHAR(10) NOT NULL,
    correo_empleado VARCHAR(100) NOT NULL UNIQUE,
    direc_empleado VARCHAR(100) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    tipo_contrato ENUM ('Término Indefinido', 'Término Fijo', 'Obra o Labor', 'Contrato de Aprendizaje') NOT NULL,
    salario_empleado DECIMAL(10,2) NOT NULL,
    estado_empleado ENUM('activo', 'inactivo') DEFAULT 'activo',
    id_auth_fk INT UNIQUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_empleado_auth FOREIGN KEY (id_auth_fk)
    REFERENCES usuarios_auth(id_auth_pk)
);

CREATE TABLE clientes (
    id_clien_pk        INT AUTO_INCREMENT PRIMARY KEY,
    nom_clien          VARCHAR(25) NOT NULL,
    apellido_clien     VARCHAR(30) NOT NULL,
    fecha_naci_cliente DATE NOT NULL,
    tel_cliente        BIGINT UNSIGNED NOT NULL,      
    correo_clien       VARCHAR(40) NOT NULL,
    direc_clien        VARCHAR(100) NOT NULL,
    estado_clien       ENUM('activo', 'inactivo') NOT NULL,
    id_auth_fk         INT UNIQUE,
    CONSTRAINT fk_cliente_auth FOREIGN KEY (id_auth_fk) REFERENCES usuarios_auth(id_auth_pk)
);

-- =====================================================
-- UBICACIONES
-- =====================================================

CREATE TABLE localidades (
    id_local_pk      INT AUTO_INCREMENT PRIMARY KEY,
    nom_local        VARCHAR(50) NOT NULL,
    cod_postal_local INT NOT NULL
);

CREATE TABLE barrios (
    id_barrio_pk       INT AUTO_INCREMENT PRIMARY KEY,
    nom_barrio         VARCHAR(50) NOT NULL,
    id_local_barrio_fk INT NOT NULL,
    CONSTRAINT fk_barrio_local FOREIGN KEY (id_local_barrio_fk) REFERENCES localidades(id_local_pk)
);

-- =====================================================
-- MENÚS Y TIPOS
-- =====================================================

CREATE TABLE tipos_menus (
    id_tipo_menu_pk INT AUTO_INCREMENT PRIMARY KEY,
    nom_tipo_menu   VARCHAR(20) NOT NULL,
    des_tipo_menu   VARCHAR(100) NOT NULL
);

CREATE TABLE menus (
    id_menu_pk       INT AUTO_INCREMENT PRIMARY KEY,
    img_menu         VARCHAR(255) NOT NULL,
    nom_menu         VARCHAR(60) NOT NULL,
    precio_menu      DECIMAL(10,2) NOT NULL,
    des_menu         TEXT NOT NULL,
    id_tipo_menu_fk  INT NOT NULL,
    disponible_menu  TINYINT(1) DEFAULT 1,           -- se actualiza automáticamente según stock
    CONSTRAINT fk_menu_tipo FOREIGN KEY (id_tipo_menu_fk) REFERENCES tipos_menus(id_tipo_menu_pk)
);

-- =====================================================
-- INVENTARIO: PROVEEDORES, UNIDADES, CATEGORÍAS Y PRODUCTOS
-- =====================================================

CREATE TABLE proveedores (
    id_provee_pk            INT AUTO_INCREMENT PRIMARY KEY,
    tipo_provee             ENUM('empresa', 'persona_natural') NOT NULL DEFAULT 'empresa',
    nom_provee              VARCHAR(100) NOT NULL,
    nit_cedula_provee       VARCHAR(15) UNIQUE NOT NULL,
    nombre_contacto_provee  VARCHAR(100) NULL,
    tel_provee              VARCHAR(10) NOT NULL,
    correo_provee           VARCHAR(50) NOT NULL,
    direc_provee            VARCHAR(100) NOT NULL,
    condicion_pago_provee   ENUM('contado', '15_dias', '30_dias', '60_dias') NULL,
    observaciones_provee    TEXT NULL,
    estado_provee           ENUM('activo', 'inactivo') NOT NULL DEFAULT 'activo'
);

CREATE TABLE proveedor_categorias (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id         INT NOT NULL,
    categoriaproducto_id INT NOT NULL,
    CONSTRAINT fk_provcate_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_provee_pk),
    CONSTRAINT fk_provcate_categoria FOREIGN KEY (categoriaproducto_id) REFERENCES categorias_productos(id_cate_produ_pk),
    UNIQUE KEY uq_prov_cate (proveedor_id, categoriaproducto_id)
);

CREATE TABLE unidades_medidas (
    id_uni_medi_pk  INT AUTO_INCREMENT PRIMARY KEY,
    nom_uni_medi    VARCHAR(20) NOT NULL,             -- ej: kilogramo, litro, unidad
    abreviatura     VARCHAR(8) NOT NULL,              -- ej: kg, L, und
    tipo_uni_medi   VARCHAR(20) NOT NULL              -- ej: peso, volumen, cantidad
);

CREATE TABLE categorias_productos (
    id_cate_produ_pk INT AUTO_INCREMENT PRIMARY KEY,
    nom_cate         VARCHAR(30) NOT NULL,
    des_cate         VARCHAR(100) NOT NULL
);

CREATE TABLE productos (
    id_produ_pk          INT AUTO_INCREMENT PRIMARY KEY,
    nom_produ            VARCHAR(50) NOT NULL,
    stock_actual_produ   DECIMAL(10,3) NOT NULL DEFAULT 0,   -- cantidad real disponible
    stock_minimo_produ   DECIMAL(10,3) NOT NULL DEFAULT 0,   -- nivel de alerta de reabastecimiento
    fecha_venci_produ    DATE NOT NULL,
    precio_uni_produ     DECIMAL(10,2) NOT NULL,
    des_produ            VARCHAR(100) NOT NULL,
    estado_produ         ENUM('disponible', 'no disponible', 'descontinuado') NOT NULL,
    id_provee_produ_fk   INT NOT NULL,
    id_uni_medi_produ_fk INT NOT NULL,
    id_cate_produ_fk     INT NOT NULL,
    CONSTRAINT fk_producto_proveedor FOREIGN KEY (id_provee_produ_fk)   REFERENCES proveedores(id_provee_pk),
    CONSTRAINT fk_producto_unidad    FOREIGN KEY (id_uni_medi_produ_fk) REFERENCES unidades_medidas(id_uni_medi_pk),
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_cate_produ_fk)     REFERENCES categorias_productos(id_cate_produ_pk)
);

-- =====================================================
-- RECETAS: qué productos necesita cada menú y en qué cantidad
-- ESTA ES LA TABLA CLAVE para el inventario
-- =====================================================

CREATE TABLE recetas_menus (
    id_receta_pk         INT AUTO_INCREMENT PRIMARY KEY,
    id_menu_fk           INT NOT NULL,
    id_produ_fk          INT NOT NULL,
    cantidad_reque       DECIMAL(10,3) NOT NULL,             -- cuánto se necesita por porción
    id_uni_medi_fk       INT NOT NULL,                       -- en qué unidad está esa cantidad
    notas                VARCHAR(100),                        -- ej: "picado fino", "sin piel"
    CONSTRAINT fk_receta_menu    FOREIGN KEY (id_menu_fk)    REFERENCES menus(id_menu_pk),
    CONSTRAINT fk_receta_produ   FOREIGN KEY (id_produ_fk)   REFERENCES productos(id_produ_pk),
    CONSTRAINT fk_receta_unidad  FOREIGN KEY (id_uni_medi_fk) REFERENCES unidades_medidas(id_uni_medi_pk),
    UNIQUE KEY uq_receta (id_menu_fk, id_produ_fk)           -- un producto una vez por receta
);

-- =====================================================
-- PEDIDOS
-- =====================================================

CREATE TABLE pedidos (
    id_pedido_pk       INT AUTO_INCREMENT PRIMARY KEY,
    fecha_pedido       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado_pedido      ENUM('pendiente', 'confirmado', 'preparando', 'listo', 'entregado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    tipo_pedido        ENUM('domicilio', 'evento') NOT NULL,
    total_pedido       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    notas_pedido       VARCHAR(200),                          -- instrucciones especiales
    id_clien_pedido_fk INT NOT NULL,
    id_emple_pedido_fk INT NULL,
    solicitud_cancelacion_pendiente TINYINT(1) NOT NULL DEFAULT 0,
    motivo_solicitud_cancelacion    VARCHAR(300),
    fecha_solicitud_cancelacion     DATETIME,
    CONSTRAINT fk_pedido_cliente  FOREIGN KEY (id_clien_pedido_fk) REFERENCES clientes(id_clien_pk),
    CONSTRAINT fk_pedido_empleado FOREIGN KEY (id_emple_pedido_fk) REFERENCES empleados(id_empleado_pk)
);

CREATE TABLE historial_estados_pedidos (
    id_historial_pk    INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_fk       INT NOT NULL,
    estado_anterior    VARCHAR(12) NOT NULL,
    estado_nuevo       VARCHAR(12) NOT NULL,
    fecha_cambio       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_auth_fk         INT NULL,
    notas              VARCHAR(300),
    CONSTRAINT fk_historial_pedido FOREIGN KEY (id_pedido_fk) REFERENCES pedidos(id_pedido_pk),
    CONSTRAINT fk_historial_auth   FOREIGN KEY (id_auth_fk) REFERENCES usuarios_auth(id_auth_pk)
);

CREATE TABLE detalles_pedidos_menus (
    id_detalle_pk              INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_fk               INT NOT NULL,
    id_menu_fk                 INT NOT NULL,
    cant_detalle               INT NOT NULL,                  -- cuántas porciones pidió
    precio_unitario            DECIMAL(10,2) NOT NULL,        -- precio al momento del pedido
    subtotal                   DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (id_pedido_fk) REFERENCES pedidos(id_pedido_pk),
    CONSTRAINT fk_detalle_menu   FOREIGN KEY (id_menu_fk)   REFERENCES menus(id_menu_pk)
);

-- =====================================================
-- Registra exactamente qué stock se descontó por cada pedido
-- Permite auditar y revertir si el pedido se cancela
-- =====================================================

CREATE TABLE consumos_pedidos (
    id_consumo_pk      INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_fk       INT NOT NULL,
    id_produ_fk        INT NOT NULL,
    cantidad_consumida DECIMAL(10,3) NOT NULL,
    id_uni_medi_fk     INT NOT NULL,
    fecha_consumo      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_consumo_pedido  FOREIGN KEY (id_pedido_fk)  REFERENCES pedidos(id_pedido_pk),
    CONSTRAINT fk_consumo_produ   FOREIGN KEY (id_produ_fk)   REFERENCES productos(id_produ_pk),
    CONSTRAINT fk_consumo_unidad  FOREIGN KEY (id_uni_medi_fk) REFERENCES unidades_medidas(id_uni_medi_pk)
);

-- =====================================================
-- MOVIMIENTOS DE INVENTARIO (entradas y salidas manuales)
-- =====================================================

CREATE TABLE movimientos_productos (
    id_movi_pk          INT AUTO_INCREMENT PRIMARY KEY,
    tipo_movi           ENUM('entrada', 'salida') NOT NULL,
    motivo_movi         VARCHAR(50) NOT NULL,                 -- ej: "compra", "merma", "ajuste"
    fecha_movi          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cant_movi           DECIMAL(10,3) NOT NULL,
    stock_anterior      DECIMAL(10,3) NOT NULL,               -- para auditoría
    stock_posterior     DECIMAL(10,3) NOT NULL,               -- para auditoría
    id_emple_movi_fk    INT NOT NULL,
    id_produ_movi_fk    INT NOT NULL,
    CONSTRAINT fk_movimiento_empleado FOREIGN KEY (id_emple_movi_fk) REFERENCES empleados(id_empleado_pk),
    CONSTRAINT fk_movimiento_producto FOREIGN KEY (id_produ_movi_fk) REFERENCES productos(id_produ_pk)
);

-- =====================================================
-- DOMICILIOS
-- =====================================================

CREATE TABLE domicilios (
    id_domi_pk        INT AUTO_INCREMENT PRIMARY KEY,
    direc_domi        VARCHAR(100) NOT NULL,
    fecha_domi        DATE NOT NULL,
    hora_entrega_domi TIME NOT NULL,
    estado_domi       ENUM('pendiente', 'en camino', 'entregado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    id_pedido_domi_fk INT NOT NULL,
    id_barrio_domi_fk INT NOT NULL,
    CONSTRAINT fk_domi_pedido FOREIGN KEY (id_pedido_domi_fk) REFERENCES pedidos(id_pedido_pk),
    CONSTRAINT fk_domi_barrio FOREIGN KEY (id_barrio_domi_fk) REFERENCES barrios(id_barrio_pk)
);

-- =====================================================
-- EVENTOS Y MESAS
-- =====================================================

CREATE TABLE mesas_eventos (
    id_mesa_pk   INT AUTO_INCREMENT PRIMARY KEY,
    num_mesa     INT NOT NULL,
    capa_mesa    INT NOT NULL,
    estado_mesa  ENUM('disponible', 'ocupada', 'reservada') NOT NULL DEFAULT 'disponible'
);

CREATE TABLE tipos_eventos (
    id_tipo_evento_pk  INT AUTO_INCREMENT PRIMARY KEY,
    nom_tipo_evento    VARCHAR(30) NOT NULL,
    des_tipo_evento    VARCHAR(100) NOT NULL
);

CREATE TABLE eventos (
    id_evento_pk        INT AUTO_INCREMENT PRIMARY KEY,
    nom_evento          VARCHAR(50) NOT NULL,
    fecha_evento        DATE NOT NULL,
    hora_inicio_evento  TIME NOT NULL,
    hora_fin_evento     TIME NOT NULL,
    ubi_evento          VARCHAR(100) NOT NULL,
    cant_invi_evento    INT NOT NULL,
    estado_evento       ENUM('pendiente', 'en revisión', 'aprobado', 'rechazado', 'programado', 'en progreso', 'finalizado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    id_tipo_evento_fk   INT NOT NULL,
    id_mesa_evento_fk   INT NOT NULL,
    id_pedido_evento_fk INT NOT NULL,
    CONSTRAINT fk_evento_tipo   FOREIGN KEY (id_tipo_evento_fk)   REFERENCES tipos_eventos(id_tipo_evento_pk),
    CONSTRAINT fk_evento_mesa   FOREIGN KEY (id_mesa_evento_fk)   REFERENCES mesas_eventos(id_mesa_pk),
    CONSTRAINT fk_evento_pedido FOREIGN KEY (id_pedido_evento_fk) REFERENCES pedidos(id_pedido_pk)
);

-- =====================================================
-- FACTURACIÓN Y PAGOS
-- =====================================================

CREATE TABLE metodos_pagos (
    id_met_pago_pk INT AUTO_INCREMENT PRIMARY KEY,
    tipo_met_pago  VARCHAR(20) NOT NULL,                      -- ej: efectivo, transferencia, nequi
    des_met_pago   VARCHAR(100)
);

CREATE TABLE facturas (
    id_factu_pk       INT AUTO_INCREMENT PRIMARY KEY,
    fecha_factu       DATE NOT NULL,
    hora_factu        TIME NOT NULL,
    total_factu       DECIMAL(10,2) NOT NULL,
    id_clien_factu_fk INT NOT NULL,
    id_pedido_factu_fk INT NOT NULL,
    CONSTRAINT fk_factura_cliente FOREIGN KEY (id_clien_factu_fk)  REFERENCES clientes(id_clien_pk),
    CONSTRAINT fk_factura_pedido  FOREIGN KEY (id_pedido_factu_fk) REFERENCES pedidos(id_pedido_pk)
);

CREATE TABLE pagos (
    id_pago_pk      INT AUTO_INCREMENT PRIMARY KEY,
    fecha_pago      DATE NOT NULL,
    hora_pago       TIME NOT NULL,
    monto_pago      DECIMAL(10,2) NOT NULL,
    estado_pago     ENUM('pendiente', 'completado', 'rechazado') NOT NULL DEFAULT 'pendiente',
    id_met_pago_fk  INT NOT NULL,
    id_factu_pago_fk INT NULL,
    id_pedido_pago_fk INT NULL,
    CONSTRAINT fk_pago_metodo  FOREIGN KEY (id_met_pago_fk)   REFERENCES metodos_pagos(id_met_pago_pk),
    CONSTRAINT fk_pago_factura FOREIGN KEY (id_factu_pago_fk) REFERENCES facturas(id_factu_pk),
    CONSTRAINT fk_pago_pedido FOREIGN KEY (id_pedido_pago_fk) REFERENCES pedidos(id_pedido_pk)
);

-- =====================================================
-- NOTIFICACIONES
-- Sistema completo de notificaciones por rol y categoría
-- =====================================================

CREATE TABLE notificaciones (
    id_notif_pk         INT AUTO_INCREMENT PRIMARY KEY,

    -- Clasificación de la notificación
    categoria           ENUM(
                            'pedido',           -- nuevo pedido, cambio estado, cancelación
                            'evento',           -- solicitud evento, aprobación, recordatorio
                            'inventario',       -- stock crítico, agotado, entradas, salidas, merma
                            'pago',             -- pago recibido, factura generada
                            'cancelacion',      -- cancelaciones por cliente/empleado/admin
                            'usuario',          -- registro de cliente, inicio/cierre de turno
                            'sistema',          -- reporte diario, alertas automáticas de tiempo
                            'mensaje'           -- mensajes directos entre roles
                        ) NOT NULL,

    -- A quién va dirigida (rol destinatario)
    destinatario_rol    ENUM('admin', 'empleado', 'cliente') NOT NULL,

    -- Usuario específico (NULL = todos los de ese rol)
    id_auth_destino_fk  INT NULL,

    -- Contenido visible
    titulo              VARCHAR(120) NOT NULL,      -- resumen corto: "📦 Nuevo pedido #45 de María"
    mensaje             VARCHAR(500) NOT NULL,      -- detalle completo con contexto

    -- Estado de lectura
    leida               TINYINT(1) DEFAULT 0,
    fecha               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ===== FK opcionales a entidades relacionadas =====
    -- Solo se llena el que corresponda al evento, los demás quedan NULL

    id_pedido_fk        INT NULL,                   -- pedidos, cancelaciones, pagos
    id_producto_fk      INT NULL,                   -- alertas de inventario, stock crítico
    id_evento_fk        INT NULL,                   -- solicitud/aprobación de eventos
    id_factura_fk       INT NULL,                   -- factura generada
    id_movi_fk          INT NULL,                   -- movimiento de inventario (entrada/salida/merma)

    -- Quién originó la notificación (empleado, cliente, o sistema=NULL)
    id_auth_origen_fk   INT NULL,

    -- ===== Constraints =====
    CONSTRAINT fk_notif_destino   FOREIGN KEY (id_auth_destino_fk)  REFERENCES usuarios_auth(id_auth_pk),
    CONSTRAINT fk_notif_origen    FOREIGN KEY (id_auth_origen_fk)   REFERENCES usuarios_auth(id_auth_pk),
    CONSTRAINT fk_notif_pedido    FOREIGN KEY (id_pedido_fk)        REFERENCES pedidos(id_pedido_pk),
    CONSTRAINT fk_notif_producto  FOREIGN KEY (id_producto_fk)      REFERENCES productos(id_produ_pk),
    CONSTRAINT fk_notif_evento    FOREIGN KEY (id_evento_fk)        REFERENCES eventos(id_evento_pk),
    CONSTRAINT fk_notif_factura   FOREIGN KEY (id_factura_fk)       REFERENCES facturas(id_factu_pk),
    CONSTRAINT fk_notif_movi      FOREIGN KEY (id_movi_fk)          REFERENCES movimientos_productos(id_movi_pk),

    -- Índices para consultas rápidas de notificaciones por rol/usuario
    INDEX idx_notif_destino_rol (destinatario_rol, leida, fecha),
    INDEX idx_notif_auth_destino (id_auth_destino_fk, leida, fecha)
);