SISTEMA DE INFORMACIÓN ACADÉMICO ADMINISTRATIVO FINANCIERO
==========================================================

Proyecto desarrollado por la **Subdirección de Desarrollo de Software** que pertenece
a la **Unidad de Telecomunicaciones e Información** de la [Universidad Nacional de Loja](http://www.unl.edu.ec)

Módulos
-------
- Talento humano
- Recaudación
- Planificacón

Requisitos
----------
1. Instalar los siguientes paquetes de forma global.
    
    ```
    # Python 3.5+
    
    sudo apt-get install python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev
    sudo apt-get install python-dev python-pip python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
    sudo apt-get install libpq-dev
    sudo apt-get install python3-dev
    
    sudo apt-get install nodejs
    sudo apt-get install nodejs-legacy
    sudo apt-get install npm
    
    Instalar manejador de versiones de node
    sudo npm install -g n
    sudo n 10.11.0
    sudo n
    selecciono la version  a utilizar
    # Se actualiza automaticamente la versión de node (10.11.0) y npm (6.4.1
)
    
    sudo npm install -g @angular/cli
    sudo npm install -g bower
    
    # Paquetes actualmente no utilizados
    #pip install scrapy
    #pip install django-cors-headers
    #pip install django-translation-manager
    ```

2. Crear una BD para el proyecto siaaf. Para desarrollo la BD nombrarla con los siguientes datos:
   
    ```
    nombre: siaaf
    usuario: siaaf
    clave: siaaf
    ```

3. Instalar un entorno virtual para la ejeción del backend del proyecto siaaf.
    # Python 3.5.2
    
    # Con VirtualenvWraaper
    sudo apt-get install virtualenvwrapper
    mkvirtualenv -p /usr/bin/python3 siaafenv
    #activar entorno
    workon siaafenv
    
    # Con virtualenv
    virtualenv siaafenv --python=python3
    #activar entorno virutalenv
    source siaafenv/bin/activate

Instalación Frontend
-----------

1. Instalar los paquetes detallados en el package.json. Ejecutar el comando desde
el directorio static:
    
    ```
    npm install
    ```

2. Coopilamos los archivos estaticos de angular desde el directorio static
   
    Opción 1: Coopilamos los archivos de ts a js
    
    ```
        npm run tsc
    ```
    Opción 2: Coopilamos los archivos de ts a js y que se coopilen automaticamente cuando se cambia algun archivo 
   
    ```
    npm run tsc:w
    ```
     
3. Coopilamos archivos stylus. Es un preprocesador que se utiliza la optimización  y edición de archivos css, 
el cual nos permite crear nuestros estilos de forma rápida.

    La instalación se basa en nodejs
    ```
    sudo npm install stylus -g
    ```

    Se lo instala globalmente para poder vincularlo desde pycharm mediante el comando stylus
    ```
    stylus -c -w *.styl
    ```
    
    Coompilar los archivos del siaaf. Dichos comandos daran como resultado los archivos .css
    ```
    stylus static/src/styles.styl
    stylus static/src/css/estilo-bst.styl
    stylus static/src/css/estilo-general.styl
    stylus static/src/css/estilo-reportes.styl
    ```

Instalación Backend
-----------
1. Activar en entorno virtual y posterior acceder a la carpeta siaaf. Este paso es 
esencial para los pasos posteriores:
    
    ```
    source directorio-entorno-virtual/bin/activate
    ```
    
2. Instalar paquetes necesarios para el backend del proyecto detallados en el archivo requerimientos_pip.txt:
    
    ```
    pip install -r requerimientos_pip
    ```

3. Ejecutamos los archivos estaticos del Django:
    
    ```
    bower install
    python manage.py collectstatic
    ```

4. Inicializamos las migraciones en la BD con el ORM de Django:
    
    ```
    python manage.py makemigrations titulacion academico alumni bienes cientifica configuracion contabilidad curricular docencia edificios organico perfil seguridad planificacion talento_humano unesco core  recaudacion
    python migrate
    ```


Datos Iniciales
----------------

1. Cargamos datos iniciales. Ejecutar dentro del shell del entorno virtual. El usuario admin o super 
usuario se genera al momento de cargar los datos inciales
    
    ```
    from app.core import util
    util.cargar_datos_iniciales()
    ```

2. Si el caso lo requiere para crear los tokens, ejecutar la siguiente instrucción para cada usuario.
   
    ```
    Token.objects.create(user=user)
    ```

Levantar aplicación para desarrollo
------------------------

1. Activar en entorno virtual
   
    ```
   source directorio-entorno-virtual/bin/activate
   ```

2. Levantar django. El manage.py utiliza por defecto el **siaa/settings/development.py** donde 
estan los datos de conección a la BD
   
    ```
    python manage.py runserver
    ```
   
    Si el caso lo requiere, ejecutar con un settings específico
   
    ```
    python manage.py runserver --settings=siaa.settings.production
    ```
   
3. Desde el directorio de static, levantar angular. Para desarrollo se trabaja con package.json y 
el servidor lite-server
   
    ```
    npm start
    ```



Levantar aplicación para producción
-------
**Le levanta la aplicación con GUNICORN y NGINX tanto el backend y frontend con https**

1. Generar certificados dentro del directorio de nginx
   
    ```
    /etc/nginx/ssl/server.crt
    /etc/nginx/ssl/server.key
    ```
2. En la ruta de aplicacion de nginx sites-available, crear un archivo de configuración ejemplo siaaf.conf: 
   
    ```
    /etc/nginx/sites-available/siaaf.conf
    ```

3. Crear un enlace simbólico del siaaf.conf en el directorio sites-enabled: 
   
    ```
    /etc/nginx/sites-enabled/siaaf.conf
    ```
    
4. En el archivo siaaf.conf configurar para que la parte static de Django y Angular se ejecuten desde nginx con https
 
    ***Ejemplo acceso por URL***
    ```
    Django: https://dominio.unl.edu.ec:8091
    Angular: https://dominio.unl.edu.ec
    ```
    ***Configuración***
    ```
    # DJANGO SIAAF
    server {
        listen 8091 default ssl;
        server_name dominio.unl.edu.ec;
        client_max_body_size 4G;
    
        ssl on;
        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
    
        location /static/ {
            alias /ruta-proyecto/siaa/staticfiles/;
        }
    
        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            if (!-f $request_filename) {
                #EJECUTADO POR GUNICORN
                proxy_pass http://dominio.unl.edu.ec:8000;
                break;
            }
        }
    }
    
    # ANGULAR SIAAF
    server {
        listen 443;
        server_name  dominio.unl.edu.ec;
    
        ssl on;
        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
    
        location / {
            root   /ruta-proyecto/siaa/static;
            index  index.html;
            try_files $uri /index.html;
        }
    }
    ```

5. Crear el archivo siaa/settings/production.py y modificar los datos según sea necesario***
    ```
    from .base import *
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'siaaf',
            'USER': 'siaaf',
            'PASSWORD': 'siaaf',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
    
6- Levantar servidor
    A. Con Gunicorn como servicio
        Se asume creado un usuario del sistema siaaf y virtualenvwrapper
        y la ruta del proyecto en /home/siaaf/siaaf (comprobar archivo wsgi)
        - Crear archivo /etc/systemd/system/siaaf_service.service
        
        '''
        [Unit]
        Description=siaaf
        After=network.target
        
        [Service]
        User=siaaf
        Environment=PYTHONUNBUFFERED=true
        WorkingDirectory=/home/siaaf/siaaf
        ExecStart=/home/siaaf/.virtualenvs/siaafenv/bin/gunicorn --workers 4 --timeout 60 -b 127.0.0.1:8000 siaaf.wsgi
        Restart=always
        RestartSec=3
        
        [Install]
        WantedBy=default.target
        '''
        
        - Recargar systemd daemon e iniciar servicio siaaf:

        sudo systemctl daemon-reload
        sudo systemctl start siaaf_service
        sudo systemctl enable siaaf_service
    
    
    B. Con gunicorn por comando de shell
        ```
        gunicorn siaa.wsgi:application --bind dominio.unl.edu.ec:8000
        ```

7. Acceder a las urls del proyecto del BANCKEND (django) y FRONTEND (angular.io).
    ```
    Backend: https://dominio.unl.edu.ec:8091
    Frontend: https://dominio.unl.edu.ec
    ```
8. Para acceder al Api del SIAAF (https://siaaf.unl.edu.ec) desde el SGA (consumir los BSG), se habilito en el archivo /etc/nginx/nginx.conf en la variable 
ssl_protocols el TLSv1, ya que el servidor del SGA esta actualmente trabajando con una versión
 antigua de OpenSSL 0.9.8o 01 Jun 2010. Si posterior se cambia el servidor SGA y el openssl esta en su versión actual,
 el siaaf debe recibir en el request el parametro verify=False.

    ```
    response = requests.request("GET", UrlSiaaf, headers, verify=False)
    ```

Levantar aplicación con SSL para django
---

1. Verificar que estén en:

    ```
    INSTALLED_APPS = (
        …
        ‘djangosecure’,
        ‘sslserver’
        …
    )
    ```
    
2. Levantar el servidor con los certificados previamente ya creados.
 
    ```
    python manage.py runsslserver --cert /etc/nginx/ssl/server.crt --key /etc/nginx/ssl/server.key
    ```

Instalar Celery
---

- Descargar e instalar redis como servicio

    
    wget http://download.redis.io/releases/redis-5.0.5.tar.gz
    tar xzf redis-4.0.8.tar.gz
    cd redis-5.0.5
    make
    sudo make install    // para instalar globalmente
    redis-server  // iniciar el servicio
    redis-cli ping // comprobar con el servidor activo redis, la respuesta que obtenemos es PONG 
    

- En el entorno


    pip install redis
    pip install celery
    pip install django-celery-beat
    
- Copiar de development.py a produccition.py
    
    
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = "America/Guayaquil"

- Agregar a aplicaciones instaladas


    INSTALLED_APPS = [
        ...
        'django_celery_beat',
    ]
    
- migrar django_celerey_beat
   
    
    python manage.py migrate
    
    
- Crear tareas programadas en admin de django , y ejecutar procesos de backend 2 terminales separadas


    celery -A siaa beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    celery -A siaa worker -l info
    