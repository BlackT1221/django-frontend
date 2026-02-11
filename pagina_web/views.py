from django.shortcuts import render
from firebase_admin import firestore, auth
from config.firebase_connection import initialize_firebase

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