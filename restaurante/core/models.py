from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# =================================
# ROLES Y USUARIOS
# =================================

class Rol(models.Model):
    ROLES = [
        ('admin',    'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente',  'Cliente'),
    ]
    id_role_pk = models.AutoField(primary_key=True)
    name       = models.CharField(max_length=20, choices=ROLES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


class UsuarioAuth(models.Model):
    id_auth_pk      = models.AutoField(primary_key=True)
    nombre_usuario  = models.CharField(max_length=50, unique=True)
    contrasena_hash = models.CharField(max_length=255)
    rol             = models.ForeignKey(Rol, on_delete=models.PROTECT,
                                        db_column='id_role_fk')
    activo          = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios_auth'

    def set_password(self, raw_password):
        self.contrasena_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena_hash)

    def __str__(self):
        return f"{self.nombre_usuario} ({self.rol.name})"
    

# =================================
# EMPLEADOS
# =================================

class Empleado(models.Model):
    ESTADOS = [
        ('activo',   'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    id_emple_pk      = models.AutoField(primary_key=True)
    nom_emple        = models.CharField(max_length=25)
    apellido_emple   = models.CharField(max_length=30)
    fecha_naci_emple = models.DateField()
    tel_emple        = models.BigIntegerField()
    correo_emple     = models.CharField(max_length=40)
    direc_emple      = models.CharField(max_length=100)
    estado_emple     = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    id_auth_fk       = models.OneToOneField(
                            UsuarioAuth,
                            on_delete=models.SET_NULL,
                            null=True, blank=True,
                            db_column='id_auth_fk'
                        )

    class Meta:
        db_table = 'empleados'

    def __str__(self):
        return f"{self.nom_emple} {self.apellido_emple}"

# =================================
# CLIENTES
# =================================

class Cliente(models.Model):
    ESTADOS = [
        ('activo',   'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    id_clien_pk        = models.AutoField(primary_key=True)
    nom_clien          = models.CharField(max_length=25)
    apellido_clien     = models.CharField(max_length=30)
    fecha_naci_cliente = models.DateField()
    tel_cliente        = models.BigIntegerField()
    correo_clien       = models.CharField(max_length=40)
    direc_clien        = models.CharField(max_length=100)
    estado_clien       = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    id_auth_fk         = models.OneToOneField(
                            UsuarioAuth,
                            on_delete=models.SET_NULL,
                            null=True, blank=True,
                            db_column='id_auth_fk'
                        )

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f"{self.nom_clien} {self.apellido_clien}"

# =================================
# PROVEEDORES
# =================================

class Proveedor(models.Model):
    ESTADOS = [
        ('activo',   'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    id_provee_pk      = models.AutoField(primary_key=True)
    nom_provee        = models.CharField(max_length=25)
    apellido_provee   = models.CharField(max_length=30, blank=True, null=True)
    fecha_naci_provee = models.DateField(blank=True, null=True)
    tel_provee        = models.BigIntegerField()
    correo_provee     = models.CharField(max_length=40)
    direc_provee      = models.CharField(max_length=100)
    estado_provee     = models.CharField(max_length=10, choices=ESTADOS, default='activo')

    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return f"{self.nom_provee} {self.apellido_provee or ''}"


# =================================
# UNIDADES DE MEDIDA
# =================================

class UnidadMedida(models.Model):
    id_uni_medi_pk = models.AutoField(primary_key=True)
    nom_uni_medi   = models.CharField(max_length=20)
    abreviatura    = models.CharField(max_length=8)
    tipo_uni_medi  = models.CharField(max_length=20)

    class Meta:
        db_table = 'unidades_medidas'

    def __str__(self):
        return f"{self.nom_uni_medi} ({self.abreviatura})"

# =================================
# CATEGORÍAS DE PRODUCTOS
# =================================

class CategoriaProducto(models.Model):
    id_cate_produ_pk = models.AutoField(primary_key=True)
    nom_cate         = models.CharField(max_length=30)
    des_cate         = models.CharField(max_length=100)

    class Meta:
        db_table = 'categorias_productos'

    def __str__(self):
        return self.nom_cate

# =================================
# PRODUCTOS
# =================================

class Producto(models.Model):
    ESTADOS = [
        ('disponible',    'Disponible'),
        ('no disponible', 'No Disponible'),
        ('descontinuado', 'Descontinuado'),
    ]
    id_produ_pk          = models.AutoField(primary_key=True)
    nom_produ            = models.CharField(max_length=50)
    stock_actual_produ   = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    stock_minimo_produ   = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fecha_venci_produ    = models.DateField()
    precio_uni_produ     = models.DecimalField(max_digits=10, decimal_places=2)
    des_produ            = models.CharField(max_length=100)
    estado_produ         = models.CharField(max_length=15, choices=ESTADOS, default='disponible')
    id_provee_produ_fk   = models.ForeignKey(
                                Proveedor,
                                on_delete=models.PROTECT,
                                db_column='id_provee_produ_fk'
                            )
    id_uni_medi_produ_fk = models.ForeignKey(
                                UnidadMedida,
                                on_delete=models.PROTECT,
                                db_column='id_uni_medi_produ_fk'
                            )
    id_cate_produ_fk     = models.ForeignKey(
                                CategoriaProducto,
                                on_delete=models.PROTECT,
                                db_column='id_cate_produ_fk'
                            )

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nom_produ


# =================================
# MOVIMIENTOS DE PRODUCTOS
# =================================

class MovimientoProducto(models.Model):
    TIPOS = [
        ('entrada', 'Entrada'),
        ('salida',  'Salida'),
    ]
    id_movi_pk       = models.AutoField(primary_key=True)
    tipo_movi        = models.CharField(max_length=10, choices=TIPOS)
    motivo_movi      = models.CharField(max_length=50)
    fecha_movi       = models.DateTimeField(auto_now_add=True)
    cant_movi        = models.DecimalField(max_digits=10, decimal_places=3)
    stock_anterior   = models.DecimalField(max_digits=10, decimal_places=3)
    stock_posterior  = models.DecimalField(max_digits=10, decimal_places=3)
    id_emple_movi_fk = models.ForeignKey(
                            'Empleado',
                            on_delete=models.PROTECT,
                            db_column='id_emple_movi_fk'
                        )
    id_produ_movi_fk = models.ForeignKey(
                            'Producto',
                            on_delete=models.PROTECT,
                            db_column='id_produ_movi_fk'
                        )

    class Meta:
        db_table = 'movimientos_productos'

    def __str__(self):
        return f"{self.tipo_movi} - {self.id_produ_movi_fk.nom_produ} ({self.cant_movi})"
    

# =================================
# MENÚS
# =================================

class TipoMenu(models.Model):
    id_tipo_menu_pk = models.AutoField(primary_key=True)
    nom_tipo_menu   = models.CharField(max_length=20)
    des_tipo_menu   = models.CharField(max_length=100)

    class Meta:
        db_table = 'tipos_menus'

    def __str__(self):
        return self.nom_tipo_menu


class Menu(models.Model):
    id_menu_pk      = models.AutoField(primary_key=True)
    img_menu        = models.ImageField(upload_to='menu/', blank=True, null=True)
    nom_menu        = models.CharField(max_length=60)
    precio_menu     = models.DecimalField(max_digits=10, decimal_places=2)
    des_menu        = models.TextField()
    id_tipo_menu_fk = models.ForeignKey(TipoMenu, on_delete=models.PROTECT,
                                        db_column='id_tipo_menu_fk')
    disponible_menu = models.BooleanField(default=True)

    class Meta:
        db_table = 'menus'

# =================================
# RECETAS DE MENÚS
# =================================

class RecetaMenu(models.Model):
    id_receta_pk    = models.AutoField(primary_key=True)
    id_menu_fk      = models.ForeignKey(Menu,         on_delete=models.CASCADE,  db_column='id_menu_fk')
    id_produ_fk     = models.ForeignKey(Producto,     on_delete=models.PROTECT,  db_column='id_produ_fk')
    cantidad_reque  = models.DecimalField(max_digits=10, decimal_places=3)
    id_uni_medi_fk  = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT,  db_column='id_uni_medi_fk')
    notas           = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'recetas_menus'
        unique_together = [('id_menu_fk', 'id_produ_fk')]

    def __str__(self):
        return f"{self.id_menu_fk.nom_menu} - {self.id_produ_fk.nom_produ}"

# =================================
# UBICACIONES (Barrios y Localidades)
# =================================

class Localidad(models.Model):
    id_local_pk      = models.AutoField(primary_key=True)
    nom_local        = models.CharField(max_length=50)
    cod_postal_local = models.IntegerField()

    class Meta:
        db_table = 'localidades'

    def __str__(self):
        return self.nom_local


class Barrio(models.Model):
    id_barrio_pk       = models.AutoField(primary_key=True)
    nom_barrio         = models.CharField(max_length=50)
    id_local_barrio_fk = models.ForeignKey(
        Localidad,
        on_delete=models.PROTECT,
        db_column='id_local_barrio_fk'
    )

    class Meta:
        db_table = 'barrios'

    def __str__(self):
        return f"{self.nom_barrio} — {self.id_local_barrio_fk.nom_local}"


# =================================
# MESAS Y TIPOS DE EVENTOS
# =================================

class MesaEvento(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('ocupada',    'Ocupada'),
        ('reservada',  'Reservada'),
    ]
    id_mesa_pk  = models.AutoField(primary_key=True)
    num_mesa    = models.IntegerField()
    capa_mesa   = models.IntegerField()
    estado_mesa = models.CharField(max_length=10, choices=ESTADOS, default='disponible')

    class Meta:
        db_table = 'mesas_eventos'

    def __str__(self):
        return f"Mesa {self.num_mesa} ({self.capa_mesa} personas)"


class TipoEvento(models.Model):
    id_tipo_evento_pk = models.AutoField(primary_key=True)
    nom_tipo_evento   = models.CharField(max_length=30)
    des_tipo_evento   = models.CharField(max_length=100)

    class Meta:
        db_table = 'tipos_eventos'

    def __str__(self):
        return self.nom_tipo_evento


# =================================
# PEDIDO BASE
# =================================

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente',   'Pendiente'),
        ('confirmado',  'Confirmado'),
        ('preparando',  'Preparando'),
        ('listo',       'Listo'),
        ('entregado',   'Entregado'),
        ('cancelado',   'Cancelado'),
    ]
    TIPOS = [
        ('domicilio', 'Domicilio'),
        ('evento',    'Evento'),
    ]

    id_pedido_pk       = models.AutoField(primary_key=True)
    fecha_pedido       = models.DateTimeField(auto_now_add=True)
    estado_pedido      = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    tipo_pedido        = models.CharField(max_length=10, choices=TIPOS)
    total_pedido       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas_pedido       = models.CharField(max_length=200, blank=True, null=True)
    id_clien_pedido_fk = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        db_column='id_clien_pedido_fk',
        related_name='pedidos'
    )
    id_emple_pedido_fk = models.ForeignKey(
        'Empleado',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_emple_pedido_fk',
        related_name='pedidos_asignados'
    )

    class Meta:
        db_table = 'pedidos'

    def __str__(self):
        return f"Pedido #{self.id_pedido_pk} — {self.id_clien_pedido_fk} ({self.tipo_pedido})"


# =================================
# DETALLE DE PEDIDO (menús pedidos)
# =================================

class DetallePedidoMenu(models.Model):
    id_detalle_pk   = models.AutoField(primary_key=True)
    cant_detalle    = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2)
    id_pedido_fk    = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido_fk',
        related_name='detalles_set'
    )
    id_menu_fk      = models.ForeignKey(
        'Menu',
        on_delete=models.PROTECT,
        db_column='id_menu_fk'
    )

    class Meta:
        db_table = 'detalles_pedidos_menus'

    def __str__(self):
        return f"{self.id_menu_fk.nom_menu} x{self.cant_detalle}"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cant_detalle * self.precio_unitario
        super().save(*args, **kwargs)


# =================================
# DOMICILIO
# =================================

class Domicilio(models.Model):
    ESTADOS = [
        ('pendiente',  'Pendiente'),
        ('en camino',  'En camino'),
        ('entregado',  'Entregado'),
    ]
    id_domi_pk        = models.AutoField(primary_key=True)
    direc_domi        = models.CharField(max_length=100)
    fecha_domi        = models.DateField()
    hora_entrega_domi = models.TimeField()
    estado_domi       = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    id_pedido_domi_fk = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido_domi_fk',
        related_name='domicilios_set'
    )
    id_barrio_domi_fk = models.ForeignKey(
        Barrio,
        on_delete=models.PROTECT,
        db_column='id_barrio_domi_fk'
    )

    class Meta:
        db_table = 'domicilios'

    def __str__(self):
        return f"Domicilio #{self.id_domi_pk} — {self.direc_domi}"


# =================================
# EVENTO
# =================================

class Evento(models.Model):
    ESTADOS = [
        ('pendiente',    'Pendiente'),
        ('en revisión',  'En revisión'),
        ('aprobado',     'Aprobado'),
        ('rechazado',    'Rechazado'),
        ('programado',   'Programado'),
        ('en progreso',  'En progreso'),
        ('finalizado',   'Finalizado'),
        ('cancelado',    'Cancelado'),
    ]
    id_evento_pk        = models.AutoField(primary_key=True)
    nom_evento          = models.CharField(max_length=50)
    fecha_evento        = models.DateField()
    hora_inicio_evento  = models.TimeField()
    hora_fin_evento     = models.TimeField()
    ubi_evento          = models.CharField(max_length=100)
    cant_invi_evento    = models.IntegerField()
    estado_evento       = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    id_tipo_evento_fk   = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
        db_column='id_tipo_evento_fk'
    )
    id_mesa_evento_fk   = models.ForeignKey(
        MesaEvento,
        on_delete=models.PROTECT,
        db_column='id_mesa_evento_fk'
    )
    id_pedido_evento_fk = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido_evento_fk',
        related_name='eventos_set'
    )

    class Meta:
        db_table = 'eventos'

    def __str__(self):
        return f"{self.nom_evento} — {self.fecha_evento}"
    

# =================================
# MÉTODOS DE PAGO
# =================================

class MetodoPago(models.Model):
    METODOS_PERMITIDOS = [
        ('efectivo',    'Efectivo'),
        ('nequi',       'Nequi'),
        ('bancolombia', 'Bancolombia'),
    ]
    id_met_pago_pk = models.AutoField(primary_key=True)
    tipo_met_pago  = models.CharField(max_length=20, choices=METODOS_PERMITIDOS)
    des_met_pago   = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'metodos_pagos'

    def __str__(self):
        return self.tipo_met_pago


# =================================
# FACTURAS
# =================================

class Factura(models.Model):
    id_factu_pk        = models.AutoField(primary_key=True)
    fecha_factu        = models.DateField()
    hora_factu         = models.TimeField()
    total_factu        = models.DecimalField(max_digits=10, decimal_places=2)
    id_clien_factu_fk  = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        db_column='id_clien_factu_fk'
    )
    id_pedido_factu_fk = models.ForeignKey(
        'Pedido',
        on_delete=models.PROTECT,
        db_column='id_pedido_factu_fk'
    )

    class Meta:
        db_table = 'facturas'

    def __str__(self):
        return f"Factura #{self.id_factu_pk} — ${self.total_factu}"


# =================================
# PAGOS
# =================================

class Pago(models.Model):
    ESTADOS = [
        ('pendiente',   'Pendiente'),
        ('completado',  'Completado'),
        ('rechazado',   'Rechazado'),
    ]
    id_pago_pk       = models.AutoField(primary_key=True)
    fecha_pago       = models.DateField()
    hora_pago        = models.TimeField()
    monto_pago       = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago      = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    referencia_pago  = models.CharField(max_length=100, blank=True, null=True)  # número Nequi / comprobante
    id_met_pago_fk   = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        db_column='id_met_pago_fk'
    )
    id_factu_pago_fk = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        db_column='id_factu_pago_fk'
    )
    
    # Nuevos campos para comprobación de pagos
    celular_origen = models.CharField(max_length=20, blank=True, null=True) # Para Nequi
    nombre_titular = models.CharField(max_length=100, blank=True, null=True) # Para Bancolombia
    comprobante_img = models.ImageField(upload_to='comprobantes/', blank=True, null=True) # Screenshot Nequi/Bancolombia
    monto_con_el_que_paga = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Efectivo

    class Meta:
        db_table = 'pagos'

    def __str__(self):
        return f"Pago #{self.id_pago_pk} — {self.estado_pago}"


# =================================
# NOTIFICACIONES
# =================================

class Notificacion(models.Model):
    TIPOS = [
        ('pedido', 'Pedido'),
        ('reserva', 'Reserva'),
        ('inventario', 'Inventario'),
        ('mensaje', 'Mensaje del Cliente'),
    ]
    id_notif_pk = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=100)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificaciones'

    def __str__(self):
        return f"{self.tipo} - {self.titulo}"