# Django + Firebase Project (Nombre del Proyecto)

Este proyecto es una aplicación web desarrollada con el framework **Django**, estructurada bajo el patrón **MVT (Model-View-Template)** y conectada a los servicios de **Firebase**.

## 🚀 Estructura del Proyecto

* `config/`: Configuración principal del proyecto (settings, urls, wsgi).
* `pagina_web/`: Aplicación principal donde reside la lógica de negocio.
* `templates/`: Archivos HTML de la interfaz de usuario.
* `venv/`: Entorno virtual de Python (excluido en Git).

---

## 🛠️ Instalación y Configuración

Sigue estos pasos para replicar el entorno de desarrollo:

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd django-frontend
```

### 2. Crear y activar el entorno virtual

* `En Linux/macOS:`

```bash
python3 -m venv venv
source venv/bin/activate
```

* `En Windows:`

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno

Crea un archivo .env dentro de la carpeta **/config** basándote en el archivo **.env.example** y añade tus credenciales secretas.

### 5. Configuración de Firebase

Este proyecto requiere una llave de servicio de Firebase para funcionar:

* Descarga tu archivo **serviceAccountKey.json** desde la consola de Firebase.
* Colócalo en la ruta: **config/serviceAccountKey.json**.

Nota: Este archivo está protegido por el **.gitignore** y nunca debe subirse al repositorio. (Lo veremos en la siguiente sesion).

### 🏃 Ejecución
Una vez configurado todo, inicia el servidor de desarrollo:
```bash
python manage.py runserver
```
En linux y macOS cambiar por "python" por "python3".
La aplicación estará disponible en: http://127.0.0.1:8000/.

### Aclaraciones para la formacion:

Chicos, queda en ustedes si quieren clonar el repo, pero todo lo que esta aqui me lo pueden preguntar en la siguiente sesion sin problema, recuerden que la idea es ir haciendo un proyecto juntos, asi que no se me adelanten. Por ahora, solo deben tenerlo al dia con lo que hicimos en formacion. Happy coding a todos, un abrazo.