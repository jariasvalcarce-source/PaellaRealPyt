import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante.settings')
django.setup()

from django.db import connection

sql = """
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('La Candelaria', 3),
    ('Centro Internacional', 3),
    ('Las Aguas', 3),
    ('La Macarena', 3),
    ('Samper Mendoza', 3),
    ('Santa Inés', 3),
    ('Lourdes', 3),
    ('Belén', 3),
    ('Egipto', 3);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('San Cristóbal Sur', 4),
    ('Veinte de Julio', 4),
    ('La Gloria', 4),
    ('Los Libertadores', 4),
    ('San Blas', 4),
    ('Quindío', 4),
    ('La Victoria', 4),
    ('Altamira', 4);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Usme Centro', 5),
    ('Alfonso López', 5),
    ('Comuneros', 5),
    ('Gran Yomasa', 5),
    ('La Flora', 5),
    ('Parques Entrenubes', 5);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Tunjuelito', 6),
    ('Abraham Lincoln', 6),
    ('Venecia', 6),
    ('San Benito', 6),
    ('El Tunal', 6),
    ('Fátima', 6);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Bosa Centro', 7),
    ('Bosa Occidental', 7),
    ('Bosa Oriental', 7),
    ('El Porvenir', 7),
    ('Apogeo', 7),
    ('San Pablo', 7),
    ('Los Laureles', 7),
    ('La Libertad', 7);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Fontibón Centro', 9),
    ('Fontibón San Pablo', 9),
    ('Modelia', 9),
    ('Capellanía', 9),
    ('Granjas de Techo', 9),
    ('Ciudad Salitre', 9),
    ('Versalles', 9),
    ('San José de Fontibón', 9);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
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

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Barrios Unidos', 12),
    ('Doce de Octubre', 12),
    ('Los Andes', 12),
    ('Alcázares', 12),
    ('Columbia', 12),
    ('Polo Club', 12),
    ('Benjamín Herrera', 12),
    ('Jorge Eliécer Gaitán', 12);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Teusaquillo', 13),
    ('Palermo', 13),
    ('Galerías', 13),
    ('Soledad', 13),
    ('Armenia', 13),
    ('Quesada', 13),
    ('La Esmeralda', 13),
    ('Nicolás de Federmann', 13),
    ('Ciudad Universitaria', 13);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('La Pepita', 14),
    ('El Listón', 14),
    ('Ricaurte', 14),
    ('La Favorita', 14),
    ('Eduardo Santos', 14),
    ('El Vergel', 14);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Antonio Nariño', 15),
    ('Ciudad Jardín Sur', 15),
    ('Restrepo', 15),
    ('Santander', 15),
    ('Sevilla', 15),
    ('Luna Park', 15);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Puente Aranda', 16),
    ('Comuneros', 16),
    ('Galán', 16),
    ('Muzú', 16),
    ('Primavera', 16),
    ('San Rafael', 16),
    ('Zona Industrial', 16);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('La Candelaria Centro', 17),
    ('Girardot', 17),
    ('Las Aguas', 17),
    ('Egipto', 17);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Diana Turbay', 18),
    ('Marruecos', 18),
    ('Quiroga', 18),
    ('Sosiego', 18),
    ('Venecia', 18),
    ('Marco Fidel Suárez', 18),
    ('San Agustín', 18);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Arborizadora', 19),
    ('El Paraíso', 19),
    ('Ieragua', 19),
    ('Lucero', 19),
    ('Perdomo', 19),
    ('San Francisco', 19),
    ('Tesoro', 19),
    ('Turquía', 19);

INSERT INTO barrios (nom_barrio, id_local_barrio_fk_id) VALUES
    ('Sumapaz Centro', 20),
    ('Nazareth', 20),
    ('Betania', 20);
"""

with connection.cursor() as cursor:
    for statement in sql.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Error executing: {statement[:50]}... -> {e}")
print("Finished running SQL.")
