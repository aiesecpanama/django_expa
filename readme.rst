=========================================
Módulo de interacción con la API de EXPA
=========================================

Introducción
-------------

Este módulo está diseñado para manejar la autenticación y la obtención de datos de la API de EXPA a python, además de 

Instalación
-----------
1. Instalar el módulo utilizando en el proyecto principal el comando ``git submodule add https://github.com/camiloforero/django_expa.git``
2. Agregar el módulo (``django_expa``) a ``INSTALLED_APPS`` dentro del archivo ``settings.py``. Esto asegura que django detecte las migraciones de la base de datos
3. Ejecutar los comandos ``python manage.py makemigrations`` y ``python manage.py migrate``
4. Copiar el archivo example_settings.py a settings.py dentro del mismo directorio


Dependencias
------------
Este módulo requiere la instalación de ``requests``, instalar usando ``pip install requests``
También requiere BeautifulSoup4, bs4 y future, future

Configuración
-------------

El archivo de configuración ``settings.py`` tiene una constante, ``DEFAULT_ACCOUNT``. Esta debería tomar el valor del correo electrónico de login de EXPA de una persona que tenga los permisos adecuados (idealmente un MC member, o la API no va a funcionar de la manera correcta, más información en la sección de tips).

Además, se pueden agregar datos de login usando la interfaz de administrador de Django. Dentro de django_expa se agrega un nuevo Login Data, donde se pone el correo electrónico y la contraseña de la cuenta a utilizar. La contraseña será codificada automáticamente a base 64 cuando quede guardada, pero ya que puede ser recuperada fácilmente es recomendable que la persona que tiene acceso a este espacio sea de confianza.

Funcionamiento
--------------
In progress

Función de generar URL
ApiDocs: Url de los apidocs, mas consejo de utilizar la versión v2

Utilización
-----------

In progress
Importar
``from django_expa import expaApi``
``api = expaApi.ExpaApi()``
Opcional algumento para decidir que cuenta se va a utilizar, si no se utiliza la que está configurada por defecto

Uso del método _buildQuery()

Uso del método load_past_interactions

Tips
----
Respecto a las funcionalidades disponibles respecto a los permisos de la cuenta que se utilice

- Una cuenta que no tenga rol en EXPA no podrá utilizar la API
- Una cuenta con rol dentro de un comité local podrá ver en ``people`` a todas las personas de su LC, y dentro de applications las aplicaciones de las personas o TNs de las cuales es EP Manager
- Una cuenta con rol **no MC** podrá ver a todas las personas del país en ``people``, pero las aplicaciones también estarán restringidad a aquellas de las cuales es EP Manager
- Una cuenta con rol de MC podrá ver tanto a todas las personas como a todas las aplicaciones, sin importar si es EP/Opportunity Manager o no.

POSTMAN es una herramienta muy útil para jugar con la API de EXPA antes de escribir código
