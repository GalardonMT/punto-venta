from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import Group, User
from django.db.models import Sum
from django.utils.timezone import make_aware, localtime
from django.http import JsonResponse, HttpResponse
from openpyxl import Workbook
from .models import Producto, Comanda, DetalleComanda, HistorialComanda, EliminacionComanda, Categoria
from .forms import ProductoForm
from openpyxl.styles import Font
from collections import defaultdict
import json
import win32print
from django.contrib.auth.hashers import make_password

# Autenticación
def login_vista(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contra = request.POST.get('password')
        user = authenticate(request, username=usuario, password=contra)
        if user is not None:
            auth_login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'core/login.html')

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            empleados_group, created = Group.objects.get_or_create(name="Empleados")
            user.groups.add(empleados_group)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') 

# Vistas principales
@login_required(login_url='login')
def inicio(request):
    usuario = request.user
    hora_actual = timezone.now()
    hoy = hora_actual.date()

    comandas_hoy = Comanda.objects.filter(estado='cerrada', fecha__date=hoy)
    detalles = DetalleComanda.objects.filter(comanda__in=comandas_hoy)

    dict_ventas = defaultdict(int)
    # Ventas activas por producto (usamos producto__id y producto__nombre)
    for v in detalles.values('producto__id', 'producto__nombre').annotate(total_vendido=Sum('cantidad')):
        dict_ventas[(v['producto__id'], v['producto__nombre'])] += v['total_vendido']

    historiales_hoy = HistorialComanda.objects.filter(fecha__date=hoy)
    for h in historiales_hoy:
        try:
            detalles_historial = json.loads(h.detalles)
            for item in detalles_historial:
                nombre_producto = item.get('producto')
                cantidad = item.get('cantidad', 0)
                if nombre_producto and cantidad:
                    # Usamos solo el nombre como clave porque no tenemos id
                    # Para evitar mezclar con productos que tienen el mismo nombre, puedes cambiar
                    # a solo usar nombre o implementar lógica para buscar id si quieres
                    dict_ventas[(None, nombre_producto)] += cantidad
        except Exception:
            pass

    # Combinar ventas por nombre (sumar ambos)
    resumen_por_nombre = defaultdict(int)
    for key, cant in dict_ventas.items():
        nombre = key[1]
        resumen_por_nombre[nombre] += cant

    # Ordenar top 3 por cantidad
    top_productos = sorted(
        [{'producto__nombre': nombre, 'total_vendido': cant} for nombre, cant in resumen_por_nombre.items()],
        key=lambda x: x['total_vendido'],
        reverse=True
    )[:3]

    return render(request, 'core/home.html', {
        'usuario': usuario,
        'hora_actual': hora_actual,
        'top_productos': top_productos,
    })

#Usuarios
@login_required(login_url='login')
def usuarios(request):
    if not request.user.groups.filter(name='Dueños').exists():
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('inicio')
    usuarios = User.objects.all().order_by('date_joined')
    total_usuarios = usuarios.count()
    return render(request, 'core/usuarios.html', {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios
    })


def comandas_por_usuario(request, user_id):
    if request.method == 'GET':
        try:
            # Obtener usuario
            usuario = User.objects.get(pk=user_id)
            
            # Obtener todas las comandas del usuario
            comandas = Comanda.objects.filter(empleado_id=user_id).order_by('-fecha')

            # Obtener solo las comandas de hoy
            hoy = timezone.now().date()
            comandas_hoy = comandas.filter(fecha__date=hoy)
            total_vendido_hoy = sum(c.total for c in comandas_hoy)
            cantidad_hoy = comandas_hoy.count()

            # Formatear datos de todas las comandas
            data = [{
                'id': c.id,
                'nombre_cliente': c.nombre_cliente,
                'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
                'estado': c.estado,
                'total': c.total
            } for c in comandas_hoy]  # solo comandas de hoy si quieres mostrar eso en el modal

            return JsonResponse({
                'comandas': data,
                'cantidad_hoy': cantidad_hoy,
                'total_vendido_hoy': total_vendido_hoy,
                'last_login': usuario.last_login.strftime('%d/%m/%Y %H:%M') if usuario.last_login else 'Nunca',
                'is_active': usuario.is_active
            })

        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        
@csrf_exempt
def cambiar_estado_usuario(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            activar = data.get('activar')

            if activar is None:
                return JsonResponse({'error': 'Falta el parámetro "activar"'}, status=400)

            user = User.objects.get(pk=user_id)
            user.is_active = bool(activar)
            user.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def editar_usuario(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            grupo_nombre = data.get('grupo')

            if not username or not password or not grupo_nombre:
                return JsonResponse({'success': False, 'error': 'Faltan datos obligatorios'})

            user = User.objects.get(pk=user_id)
            user.username = username
            user.password = make_password(password)
            user.save()

            # Actualizar grupo
            grupo = Group.objects.filter(name=grupo_nombre).first()
            if grupo:
                user.groups.clear()
                user.groups.add(grupo)
            else:
                return JsonResponse({'success': False, 'error': f'Grupo "{grupo_nombre}" no encontrado'})

            return JsonResponse({'success': True})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=user_id)
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@login_required(login_url='login')
def venta(request):
    productos = Producto.objects.all()
    comandas = Comanda.objects.all().order_by('-fecha')
    categorias = Categoria.objects.all()
    return render(request, 'core/venta.html', {'productos': productos, 'comandas': comandas, 'categorias': categorias})


@login_required(login_url='login')
def reportes(request):
    if not request.user.groups.filter(name='Dueños').exists():
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('inicio')

    filtro = request.GET.get('filtro', 'diario')
    hoy = timezone.localdate()
    historial_queryset = None

    if filtro == 'diario':
        historial_queryset = HistorialComanda.objects.filter(fecha__date=hoy)
    elif filtro == 'semanal':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        historial_queryset = HistorialComanda.objects.filter(fecha__date__gte=inicio_semana)
    elif filtro == 'mensual':
        historial_queryset = HistorialComanda.objects.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        )
    else:
        historial_queryset = HistorialComanda.objects.none()

    # Total de ventas del queryset completo (sin paginación)
    total_ventas = historial_queryset.aggregate(total=Sum('total'))['total'] or 0

    # Paginación
    page_number = request.GET.get('page')
    paginator = Paginator(historial_queryset.order_by('-fecha'), 13)
    historial = paginator.get_page(page_number)

    return render(request, 'core/reportes.html', {
        'historial': historial,
        'total_ventas': total_ventas,
        'filtro': filtro,
    })


@require_POST
@login_required(login_url='login')
def nueva_comanda(request):
    comanda = Comanda.objects.create(fecha=timezone.now(), estado='abierta', total=0)
    return redirect('venta')


@csrf_exempt
@require_POST
def verificar_superusuario(request):
    try:
        datos = json.loads(request.body)

        username = datos.get('username')
        password = datos.get('password')

        if not username or not password:
            return JsonResponse({
                'es_superusuario': False,
                'error': 'Usuario y contraseña son requeridos'
            }, status=400)

        user = authenticate(username=username, password=password)

        if user and (user.is_superuser or user.groups.filter(name='Dueños').exists()):
            return JsonResponse({
                'es_superusuario': True,
                'mensaje': 'Credenciales válidas'
            })

        return JsonResponse({
            'es_superusuario': False,
            'error': 'Credenciales incorrectas o no tiene privilegios de administrador'
        }, status=403)

    except Exception as e:
        return JsonResponse({
            'es_superusuario': False,
            'error': str(e)
        }, status=500)



# Comandas
@require_POST
@login_required(login_url='login')
def agregar_a_comanda(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))

    producto = get_object_or_404(Producto, id=producto_id)
    subtotal = cantidad * producto.precio

    detalle, creado = DetalleComanda.objects.get_or_create(comanda=comanda, producto=producto)
    if creado:
        detalle.cantidad = cantidad
        detalle.subtotal = subtotal
    else:
        detalle.cantidad += cantidad
        detalle.subtotal += subtotal
    detalle.save()

    comanda.total += subtotal
    comanda.fecha = timezone.now()
    comanda.save()

    return redirect('venta')


def api_usuario_detalle(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
        data = {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'date_joined': usuario.date_joined.strftime('%d/%m/%Y %H:%M'),
            'last_login': usuario.last_login.strftime('%d/%m/%Y %H:%M') if usuario.last_login else None,
            'is_active': usuario.is_active
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)


# Productos
@login_required(login_url='login')
def productos(request):
    if not request.user.groups.filter(name='Dueños').exists():
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('inicio')

    productos = Producto.objects.all()
    form = ProductoForm()

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)  
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" agregado exitosamente.')
            return redirect('productos')
        else:
            messages.error(request, 'Error al agregar el producto. Verifica los datos.')

    return render(request, 'core/productos.html', {
        'productos': productos,
        'form': form,
        'categorias': Categoria.objects.all(),
    })

@csrf_exempt
@login_required
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_categoria')
        if nombre:
            Categoria.objects.get_or_create(nombre=nombre)
    return redirect('productos')

@csrf_exempt
@login_required
def eliminar_categoria(request, categoria_id):
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, id=categoria_id)
        categoria.delete()
    return redirect('productos')


@login_required(login_url='login')
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('productos')

@require_POST
@login_required(login_url='login')
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    producto.nombre = request.POST.get('nombre')
    producto.precio = request.POST.get('precio')
    producto.descripcion = request.POST.get('descripcion')

    categoria_id = request.POST.get('categoria')
    if categoria_id:
        producto.categoria = Categoria.objects.get(id=categoria_id)
    else:
        producto.categoria = None

    borrar_imagen = request.POST.get('borrar_imagen')
    if borrar_imagen == '1':
        # Poner la imagen por defecto (o borrar la imagen actual)
        producto.imagen.delete(save=False)  # Borra archivo actual (opcional)
        producto.imagen = None  # Limpia campo para que use default en la plantilla

    elif 'imagen' in request.FILES:
        producto.imagen = request.FILES['imagen']

    producto.save()
    return redirect('productos')

@csrf_exempt
@login_required(login_url='login')
def guardar_comanda(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('DATA:', data)
            cliente_nombre = data.get('cliente')
            productos = data.get('productos')
            print('PRODUCTOS:', productos)
            estado = data.get('estado')
            metodo_pago = data.get('metodo_pago') or ''
            tipo_servicio = data.get('tipo_servicio') or ''
            monto_efectivo = data.get('monto_efectivo') or 0
            monto_tarjeta_debito = data.get('monto_tarjeta_debito') or 0
            monto_tarjeta_credito = data.get('monto_tarjeta_credito') or 0
            monto_transferencia = data.get('monto_transferencia') or 0
            print('EFECTIVO:', monto_efectivo, 'DEBITO:', monto_tarjeta_debito, 'CREDITO:', monto_tarjeta_credito, 'TRANSFERENCIA:', monto_transferencia)
            if not cliente_nombre or not productos or not estado:
                print('ERROR: Datos incompletos')
                return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
            total = sum(int(item['subtotal']) for item in productos)
            print('TOTAL:', total)
            efectivo = 0
            tarjetaD = 0
            tarjetaC = 0
            transferencia = 0
            if metodo_pago == 'efectivo':
                efectivo = total
            elif metodo_pago == 'tarjeta_debito':
                tarjetaD = total
            elif metodo_pago == 'tarjeta_credito':
                tarjetaC = total
            elif metodo_pago == 'transferencia':
                transferencia = total
            elif metodo_pago == 'mixto':
                efectivo = int(monto_efectivo) if monto_efectivo else 0
                tarjetaD = int(monto_tarjeta_debito) if monto_tarjeta_debito else 0
                tarjetaC = int(monto_tarjeta_credito) if monto_tarjeta_credito else 0
                transferencia = int(monto_transferencia) if monto_transferencia else 0
                suma = efectivo + tarjetaD + tarjetaC + transferencia
                print('SUMA:', suma)
                if suma != total:
                    print('ERROR: La suma de los montos no coincide con el total')
                    return JsonResponse({'status': 'error', 'message': 'La suma de los montos no coincide con el total'}, status=400)
            nota = data.get('nota_comanda')
            print('NOTA:', nota)
            comanda = Comanda.objects.create(
                nombre_cliente=cliente_nombre,
                estado=estado,
                total=total,
                empleado=request.user,
                metodo_pago=metodo_pago,
                tipo_servicio=tipo_servicio,
                monto_efectivo=efectivo,
                monto_tarjeta_credito=tarjetaC,
                monto_tarjeta_debito=tarjetaD,
                monto_transferencia=transferencia,
                nota=nota
            )
            print('COMANDA:', comanda)
            for item in productos:
                print('ITEM:', item)
                producto = Producto.objects.get(pk=item['productoId'])
                DetalleComanda.objects.create(
                    comanda=comanda,
                    producto=producto,
                    cantidad=item['cantidad'],
                    subtotal=item['subtotal']
                )
            if comanda.estado == 'cerrada':
                print('IMPRIMIENDO BOLETA Y COMANDA COCINA')
                
                # Imprimir boleta thermal de manera independiente
                try:
                    imprimir_boleta_thermal(comanda)
                    print('✅ BOLETA THERMAL COMPLETADA')
                except Exception as thermal_error:
                    print(f'❌ ERROR EN BOLETA THERMAL: {str(thermal_error)}')
                    # Continúa sin interrumpir
                
                # Imprimir comanda de cocina de manera independiente
                try:
                    imprimir_comanda_cocina(comanda)
                    print('✅ COMANDA COCINA COMPLETADA')
                except Exception as cocina_error:
                    print(f'❌ ERROR EN COMANDA COCINA: {str(cocina_error)}')
                    # Continúa sin interrumpir
            
            print('OK - Comanda guardada exitosamente')
            return JsonResponse({'status': 'ok', 'comanda_id': comanda.id})
        except Exception as e:
            print('ERROR EXCEPTION:', str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@login_required(login_url='login')
def comandas_json(request):
    # Obtén los IDs de las comandas en el historial
    ids_historial = set(HistorialComanda.objects.values_list('id', flat=True))
    comandas = Comanda.objects.all().order_by('-id')  # más recientes primero
    data = []
    for c in comandas:
        data.append({
            'id': c.id,
            'cliente': c.nombre_cliente or 'No asignado',
            'estado': c.estado,
            'es_historial': c.id in ids_historial  # <-- Indica si está en historial
        })
    return JsonResponse({'comandas': data})


# editar - eliminar comanda


@login_required
def comanda_detalle(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    detalles = DetalleComanda.objects.filter(comanda=comanda)

    data = {
        'id': comanda.id,
        'cliente': comanda.nombre_cliente or '',
        'total': comanda.total,
        'metodo_pago': comanda.metodo_pago,
        'tipo_servicio': comanda.tipo_servicio,
        'monto_efectivo': comanda.monto_efectivo,
        'monto_tarjeta_debito': comanda.monto_tarjeta_debito,
        'monto_tarjeta_credito': comanda.monto_tarjeta_credito,
        'monto_transferencia': comanda.monto_transferencia,
        'nota_comanda': comanda.nota or '',
        'detalles': [
            {
                'producto': d.producto.nombre,
                'producto_id': d.producto.id,
                'cantidad': d.cantidad,
                'subtotal': d.subtotal,
                'imagen': d.producto.imagen.url if d.producto.imagen else ''
            } for d in detalles
        ]

    }
    return JsonResponse(data)

@login_required
def historial_comanda_detalle(request, comanda_id):
    comanda = get_object_or_404(HistorialComanda, id=comanda_id)
    detalles = json.loads(comanda.detalles) if comanda.detalles else []

    data = {
        'id': comanda.id,
        'cliente': comanda.nombre_cliente or '',
        'total': comanda.total,
        'metodo_pago': comanda.metodo_pago,
        'tipo_servicio': comanda.tipo_servicio,
        'monto_efectivo': comanda.monto_efectivo,
        'monto_tarjeta_debito': comanda.monto_tarjeta_debito,
        'monto_tarjeta_credito': comanda.monto_tarjeta_credito,
        'monto_transferencia': comanda.monto_transferencia,
        'cerrado_por': comanda.cerrado_por.username if comanda.cerrado_por else '',
        'fecha': comanda.fecha.strftime('%d/%m/%Y %H:%M') if comanda.fecha else '',
        'nota_comanda': getattr(comanda, 'nota', ''),  # <-- agrega esto si tienes el campo
        'detalles': detalles,
    }
    return JsonResponse(data)

@require_http_methods(["POST"])
@login_required
def eliminar_comanda(request, comanda_id):
    try:
        data = json.loads(request.body)
        motivo = data.get('motivo')

        if not motivo:
            return JsonResponse({'status': 'error', 'message': 'Debe ingresar un motivo'}, status=400)

        comanda = get_object_or_404(Comanda, id=comanda_id)

        # Guardar en tabla de eliminaciones
        from .models import EliminacionComanda  # asegúrate que esté importado arriba

        EliminacionComanda.objects.create(
            comanda_id=comanda.id,
            nombre_cliente=comanda.nombre_cliente,
            total=comanda.total,
            motivo=motivo,
            eliminado_por=request.user
        )

        comanda.delete()
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def editar_comanda(request, id):
    try:
        data = json.loads(request.body)
        cliente = data.get('cliente')
        estado = data.get('estado')
        metodo_pago = data.get('metodo_pago')
        tipo_servicio = data.get('tipo_servicio')
        monto_efectivo = data.get('monto_efectivo') or 0
        monto_tarjeta_debito = data.get('monto_tarjeta_debito') or 0
        monto_tarjeta_credito = data.get('monto_tarjeta_credito') or 0
        monto_transferencia = data.get('monto_transferencia') or 0
        productos = data.get('productos', [])

        comanda = Comanda.objects.get(pk=id)

        # Eliminar detalles anteriores
        DetalleComanda.objects.filter(comanda=comanda).delete()

        # Agregar los nuevos detalles y calcular total
        total = 0
        for item in productos:
            producto = Producto.objects.get(pk=item['productoId'])
            cantidad = int(item['cantidad'])
            subtotal = int(item['subtotal'])
            DetalleComanda.objects.create(
                comanda=comanda,
                producto=producto,
                cantidad=cantidad,
                subtotal=subtotal
            )
            total += subtotal

        # Actualizar info general
        comanda.nombre_cliente = cliente
        comanda.estado = estado
        comanda.metodo_pago = metodo_pago
        comanda.tipo_servicio = tipo_servicio
        comanda.total = total

        # Asignar montos segun metodo
        if metodo_pago == 'efectivo':
            comanda.monto_efectivo = total
            comanda.monto_tarjeta_debito = 0
            comanda.monto_tarjeta_credito = 0
            comanda.monto_transferencia = 0
        elif metodo_pago == 'tarjeta_credito':
            comanda.monto_efectivo = 0
            comanda.monto_tarjeta_debito = 0
            comanda.monto_tarjeta_credito = total
            comanda.monto_transferencia = 0
        elif metodo_pago == 'tarjeta_debito':
            comanda.monto_efectivo = 0
            comanda.monto_tarjeta_debito = total
            comanda.monto_tarjeta_credito = 0
            comanda.monto_transferencia = 0
        elif metodo_pago == 'transferencia':
            comanda.monto_transferencia = total
            comanda.monto_efectivo = 0
            comanda.monto_tarjeta_debito = 0
            comanda.monto_tarjeta_credito = 0
        elif metodo_pago == 'mixto':
            efectivo = int(monto_efectivo) if monto_efectivo else 0
            tarjetaD = int(monto_tarjeta_debito) if monto_tarjeta_debito else 0
            tarjetaC = int(monto_tarjeta_credito) if monto_tarjeta_credito else 0
            transferencia = int(monto_transferencia) if monto_transferencia else 0

            if efectivo + tarjetaD + tarjetaC + transferencia != total:
                return JsonResponse({'status': 'error', 'message': 'La suma de los montos no coincide con el total'}, status=400)

            comanda.monto_efectivo = efectivo
            comanda.monto_tarjeta_debito = tarjetaD
            comanda.monto_tarjeta_credito = tarjetaC
            comanda.monto_transferencia = transferencia
        else:
            comanda.monto_efectivo = None
            comanda.monto_tarjeta_debito = None
            comanda.monto_tarjeta_credito = None
            comanda.monto_transferencia = None

        comanda.nota = data.get('nota_comanda')
        comanda.save()

        if comanda.estado == 'cerrada':
            # Imprimir boleta thermal de manera independiente
            try:
                imprimir_boleta_thermal(comanda)
                print(f"✅ Boleta thermal impresa exitosamente para comanda {comanda.id}")
            except Exception as thermal_error:
                print(f"❌ Error en boleta thermal para comanda {comanda.id}: {thermal_error}")
            
            # Imprimir comanda de cocina de manera independiente
            try:
                imprimir_comanda_cocina(comanda)
                print(f"✅ Comanda de cocina impresa exitosamente para comanda {comanda.id}")
            except Exception as cocina_error:
                print(f"❌ Error en comanda de cocina para comanda {comanda.id}: {cocina_error}")

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
@csrf_exempt
@login_required(login_url='login')
def cerrar_caja(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            admin_username = data.get('admin_username')

            # Verificamos que exista el usuario
            admin_user = User.objects.get(username=admin_username)

            # ⚠️ Verificar si existen comandas abiertas
            comandas_abiertas = Comanda.objects.filter(estado='abierta')
            if comandas_abiertas.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No se puede cerrar la caja: hay comandas abiertas. Debe cerrarlas o eliminarlas primero.'
                }, status=400)

            # Obtener todas las comandas cerradas
            comandas_cerradas = Comanda.objects.filter(estado='cerrada')

            for comanda in comandas_cerradas:
                detalles = DetalleComanda.objects.filter(comanda=comanda)
                lista_productos = []

                for detalle in detalles:
                    lista_productos.append({
                        'producto': detalle.producto.nombre,
                        'cantidad': detalle.cantidad,
                        'subtotal': detalle.subtotal
                    })

                # Guardar en historial
                HistorialComanda.objects.create(
                    fecha=comanda.fecha,
                    nombre_cliente=comanda.nombre_cliente,
                    empleado=comanda.empleado,
                    total=comanda.total,
                    metodo_pago=comanda.metodo_pago,
                    monto_efectivo=comanda.monto_efectivo,
                    monto_tarjeta_debito=comanda.monto_tarjeta_debito,
                    monto_tarjeta_credito=comanda.monto_tarjeta_credito,
                    monto_transferencia=comanda.monto_transferencia,
                    tipo_servicio=comanda.tipo_servicio,
                    detalles=json.dumps(lista_productos),
                    cerrado_por=admin_user  
                )

            # Eliminar todas las comandas
            Comanda.objects.all().delete()

            return JsonResponse({'status': 'ok'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@csrf_exempt
def verificar_y_eliminar_comanda(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('admin')
        password = data.get('pass')
        motivo = data.get('motivo')
        comanda_id = data.get('comanda_id')

        # Verificar usuario y contraseña
        user = authenticate(username=username, password=password)

        if user is None or (user.username != 'admin' and not user.groups.filter(name='Dueños').exists()):
            return JsonResponse({'success': False, 'error': 'Credenciales incorrectas o sin permisos.'})

        try:
            comanda = Comanda.objects.get(id=comanda_id)
        except Comanda.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comanda no encontrada.'})

        # Guardar registro de eliminación
        EliminacionComanda.objects.create(
            comanda_id=comanda.id,
            nombre_cliente=comanda.nombre_cliente,
            total=comanda.total,
            motivo=motivo,
            eliminado_por=user
        )

        comanda.delete()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@csrf_exempt
def verificar_admin_y_eliminar_comandas_eliminadas(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is None or (user.username != 'admin' and not user.groups.filter(name='Dueños').exists()):
            return JsonResponse({'success': False, 'error': 'Credenciales incorrectas o sin permisos.'})

        EliminacionComanda.objects.all().delete()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# Lista de meses en español
MESES_ES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]

def exportar_reportes_mes(request):
    hoy = datetime.today()
    año_actual = datetime.now().year

    try:
        mes = int(request.GET.get('mes', hoy.month))
        año = int(request.GET.get('año', hoy.year))
    except ValueError:
        mes = hoy.month
        año = hoy.year

    if request.GET.get('exportar') != '1':
        años = list(range(2020, max(año_actual + 1, 2031)))
        context = {
            'meses': MESES_ES,
            'años': años,
            'mes_seleccionado': mes,
            'año_seleccionado': año,
        }
        return render(request, 'core/exportar_reportes_mes.html', context)

    reportes = HistorialComanda.objects.filter(fecha__year=año, fecha__month=mes).order_by('fecha')

    wb = Workbook()
    ws = wb.active
    ws.title = f"Reportes_{año}_{mes:02d}"

    encabezados = ['ID', 'Fecha', 'Empleado', 'Cliente', 'Método de pago', 'Monto efectivo', 'Monto tarjeta debito', 'Monto tarjeta credito', 'Monto transferencia','Tipo de servicio', 'Cerrado por', 'Total'] 
    ws.append(encabezados)

    total_general = 0
    for reporte in reportes:
        fila = [
            reporte.id,
            reporte.fecha.strftime('%d/%m/%Y %H:%M') if reporte.fecha else '',
            reporte.empleado.username if reporte.empleado else '',
            reporte.nombre_cliente or '',
            reporte.metodo_pago or '',
            reporte.monto_efectivo or 0,
            reporte.monto_tarjeta_debito or 0,
            reporte.monto_tarjeta_credito or 0,
            reporte.monto_transferencia or 0,
            reporte.tipo_servicio or '',
            reporte.cerrado_por.username if reporte.cerrado_por else '',
            reporte.total or 0,
        ]
        ws.append(fila)
        total_general += reporte.total or 0

    ws.append([])  # fila vacía

    fila_total = ['','','','','','','','','Total General:', total_general]
    ws.append(fila_total)

    bold_font = Font(bold=True)
    for cell in ws[ws.max_row]:
        cell.font = bold_font

    nombre_mes = dict(MESES_ES).get(mes, f"{mes:02d}")
    filename = f"reportes_{nombre_mes}_{año}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response


def exportar_reportes_anual(request):
    hoy = datetime.today()
    año_actual = datetime.now().year
    
    try:
        año = int(request.GET.get('año', hoy.year))
    except ValueError:
        año = hoy.year

    if request.GET.get('exportar_anual') != '1':
        años = list(range(2020, max(año_actual + 1, 2031))) 
        context = {
            'años': años,
            'año_seleccionado': año,
        }
        return render(request, 'core/exportar_reportes_anual.html', context)

    reportes = HistorialComanda.objects.filter(fecha__year=año).order_by('fecha')

    wb = Workbook()
    ws = wb.active
    ws.title = f"Reportes_{año}"

    encabezados = ['ID', 'Fecha', 'Empleado', 'Cliente', 'Método de pago', 'Monto efectivo', 'Monto tarjeta debito','Monto tarjeta credito', 'Monto transferencia','Tipo de servicio', 'Cerrado por', 'Total'] 
    ws.append(encabezados)

    total_general = 0
    for reporte in reportes:
        fila = [
            reporte.id,
            reporte.fecha.strftime('%d/%m/%Y %H:%M') if reporte.fecha else '',
            reporte.empleado.username if reporte.empleado else '',
            reporte.nombre_cliente or '',
            reporte.metodo_pago or '',
            reporte.monto_efectivo or 0,
            reporte.monto_tarjeta_debito or 0,
            reporte.monto_tarjeta_credito or 0,
            reporte.monto_transferencia or 0,
            reporte.tipo_servicio or '',
            reporte.cerrado_por.username if reporte.cerrado_por else '',
            reporte.total or 0,
        ]
        ws.append(fila)
        total_general += reporte.total or 0

    ws.append([])  # fila vacía

    fila_total = ['','','','','','','','','Total General:', total_general]
    ws.append(fila_total)

    bold_font = Font(bold=True)
    for cell in ws[ws.max_row]:
        cell.font = bold_font

    filename = f"reportes_anual_{año}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response

def imprimir_boleta_thermal(comanda):
    hoy = timezone.localdate()
    n_diario = Comanda.objects.filter(fecha__date=hoy, estado='cerrada', id__lte=comanda.id).count()

    detalles = DetalleComanda.objects.filter(comanda=comanda)
    usuario = comanda.empleado.username if comanda.empleado else ''
    # Ajusta la fecha/hora a la zona horaria activa (Chile)
    fecha_chile = timezone.localtime(comanda.fecha)
    fecha_hora = fecha_chile.strftime('%d/%m/%Y %H:%M')

    ticket = ""
    ticket += "        Mata el hambre\n"
    ticket += "-"*32 + "\n"
    ticket += f"N interno: {comanda.id}\n"
    ticket += f"N diario: {n_diario}\n"
    ticket += f"Responsable: {usuario}\n"
    ticket += f"Fecha: {fecha_hora}\n"
    ticket += "-"*32 + "\n"
    # Eliminar encabezado de cantidad, orden y precio
    # ticket += f"{'Cant':<4} {'Orden':<20} {'Precio':>8}\n"
    # ticket += "-"*40 + "\n"
    max_width = 32
    for det in detalles:
        price_str = f"${det.subtotal:,.0f}"
        prod_str = f"{det.cantidad} x {det.producto.nombre}"
        avail_width = max_width - len(price_str) - 1
        if len(prod_str) > avail_width:
            # Buscar el último espacio antes del límite para no cortar palabras
            cut = prod_str[:avail_width].rfind(' ')
            if cut == -1:
                cut = avail_width
            first_line = prod_str[:cut]
            rest = prod_str[cut:].lstrip()
            ticket += f"{first_line:<{avail_width}}{price_str:>{len(price_str)+1}}\n"
            # Resto del nombre en líneas siguientes, sin cortar palabras
            words = rest.split()
            line = ''
            for word in words:
                if len(line) + len(word) + (1 if line else 0) <= max_width:
                    line += (' ' if line else '') + word
                else:
                    ticket += f"{line}\n"
                    line = word
            if line:
                ticket += f"{line}\n"
        else:
            ticket += f"{prod_str:<{avail_width}} {price_str:>{len(price_str)}}\n"
    ticket += "-"*32 + "\n"
    if getattr(comanda, 'nota', None):
        ticket += f"Nota: {comanda.nota}\n"
        ticket += "-"*32 + "\n"
    ticket += f"{'Total:':<25}"
    ticket += f"${comanda.total:,.0f}\n"
    ticket += "iva incluido\n"
    ticket += "-"*32 + "\n"
    ticket += f"{comanda.tipo_servicio}, {comanda.nombre_cliente}\n"
    ticket += "\n\n"

    # Imprimir en la impresora de clientes
    printer_name = "CAJA"
    try:
        print(f"[THERMAL] Intentando imprimir en: {printer_name}")
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Boleta", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, ticket.encode('utf-8'))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(f"[THERMAL] ✅ Boleta impresa exitosamente en {printer_name}")
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f"[THERMAL] ❌ Error al imprimir en {printer_name}: {str(e)}")
        raise

def comandas_eliminadas(request):
    if not request.user.groups.filter(name='Dueños').exists():
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('inicio')

    todas = EliminacionComanda.objects.all().order_by('-fecha_eliminacion')
    paginator = Paginator(todas, 50)  # 50 por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/comandas_eliminadas.html', {'comandas': page_obj})

def comandas_eliminadas_json(request):
    data = []
    for e in EliminacionComanda.objects.select_related('eliminado_por'):
        data.append({
            "comanda_id": e.comanda_id,
            "nombre_cliente": e.nombre_cliente,
            "total": e.total,
            "motivo": e.motivo,
            "fecha_eliminacion": e.fecha_eliminacion.strftime("%d/%m/%Y %H:%M"),
            "eliminado_por_nombre": e.eliminado_por.username if e.eliminado_por else "Desconocido",
        })
    return JsonResponse({"eliminadas": data})


@require_POST
@login_required
def reabrir_comanda(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id, estado='cerrada')
    comanda.estado = 'abierta'
    comanda.save()
    return JsonResponse({'status': 'ok'})



def imprimir_comanda_cocina(comanda):
    hoy = timezone.localdate()
    n_diario = Comanda.objects.filter(fecha__date=hoy, estado='cerrada', id__lte=comanda.id).count()
    detalles = DetalleComanda.objects.filter(comanda=comanda)
    usuario = comanda.empleado.username if comanda.empleado else ''
    fecha_chile = timezone.localtime(comanda.fecha)
    fecha_hora = fecha_chile.strftime('%d/%m/%Y %H:%M')

    ticket = ""
    ticket += f"N interno: {comanda.id}\n"
    ticket += f"N diario: {n_diario}\n"
    ticket += f"Fecha: {fecha_hora}\n"
    ticket += f"Responsable: {usuario}\n"
    ticket += "-"*32 + "\n"
    max_width = 32
    for det in detalles:
        prod_str = f"{det.cantidad} x {det.producto.nombre}"
        # Print product name, wrap if too long
        rest = prod_str
        while rest:
            ticket += f"{rest[:max_width]}\n"
            rest = rest[max_width:]
    ticket += "-"*32 + "\n"
    if getattr(comanda, 'nota', None):
        ticket += f"Nota: {comanda.nota}\n"
        ticket += "-"*32 + "\n"
    ticket += f"{comanda.tipo_servicio}, {comanda.nombre_cliente}\n"
    ticket += "\n\n"

    # Imprimir en la impresora de cocina
    printer_name = "COCINA"
    try:
        print(f"[COCINA] Intentando imprimir en: {printer_name}")
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Comanda Cocina", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, ticket.encode('utf-8'))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(f"[COCINA] ✅ Comanda impresa exitosamente en {printer_name}")
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f"[COCINA] ❌ Error al imprimir en {printer_name}: {str(e)}")
        raise        

@require_POST
@login_required
def imprimir_boleta_ventas_dia(request):
    from django.utils import timezone
    import win32print

    hoy = timezone.localdate()
    numero_turno = 1  # Cambia esto según tu lógica de turnos

    ventas = HistorialComanda.objects.filter(fecha__date=hoy)
    total_venta = 0
    total_pedidos = ventas.count()
    metodos = {}

    for v in ventas:
        metodo = (v.metodo_pago or "Otros").strip().lower()
        if metodo == "mixto":
            if hasattr(v, "monto_efectivo") and v.monto_efectivo:
                metodos["Efectivo"] = metodos.get("Efectivo", 0) + v.monto_efectivo
            if hasattr(v, "monto_tarjeta_debito") and v.monto_tarjeta_debito:
                metodos["Tarjeta Debito"] = metodos.get("Tarjeta Debito", 0) + v.monto_tarjeta_debito
            if hasattr(v, "monto_tarjeta_credito") and v.monto_tarjeta_credito:
                metodos["Tarjeta Credito"] = metodos.get("Tarjeta Credito", 0) + v.monto_tarjeta_credito
            if hasattr(v, "monto_transferencia") and v.monto_transferencia:
                metodos["Transferencia"] = metodos.get("Transferencia", 0) + v.monto_transferencia
        elif metodo == "efectivo":
            metodos["Efectivo"] = metodos.get("Efectivo", 0) + (getattr(v, "monto_efectivo", 0) or v.total or 0)
        elif metodo == "tarjeta_debito":
            metodos["Tarjeta Debito"] = metodos.get("Tarjeta Debito", 0) + (getattr(v, "monto_tarjeta_debito", 0) or v.total or 0)
        elif metodo == "tarjeta_credito":
            metodos["Tarjeta Credito"] = metodos.get("Tarjeta Credito", 0) + (getattr(v, "monto_tarjeta_credito", 0) or v.total or 0)
        elif metodo == "transferencia":
            metodos["Transferencia"] = metodos.get("Transferencia", 0) + (getattr(v, "monto_transferencia", 0) or v.total or 0)
        else:
            nombre = v.metodo_pago.strip().title() if v.metodo_pago else "Otros"
            metodos[nombre] = metodos.get(nombre, 0) + v.total
        total_venta += v.total

    usuario = request.user.username if request.user.is_authenticated else 'Sistema'
    fecha_hora = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')

    ticket = ""
    ticket += f"Resumen de venta: {hoy.strftime('%d/%m/%Y')}\n"
    ticket += "-"*32 + "\n"
    ticket += "Resumen de Boletas, Transbank y otros:\n"
    for metodo, monto in metodos.items():
        ticket += f"{metodo:<22}${monto:,.0f}\n"
    ticket += "-"*32 + "\n"
    ticket += f"Total venta: ${total_venta:,.0f}\n"
    ticket += f"{'Total de pedidos del dia:':<30}{total_pedidos}\n"
    ticket += "-"*32 + "\n"
    # Centrar la fecha al final
    ticket += f"{fecha_hora:^{32}}\n"
    ticket += "\n\n"

    # Imprimir en una impresora específica
    printer_name = "CAJA"  # Cambia por el nombre de la impresora que quieras usar
    try:
        print(f"[CAJA] Intentando imprimir en: {printer_name}")
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ventas del Día", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, ticket.encode('utf-8'))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(f"[CAJA] ✅ Reporte de ventas impreso exitosamente en {printer_name}")
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f"[CAJA] ❌ Error al imprimir en {printer_name}: {str(e)}")
        # No hacer raise aquí para que no interrumpa la respuesta HTTP

    return HttpResponse("Boleta de ventas del día enviada a la impresora.")

@csrf_exempt
@login_required
def imprimir_boleta_comanda(request, comanda_id):
    if request.method == 'POST':
        try:
            comanda = Comanda.objects.get(id=comanda_id)
            imprimir_boleta_thermal(comanda)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@csrf_exempt
@login_required
def imprimir_boleta_cocina_view(request, comanda_id):
    if request.method == 'POST':
        try:
            comanda = Comanda.objects.get(id=comanda_id)
            imprimir_comanda_cocina(comanda)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})