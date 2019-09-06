from django.contrib import admin
from django.urls import include
from django.urls import path

from siaa import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'admin/', admin.site.urls),
    path('autenticacion/', include('app.autenticacion.urls')),
    path('academico/', include('app.academico.urls')),
    path('cientifica/', include('app.cientifica.urls')),
    path('core/', include('app.core.urls')),
    path('hveterinario/', include('app.hveterinario.urls')),
    path('reporte/', include('app.reporte.urls')),
    path('organico/', include('app.organico.urls')),
    path('planificacion/', include('app.planificacion.urls')),
    path('seguridad/', include('app.seguridad.urls')),
    path('seguridad-informacion/', include('app.seguridad_informacion.urls')),
    path('talento-humano/', include('app.talento_humano.urls')),
    path('tesoreria/', include('app.tesoreria.urls')),

    # Url de api
    path('api/v1/bienes/', include('api.bienes.urls')),
    path('api/v1/configuracion/', include('api.configuracion.urls')),
    path('api/v1/core/', include('api.core.urls')),
    path('api/v1/curricular/', include('api.curricular.urls' )),
    path('api/v1/organico/', include('api.organico.urls')),
    path('api/v1/recaudacion/', include('api.recaudacion.urls')),
    path('api/v1/seguridad/', include('api.seguridad.urls')),
    path('api/v1/talento-humano/', include('api.talento_humano.urls')),

    #Url servicios externos
    path('api/v1/bsg/', include(('api.bsg.urls', 'api_bsg'))),
    path('api/v1/banco/', include(('api.banco.urls', 'api_banco'))),
    path('api/v1/eventos/', include(('api.eventos.urls', 'api_eventos'))),
    path('api/v1/google/', include(('api.google.urls', 'api_google'))),
    path('api/v1/ldap/', include(('api.ldap.urls', 'api_ldap'))),
    path('api/v1/sga/', include(('api.sga.urls', 'api_sga'))),
]
