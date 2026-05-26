USE script_restaurante_u;
-- ========================================
-- DATOS - MENÚ
-- ========================================
INSERT INTO tipos_menus (nom_tipo_menu, des_tipo_menu) VALUES 
('Platos Principales', 'Paellas y platos fuertes'),
('Bebidas', 'Bebidas y vinos'),
('Postres', 'Postres caseros'),
('Aperitivos', 'Tapas y entradas');

-- Platos Principales
INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/paella-valenciana.jpg', 'Paella Valenciana Tradicional', 45000, 'Arroz con pollo, conejo, judías verdes, garrofón y azafrán. Receta tradicional valenciana.', 1, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/paella-mariscos.jpg', 'Paella de Mariscos', 52000, 'Arroz bomba con langostinos, mejillones, calamares, pulpo y azafrán del mediterráneo.', 1, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/paella-mixta.jpg', 'Paella Mixta', 48000, 'Combinación perfecta de carnes y mariscos con arroz bomba y azafrán.', 1, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/arroz-negro.jpg', 'Arroz Negro', 44000, 'Arroz bomba con tinta de calamar, calamares frescos y langostinos.', 1, 1);

-- Bebidas
INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/sandria-roja.jpg', 'Sangría Española', 18000, 'Vino tinto con frutas frescas, canela y especias tradicionales españolas.', 2, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/vino-rioja-crianza.jpg', 'Vino Rioja Crianza', 25000, 'Vino tinto español de la D.O. Rioja. Añejado 12 meses en barrica de roble.', 2, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/cerveza-estrella-galicia.jpg', 'Cerveza Estrella Galicia', 8000, 'Cerveza española premium con sabor tradicional y refrescante.', 2, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/agua.jpg', 'Agua Mineral con Gas', 5000, 'Agua mineral natural con gas, refrescante.', 2, 1);

-- Postres
INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/flan-coco.jpg', 'Flan de Coco', 12000, 'Delicioso flan casero elaborado con coco fresco rallado y caramelo artesanal.', 3, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/crema-catalana.jpg', 'Crema Catalana', 14000, 'Postre tradicional catalán con crema pastelera y azúcar caramelizado.', 3, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/churros-chocolate.jpg', 'Churros con Chocolate', 16000, 'Churros recién fritos acompañados de chocolate caliente espeso.', 3, 1);

-- Aperitivos
INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/tabla-tapas.jpg', 'Tabla de Tapas', 28000, 'Selección de jamón ibérico, quesos manchegos, aceitunas y panes artesanales.', 4, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/gambas-ajillo.jpg', 'Gambas al Ajillo', 22000, 'Langostinos frescos salteados con ajo, guindilla y aceite de oliva.', 4, 1);

INSERT INTO menus (img_menu, nom_menu, precio_menu, des_menu, id_tipo_menu_fk, disponible_menu) 
VALUES ('img/menú/patatas-bravas.jpg', 'Patatas Bravas', 15000, 'Patatas fritas con salsa brava picante y alioli casero.', 4, 1);