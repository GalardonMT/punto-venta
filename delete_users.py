#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aplicacion.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Categoria, EliminacionComanda, HistorialComanda, Producto

# Obtener el número de registros antes de eliminar
user_count = User.objects.count()
categoria_count = Categoria.objects.count()
eliminacion_count = EliminacionComanda.objects.count()
historial_count = HistorialComanda.objects.count()
producto_count = Producto.objects.count()

# Verificar si la tabla core_impresora existe y contar registros
cursor = connection.cursor()
try:
    cursor.execute("SELECT COUNT(*) FROM core_impresora")
    impresora_count = cursor.fetchone()[0]
    impresora_exists = True
except:
    impresora_count = 0
    impresora_exists = False

print(f"Usuarios encontrados: {user_count}")
print(f"Categorías encontradas: {categoria_count}")
print(f"Eliminaciones de comanda encontradas: {eliminacion_count}")
print(f"Historiales de comanda encontrados: {historial_count}")
print(f"Productos encontrados: {producto_count}")
if impresora_exists:
    print(f"Impresoras encontradas: {impresora_count}")
else:
    print("Tabla core_impresora no existe")

# Eliminar usuarios
if user_count > 0:
    deleted_count, deleted_objects = User.objects.all().delete()
    print(f"Se eliminaron {deleted_count} usuarios exitosamente")
    print("Detalles de eliminación usuarios:", deleted_objects)
else:
    print("No hay usuarios para eliminar")

# Eliminar categorías
if categoria_count > 0:
    deleted_count_cat, deleted_objects_cat = Categoria.objects.all().delete()
    print(f"Se eliminaron {deleted_count_cat} categorías exitosamente")
    print("Detalles de eliminación categorías:", deleted_objects_cat)
else:
    print("No hay categorías para eliminar")

# Eliminar eliminaciones de comanda
if eliminacion_count > 0:
    deleted_count_elim, deleted_objects_elim = EliminacionComanda.objects.all().delete()
    print(f"Se eliminaron {deleted_count_elim} eliminaciones de comanda exitosamente")
    print("Detalles de eliminación comandas:", deleted_objects_elim)
else:
    print("No hay eliminaciones de comanda para eliminar")

# Eliminar historial de comandas
if historial_count > 0:
    deleted_count_hist, deleted_objects_hist = HistorialComanda.objects.all().delete()
    print(f"Se eliminaron {deleted_count_hist} historiales de comanda exitosamente")
    print("Detalles de eliminación historial:", deleted_objects_hist)
else:
    print("No hay historiales de comanda para eliminar")

# Eliminar productos
if producto_count > 0:
    deleted_count_prod, deleted_objects_prod = Producto.objects.all().delete()
    print(f"Se eliminaron {deleted_count_prod} productos exitosamente")
    print("Detalles de eliminación productos:", deleted_objects_prod)
else:
    print("No hay productos para eliminar")

# Eliminar impresoras usando SQL directo
if impresora_exists and impresora_count > 0:
    cursor.execute("DELETE FROM core_impresora")
    print(f"Se eliminaron {impresora_count} impresoras exitosamente")
    cursor.execute("SELECT COUNT(*) FROM core_impresora")
    remaining_impresoras = cursor.fetchone()[0]
    print(f"Impresoras restantes: {remaining_impresoras}")
elif impresora_exists:
    print("No hay impresoras para eliminar")

# Verificar que se eliminaron
remaining_users = User.objects.count()
remaining_categorias = Categoria.objects.count()
remaining_eliminaciones = EliminacionComanda.objects.count()
remaining_historial = HistorialComanda.objects.count()
remaining_productos = Producto.objects.count()
print(f"Usuarios restantes: {remaining_users}")
print(f"Categorías restantes: {remaining_categorias}")
print(f"Eliminaciones de comanda restantes: {remaining_eliminaciones}")
print(f"Historiales de comanda restantes: {remaining_historial}")
print(f"Productos restantes: {remaining_productos}")
