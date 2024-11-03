import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import *
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator


def admin_or_secretaria_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user_type = request.user.tipousuario.idtipousuario
        if user_type == 1 or user_type == 2:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('404')
    return _wrapped_view_func

def admin_jefe_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user_type = request.user.tipousuario.idtipousuario
        if user_type == 1 or user_type == 3:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('404')
    return _wrapped_view_func


def admin_or_secretaria_or_jefe_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user_type = request.user.tipousuario.idtipousuario
        if user_type == 1 or user_type == 2 or user_type == 3:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('404')
    return _wrapped_view_func

def admin_or_abogado_or_jefe_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user_type = request.user.tipousuario.idtipousuario
        if user_type == 1 or user_type == 4 or user_type == 3:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('404')
    return _wrapped_view_func

@login_required
def vista404(request):
    return render(request, 'SIGEA_APP/404.html')


@login_required
def index(request):
    user_type = request.user.tipousuario.idtipousuario
    context = {'pruebita': user_type}

    if request.method == 'POST':
        # Cambiar el estado de una actividad
        actividad_id = request.POST.get('actividad_id')
        nuevo_estado = request.POST.get('nuevo_estado')

        if actividad_id and nuevo_estado:
            try:
                actividad = Actividades.objects.get(pk=actividad_id)
                actividad.estadoactividad_id = nuevo_estado
                actividad.save()
            except Actividades.DoesNotExist:
                pass  # Manejar el error según sea necesario

    if user_type == 1:  # Administrador
        # Obtener las actividades programadas
        actividades_programadas = Actividades.objects.all().order_by('fechaactividad')

        # Obtener los departamentos y las evaluaciones por departamento
        departamentos = Departamentos.objects.all()
        evaluaciones_por_departamento = []
        evaluaciones_data = []
        for departamento in departamentos:
            evaluaciones = Evaluacion.objects.filter(idusuario__idservicio__iddepartamento=departamento)
            evaluaciones_por_departamento.append({
                'departamento': departamento.divisiondepartamento,
                'evaluaciones': evaluaciones
            })
            # Datos para el gráfico
            evaluaciones_data.append({
                'departamento': departamento.divisiondepartamento,
                'evaluaciones_count': evaluaciones.count()
            })

        # Datos para el gráfico de actividades
        actividades_data = [
            {'actividad': actividad.nombreactividad, 'fecha': actividad.fechaactividad.strftime('%Y-%m-%d')}
            for actividad in actividades_programadas
        ]

        # Agregar los datos al contexto
        context.update({
            'actividades_programadas': actividades_programadas,
            'evaluaciones_por_departamento': evaluaciones_por_departamento,
            'evaluaciones_data': evaluaciones_data,
            'actividades_data': actividades_data,
            'estados': EstadoActividad.objects.all()  # Para los botones de cambio de estado
        })

        return render(request, 'SIGEA_APP/admin/index.html', context)

    # Otros tipos de usuarios
    elif user_type == 2:  # Secretaria
        return render(request, 'SIGEA_APP/secretaria/index.html', context)
    
    elif user_type == 3:  # Jefe de departamento
        return render(request, 'SIGEA_APP/jefe_departamento/index.html', context)
    
    elif user_type == 4:  # Abogado
        return render(request, 'SIGEA_APP/abogado/index.html', context)
    
    else:
        return redirect('login')


@login_required
@csrf_exempt
def actualizar_estado_actividad(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_actividad = data.get('idActividad')
            nuevo_estado_id = data.get('nuevoEstado')

            actividad = Actividades.objects.get(idactividad=id_actividad)
            nuevo_estado = EstadoActividad.objects.get(idestado=nuevo_estado_id)

            # Actualizamos el estado de la actividad
            actividad.estadoactividad = nuevo_estado
            actividad.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

 
 
 
def login_V(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'registration/login.html', {'error_message': 'Datos Incorrectos'})
    return render(request, 'registration/login.html')

def exit(request):
    logout(request)
    return redirect('login')

#Perfil de usuario
@login_required
def edit_profile(request):
    user_type = request.user.tipousuario.idtipousuario
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    context = {
        'pruebita': user_type,
        'form': form
    }
    
    return render(request, 'SIGEA_APP/CRUD_USUARIOS/edit_profile.html', context)



@require_POST
@admin_or_secretaria_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    return JsonResponse({'success': True})



@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_or_secretaria_required # Decorador para permitir solo a los administradores y secretarias acceder a la vista
def usuario_list(request):
    user_type = request.user.tipousuario.idtipousuario  # Obtener el tipo de usuario
    query = request.GET.get('q', '')  # Obtener el valor del parámetro 'q' de la URL
    departamento_id = request.GET.get('departamento', None)  # Obtener el valor del parámetro 'departamento' de la URL

    usuarios = Usuario.objects.all().select_related('idservicio__iddepartamento')

    if query:
        usuarios = usuarios.filter(Q(nombre__icontains=query) | Q(apellido__icontains=query))

    if departamento_id:
        usuarios = usuarios.filter(idservicio__iddepartamento__iddepartamento=departamento_id)

    departamentos = Departamentos.objects.all()  # Obtener todos los departamentos para el filtro

    paginator=Paginator(usuarios,7)
    pagina = request.GET.get("page") or 1
    posts = paginator.get_page(pagina)

    context = {
        'pruebita': user_type,
        'usuarios': usuarios,
        'query': query,
        'page_obj':posts,
        'departamentos': departamentos,
        'selected_departamento': int(departamento_id) if departamento_id else None,
    }
    return render(request, 'SIGEA_APP/CRUD_USUARIOS/usuario_list.html', context)

@login_required
@csrf_exempt
@admin_or_secretaria_required
def usuario_create(request):
    if request.method == 'POST':
        
        #ALLAN ESTUVO AQUI, CORREO DE CONFIRMACIÖN DE CREACIÖN DE USUARIO
        subject = "¡Excelente! Se ha creado un usuario"
        message ="Ahora formas parte de nuestra empresa, LANS LAW GLOBAL está feliz de tenerte, tus credenciales son:\nCorreo: "+request.POST["email"]+"\nContraseña: "+request.POST["password"]
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[request.POST["email"]]
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = UsuarioForm()
        if 'departamento_id' in request.GET:
            departamento_id = request.GET.get('departamento_id')
            if departamento_id:
                servicios = Servicios.objects.filter(iddepartamento=departamento_id)
                departamento = Departamentos.objects.get(pk=departamento_id)
                return JsonResponse({
                    'servicios': list(servicios.values('idservicio', 'nombreservicio')),
                    'division': departamento.divisiondepartamento
                })
    return render(request, 'SIGEA_APP/CRUD_USUARIOS/usuario_form.html', {'form': form})

@login_required
@csrf_exempt
@admin_or_secretaria_required
def usuario_update(request, idusuario):
    usuario = get_object_or_404(Usuario, idusuario=idusuario)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = UsuarioForm(instance=usuario)
        initial_data = {
            'divisiondepartamento': usuario.idservicio.iddepartamento.divisiondepartamento if usuario.idservicio else ''
        }
        form.initial.update(initial_data)
    return render(request, 'SIGEA_APP/CRUD_USUARIOS/usuario_form.html', {'form': form})

def usuario_detail(request, idusuario):
    usuario = get_object_or_404(Usuario, idusuario=idusuario)
    return render(request, 'SIGEA_APP/CRUD_USUARIOS/usuario_detail.html', {'usuario': usuario})

@login_required
@csrf_exempt
@admin_or_secretaria_required
def usuario_delete(request, idusuario):
    usuario = get_object_or_404(Usuario, idusuario=idusuario)
    if request.method == 'POST':
        usuario.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

#Views para departamentos
@login_required
@admin_jefe_required
def departamento_list(request):
    departamentos = Departamentos.objects.all()
    user_type = request.user.tipousuario.idtipousuario
    # Si estás renderizando los datos de los departamentos
    
    context = []
    for depto in departamentos:
        responsable = depto.responsabledepartamento  # Ya es un objeto Usuario
        context.append({
            'iddepartamento': depto.iddepartamento,
            'divisiondepartamento': depto.divisiondepartamento,
            'responsable_nombre': responsable.nombre if responsable else 'Sin responsable',
            'responsable_apellido': responsable.apellido if responsable else '',
            'responsable_email': responsable.email if responsable else 'N/A'
        })

    return render(request, 'SIGEA_APP/CRUD_DEPARTAMENTOS/departamento_list.html', {'departamentos': context, 'pruebita': user_type})

@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_jefe_required
def departamento_create(request): #Vista para crear un usuario
    if request.method == 'POST': #Si el método es POST, se crea un formulario con los datos del usuario.
        form = DepartamentosForm(request.POST) #Se crea un formulario con los datos del usuario.
        if form.is_valid(): #Si el formulario es válido, se guarda el usuario en la base de datos.
            form.save() #Se guarda el usuario en la base de datos.
            return JsonResponse({'success': True}) #Se retorna un JSON con el mensaje de éxito.
        else:
            return JsonResponse({'success': False, 'errors': form.errors}) #Si el formulario no es válido, se retorna un JSON con el mensaje de error.
    else:
        form = DepartamentosForm()
    return render(request, 'SIGEA_APP/CRUD_DEPARTAMENTOS/departamento_form.html', {'form': form}) #Si el método no es POST, se muestra el formulario para crear un usuario.

@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_jefe_required
def departamento_update(request, iddepartamento):
    departamento = get_object_or_404(Departamentos, iddepartamento=iddepartamento)
    if request.method == 'POST':
        form = DepartamentosForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DepartamentosForm(instance=departamento)
    return render(request, 'SIGEA_APP/CRUD_DEPARTAMENTOS/departamento_form.html', {'form': form})

@admin_jefe_required
def departameto_detail(request, iddepartamento):
    departamento = get_object_or_404(Departamentos, iddepartamento=iddepartamento)
    responsable = departamento.responsabledepartamento
    context = {
        'departamento': departamento,
        'responsable_nombre': responsable.nombre if responsable else 'Sin responsable',
        'responsable_apellido': responsable.apellido if responsable else '',
        'responsable_email': responsable.email if responsable else 'N/A'
    }
    return render(request, 'SIGEA_APP/CRUD_DEPARTAMENTOS/departamento_detail.html', context)


@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_jefe_required
def departamento_delete(request, iddepartamento):
    departamento = get_object_or_404(Departamentos, iddepartamento=iddepartamento)
    if request.method == 'POST':
        departamento.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


#Views para servicios
@login_required
@admin_jefe_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
def servicio_list(request):
    user_type = request.user.tipousuario.idtipousuario
    
    # Obtener el departamento desde la URL o un formulario
    departamento_id = request.GET.get('departamento_id')

    
    if departamento_id:
        servicios = Servicios.objects.filter(iddepartamento=departamento_id)
    else:
        servicios = Servicios.objects.all()
    
    departamentos = Departamentos.objects.all()  # Obtener todos los departamentos para el filtro

    paginator=Paginator(servicios,3)
    pagina = request.GET.get("page") or 1
    posts = paginator.get_page(pagina)
    
    context = {
        'pruebita': user_type,
        'servicio': servicios,
        'page_obj': posts,
        'departamentos': departamentos,  # Pasar departamentos al contexto
        'selected_departamento_id': departamento_id,  # Pasar el departamento seleccionado al contexto
    }
    
    return render(request, 'SIGEA_APP/CRUD_SERVICIO/servicio_list.html', context)


@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_jefe_required
def servicio_create(request): #Vista para crear un usuario
    if request.method == 'POST': #Si el método es POST, se crea un formulario con los datos del usuario.
        form = ServiciosForm(request.POST) #Se crea un formulario con los datos del usuario.
        if form.is_valid(): #Si el formulario es válido, se guarda el usuario en la base de datos.
            form.save() #Se guarda el usuario en la base de datos.
            return JsonResponse({'success': True}) #Se retorna un JSON con el mensaje de éxito.
        else:
            return JsonResponse({'success': False, 'errors': form.errors}) #Si el formulario no es válido, se retorna un JSON con el mensaje de error.
    else:
        form = ServiciosForm()
    return render(request, 'SIGEA_APP/CRUD_SERVICIO/servicio_form.html', {'form': form}) #Si el método no es POST, se muestra el formulario para crear un usuario.

@login_required
@csrf_exempt
@admin_jefe_required
def servicio_update(request, idservicio):
    servicio = get_object_or_404(Servicios, idservicio=idservicio)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ServiciosForm(instance=servicio)
    return render(request, 'SIGEA_APP/CRUD_SERVICIO/servicio_form.html', {'form': form})

@login_required
@admin_jefe_required
def servicio_detail(request, idservicio):  # Usamos idusuario aquí #Vista para ver los detalles de un usuario
    servicios = get_object_or_404(Servicios, idservicio=idservicio)  # y aquí también #Se obtiene el usuario a mostrar.
    return render(request, 'SIGEA_APP/CRUD_SERVICIO/servicio_detail.html', {'servicios': servicios}) #Se renderiza la plantilla usuario_detail.html con los datos del usuario.

@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_jefe_required
def servicio_delete(request, idservicio):  # Usamos idusuario aquí #Vista para eliminar un usuario
    servicios = get_object_or_404(Servicios	, idservicio=idservicio)  # y aquí también #Se obtiene el usuario a eliminar.
    if request.method == 'POST': #Si el método es POST, se elimina el usuario de la base de datos.
        servicios.delete() #Se elimina el usuario de la base de datos.
        return JsonResponse({'success': True}) #Se retorna un JSON con el mensaje de éxito.
    return JsonResponse({'success': False}) #Si el método no es POST, se retorna un JSON con el mensaje de error.


#ACTIVIDADES
@login_required
def actividades(request):
    user_type = request.user.tipousuario.idtipousuario
    actividades = Actividades.objects.all()
    usuarios = Usuario.objects.all()
    
    context = {
        'pruebita': user_type,
        'actividades': actividades,
        'usuarios': usuarios
    }
    
    return render(request, 'SIGEA_APP/CRUD_EVENT/event.html', context)

@login_required
@csrf_exempt
@admin_or_secretaria_required
def actividades_list_template(request):
    user_type = request.user.tipousuario.idtipousuario  # Obtener el tipo de usuario
    
    actividades = Actividades.objects.all()
    
    estados = EstadoActividad.objects.all()

    query = request.GET.get('q', None)
    if query:
        actividades = Actividades.objects.filter(nombreactividad__icontains=query)
    else:
        actividades = Actividades.objects.all()

    # Paginación
    paginator = Paginator(actividades, 8)
    page_number = request.GET.get("page") or 1
    posts = paginator.get_page(page_number)
    
    context = {
        'pruebita': user_type,
        'estados': estados,
        'page_obj':posts,
        'actividades': actividades,
    }
    return render(request, 'SIGEA_APP/CRUD_EVENT/actividades_list.html', context)

def actividades_list(request):
    actividades = Actividades.objects.all()
    actividades_json = []
    
    for acti in actividades:
        invitados = invitados_actividad.objects.all()  # Obtener todos los invitados de la actividad
        invitados_list = []
        for invitado in invitados:
            if acti == invitado.idactividad:
                invitados_list.append({
                'nombre': invitado.idusuario.nombre,
                'apellido': invitado.idusuario.apellido,
            })
        
        actividades_json.append({
            'title': acti.nombreactividad,
            'start': acti.fechaactividad.isoformat(),
            'end': acti.fechafin.isoformat(),
            'description': acti.descripcionactividad,
            'typeact': acti.tipoactividad,
            'idacti': acti.idactividad,
            'invitados': invitados_list,
            'archivoactividad': acti.docanexoactividad.url if acti.docanexoactividad else None,  # Añadir URL del archivo
        })
    
    return JsonResponse(actividades_json, safe=False)


@csrf_exempt
def actividades_create(request):
    if request.method == 'POST':
        nombreactividad = request.POST.get('nombreactividad')
        tipoactividad = request.POST.get('tipoactividad')
        descripcionactividad = request.POST.get('descripcionactividad')
        fechaactividad = request.POST.get('fechaactividad')
        fechafin = request.POST.get('fechafin')
        invitados_ids = request.POST.getlist('invitadosactividad')
        usuario = get_object_or_404(Usuario, email=request.user.email)

        # Manejo del archivo
        archivoactividad = request.FILES.get('docanexoactividad')
        
        nuevo_evento = Actividades(
            nombreactividad=nombreactividad, 
            descripcionactividad=descripcionactividad, 
            fechaactividad=fechaactividad, 
            tipoactividad=tipoactividad, 
            idusuario=usuario, 
            fechafin=fechafin,
            docanexoactividad=archivoactividad  # Asegúrate de que este campo esté en el modelo
        )
        nuevo_evento.save()

        for invitado_id in invitados_ids:
            invitado = invitados_actividad(idactividad=nuevo_evento, idusuario_id=invitado_id)
            invitado.save()
            #ALLAN ESTUVO AQUI, CORREO DE CONFIRMACIÖN DE CREACIÖN DE USUARIO
            subject = "Se te ha invitado a una Actividad"
            message = "Se le informa que ha sido invitado a participar en la actividad "+request.POST['nombreactividad']+", la actividad se llevará acabo desde: \nInicio: "+request.POST['fechaactividad']+"\nFin: "+request.POST['fechafin']+"\n¡TE ESPERAMOS!"
            email_from=settings.EMAIL_HOST_USER
            recipient_list=[invitado.idusuario.email] #QUE PENDEJO EL QUE LO CAMBIÓ EN EL MODELO Y NO LE AVISÓ A NADIE
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        return JsonResponse({'success': True, 'message': 'Has creado un evento exitosamente'})
    else:
        return JsonResponse({'success': False, 'message': 'La solicitud debe ser de tipo POST'})

@login_required
@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_or_secretaria_required # Decorador para permitir solo a los administradores y secretarias acceder a la vista
def cambiar_estado(request, idactividad):
    if request.method == 'POST':
        try:
            nuevo_estado = get_object_or_404(EstadoActividad, idestado=request.POST.get('estado'))
            actividad = get_object_or_404(Actividades, idactividad=idactividad)
            #print(f'este es el estado que estoy guardando {nuevo_estado.idestado}')
            #print(f'este es el estado que estoy guardando {actividad.nombreactividad}' )
            #print(f'este es el estado que estoy guardando {actividad.estadoactividad}' )
            # Asignar el ID de estado correspondiente basado en el nuevo estado recibido
            actividad.estadoactividad = nuevo_estado
            #print(f'este es el estado que estoy guardando {actividad.estadoactividad}' )
            actividad.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})



@admin_or_secretaria_or_jefe_required
def search_users(request):
    query = request.GET.get('q')
    usuarios = Usuario.objects.filter(nombre__icontains=query) | Usuario.objects.filter(apellido__icontains=query)
    results = [{'id': usuario.idusuario, 'nombre': usuario.nombre, 'apellido': usuario.apellido} for usuario in usuarios]
    return JsonResponse(results, safe=False)

@csrf_exempt # Decorador para deshabilitar la protección CSRF
@admin_or_secretaria_or_jefe_required
def actividad_delete(request, idactividad):  # Usamos idusuario aquí #Vista para eliminar un usuario
    actividad = get_object_or_404(Actividades, idactividad=idactividad)  # y aquí también #Se obtiene el usuario a eliminar.
    if request.method == 'POST': #Si el método es POST, se elimina el usuario de la base de datos.
        invitados = invitados_actividad.objects.filter(idactividad_id=idactividad)
        for inv in invitados:
            inv.delete()
        actividad.delete() #Se elimina el usuario de la base de datos.
        return JsonResponse({'success': True}) #Se retorna un JSON con el mensaje de éxito.
    return JsonResponse({'success': False}) #Si el método no es POST, se retorna un JSON con el mensaje de error.


@csrf_exempt
@admin_or_secretaria_or_jefe_required
def actividades_update(request, idactividad):
    actividad = get_object_or_404(Actividades, idactividad=idactividad)

    if request.method == 'POST':
        data = request.POST.copy()
        invs = None
        if data.getlist('invitadosactividad'):
            invs = data.pop('invitadosactividad')
        
        # Guardamos una referencia al archivo actual
        archivo_actual = actividad.docanexoactividad

        # Cargar el formulario con datos y archivos (si se ha subido uno nuevo)
        form = ActividadesForm(data, request.FILES, instance=actividad)

        if form.is_valid():
            # Eliminar archivo antiguo si hay un archivo nuevo
            if 'docanexoactividad' in request.FILES:
                if archivo_actual:
                    archivo_actual.delete(save=False)  # Borrar el archivo anterior

                # Asignar el nuevo archivo al campo antes de guardar
                actividad.docanexoactividad = request.FILES['docanexoactividad']
            
            # Guardar la actividad con el nuevo archivo (si se proporcionó)
            actividad.save()

            # Actualizar invitados
            invitados = invitados_actividad.objects.filter(idactividad=actividad)
            for invitado in invitados:
                if not invs:
                    invitado.delete()
                elif str(invitado.idusuario.idusuario) not in invs:
                    invitado.delete()
            if invs:
                for i in invs:
                    i = int(i)
                    if not invitados_actividad.objects.filter(idactividad=actividad, idusuario_id=i).exists():
                        user_ex = Usuario.objects.get(idusuario=i)
                        nuevo_inv = invitados_actividad(idactividad=actividad, idusuario=user_ex)
                        nuevo_inv.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ActividadesForm(instance=actividad)
    return render(request, 'SIGEA_APP/CRUD_EVENT/editar_actividad.html', {'form': form})





@csrf_exempt
def recordatorio_create(request):
    if request.method == 'POST':
        nombrerecordatorio = request.POST.get('nombrerecordatorio')
        fecharecordatorio = request.POST.get('fecharecordatorio')
        descripcionrecordatorio = request.POST.get('descripcionrecordatorio')
        idactividad = request.POST.get('idactividad')
        idacti = Actividades.objects.get(idactividad=idactividad)

        # Crea un nuevo evento en la base de datos
        nuevo_recordatorio = Recordatorio(
            nombrerecordatorio=nombrerecordatorio, 
            descripcionrecordatorio=descripcionrecordatorio, 
            fecharecordatorio=fecharecordatorio,
            idactividad=idacti,
        )
        nuevo_recordatorio.save()
        # Devuelve una respuesta JSON indicando que la creación del evento fue exitosa
        return JsonResponse({'success': True, 'message':'Has creado un recordatorio exitosamente'})
    else:
        # Si la solicitud no es de tipo POST, devuelve un error
        return JsonResponse({'success': False, 'message': 'La solicitud debe ser de tipo POST'})

@login_required
@admin_jefe_required
@csrf_exempt
def evaluacion_list(request):
    user_type = request.user.tipousuario.idtipousuario
    query = request.GET.get('q', None)
    
    # Filtrar evaluaciones según el nombre o apellido del usuario
    if query:
        evaluaciones = Evaluacion.objects.filter(idusuario__nombre__icontains=query) | Evaluacion.objects.filter(idusuario__apellido__icontains=query)
    else:
        evaluaciones = Evaluacion.objects.all()
    
    # Paginación
    paginator = Paginator(evaluaciones, 7)
    page_number = request.GET.get("page") or 1
    posts = paginator.get_page(page_number)

    context = {
        'pruebita': user_type,
        'evaluaciones': evaluaciones,
        'page_obj':posts,
        'plandes': Plandesarrollo.objects.all()
    }
    
    return render(request, 'SIGEA_APP/CRUD_EVALUACIONES/evaluacion_list.html', context)


@login_required
@admin_jefe_required
@csrf_exempt
def evaluacion_create(request):
    jefe_departamento = request.user  # Asumiendo que el jefe de departamento es el usuario actual
    departamento = Departamentos.objects.filter(responsabledepartamento=jefe_departamento).first()
    user = request.user
    jefe_departamento = None
    
    if user.tipousuario.descripcion == 'Jefe de Departamento':
        jefe_departamento = user.idservicio.iddepartamento  # Ajustar según el modelo
    
    if request.method == 'POST':
        form = EvaluacionForm(request.POST, jefe_departamento=jefe_departamento)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EvaluacionForm(jefe_departamento=jefe_departamento)
        if jefe_departamento:
            departamento = jefe_departamento.divisiondepartamento
            cantidad_empleados = Usuario.objects.filter(idservicio__iddepartamento=jefe_departamento).count()
        else:
            departamento = None
            cantidad_empleados = None

    return render(request, 'SIGEA_APP/CRUD_EVALUACIONES/evaluacion_form.html', {
        'form': form,
        'departamento': departamento,
        'cantidad_empleados': cantidad_empleados
    })



@login_required
@csrf_exempt
def evaluacion_update(request, id):
    evaluacion = get_object_or_404(Evaluacion, idevaluacion=id)
    if request.method == 'POST':
        form = EvaluacionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EvaluacionForm(instance=evaluacion)
    return render(request, 'SIGEA_APP/CRUD_EVALUACIONES/evaluacion_form.html', {'form': form})

@login_required
@csrf_exempt
def evaluacion_delete(request, id):
    evaluacion = get_object_or_404(Evaluacion, idevaluacion=id)
    if request.method == 'POST':
        evaluacion.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': 'Método no permitido'})



@login_required
@csrf_exempt
@admin_jefe_required
def evaluacion_update(request, idevaluacion):
    evaluacion = get_object_or_404(Evaluacion, idevaluacion=idevaluacion)
    if request.method == 'POST':
        form = EvaluacionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EvaluacionForm(instance=evaluacion)
    return render(request, 'SIGEA_APP/CRUD_EVALUACIONES/evaluacion_form.html', {'form': form})

@login_required
@admin_jefe_required
def evaluacion_detail(request, idevaluacion):
    evaluacion = get_object_or_404(Evaluacion, idevaluacion=idevaluacion)
    return render(request, 'SIGEA_APP/CRUD_EVALUACIONES/evaluacion_detail.html', {'evaluacion': evaluacion})

@login_required
@csrf_exempt
@admin_jefe_required
def evaluacion_delete(request, idevaluacion):
    evaluacion = get_object_or_404(Evaluacion, idevaluacion=idevaluacion)
    if request.method == 'POST':
        if evaluacion.idplandes:
            evaluacion.idplandes.delete() 
        evaluacion.delete() 
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
@admin_jefe_required
def plandesarrollo_create(request, idevaluacion):
    if request.method == 'POST':
        eva = Evaluacion.objects.get(idevaluacion=idevaluacion)
        data = request.POST.copy()
        data['idevaluacion'] = eva
        DF = PlanDesarolloForm(data)
        if DF.is_valid():
            d = DF.save()
            eva.idplandes = d
            eva.save()
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    else:
        DesarolloForm = PlanDesarolloForm()
        user_type = request.user.tipousuario.idtipousuario
        context = {     
            'pruebita': user_type,
            'DesarolloForm': DesarolloForm
        }
    return render(request, 'SIGEA_APP/PLANESDES/plandesarrollo_create.html', context)

@login_required
@csrf_exempt
@admin_jefe_required
def plandesarrollo_update(request, idevaluacion, idplandes):
    plandes = Plandesarrollo.objects.get(idplandes=idplandes)
    if request.method == 'POST':
        eva = Evaluacion.objects.get(idevaluacion=idevaluacion)
        DF = PlanDesarolloForm(request.POST, instance=plandes)
        if DF.is_valid():
            d = DF.save()
            eva.idplandes = d
            eva.save()
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    else:
        DesarolloForm = PlanDesarolloForm(instance=plandes)
        user_type = request.user.tipousuario.idtipousuario
        context = {     
            'pruebita': user_type,
            'DesarolloForm': DesarolloForm
        }
    return render(request, 'SIGEA_APP/PLANESDES/plandesarrollo_update.html', context)

@login_required
@csrf_exempt
@admin_jefe_required
def plandesarollo_delete(request, idplandes):
    plan = get_object_or_404(Plandesarrollo, idplandes=idplandes)
    if request.method == 'POST':
        plan.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def casos_activos_cliente(request, cliente_id):
    # Asegúrate de que el filtro esté aplicando los estados "Iniciado" y "En proceso" correctamente.
    casos_activos = Caso.objects.filter(idCliente_id=cliente_id, estadoCaso__in=["Iniciado", "En proceso"])
    casos_data = list(casos_activos.values('idCaso', 'nombreCaso', 'descripcionCaso'))
    
    return JsonResponse({'casos': casos_data})

@login_required
@admin_or_secretaria_required
@csrf_exempt
def cliente_list(request):
    user_type = request.user.tipousuario.idtipousuario
    query = request.GET.get('q', '').strip()
    selected_tipocliente = request.GET.get('tipocliente', '')
    
    # Inicializa el queryset de clientes
    clientes = Cliente.objects.all()

    # Filtro por nombre si se ingresó un término de búsqueda
    if query:
        clientes = clientes.filter(nombre__icontains=query)

    # Filtro por tipo de cliente si se seleccionó uno
    if selected_tipocliente:
        clientes = clientes.filter(idTipo__idtipoCliente=selected_tipocliente)  # Usa `idTipo_id` para filtrar por clave foránea

    # Paginación
    paginator = Paginator(clientes, 7)
    page_number = request.GET.get("page") or 1
    posts = paginator.get_page(page_number)

    # Carga de los tipos de clientes para el filtro
    tipoclientes = TipoCliente.objects.all()

    # Contexto
    context = {
        'pruebita': user_type,
        'page_obj': posts,  # El queryset paginado
        'tipoclientes': tipoclientes,
        'selected_tipocliente': selected_tipocliente,
        'q': query,
    }

    return render(request, 'SIGEA_APP/CRUD_CLIENTE/cliente_list.html', context)

@login_required
@csrf_exempt
@admin_or_secretaria_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ClienteForm()
    return render(request, 'SIGEA_APP/CRUD_CLIENTE/cliente_form.html', {'form': form})

@login_required
@csrf_exempt
@admin_or_secretaria_required
def cliente_update(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'SIGEA_APP/CRUD_CLIENTE/cliente_form.html', {'form': form})

@login_required
@csrf_exempt
@admin_or_secretaria_required
def cliente_delete(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# CONTROL DE ASISTENCIA
@login_required
@csrf_exempt
def registroasistencia_list(request):
    user_type = request.user.tipousuario.idtipousuario  # Obtener el tipo de usuario
    usuario_id = request.GET.get('usuario_id')
    dia = request.GET.get('dia')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    # Filtrar los registros de asistencia
    registros = RegistroAsistencia.objects.all()

    # Obtener todos los usuarios (empleados)
    usuarios = Usuario.objects.all()

    # Aplicar filtro por usuario si está seleccionado
    if usuario_id:
        registros = registros.filter(empleado_id=usuario_id)

    # Filtrar por día, mes y año si están definidos
    if dia:
        registros = registros.filter(fecha__day=dia)
    if mes:
        registros = registros.filter(fecha__month=mes)
    if anio:
        registros = registros.filter(fecha__year=anio)

    # Paginación
    paginator = Paginator(registros, 7)
    page_number = request.GET.get("page") or 1
    posts = paginator.get_page(page_number)

    # Cargar el menú con pruebita (tipo de usuario)
    context = {
        'pruebita': user_type,  # Pasar el tipo de usuario al contexto
        'registros': registros,  # Registros filtrados
        'usuarios': usuarios,  # Lista de usuarios para el filtro
        'selected_usuario_id': usuario_id,  # Usuario seleccionado
        'page_obj':posts,
        'dia': dia,
        'mes': mes,
        'anio': anio,
    }

    return render(request, 'SIGEA_APP/CRUD_CONTROL_ASISTENCIAS/registroasistencia_list.html', context)



@csrf_exempt
def registroasistencia_create(request):
    if request.method == 'POST':
        form = RegistroAsistenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = RegistroAsistenciaForm()
    return render(request, 'SIGEA_APP/CRUD_CONTROL_ASISTENCIAS/registroasistencia_form.html', {'form': form})


@csrf_exempt
def registroasistencia_update(request, idregistro):
    registro = get_object_or_404(RegistroAsistencia, idregistro=idregistro)
    
    if request.method == 'POST':
        form = RegistroAsistenciaForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegistroAsistenciaForm(instance=registro)  # Cargar el registro existente

    return render(request, 'SIGEA_APP/CRUD_CONTROL_ASISTENCIAS/registroasistencia_form.html', {'form': form})


@require_POST
@csrf_exempt
def registroasistencia_delete(request, idregistro):
    registro = get_object_or_404(RegistroAsistencia, idregistro=idregistro)
    try:
        registro.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


#Views para Casos
@login_required
def caso_list(request):
    casos = Caso.objects.all()
    user_type = request.user.tipousuario.idtipousuario
    
    query = request.GET.get('q', None)

    if query:
        casos = Caso.objects.filter(idCliente__nombre__icontains=query)
    else:
        casos = Caso.objects.all()

    # Paginación
    paginator = Paginator(casos, 7)
    page_number = request.GET.get("page") or 1
    posts = paginator.get_page(page_number)

    context = {
        'pruebita': user_type,
        'caso': casos,
        'page_obj':posts,
    }
    
    return render(request, 'SIGEA_APP/CRUD_CASOS/caso_list.html', context)


@login_required
@csrf_exempt
def caso_create(request): #Vista para crear un caso
    if request.method == 'POST': #Si el método es POST, se crea un formulario con los datos del caso.
        form = CasoForm(request.POST) #Se crea un formulario con los datos del caso.
        if form.is_valid(): #Si el formulario es válido, se guarda el caso en la base de datos.
            form.save() #Se guarda el caso en la base de datos.
            return JsonResponse({'success': True}) #Se retorna un JSON con el mensaje de éxito.
        else:
            return JsonResponse({'success': False, 'errors': form.errors}) #Si el formulario no es válido, se retorna un JSON con el mensaje de error.
    else:
        form = CasoForm()
    return render(request, 'SIGEA_APP/CRUD_CASOS/caso_form.html', {'form': form}) #Si el método no es POST, se muestra el formulario para crear un caso.

@login_required
@csrf_exempt
def caso_update(request, idCaso):
    caso = get_object_or_404(Caso, idCaso=idCaso)
    if request.method == 'POST':
        form = CasoForm(request.POST, instance=caso)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CasoForm(instance=caso)
    return render(request, 'SIGEA_APP/CRUD_CASOS/caso_form.html', {'form': form})


def caso_detail(request, idCaso):
    caso = get_object_or_404(Caso, idCaso=idCaso)
    cliente = caso.idCliente
    context = {
        'caso': caso,
        'cliente_nombre': cliente.nombre if cliente else 'Sin cliente',
        'cliente_email': cliente.email if cliente else 'N/A'
    }
    return render(request, 'SIGEA_APP/CRUD_CASOS/caso_detail.html', context)

@login_required
@csrf_exempt
def caso_delete(request, idCaso):
    caso = get_object_or_404(Caso, idCaso=idCaso)
    if request.method == 'POST':
        caso.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})






