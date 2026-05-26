-- =====================================================
-- DATOS INICIALES (roles y métodos de pago)
-- =====================================================

INSERT INTO roles (name) VALUES ('admin'), ('empleado'), ('cliente');

INSERT INTO empleados 
(nom_emple, apellido_emple, fecha_naci_emple, tel_emple, correo_emple, direc_emple, estado_emple, id_auth_fk)
VALUES
('Juan', 'Pérez', '1995-06-15', 3001234567, 'juan.perez@gmail.com', 'Calle 10 #20-30', 'activo', NULL),
('Laura', 'Gómez', '1990-03-22', 3019876543, 'laura.gomez@gmail.com', 'Carrera 15 #45-60', 'inactivo', NULL);

INSERT INTO clientes 
(nom_clien, apellido_clien, fecha_naci_cliente, tel_cliente, correo_clien, direc_clien, estado_clien, id_auth_fk)
VALUES
('Carlos', 'Ramírez', '2000-11-10', 3024567890, 'carlos.ramirez@gmail.com', 'Av 30 #12-50', 'activo', NULL),
('Ana', 'Martínez', '1998-08-05', 3007654321, 'ana.martinez@gmail.com', 'Calle 50 #25-80', 'inactivo', NULL);

INSERT INTO metodos_pagos (tipo_met_pago, des_met_pago) VALUES
    ('efectivo',      'Pago en efectivo al recibir'),
    ('transferencia', 'Transferencia bancaria'),
    ('nequi',         'Pago por Nequi'),
    ('daviplata',     'Pago por Daviplata');

INSERT INTO unidades_medidas (nom_uni_medi, abreviatura, tipo_uni_medi) VALUES
    ('kilogramo',  'kg',  'peso'),
    ('gramo',      'g',   'peso'),
    ('litro',      'L',   'volumen'),
    ('mililitro',  'ml',  'volumen'),
    ('unidad',     'und', 'cantidad'),
    ('porción',    'por', 'cantidad');

INSERT INTO localidades (nom_local, cod_postal_local) VALUES 
('Bogotá', 110111),
('Chapinero', 110221),
('Usaquén', 110111),
('Suba', 111121);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES 
('Chapinero', 1),
('Usaquén', 1),
('Centro', 1),
('Suba Centro', 4),
('La Calleja', 3),
('Santa Bárbara', 3);

INSERT INTO mesas_eventos (num_mesa, capa_mesa, estado_mesa) VALUES
(1, 6, 'disponible'),
(2, 8, 'disponible'),
(3, 10, 'disponible'),
(4, 4, 'ocupada'),
(5, 12, 'reservada');

INSERT INTO tipos_eventos (nom_tipo_evento, des_tipo_evento) VALUES
('Cumpleaños', 'Celebración de cumpleaños'),
('Corporativo', 'Evento empresarial'),
('Boda', 'Celebración de matrimonio'),
('Aniversario', 'Celebración de aniversario'),
('Graduación', 'Celebración de grado académico');

INSERT INTO categorias_productos (nom_cate, des_cate) VALUES
('Carnes', 'Productos cárnicos'),
('Vegetales', 'Verduras y hortalizas'),
('Lacteos', 'Productos lácteos'),
('Bebidas', 'Bebidas y líquidos'),
('Granos', 'Granos y cereales'),
('Condimentos', 'Especias y condimentos'),
('Pescados', 'Productos del mar');

