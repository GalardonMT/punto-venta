from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Comanda(models.Model):
    nombre_cliente = models.CharField(max_length=100, default="No asignado")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=[('abierta','Abierta'),('cerrada','Cerrada')], default='abierta')
    total = models.IntegerField()

    # Nuevo campo: Empleado
    empleado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Nuevo campo: Metodo de pago (con default!)
    metodo_pago = models.CharField(
        max_length=50,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta_credito', 'Tarjeta Crédito'),
            ('tarjeta_debito', 'Tarjeta Débito'),
            ('transferencia', 'Transferencia'),
            ('mixto', 'Mixto'),
        ],
        default='efectivo'
    )

    # Campos para pagos mixtos
    monto_efectivo = models.IntegerField(null=True, blank=True)
    monto_tarjeta_debito = models.IntegerField(null=True, blank=True)
    monto_tarjeta_credito = models.IntegerField(null=True, blank=True)
    monto_transferencia = models.IntegerField(null=True, blank=True)

    # Nuevo campo: tipo de servicio (con default!)
    tipo_servicio = models.CharField(
        max_length=50,
        choices=[
            ('servir', 'Servir'),
            ('delivery', 'Delivery'),
            ('reserva', 'Reserva'),
        ],
        default='servir'
    )
    nota = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Comanda #{self.id} - {self.estado}"


class Ingredientes(models.Model):
    nombre = models.CharField(max_length=50)
    stock_actual = models.FloatField()

    def __str__(self):
        return self.nombre
    
class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingredientes = models.ForeignKey(Ingredientes, on_delete=models.CASCADE)
    dpo = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    fecha_hora = models.IntegerField()

class producto_ingrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingredientes = models.ForeignKey(Ingredientes, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    
class DetalleComanda(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.IntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class HistorialComanda(models.Model):
    fecha = models.DateTimeField()
    nombre_cliente = models.CharField(max_length=100)
    empleado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ventas_realizadas')
    total = models.IntegerField()
    metodo_pago = models.CharField(max_length=50)
    monto_efectivo = models.IntegerField(null=True, blank=True)
    monto_tarjeta_debito = models.IntegerField(null=True, blank=True)
    monto_tarjeta_credito = models.IntegerField(null=True, blank=True)
    monto_transferencia = models.IntegerField(null=True, blank=True)
    tipo_servicio = models.CharField(max_length=50)
    detalles = models.TextField()

    # Nuevo campo: quién cerró la caja
    cerrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cierres_realizados')

    def __str__(self):
        return f"Historial - {self.fecha} - Total: {self.total}"
    
class EliminacionComanda(models.Model):
    comanda_id = models.IntegerField()
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    total = models.IntegerField()
    motivo = models.TextField()
    eliminado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Eliminada #{self.comanda_id} - {self.fecha_eliminacion.strftime('%d/%m/%Y %H:%M')}"
