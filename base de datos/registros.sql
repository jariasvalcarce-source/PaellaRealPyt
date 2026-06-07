-- =====================================================
-- DATOS INICIALES (roles y métodos de pago)
-- =====================================================

INSERT INTO roles (name) VALUES ('admin'), ('empleado'), ('cliente');

INSERT INTO tipos_menus (nom_tipo_menu, des_tipo_menu) VALUES
    ('Paellas',    'Platos principales de arroz tipo paella'),
    ('Bebidas',    'Bebidas frías, calientes y vinos'),
    ('Postres',    'Postres dulces y caseros'),
    ('Aperitivos', 'Entradas y tapas para compartir');

-- =====================
-- UNIDADES DE MEDIDA
-- =====================

INSERT INTO unidades_medidas (nom_uni_medi, abreviatura, tipo_uni_medi) VALUES
    ('kilogramo', 'kg',  'peso'),
    ('gramo',     'g',   'peso'),
    ('litro',     'L',   'volumen'),
    ('mililitro', 'ml',  'volumen'),
    ('unidad',    'und', 'cantidad');

-- =====================
-- CATEGORÍAS DE PRODUCTOS
-- =====================    

INSERT INTO categorias_productos (nom_cate, des_cate) VALUES
    ('Carnes',      'Productos cárnicos'),
    ('Mariscos',    'Productos del mar'),
    ('Vegetales',   'Verduras y hortalizas'),
    ('Granos',      'Arroces y cereales'),
    ('Condimentos', 'Especias y sazonadores'),
    ('Lacteos',     'Productos lácteos'),
    ('Bebidas',     'Líquidos y bebidas');

-- =====================
-- MÉTODOS DE PAGO
-- =====================    

INSERT INTO metodos_pagos (tipo_met_pago, des_met_pago) VALUES
    ('efectivo',      'Pago en efectivo al recibir'),
    ('transferencia', 'Transferencia bancaria'),
    ('nequi',         'Pago por Nequi'),
    ('daviplata',     'Pago por Daviplata');

-- =====================
-- MESAS Y EVENTOS
-- =====================    

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

-- =====================
-- LOCALIDADES
-- =====================

INSERT INTO localidades (nom_local, cod_postal_local) VALUES 
    ('Usaquén', 110111),
    ('Chapinero', 110211),
    ('Santa Fe', 110311),
    ('San Cristóbal', 110411),
    ('Usme', 110511),
    ('Tunjuelito', 110611),
    ('Bosa', 110711),
    ('Kennedy', 110811),
    ('Fontibón', 110911),
    ('Engativá', 111011),
    ('Suba', 111111),
    ('Barrios Unidos', 111211),
    ('Teusaquillo', 111311),
    ('Los Mártires', 111411),
    ('Antonio Nariño', 111511),
    ('Puente Aranda', 111611),
    ('La Candelaria', 111711),
    ('Rafael Uribe Uribe', 111811),
    ('Ciudad Bolívar', 111911),
    ('Sumapaz', 112011);

-- =====================
-- 1. USAQUÉN
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Usaquén', 1),
    ('Santa Bárbara', 1),
    ('Santa Bárbara Oriental', 1),
    ('Country Club', 1),
    ('La Calleja', 1),
    ('Cedritos', 1),
    ('Bella Suiza', 1),
    ('Niza', 1),
    ('San Patricio', 1),
    ('Toberín', 1),
    ('Los Cedros', 1),
    ('Barrancas', 1),
    ('Verbenal', 1),
    ('La Uribe', 1),
    ('San Cristóbal Norte', 1);

-- =====================
-- 2. CHAPINERO
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Chapinero Central', 2),
    ('Chapinero Alto', 2),
    ('El Lago', 2),
    ('Quinta Camacho', 2),
    ('Rosales', 2),
    ('El Refugio', 2),
    ('La Cabrera', 2),
    ('Chicó Norte', 2),
    ('Chicó Reservado', 2),
    ('Nogal', 2),
    ('Pardo Rubio', 2),
    ('Belén', 2),
    ('Granada', 2),
    ('San Martín', 2);

-- =====================
-- 3. SANTA FE
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('La Candelaria', 3),
    ('Centro Internacional', 3),
    ('Las Aguas', 3),
    ('La Macarena', 3),
    ('Samper Mendoza', 3),
    ('Santa Inés', 3),
    ('Lourdes', 3),
    ('Belén', 3),
    ('Egipto', 3);

-- =====================
-- 4. SAN CRISTÓBAL
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('San Cristóbal Sur', 4),
    ('Veinte de Julio', 4),
    ('La Gloria', 4),
    ('Los Libertadores', 4),
    ('San Blas', 4),
    ('Quindío', 4),
    ('La Victoria', 4),
    ('Altamira', 4);

-- =====================
-- 5. USME
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Usme Centro', 5),
    ('Alfonso López', 5),
    ('Comuneros', 5),
    ('Gran Yomasa', 5),
    ('La Flora', 5),
    ('Parques Entrenubes', 5);

-- =====================
-- 6. TUNJUELITO
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Tunjuelito', 6),
    ('Abraham Lincoln', 6),
    ('Venecia', 6),
    ('San Benito', 6),
    ('El Tunal', 6),
    ('Fátima', 6);

-- =====================
-- 7. BOSA
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Bosa Centro', 7),
    ('Bosa Occidental', 7),
    ('Bosa Oriental', 7),
    ('El Porvenir', 7),
    ('Apogeo', 7),
    ('San Pablo', 7),
    ('Los Laureles', 7),
    ('La Libertad', 7);

-- =====================
-- 8. KENNEDY
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Kennedy Central', 8),
    ('Américas', 8),
    ('Carvajal', 8),
    ('Castilla', 8),
    ('Gran Britalia', 8),
    ('Patio Bonito', 8),
    ('Timiza', 8),
    ('Tintal', 8),
    ('Corabastos', 8),
    ('Bavaria', 8),
    ('Marsella', 8),
    ('Alquería', 8);

-- =====================
-- 9. FONTIBÓN
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Fontibón Centro', 9),
    ('Fontibón San Pablo', 9),
    ('Modelia', 9),
    ('Capellanía', 9),
    ('Granjas de Techo', 9),
    ('Ciudad Salitre', 9),
    ('Versalles', 9),
    ('San José de Fontibón', 9);

-- =====================
-- 10. ENGATIVÁ
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Engativá', 10),
    ('Álamos', 10),
    ('Bolivia', 10),
    ('Boyacá Real', 10),
    ('El Cortijo', 10),
    ('Garcés Navas', 10),
    ('Jardín Botánico', 10),
    ('Las Ferias', 10),
    ('Minuto de Dios', 10),
    ('Santa Cecilia', 10),
    ('Tabora', 10),
    ('Villa Amalia', 10);

-- =====================
-- 11. SUBA
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Suba Centro', 11),
    ('Alhambra', 11),
    ('Casa Blanca Suba', 11),
    ('Britalia', 11),
    ('El Prado', 11),
    ('La Alambra', 11),
    ('La Gaitana', 11),
    ('Lisboa', 11),
    ('Niza', 11),
    ('Rincón', 11),
    ('San José del Prado', 11),
    ('Tibabuyes', 11),
    ('Villa del Prado', 11),
    ('Compartir', 11),
    ('Aures', 11);

-- =====================
-- 12. BARRIOS UNIDOS
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Barrios Unidos', 12),
    ('Doce de Octubre', 12),
    ('Los Andes', 12),
    ('Alcázares', 12),
    ('Columbia', 12),
    ('Polo Club', 12),
    ('Benjamín Herrera', 12),
    ('Jorge Eliécer Gaitán', 12);

-- =====================
-- 13. TEUSAQUILLO
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Teusaquillo', 13),
    ('Palermo', 13),
    ('Galerías', 13),
    ('Soledad', 13),
    ('Armenia', 13),
    ('Quesada', 13),
    ('La Esmeralda', 13),
    ('Nicolás de Federmann', 13),
    ('Ciudad Universitaria', 13);

-- =====================
-- 14. LOS MÁRTIRES
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('La Pepita', 14),
    ('El Listón', 14),
    ('Ricaurte', 14),
    ('La Favorita', 14),
    ('Eduardo Santos', 14),
    ('El Vergel', 14);

-- =====================
-- 15. ANTONIO NARIÑO
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Antonio Nariño', 15),
    ('Ciudad Jardín Sur', 15),
    ('Restrepo', 15),
    ('Santander', 15),
    ('Sevilla', 15),
    ('Luna Park', 15);

-- =====================
-- 16. PUENTE ARANDA
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Puente Aranda', 16),
    ('Comuneros', 16),
    ('Galán', 16),
    ('Muzú', 16),
    ('Primavera', 16),
    ('San Rafael', 16),
    ('Zona Industrial', 16);

-- =====================
-- 17. LA CANDELARIA
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('La Candelaria Centro', 17),
    ('Girardot', 17),
    ('Las Aguas', 17),
    ('Egipto', 17);

-- =====================
-- 18. RAFAEL URIBE URIBE
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Diana Turbay', 18),
    ('Marruecos', 18),
    ('Quiroga', 18),
    ('Sosiego', 18),
    ('Venecia', 18),
    ('Marco Fidel Suárez', 18),
    ('San Agustín', 18);

-- =====================
-- 19. CIUDAD BOLÍVAR
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Arborizadora', 19),
    ('El Paraíso', 19),
    ('Ieragua', 19),
    ('Lucero', 19),
    ('Perdomo', 19),
    ('San Francisco', 19),
    ('Tesoro', 19),
    ('Turquía', 19);

-- =====================
-- 20. SUMAPAZ
-- =====================
INSERT INTO barrios (nom_barrio, id_local_barrio_fk) VALUES
    ('Sumapaz Centro', 20),
    ('Nazareth', 20),
    ('Betania', 20);

-- =====================================================
-- PRODUCTOS
-- =====================================================

INSERT INTO productos (nom_produ, stock_actual_produ, stock_minimo_produ, fecha_venci_produ, precio_uni_produ, des_produ, estado_produ, id_provee_produ_fk, id_uni_medi_produ_fk, id_cate_produ_fk) VALUES
    -- CARNES (id_cate=1) | unidad: kg(1)
    ('Pollo Fresco',    15,  5,   '2026-05-20', 12000,  'Pollo fresco de granja para paellas',            'disponible', 2,  1, 1),
    ('Conejo Fresco',   6,   2,   '2026-05-18', 25000,  'Conejo fresco para paella valenciana',           'disponible', 2,  1, 1),
    ('Jamón Serrano',   3,   1,   '2026-12-31', 85000,  'Jamón serrano español premium',                  'disponible', 3,  1, 1),

    -- MARISCOS (id_cate=2) | unidad: kg(1)
    ('Langostinos',     22,  8,   '2026-05-15', 85000,  'Langostinos frescos del Pacífico',               'disponible', 9,  1, 2),
    ('Mejillones',      35,  8,   '2026-05-14', 45000,  'Mejillones frescos en concha',                   'disponible', 9,  1, 2),
    ('Calamares',       13,  5,   '2026-05-16', 55000,  'Calamares frescos limpios',                      'disponible', 9,  1, 2),
    ('Pulpo',           3,   1,   '2026-05-17', 95000,  'Pulpo fresco del Pacífico',                      'disponible', 9,  1, 2),
    ('Tinta de Calamar',0.3, 0.1, '2026-09-30', 125000, 'Tinta de calamar natural',                       'disponible', 9,  1, 2),

    -- VEGETALES (id_cate=3) | unidad: kg(1)
    ('Judías Verdes',   3,   1,   '2026-05-25', 5500,   'Judías verdes frescas',                          'disponible', 6,  1, 3),
    ('Tomate',          15,  5,   '2026-05-22', 3800,   'Tomate chonto fresco',                           'disponible', 6,  1, 3),
    ('Ajo',             3,   1,   '2026-07-30', 12000,  'Ajo fresco pelado',                              'disponible', 6,  1, 3),
    ('Papa',            9,   3,   '2026-06-15', 2500,   'Papa criolla colombiana',                        'disponible', 6,  1, 3),
    ('Ají',             2,   0.5, '2026-05-20', 8500,   'Ají dulce fresco',                               'disponible', 6,  1, 3),
    ('Aceitunas',       0.03,0.005,'2027-03-31', 18000,  'Aceitunas verdes españolas',                    'disponible', 7,  1, 3),
    ('Fruta Mixta',     15,  5,   '2026-05-18', 6500,   'Mezcla de frutas frescas de temporada',          'disponible', 6,  1, 3),
    ('Pimentón',        2,   0.5, '2026-09-30', 15000,  'Pimentón dulce español',                         'disponible', 7,  1, 3),

    -- GRANOS (id_cate=4) | unidad: kg(1)
    ('Arroz Bomba',     72,  20,  '2027-12-31', 8500,   'Arroz bomba español para paellas',               'disponible', 4,  1, 4),
    ('Harina de Trigo', 22,  6,   '2026-10-30', 3500,   'Harina de trigo todo uso',                       'disponible', 5,  1, 4),
    ('Pan Baguette',    3,   1,   '2026-05-10', 4500,   'Pan baguette francés fresco',                    'disponible', 5,  1, 4),

    -- CONDIMENTOS (id_cate=5) | unidad: kg(1) salvo aceite(L=3) y vainilla(ml=4)
    ('Azafrán',         0.5, 0.1, '2026-12-31', 450000, 'Azafrán español en hebras puro',                 'disponible', 7,  1, 5),
    ('Sal Marina',      3,   1,   '2028-12-31', 2500,   'Sal marina gruesa',                              'disponible', 8,  1, 5),
    ('Azúcar',          12,  4,   '2027-06-30', 3200,   'Azúcar blanca refinada',                         'disponible', 8,  1, 5),
    ('Canela',          1,   0.3, '2026-11-30', 22000,  'Canela en rama de Ceilán',                       'disponible', 7,  1, 5),
    ('Maicena',         3,   1,   '2027-04-30', 4500,   'Fécula de maíz',                                 'disponible', 8,  1, 5),
    ('Esencia de Vainilla', 0.01,0.002,'2026-08-31',35000,'Esencia pura de vainilla',                     'disponible', 8,  4, 5),
    ('Aceite de Oliva', 50,  15,  '2027-01-31', 45000,  'Aceite de oliva extra virgen español',           'disponible', 8,  3, 5),
    ('Chocolate',       15,  5,   '2026-10-31', 28000,  'Chocolate oscuro 70% cacao',                     'disponible', 8,  1, 5),
    ('Coco Rallado',    10,  3,   '2026-07-31', 18000,  'Coco rallado deshidratado',                      'disponible', 7,  1, 5),
    ('Mayonesa',        0.02,0.005,'2026-06-30', 8500,  'Mayonesa tradicional',                           'disponible', 8,  1, 5),

    -- LACTEOS (id_cate=6) | leche y crema: L(3) | huevo: und(5) | queso: kg(1)
    ('Leche Entera',    30,  10,  '2026-05-20', 4500,   'Leche entera pasteurizada',                      'disponible', 11, 3, 6),
    ('Crema de Leche',  12,  4,   '2026-05-18', 8500,   'Crema de leche espesa',                          'disponible', 11, 3, 6),
    ('Huevo',           120, 40,  '2026-05-30', 650,    'Huevo AA fresco',                                'disponible', 11, 5, 6),
    ('Queso',           4,   1.5, '2026-06-15', 38000,  'Queso parmesano rallado',                        'disponible', 11, 1, 6),

    -- BEBIDAS (id_cate=7) | vino y jugos: L(3) | agua y cerveza: und(5)
    ('Vino Tinto',      15,  5,   '2028-12-31', 35000,  'Vino tinto Rioja reserva',                       'disponible', 10, 3, 7),
    ('Jugo de Naranja', 6,   2,   '2026-05-25', 8500,   'Jugo de naranja natural',                        'disponible', 10, 3, 7),
    ('Agua Mineral',    7,   2,   '2027-12-31', 2500,   'Agua mineral sin gas',                           'disponible', 10, 5, 7),
    ('Cerveza',         100, 30,  '2026-12-31', 3500,   'Cerveza lager nacional',                         'disponible', 10, 5, 7);
    
-- =====================================================
-- RECETAS
-- =====================================================
SELECT id_produ_pk, nom_produ FROM productos ORDER BY id_produ_pk;
-- =====================================================
-- MENÚ 1: PAELLA VALENCIANA TRADICIONAL
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (1, 39, 300, 2, 'cortado en trozos medianos, sin piel en exceso, se sofríe al inicio hasta dorar'),
    (1, 40, 200, 2, 'cortado en trozos pequeños, se cocina junto con el pollo hasta dorar'),
    (1, 55, 200, 2, 'se añade después del sofrito, distribuir uniformemente, no revolver durante cocción'),
    (1, 47, 100, 2, 'limpias y cortadas en trozos, se sofríen con las carnes para liberar sabor'),
    (1, 48, 80,  2, 'triturado, se cocina hasta que reduzca y concentre su sabor'),
    (1, 49, 10,  2, 'picado finamente, se añade antes del tomate para aromatizar'),
    (1, 58, 5,   2, 'disuelto previamente en caldo caliente, da color y aroma característico'),
    (1, 59, 5,   2, 'se añade al gusto durante la cocción para equilibrar sabores'),
    (1, 64, 50,  4, 'se utiliza al inicio para sofreír las carnes y verduras, base fundamental');

-- =====================================================
-- MENÚ 2: PAELLA DE MARISCOS
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (2, 42, 200, 2, 'limpios y sin cáscara, se saltean ligeramente al inicio para sellar su sabor'),
    (2, 43, 150, 2, 'previamente lavados y sin impurezas, se añaden durante cocción para que se abran'),
    (2, 44, 150, 2, 'cortados en rodajas, se sofríen al inicio junto con los langostinos'),
    (2, 45, 100, 2, 'cocido previamente y cortado en trozos pequeños, aporta textura y sabor'),
    (2, 55, 200, 2, 'se agrega después del sofrito, distribuir uniformemente, no revolver durante cocción'),
    (2, 48, 80,  2, 'triturado, se añade al sofrito para formar la base del sabor'),
    (2, 49, 10,  2, 'picado finamente, se incorpora al inicio del sofrito para aromatizar el aceite'),
    (2, 58, 5,   2, 'disuelto en caldo caliente, da color y aroma característico al arroz'),
    (2, 59, 5,   2, 'se agrega al gusto durante la cocción para resaltar los sabores del mar'),
    (2, 64, 50,  4, 'se utiliza para sofreír los mariscos y preparar la base del plato');

-- =====================================================
-- MENÚ 3: PAELLA MIXTA
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (3, 39, 200, 2, 'cortado en trozos medianos, se sofríe al inicio hasta dorar para sellar y aportar sabor'),
    (3, 42, 150, 2, 'limpios y sin cáscara, se saltean ligeramente junto con el pollo'),
    (3, 44, 120, 2, 'cortados en rodajas, se sofríen junto con los demás ingredientes'),
    (3, 55, 200, 2, 'se añade después del sofrito, distribuir uniformemente, no revolver durante cocción'),
    (3, 48, 80,  2, 'triturado, se incorpora al sofrito para crear la base del sabor'),
    (3, 54, 50,  2, 'cortado en tiras o trozos pequeños, se añade al sofrito para dar color y sabor'),
    (3, 49, 10,  2, 'picado finamente, se agrega al inicio del sofrito para aromatizar'),
    (3, 58, 5,   2, 'disuelto en caldo caliente, se incorpora al arroz para dar color y aroma'),
    (3, 59, 5,   2, 'se añade al gusto durante la cocción para equilibrar los sabores'),
    (3, 64, 50,  4, 'se utiliza para sofreír todos los ingredientes y formar la base del plato');

-- =====================================================
-- MENÚ 4: ARROZ NEGRO
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (4, 44, 180, 2, 'limpios y cortados en rodajas, se sofríen al inicio para aportar el sabor principal'),
    (4, 42, 150, 2, 'pelados y limpios, se saltean ligeramente junto con los calamares'),
    (4, 55, 200, 2, 'se añade después del sofrito, distribuir uniformemente, no revolver durante cocción'),
    (4, 46, 10,  2, 'se disuelve en el caldo, da el color negro característico y sabor intenso'),
    (4, 48, 80,  2, 'triturado, base del sofrito para aportar acidez y cuerpo'),
    (4, 49, 10,  2, 'picado finamente, se añade al inicio para aromatizar el aceite'),
    (4, 59, 5,   2, 'se agrega al gusto durante la cocción'),
    (4, 64, 50,  4, 'se utiliza para sofreír los ingredientes y formar la base del plato');

-- =====================================================
-- MENÚ 5: SANGRÍA ESPAÑOLA
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (5, 72, 250, 4, 'base principal de la bebida, se utiliza frío para dar el sabor característico'),
    (5, 73, 100, 4, 'se añade para aportar frescura y un toque cítrico que equilibra el vino'),
    (5, 74, 50,  4, 'se incorpora para suavizar la mezcla y darle un toque refrescante'),
    (5, 60, 10,  2, 'se disuelve en la mezcla para endulzar al gusto'),
    (5, 61, 2,   2, 'se añade en rama o en polvo para aromatizar la bebida'),
    (5, 53, 100, 2, 'naranja o limón en rodajas, dan sabor y presentación');

-- =====================================================
-- MENÚ 6: VINO RIOJA CRIANZA
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (6, 72, 250, 4, 'se sirve directamente, previamente conservado a temperatura adecuada para resaltar sus propiedades');

-- =====================================================
-- MENÚ 7: CERVEZA ESTRELLA GALICIA
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (7, 75, 1, 5, 'bebida lista para consumo, se utiliza directamente desde su envase, 330ml');

-- =====================================================
-- MENÚ 8: AGUA MINERAL CON GAS
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (8, 74, 1, 5, 'bebida lista para consumo, con gas natural o añadido, 500ml');

-- =====================================================
-- MENÚ 9: FLAN DE COCO
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (9, 68, 250, 4, 'base principal del flan, se utiliza para formar la mezcla líquida'),
    (9, 69, 100, 4, 'se añade para dar una textura más cremosa y suave al flan'),
    (9, 70, 2,   5, 'da consistencia y permite que el flan cuaje al cocinarse'),
    (9, 60, 50,  2, 'se utiliza tanto para la mezcla como para preparar el caramelo'),
    (9, 66, 80,  2, 'ingrediente principal que aporta el sabor característico del postre');

-- =====================================================
-- MENÚ 10: CREMA CATALANA
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (10, 68, 250, 4, 'base principal de la crema, se calienta para infusionar sabores'),
    (10, 69, 100, 4, 'aporta una textura más suave y cremosa'),
    (10, 70, 2,   5, 'se utilizan principalmente las yemas para espesar y dar consistencia'),
    (10, 60, 40,  2, 'se usa para endulzar y también para formar la capa caramelizada en superficie'),
    (10, 62, 10,  2, 'se disuelve en un poco de leche fría para espesar la preparación'),
    (10, 61, 2,   2, 'se utiliza para aromatizar la leche durante la cocción'),
    (10, 63, 5,   4, 'aromatizante, se incorpora junto con la canela durante la infusión');

-- =====================================================
-- MENÚ 11: CHURROS CON CHOCOLATE
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (11, 56, 150, 2, 'base de la masa, se mezcla con agua para formar la consistencia de los churros'),
    (11, 59, 2,   2, 'se añade a la masa para equilibrar el sabor'),
    (11, 64, 500, 4, 'se utiliza para freír los churros hasta que queden dorados y crujientes'),
    (11, 60, 50,  2, '30g se espolvorean sobre los churros fritos, 20g para endulzar el chocolate'),
    (11, 68, 250, 4, 'base del chocolate caliente para acompañar los churros'),
    (11, 65, 100, 2, 'se derrite en la leche para formar la bebida espesa'),
    (11, 62, 10,  2, 'se utiliza para espesar el chocolate y darle textura cremosa');

-- =====================================================
-- MENÚ 12: TABLA DE TAPAS
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (12, 41, 100, 2, 'cortado en lonjas finas, se sirve directamente como parte principal de la tabla'),
    (12, 71, 120, 2, 'cortado en cubos o láminas, se utiliza para acompañar el jamón'),
    (12, 52, 80,  2, 'se sirven enteras como complemento salado'),
    (12, 57, 150, 2, 'cortado en rebanadas, se sirve como acompañamiento base');

-- =====================================================
-- MENÚ 13: GAMBAS AL AJILLO
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (13, 42, 200, 2, 'limpios y pelados, son el ingrediente principal, se cocinan rápidamente'),
    (13, 49, 15,  2, 'picado en láminas, se sofríe para aromatizar el aceite'),
    (13, 64, 50,  4, 'base de la cocción, donde se sofríen todos los ingredientes'),
    (13, 59, 3,   2, 'se añade al gusto para resaltar sabores'),
    (13, 51, 5,   2, 'picado, se incorpora para dar un toque picante');

-- =====================================================
-- MENÚ 14: PATATAS BRAVAS
-- =====================================================
INSERT INTO recetas_menus (id_menu_fk, id_produ_fk, cantidad_reque, id_uni_medi_fk, notas) VALUES
    (14, 50, 300, 2, 'cortada en cubos medianos, se fríe hasta quedar dorada y crujiente'),
    (14, 64, 300, 4, 'se utiliza para freír las papas'),
    (14, 48, 100, 2, 'triturado, base de la salsa brava para aportar acidez y cuerpo'),
    (14, 49, 10,  2, 'picado, se usa para dar sabor a la salsa brava'),
    (14, 59, 5,   2, 'se añade al gusto'),
    (14, 51, 5,   2, 'aporta el picante característico de la salsa brava'),
    (14, 67, 50,  2, 'se utiliza para preparar el alioli');
