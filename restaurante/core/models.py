from decimal import Decimal

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
    correo          = models.CharField(max_length=40, blank=True, null=True)
    rol             = models.ForeignKey(Rol, on_delete=models.PROTECT,
                                        db_column='id_role_fk')
    activo          = models.BooleanField(default=True)
    requiere_cambio_pw = models.BooleanField(default=False)
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
    TIPO_DOC_CHOICES = [
        ('Cédula de Ciudadanía', 'Cédula de Ciudadanía'),
        ('Cédula de Extranjería', 'Cédula de Extranjería'),
        ('Pasaporte', 'Pasaporte'),
        ('Tarjeta de Identidad', 'Tarjeta de Identidad'),
    ]
    TIPO_CONTRATO_CHOICES = [
        ('Término Indefinido', 'Término Indefinido'),
        ('Término Fijo', 'Término Fijo'),
        ('Obra o Labor', 'Obra o Labor'),
        ('Contrato de Aprendizaje', 'Contrato de Aprendizaje'),
    ]

    id_emple_pk      = models.AutoField(primary_key=True, db_column='id_empleado_pk')
    foto_empleado    = models.CharField(max_length=255, default='default.png')
    nom_emple        = models.CharField(max_length=50, db_column='nom_empleado')
    apellido_emple   = models.CharField(max_length=50, db_column='apellido_empleado')
    fecha_naci_emple = models.DateField(db_column='fecha_naci_empleado')
    tipo_doc         = models.CharField(max_length=50, choices=TIPO_DOC_CHOICES)
    num_doc          = models.CharField(max_length=12, unique=True)
    tel_emple        = models.CharField(max_length=10, db_column='tel_empleado')
    correo_emple     = models.CharField(max_length=100, db_column='correo_empleado', unique=True)
    direc_emple      = models.CharField(max_length=100, db_column='direc_empleado')
    fecha_ingreso    = models.DateField()
    tipo_contrato    = models.CharField(max_length=50, choices=TIPO_CONTRATO_CHOICES)
    salario_empleado = models.DecimalField(max_digits=10, decimal_places=2)
    estado_emple     = models.CharField(max_length=10, choices=ESTADOS, default='activo', db_column='estado_empleado')
    id_auth_fk       = models.OneToOneField(
                            UsuarioAuth,
                            on_delete=models.SET_NULL,
                            null=True, blank=True,
                            db_column='id_auth_fk'
                        )
    fecha_registro   = models.DateTimeField(auto_now_add=True, blank=True, null=True)

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
    foto_cliente       = models.CharField(max_length=255, default='default.png')
    nom_clien          = models.CharField(max_length=25)
    apellido_clien     = models.CharField(max_length=30)
    fecha_naci_cliente = models.DateField()
    tel_cliente        = models.CharField(max_length=10)
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
    TIPOS_PROVEEDOR = [
        ('empresa', 'Empresa'),
        ('persona_natural', 'Persona Natural'),
    ]
    CONDICIONES_PAGO = [
        ('contado', 'Contado'),
        ('15_dias', '15 días'),
        ('30_dias', '30 días'),
        ('60_dias', '60 días'),
    ]

    id_provee_pk           = models.AutoField(primary_key=True)
    tipo_provee            = models.CharField(max_length=20, choices=TIPOS_PROVEEDOR, default='empresa')
    nom_provee             = models.CharField(max_length=100)
    nit_cedula_provee      = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nombre_contacto_provee = models.CharField(max_length=100, blank=True, null=True)
    tel_provee             = models.CharField(max_length=10)
    correo_provee          = models.CharField(max_length=50)
    direc_provee           = models.CharField(max_length=100)
    condicion_pago_provee  = models.CharField(max_length=20, choices=CONDICIONES_PAGO, blank=True, null=True)
    observaciones_provee   = models.TextField(max_length=300, blank=True, null=True)
    estado_provee          = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    
    # Relación ManyToMany para las categorías que suministra el proveedor
    categorias_provee      = models.ManyToManyField('CategoriaProducto', db_table='proveedor_categorias', blank=True)

    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return self.nom_provee


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
    nom_produ            = models.CharField(max_length=50, unique=True)
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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock_actual_produ__gte=0),
                name='stock_actual_no_negativo'
            ),
            models.CheckConstraint(
                condition=models.Q(stock_minimo_produ__gt=0),
                name='stock_minimo_positivo'
            )
        ]

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
    origen_movi      = models.CharField(max_length=20, default='manual')
    nota_movi        = models.TextField(blank=True, null=True)
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

    @staticmethod
    def _format_decimal(value):
        if value == value.to_integral_value():
            return str(value.quantize(Decimal('1')))
        return format(value.normalize(), 'f')

    @staticmethod
    def _conversion_pair(unidad_abreviatura):
        unidad = unidad_abreviatura.strip().lower() if unidad_abreviatura else ''
        pairs = {
            'kg': ('g', Decimal('1000')),
            'g': ('kg', Decimal('0.001')),
            'l': ('ml', Decimal('1000')),
            'ml': ('l', Decimal('0.001')),
            'm': ('cm', Decimal('100')),
            'cm': ('m', Decimal('0.01')),
            'km': ('m', Decimal('1000')),
            'm3': ('l', Decimal('1000')),
        }
        return pairs.get(unidad, None)

    @staticmethod
    def _format_base_unit(value, unidad_abreviatura):
        original = MovimientoProducto._format_decimal(value)
        unidad = unidad_abreviatura.strip().upper() if unidad_abreviatura else ''
        return f"{original} {unidad}"

    @staticmethod
    def _format_with_conversion(value, unidad_abreviatura):
        original = MovimientoProducto._format_decimal(value)
        unidad = unidad_abreviatura.strip() if unidad_abreviatura else ''
        conversion = MovimientoProducto._conversion_pair(unidad_abreviatura)
        if conversion:
            unidad_equivalente, factor = conversion
            valor_convertido = (value * factor).quantize(Decimal('1')) if factor >= 1 else value * factor
            converted = MovimientoProducto._format_decimal(valor_convertido)
            return f"{original}{unidad} - {converted}{unidad_equivalente}"
        return f"{original}{unidad}"

    @property
    def cant_movi_display(self):
        return self._format_base_unit(self.cant_movi, self.id_produ_movi_fk.id_uni_medi_produ_fk.abreviatura)

    @property
    def cant_movi_display_detailed(self):
        return self._format_with_conversion(self.cant_movi, self.id_produ_movi_fk.id_uni_medi_produ_fk.abreviatura)

    @property
    def stock_anterior_display(self):
        return self._format_base_unit(self.stock_anterior, self.id_produ_movi_fk.id_uni_medi_produ_fk.abreviatura)

    @property
    def stock_posterior_display(self):
        return self._format_base_unit(self.stock_posterior, self.id_produ_movi_fk.id_uni_medi_produ_fk.abreviatura)

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

    id_pedido_pk       = models.AutoField(primary_key=True)
    fecha_pedido       = models.DateTimeField(auto_now_add=True)
    estado_pedido      = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    tipo_pedido        = models.CharField(max_length=20, default='domicilio', editable=False)
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
    
    # Solicitud de cancelación
    solicitud_cancelacion_pendiente = models.BooleanField(default=False)
    motivo_solicitud_cancelacion = models.CharField(max_length=300, blank=True, null=True)
    fecha_solicitud_cancelacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos'

    def __str__(self):
        return f"Pedido #{self.id_pedido_pk} — {self.id_clien_pedido_fk} ({self.tipo_pedido})"


# =================================
# HISTORIAL ESTADO PEDIDO
# =================================

class HistorialEstadoPedido(models.Model):
    id_historial_pk = models.AutoField(primary_key=True)
    id_pedido_fk    = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='id_pedido_fk', related_name='historial_estados')
    estado_anterior = models.CharField(max_length=12, choices=Pedido.ESTADOS)
    estado_nuevo    = models.CharField(max_length=12, choices=Pedido.ESTADOS)
    fecha_cambio    = models.DateTimeField(auto_now_add=True)
    id_auth_fk      = models.ForeignKey(UsuarioAuth, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_auth_fk')
    notas           = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'historial_estados_pedidos'

    def __str__(self):
        return f"Pedido #{self.id_pedido_fk_id}: {self.estado_anterior} -> {self.estado_nuevo}"


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
        ('cancelado',  'Cancelado'),
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
        db_column='id_factu_pago_fk',
        null=True, blank=True
    )
    id_pedido_pago_fk = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        db_column='id_pedido_pago_fk',
        null=True, blank=True
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
    CATEGORIAS = [
        ('pedido', 'Pedido'),
        ('inventario', 'Inventario'),
        ('pago', 'Pago'),
        ('cancelacion', 'Cancelación'),
        ('usuario', 'Usuario'),
        ('sistema', 'Sistema'),
        ('mensaje', 'Mensaje'),
    ]
    ROLES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]
    id_notif_pk = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=CATEGORIAS, db_column='categoria')
    destinatario_rol = models.CharField(max_length=20, choices=ROLES)
    id_auth_destino_fk = models.ForeignKey(UsuarioAuth, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_auth_destino_fk', related_name='notificaciones_recibidas')
    titulo = models.CharField(max_length=120)
    mensaje = models.CharField(max_length=500)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    
    # FKs opcionales
    id_pedido_fk = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_pedido_fk')
    id_producto_fk = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_producto_fk')
    id_factura_fk = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_factura_fk')
    id_movi_fk = models.ForeignKey(MovimientoProducto, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_movi_fk')
    id_auth_origen_fk = models.ForeignKey(UsuarioAuth, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_auth_origen_fk', related_name='notificaciones_enviadas')

    class Meta:
        db_table = 'notificaciones'

    def __str__(self):
        return f"{self.tipo} - {self.titulo}"


class ConsumoPedido(models.Model):
    id_consumo_pk      = models.AutoField(primary_key=True)
    id_pedido_fk       = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='id_pedido_fk')
    id_produ_fk        = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column='id_produ_fk')
    cantidad_consumida = models.DecimalField(max_digits=10, decimal_places=3)
    id_uni_medi_fk     = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, db_column='id_uni_medi_fk')
    fecha_consumo      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consumos_pedidos'

    def __str__(self):
        return f"Consumo Pedido #{self.id_pedido_fk.id_pedido_pk} - {self.id_produ_fk.nom_produ}"


# =================================
# CONFIGURACIÓN DEL SISTEMA
# =================================

class ConfiguracionSistema(models.Model):
    id_config_pk = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=50, unique=True)
    valor_booleano = models.BooleanField(default=False)
    valor_texto = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'configuracion_sistema'

    def __str__(self):
        return self.clave

class Favorito(models.Model):
    id_favorito = models.AutoField(primary_key=True)
    id_cliente_fk = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    id_menu_fk = models.ForeignKey('Menu', on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_favoritos'
        unique_together = ('id_cliente_fk', 'id_menu_fk')

class CarritoItem(models.Model):
    id_carrito_item = models.AutoField(primary_key=True)
    id_cliente_fk = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    id_menu_fk = models.ForeignKey('Menu', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_carrito_items'
        unique_together = ('id_cliente_fk', 'id_menu_fk')

class CampanaEmail(models.Model):
    id_campana_pk = models.AutoField(primary_key=True)
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    total_destinatarios = models.IntegerField(default=0)
    enviado_por_fk = models.ForeignKey('UsuarioAuth', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tbl_campanas_email'
