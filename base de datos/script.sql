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
    id_role_fk       INT NOT NULL,
    activo           TINYINT(1) DEFAULT 1,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auth_role FOREIGN KEY (id_role_fk) REFERENCES roles(id_role_pk)
);
SELECT * FROM usuarios_auth;
SELECT * FROM roles;
-- =====================================================
-- PERSONAS: EMPLEADOS Y CLIENTES
-- =====================================================

CREATE TABLE empleados (
    id_emple_pk      INT AUTO_INCREMENT PRIMARY KEY,
    nom_emple        VARCHAR(25) NOT NULL,
    apellido_emple   VARCHAR(30) NOT NULL,
    fecha_naci_emple DATE NOT NULL,
    tel_emple        BIGINT UNSIGNED NOT NULL,       
    correo_emple     VARCHAR(40) NOT NULL,
    direc_emple      VARCHAR(100) NOT NULL,
    estado_emple     ENUM('activo', 'inactivo') NOT NULL,
    id_auth_fk       INT UNIQUE,
    CONSTRAINT fk_empleado_auth FOREIGN KEY (id_auth_fk) REFERENCES usuarios_auth(id_auth_pk)
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
    id_provee_pk       INT AUTO_INCREMENT PRIMARY KEY,
    nom_provee         VARCHAR(25) NOT NULL,
    apellido_provee    VARCHAR(30),
    fecha_naci_provee  DATE,
    tel_provee         BIGINT UNSIGNED NOT NULL,
    correo_provee      VARCHAR(40) NOT NULL,
    direc_provee       VARCHAR(100) NOT NULL,
    estado_provee      ENUM('activo', 'inactivo') NOT NULL
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
    cantidad_reque  DECIMAL(10,3) NOT NULL,                  -- cuánto se necesita por porción
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
    CONSTRAINT fk_pedido_cliente  FOREIGN KEY (id_clien_pedido_fk) REFERENCES clientes(id_clien_pk),
    CONSTRAINT fk_pedido_empleado FOREIGN KEY (id_emple_pedido_fk) REFERENCES empleados(id_emple_pk)
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
-- CONSUMOS POR PEDIDO (TABLA NUEVA)
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
    CONSTRAINT fk_movimiento_empleado FOREIGN KEY (id_emple_movi_fk) REFERENCES empleados(id_emple_pk),
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
    estado_domi       ENUM('pendiente', 'en camino', 'entregado') NOT NULL DEFAULT 'pendiente',
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
    id_factu_pago_fk INT NOT NULL,
    CONSTRAINT fk_pago_metodo  FOREIGN KEY (id_met_pago_fk)   REFERENCES metodos_pagos(id_met_pago_pk),
    CONSTRAINT fk_pago_factura FOREIGN KEY (id_factu_pago_fk) REFERENCES facturas(id_factu_pk)
);