#capa de servicio/lógica de negocio

from app.models import Favourite  # Asegúrate de que esta importación es correcta
from ..persistence import repositories
from django.contrib.auth import get_user
from ..transport.transport import getAllImages as get_data_from_api
from ..utilities.translator import fromRequestIntoCard

################################################################################################
def getAllImages(input=None):
    json_collection = get_data_from_api(input)  # Llama a la función de transport.py
    images = []  # Inicializa la lista de imágenes (Cards)

    # Recorre la colección de datos JSON crudos y crea objetos Card
    for item in json_collection:
        # Verifica si el objeto tiene la clave 'image'
        if 'image' in item:
            # Convierte el item en un objeto Card y agrégalo a la lista
            images.append(fromRequestIntoCard(item))
        else:
            print("[services.py]: Se encontró un objeto sin clave 'image', omitiendo...")

    # Aplica el filtro si se proporciona input
    if input:
        images = [image for image in images if input.lower() in image.name.lower()]

    return images

################################################################################################
# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    # Obtiene los datos del formulario (del template)
    name = request.POST.get('name')
    url = request.POST.get('url')
    status = request.POST.get('status')
    last_location = request.POST.get('last_location')
    first_seen = request.POST.get('first_seen')
    
    # Asignar el usuario actual
    user = request.user
    
    # Crear un objeto Card (o lo que se necesite) y guardarlo como favorito
    fav = Favourite(
        name=name,
        url=url,
        status=status,
        last_location=last_location,
        first_seen=first_seen,
        user=user
    )
    
    return repositories.saveFavourite(fav)  # Guardamos el favorito en la base de datos
###################################################################################################

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []  # Si no está autenticado, no muestra favoritos
    
    user = request.user
    favourite_list = repositories.getAllFavourites(user)  # Llamamos a la capa DAO para obtener favoritos

    return favourite_list  # Retorna la lista de favoritos para la vista

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.deleteFavourite(favId) # borramos un favorito por su ID.
