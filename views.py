# capa de vista/presentación

#Alta de Usuarios
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
#

from app.models import Favourite  # Asegúrate de que esta importación es correcta
from .layers.persistence import repositories
from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .layers.transport.transport import getAllImages
from .layers.utilities.translator import fromRequestIntoCard , fromTemplateIntoCard # Importa la función para convertir datos en Card

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados que corresponden a las imágenes de la API y los favoritos del usuario, y los usa para dibujar el correspondiente template.
# si el opcional de favoritos no está desarrollado, devuelve un listado vacío.
############################
def home(request):
    # Obtener personajes de la API
    images_data = getAllImages()  # Asumiendo que esta función retorna una lista de imágenes
    images = [fromRequestIntoCard(image_data) for image_data in images_data]
    
    # Si el usuario está autenticado, obtenemos sus favoritos
    favourite_list = []
    if request.user.is_authenticated:
        favourite_list = services.getAllFavourites(request)  # Obtiene los favoritos del usuario

    if request.method == 'POST' and 'add_character' in request.POST:
        # Lógica para añadir el personaje a favoritos
        services.saveFavourite(request)
    
    return render(request, 'home.html', {
        'images': images,
        'favourite_list': favourite_list  # Asegura que los favoritos estén disponibles en el template
    })

##################################

##################################

def search(request):
    search_msg = request.POST.get('query', '')

    if search_msg != '':  # Si hay algo en la búsqueda
        # Obtener personajes de la API filtrados por el query
        images_data = getAllImages(search_msg)
        images = [fromRequestIntoCard(image_data) for image_data in images_data]

        # Obtener la lista de favoritos, si el usuario está autenticado
        favourite_list = []  # O aquí puedes cargar los favoritos desde la base de datos si es necesario

        return render(request, 'home.html', {
            'images': images,
            'favourite_list': favourite_list
        })
    else:
        return redirect('home')  # Si la búsqueda está vacía, redirige a la página principal

#################################

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    # Obtener los favoritos del usuario
    favourite_list = services.getAllFavourites(request)
    
    return render(request, 'favourites.html', { 'favourite_list': favourite_list })

@login_required
def saveFavourite(request):
    if request.method == 'POST':
        # Obtener los datos del formulario enviados desde el template home.html
        name = request.POST.get('name')
        url = request.POST.get('url')
        status = request.POST.get('status')
        last_location = request.POST.get('last_location')
        first_seen = request.POST.get('first_seen')
        
        # Crear un objeto 'Favourite' que corresponde al personaje a añadir a favoritos
        favourite = Favourite(
            name=name,
            url=url,
            status=status,
            last_location=last_location,
            first_seen=first_seen,
            user=request.user  # Asignar el usuario autenticado
        )

        # Guardar el favorito en la base de datos
        repositories.saveFavourite(favourite)

        # Redirigir a la página principal o a favoritos, dependiendo del flujo que prefieras
        return redirect('home')
    else:
        return redirect('home')

@login_required
def deleteFavourite(request):
    if request.method == 'POST':
        # Obtener el id del favorito a eliminar desde el formulario
        fav_id = request.POST.get('id')

        # Intentamos eliminar el favorito usando el id proporcionado
        if fav_id:
            # Llamamos al repositorio para eliminar el favorito
            success = repositories.deleteFavourite(fav_id)
            
            # Si la eliminación fue exitosa, redirigimos a la página de favoritos
            if success:
                return redirect('favoritos')
            else:
                # Si hubo un error (por ejemplo, el favorito no existe), podríamos mostrar un mensaje de error o redirigir
                return redirect('favoritos')  # O retornar un mensaje de error si es necesario
    else:
        return redirect('favoritos')
    
@login_required
def exit(request):
    # Cerrar la sesión del usuario
    logout(request)
    
    # Redirigir al usuario a la página de inicio o login después de cerrar sesión
    return redirect('index-page')  # Redirige a la página de inicio o podrías redirigir a 'login' si prefieres

#Alta de Usuarios
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Autentica al usuario inmediatamente después de registrar
            return redirect('home')  # Redirige a la página de inicio o a cualquier otra página
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
#
