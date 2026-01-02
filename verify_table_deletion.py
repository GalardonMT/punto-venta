#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aplicacion.settings')
django.setup()

# Verificar si la tabla core_impresora existe
cursor = connection.cursor()
try:
    cursor.execute("SELECT COUNT(*) FROM core_impresora")
    print("❌ La tabla core_impresora TODAVÍA EXISTE")
    count = cursor.fetchone()[0]
    print(f"Registros en la tabla: {count}")
except Exception as e:
    print("✅ La tabla core_impresora ha sido ELIMINADA COMPLETAMENTE")
    print(f"Error al acceder a la tabla (esto es esperado): {e}")

# Listar todas las tablas que empiecen con 'core_'
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'core_%'
    ORDER BY name
""")
tables = cursor.fetchall()
print("\n📋 Tablas existentes que empiezan con 'core_':")
for table in tables:
    print(f"  - {table[0]}")
