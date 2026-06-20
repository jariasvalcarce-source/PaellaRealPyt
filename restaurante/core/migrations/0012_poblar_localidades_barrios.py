from django.db import migrations

def poblar_datos(apps, schema_editor):
    Localidad = apps.get_model('core', 'Localidad')
    Barrio = apps.get_model('core', 'Barrio')
    
    localidades_data = [
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
        ('Sumapaz', 112011)
    ]
    
    localidades_objs = []
    for i, (nom, cp) in enumerate(localidades_data, start=1):
        if not Localidad.objects.filter(nom_local=nom).exists():
            localidades_objs.append(Localidad(id_local_pk=i, nom_local=nom, cod_postal_local=str(cp)))
            
    if localidades_objs:
        Localidad.objects.bulk_create(localidades_objs, ignore_conflicts=True)
        
    barrios_data = [
        # 1. USAQUÉN
        (1, ['Usaquén', 'Santa Bárbara', 'Santa Bárbara Oriental', 'Country Club', 'La Calleja', 'Cedritos', 'Bella Suiza', 'Niza', 'San Patricio', 'Toberín', 'Los Cedros', 'Barrancas', 'Verbenal', 'La Uribe', 'San Cristóbal Norte']),
        # 2. CHAPINERO
        (2, ['Chapinero Central', 'Chapinero Alto', 'El Lago', 'Quinta Camacho', 'Rosales', 'El Refugio', 'La Cabrera', 'Chicó Norte', 'Chicó Reservado', 'Nogal', 'Pardo Rubio', 'Belén', 'Granada', 'San Martín']),
        # 3. SANTA FE
        (3, ['La Candelaria', 'Centro Internacional', 'Las Aguas', 'La Macarena', 'Samper Mendoza', 'Santa Inés', 'Lourdes', 'Belén', 'Egipto']),
        # 4. SAN CRISTÓBAL
        (4, ['San Cristóbal Sur', 'Veinte de Julio', 'La Gloria', 'Los Libertadores', 'San Blas', 'Quindío', 'La Victoria', 'Altamira']),
        # 5. USME
        (5, ['Usme Centro', 'Alfonso López', 'Comuneros', 'Gran Yomasa', 'La Flora', 'Parques Entrenubes']),
        # 6. TUNJUELITO
        (6, ['Tunjuelito', 'Abraham Lincoln', 'Venecia', 'San Benito', 'El Tunal', 'Fátima']),
        # 7. BOSA
        (7, ['Bosa Centro', 'Bosa Occidental', 'Bosa Oriental', 'El Porvenir', 'Apogeo', 'San Pablo', 'Los Laureles', 'La Libertad']),
        # 8. KENNEDY
        (8, ['Kennedy Central', 'Américas', 'Carvajal', 'Castilla', 'Gran Britalia', 'Patio Bonito', 'Timiza', 'Tintal', 'Corabastos', 'Bavaria', 'Marsella', 'Alquería']),
        # 9. FONTIBÓN
        (9, ['Fontibón Centro', 'Fontibón San Pablo', 'Modelia', 'Capellanía', 'Granjas de Techo', 'Ciudad Salitre', 'Versalles', 'San José de Fontibón']),
        # 10. ENGATIVÁ
        (10, ['Engativá', 'Álamos', 'Bolivia', 'Boyacá Real', 'El Cortijo', 'Garcés Navas', 'Jardín Botánico', 'Las Ferias', 'Minuto de Dios', 'Santa Cecilia', 'Tabora', 'Villa Amalia']),
        # 11. SUBA
        (11, ['Suba Centro', 'Alhambra', 'Casa Blanca Suba', 'Britalia', 'El Prado', 'La Alambra', 'La Gaitana', 'Lisboa', 'Niza', 'Rincón', 'San José del Prado', 'Tibabuyes', 'Villa del Prado', 'Compartir', 'Aures']),
        # 12. BARRIOS UNIDOS
        (12, ['Barrios Unidos', 'Doce de Octubre', 'Los Andes', 'Alcázares', 'Columbia', 'Polo Club', 'Benjamín Herrera', 'Jorge Eliécer Gaitán']),
        # 13. TEUSAQUILLO
        (13, ['Teusaquillo', 'Palermo', 'Galerías', 'Soledad', 'Armenia', 'Quesada', 'La Esmeralda', 'Nicolás de Federmann', 'Ciudad Universitaria']),
        # 14. LOS MÁRTIRES
        (14, ['La Pepita', 'El Listón', 'Ricaurte', 'La Favorita', 'Eduardo Santos', 'El Vergel']),
        # 15. ANTONIO NARIÑO
        (15, ['Antonio Nariño', 'Ciudad Jardín Sur', 'Restrepo', 'Santander', 'Sevilla', 'Luna Park']),
        # 16. PUENTE ARANDA
        (16, ['Puente Aranda', 'Comuneros', 'Galán', 'Muzú', 'Primavera', 'San Rafael', 'Zona Industrial']),
        # 17. LA CANDELARIA
        (17, ['La Candelaria Centro', 'Girardot', 'Las Aguas', 'Egipto']),
        # 18. RAFAEL URIBE URIBE
        (18, ['Diana Turbay', 'Marruecos', 'Quiroga', 'Sosiego', 'Venecia', 'Marco Fidel Suárez', 'San Agustín']),
        # 19. CIUDAD BOLÍVAR
        (19, ['Arborizadora', 'El Paraíso', 'Ieragua', 'Lucero', 'Perdomo', 'San Francisco', 'Tesoro', 'Turquía']),
        # 20. SUMAPAZ
        (20, ['Sumapaz Centro', 'Nazareth', 'Betania']),
    ]
    
    barrios_objs = []
    for loc_id, barrios in barrios_data:
        loc = Localidad.objects.filter(id_local_pk=loc_id).first()
        if loc:
            for b in barrios:
                if not Barrio.objects.filter(nom_barrio=b, id_local_barrio_fk_id=loc_id).exists():
                    barrios_objs.append(Barrio(nom_barrio=b, id_local_barrio_fk=loc))
                    
    if barrios_objs:
        Barrio.objects.bulk_create(barrios_objs, ignore_conflicts=True)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_producto_nom_produ_and_more'),
    ]

    operations = [
        migrations.RunPython(poblar_datos),
    ]
