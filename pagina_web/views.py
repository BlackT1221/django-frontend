from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from config.firebase_connection import initialize_firebase
from functools import wraps
import requests
import os

# Inicializar la base de datos con firestore

db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Vamos a crear en firebase auth
            user = auth.create_user(
                email = email,
                password = password
            )

            # Crear en firestore

            db.collection('perfiles').document(user.uid).set({
                'email' : email,
                'uid' : user.uid,
                'rol' : 'aprendiz',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'registro.html', {'mensaje': mensaje})

# -- Logica para el inicio de sesion

# Decorador de seguridad

def login_required_firebase(view_func):
    """
    Este decorador personalizado, va a proteger nuestras
    vistas si el usuario no ha iniciado sesion.
    Si el UID no existe, lo va a enviar a iniciar sesion.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "Warning, no has iniciado sesion")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Logica para solicitarle a google la validacion

def iniciar_sesion(request):
    # Si ya esta loggeado, lo redirijo al dashboard

    if ('uid') in request.session:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        # Endpoint oficial de google 
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email" : email,
            "password" : password,
            "returnSecureToken" : True
        }

        try:
            # Peticion http al servicio de autenticacion de google

            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200:
                #Todo fue bien
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['idToken'] = data['idToken'] # Token temporal de acceso
                messages.success(request, f"✅ Acceso correcto al sistema")
                return redirect('dashboard')
            else:
                # Error: Analizar el error
                error_message = data.get('error', {}).get('message', 'UNKNOWN_ERROR')

                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS': 'La contraseña es incorrecta o el correo no es válido.',
                    'EMAIL_NOT_FOUND': 'Este correo no está registrado en el sistema.',
                    'USER_DISABLED': 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Demasiados intentos fallidos. Espere unos minutos.'
                }

                mensaje_usuario = errores_comunes.get(error_message, "Error de autenticacion, revisa tus credenciales")
                messages.error(request, mensaje_usuario)
        
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexion con el servidor")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    
    return render(request, 'login.html')

def cerrar_sesion(request):
    # Limpiar la sesion, y luego se redirige
    request.session.flush()
    messages.info(request, "Has cerrado sesion correctamente")
    return redirect('login')

@login_required_firebase # Verifica que el usuario esta loggeado
def dashboard(request):
    """
    Panel principal. Este solo es accesible si el decorador lo permite.
    Recuperar los datos de firestore.
    """

    uid = request.session.get('uid')
    datos_usuario = {}

    try:
        # Consulta a firestore usando nuestro SDK
        doc_ref = db.collection('perfiles').document(uid)
        doc = doc_ref.get()

        if doc.exists:
            datos_usuario = doc.to_dict()
        else:
            # Si entra en el auth pero no tiene un perfil en firestore, manejo el caso
            datos_usuario = {
                'email' : request.session.get('email'),
                'uid' :  request.session.get('uid'),
                'rol' : 'aprendiz',
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            }

    except Exception as e:
        messages.error(request, f"Error al cargar los datos de la BD: {e}")
    return render(request, 'dashboard.html', {'datos': datos_usuario})

@login_required_firebase
def listar_tareas(request):
    """
    READ: Recuperar las tareas del usuario desde firestore
    """

    uid = request.session.get('uid')
    tareas = []

    try:
        #Vamos a filtrar las tareas del usuario

        docs = db.collection('tareas').where('usuario_id', '==', uid).stream()
        for doc in docs:
            tarea = doc.to_dict()
            tarea['id'] = doc.id
            tareas.append(tarea)
    except Exception as e:
        messages.error(request, f"Hubo un error al obtener las tareas {e}")
    
    return render(request, 'tareas/listar.html', {'tareas' : tareas})

@login_required_firebase # Verifica que el usuario esta loggeado
def crear_tarea(request):
    """
    CREATE: Reciben los datos desde el formulario y se almacenan
    """
    if (request.method == 'POST'):
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        uid = request.session.get('uid')

        try:
            db.collection('tareas').add({
                'titulo': titulo,
                'descripcion': descripcion,
                'estado': 'Pendiente',
                'usuario_id': uid,
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })
            messages.success(request, "tarea creada con exito")
            return redirect('listar_tareas')
        except Exception as e:
            messsages.error(request, f"Error al crear la tarea {e}")
        
    return render(request, 'tareas/form.html')

@login_required_firebase # Verifica que el usuario esta loggeado
def eliminar_tarea(request, tarea_id):
    """
    DELETE: Eliminar un documento especifico por id
    """
    try:
        db.collection('tareas').document(tarea_id).delete()
        messages.success(request, "🗑️ Tarea eliminada.")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")

    return redirect('listar_tareas')
    
@login_required_firebase # Verifica que el usuario esta loggeado
def editar_tarea(request, tarea_id):
    """
    UPDATE: Recupera los datos de la tarea especifica y actualiza los campos en firebase
    """
    uid = request.session.get('uid')
    tarea_ref = db.collection('tareas').document(tarea_id)

    try:
        doc = tarea_ref.get()
        if not doc.exists:
            messages.error(request, "La tarea no existe")
            return redirect('listar_tareas')
        
        tarea_data = doc.to_dict()

        if tarea_data.get('usuario_id') != uid:
            messages.error(request, "No tienes permiso para editar esta tarea")
            return redirect('listar_tareas')
        
        if request.method == 'POST':
            nuevo_titulo = request.POST.get('titulo')
            nueva_desc = request.POST.get('descripcion')
            nuevo_estado = request.POST.get('estado')

            tarea_ref.update({
                'titulo': nuevo_titulo,
                'descripcion': nueva_desc,
                'estado': nuevo_estado,
                'fecha_actualizacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Tarea actualizada correctamente.")
            return redirect('listar_tareas')
    except Exception as e:
        messages.error(request, f"Error al editar la tarea: {e}")
        return redirect('listar_tareas')
    
    return render(request, 'tareas/editar.html', {'tarea': tarea_data, 'id': tarea_id})