"""
URL configuration for aplicacion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core.views import imprimir_boleta_comanda, login_vista, historial_comanda_detalle, comandas_por_usuario, eliminar_usuario,reabrir_comanda, cambiar_estado_usuario, editar_usuario, registro, inicio, productos, usuarios, verificar_admin_y_eliminar_comandas_eliminadas, comandas_eliminadas_json, imprimir_boleta_ventas_dia, comandas_eliminadas, exportar_reportes_anual,comandas_por_usuario, venta, eliminar_categoria, crear_categoria, reportes, eliminar_producto,verificar_y_eliminar_comanda, cerrar_caja, editar_producto, logout_view, nueva_comanda, agregar_a_comanda, guardar_comanda, comandas_json, comanda_detalle, eliminar_comanda, editar_comanda, verificar_superusuario, api_usuario_detalle, exportar_reportes_mes
from core import views
#staticos
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login_vista, name='login'),
    path('registro/', registro, name='registro'),
    path("logout/", logout_view, name="logout"), 
    path('inicio/', inicio, name='inicio'),
    path('usuarios/', usuarios, name='usuarios'),
    path('api/comandas/<int:user_id>/', comandas_por_usuario, name='comandas_por_usuario'),
    path('api/cambiar_estado_usuario/<int:user_id>/', cambiar_estado_usuario),
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('verificar-superusuario/', verificar_superusuario, name='verificar_superusuario'),
    path('verificar-y-eliminar-comanda/', verificar_y_eliminar_comanda, name='verificar_y_eliminar_comanda'),
    path('venta/', venta, name='venta'),
    path('reportes/', reportes , name='reportes'),
    path('nueva-comanda/', nueva_comanda, name='nueva_comanda'),
    path('venta/<int:comanda_id>/agregar/', agregar_a_comanda, name='agregar_a_comanda'),
    path('productos/', productos, name='productos'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('guardar_comanda/', guardar_comanda, name='guardar_comanda'),
    path('comandas-json/', comandas_json, name='comandas_json'),
    path('comanda-detalle/<int:comanda_id>/', comanda_detalle, name='comanda_detalle'),
    path('eliminar-comanda/<int:comanda_id>/', eliminar_comanda, name='eliminar_comanda'),
    path('crear_categoria/', crear_categoria, name='crear_categoria'),
    path('eliminar_categoria/<int:categoria_id>/', eliminar_categoria, name='eliminar_categoria'),
    path('editar-comanda/<int:id>/', editar_comanda, name='editar_comanda'),
    path('cerrar-caja/', cerrar_caja, name='cerrar_caja'),
    path('api/usuario/<int:user_id>/', api_usuario_detalle, name='api_usuario_detalle'),
    path('exportar-reportes-mes/', exportar_reportes_mes, name='exportar_reportes_mes'),
    path('imprimir-boleta-ventas-dia/', imprimir_boleta_ventas_dia, name='imprimir_boleta_ventas_dia'),
    path('exportar-reportes-anual/', exportar_reportes_anual, name='exportar_reportes_anual'),
    path('comandas-eliminadas/', comandas_eliminadas, name='comandas_eliminadas'),
    path('comandas-eliminadas-json/', comandas_eliminadas_json, name='comandas_eliminadas_json'),
    path('reabrir-comanda/<int:comanda_id>/', reabrir_comanda, name='reabrir_comanda'),
    path('eliminar_usuario/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('eliminar-comandas-con-verificacion/', verificar_admin_y_eliminar_comandas_eliminadas, name='eliminar_comandas_con_verificacion'),
    path('historial-comanda-detalle/<int:comanda_id>/', historial_comanda_detalle, name='historial_comanda_detalle'),
    path('imprimir-boleta-comanda/<int:comanda_id>/', imprimir_boleta_comanda, name='imprimir_boleta_comanda'),
    path('imprimir-boleta-cocina/<int:comanda_id>/', views.imprimir_boleta_cocina_view, name='imprimir_boleta_cocina'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

