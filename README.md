# Sistema de Punto de Venta (POS)

Un sistema de Punto de Venta robusto desarrollado con **Django** y **Python**. Este sistema está diseñado para gestionar ventas, inventario, clientes y órdenes (comandas) en un entorno de restaurante, cafetería o comercio similar.

## 🚀 Características Principales

*   **Gestión de Comandas (Órdenes):**
    *   Manejo de órdenes en diferentes estados (Abierta, Cerrada).
    *   Soporte para múltiples tipos de servicio: *Servir (en mesa)*, *Delivery* y *Reservas*.
    *   Asignación de empleados a cada comanda.
*   **Gestión de Pagos:**
    *   Soporte para múltiples métodos de pago: *Efectivo, Tarjeta de Crédito, Tarjeta de Débito, Transferencia*.
    *   Pagos Mixtos (ej. una parte en efectivo y otra con tarjeta).
*   **Catálogo de Productos:**
    *   Clasificación de productos por *Categorías*.
    *   Imágenes, descripciones y precios por producto.
*   **Control de Inventario y Recetas:**
    *   Gestión de *Ingredientes* y su stock actual.
    *   Relación entre productos e ingredientes (recetas) para un control preciso de mermas e inventario.
*   **Gestión de Clientes:**
    *   Registro de clientes con nombre y teléfono.
    *   Múltiples direcciones de entrega para servicio de Delivery.
*   **Historial y Auditoría:**
    *   Historial completo de comandas cobradas y cerradas.
    *   Registro de cierres de caja por empleado.
    *   Registro y motivos de eliminación de comandas (auditoría).

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3.12, Django 6.0
*   **Manejo de Imágenes:** Pillow
*   **Base de datos:** SQLite (por defecto en Django) / configurable a PostgreSQL/MySQL
*   **Otras librerías:** `openpyxl` (para exportación de reportes), `asgiref`, `sqlparse`

## ⚙️ Requisitos Previos

Asegúrate de tener instalado en tu sistema:
*   [Python 3.12+](https://www.python.org/downloads/)
*   `pip` (Administrador de paquetes de Python)
*   Se recomienda el uso de entornos virtuales (`venv` o `pipenv`).

## 💻 Instalación y Ejecución Local

Sigue estos pasos para correr el proyecto en tu máquina local:

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd punto-venta
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Opcional: Si usas pipenv, puedes ejecutar `pipenv install`)*

4.  **Aplicar las migraciones de la base de datos:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Crear un superusuario (Administrador):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Iniciar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

7.  **Acceder al sistema:**
    *   Abre tu navegador web y ve a `http://127.0.0.1:8000/`
    *   Panel de administración: `http://127.0.0.1:8000/admin/`

## 📁 Estructura del Proyecto

*   `aplicacion/` - Configuración principal del proyecto Django (`settings.py`, `urls.py`, etc).
*   `core/` - Aplicación principal que contiene la lógica de negocio, modelos (`models.py`), vistas y plantillas.
*   `media/` - Directorio donde se almacenan las imágenes subidas de los productos.
*   `requirements.txt` - Lista de dependencias del proyecto.
