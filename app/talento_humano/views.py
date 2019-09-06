# -*- coding: utf-8 -*-
import os
from datetime import datetime
from datetime import timedelta
from itertools import count

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from weasyprint import HTML, CSS

from app.cientifica.models import ProduccionCientifica
from app.configuracion.models import Planificacion, DetallePlanificacion
from app.core.utils import fecha
from app.core.utils.google import get_usuario
from app.core.models import Expediente, PeriodoFiscal, CatalogoItem, Persona, Direccion, Relacion
from app.core.utils.enums import MensajesEnum
from app.organico.models import UAA
from app.seguridad.models import Usuario
from app.talento_humano.forms import ActividadEsencialForm, DestrezaForm, ConocimientoForm, PuestoForm, \
    AsignacionDePuestoForm, CrearFuncionarioUsuarioForm, AsignacionDePuestoFuncionarioForm, \
    AsignacionDePuestoTerminacionForm, AgregarUsuarioForm, PersonaForm, UAAPuestoForm, AsignacionPuestoUAAPuestoForm, \
    DetallePlanificacionForm, AusentismoFuncionarioForm, AsignacionPuestoUAAPuestoPuroForm, \
    AsignacionDePuestoEditarForm, AsignacionDePuestoRenovacionForm, ReporteForm, RegistroVacacionesForm, \
    CompensacionDiasForm, ReporteVacacionesPeriodoForm, ReporteVacacionesPendientesForm, ReporteGeneral, \
    TrayectoriaLaboralExternaForm, EvaluacionDesempenioForm, FormacionAcademicaForm, InformacionBancariaForm, \
    DeclaracionBienesForm, CapacitacionForm
from app.talento_humano.models import Puesto, ActividadEsencial, Conocimiento, Destreza, AsignacionPuesto, \
    Vacaciones, UAAPuesto, RegistroVacaciones, Ausentismo, RegimenLaboral, GrupoOcupacional, CompensacionDias, \
    AusentismoFuncionario, TrayectoriaLaboralExterna, EvaluacionDesempenio, Funcionario, FormacionAcademica, \
    DeclaracionBienes, InformacionBancaria, Capacitacion
from app.reporte.utils.excel import generar_excel, retornar_excel

from app.reporte.utils import pdf as pdfUtil
#from django.db.models import Q
import csv
from django.db import connection
import xlwt
import requests
from io import BytesIO
from zipfile import ZipFile


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

##########################################################################################
# Inicio para refactorizar
##########################################################################################

@login_required
def index(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    return render(request, 'talento_humano/index.html', locals())


# <editor-fold desc="funcionarios">


@login_required
def funcionarios(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_funcionarios = Funcionario.buscar(filtro)
    else:
        lista_funcionarios = Funcionario.objects.all()
    paginator = Paginator(lista_funcionarios, numero_items)

    try:
        funcionarios = paginator.page(page)
    except PageNotAnInteger:
        funcionarios = paginator.page(1)
    except EmptyPage:
        funcionarios = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/funcionarios/index.html', locals())


@login_required
def cargar_fotografias(request):
    usuario = request.user
    if not usuario.is_admin:
        raise PermissionDenied
    funcionarios = Funcionario.objects.all()
    for funcionario in funcionarios:
        user_google = get_usuario(funcionario.usuario.nombre_de_usuario)
        if user_google:
            url = user_google.get('thumbnailPhotoUrl')
            if url:
                funcionario.usuario.foto_url = url
                funcionario.usuario.save()
    return HttpResponseRedirect(reverse('talento_humano:funcionarios.index'))


@login_required
def validar_email(request, id_funcionario):
    """
    valida si el email de un funcionario está registrado en google y actualiza la fotografía
    :param request:
    :param id_funcionario: El identificador del funcionario
    :return: La página principal del funcionario
    """
    user = request.user
    if not user.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)

    user_google = get_usuario(funcionario.usuario.nombre_de_usuario)
    if user_google:
        funcionario.usuario.google = True
        messages.warning(request, 'El email se ha encontrado')
        url = user_google.get('thumbnailPhotoUrl')
        if url:
            funcionario.usuario.foto_url = url

        funcionario.usuario.save()
    else:
        messages.warning(request, 'Email no encontrado')

    return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))


@login_required
def agregar_funcionario(request):
    """
    Funcionalidad que agrega un funcionario en modo inactivo, siempre y cuando se proporcione
    un número de cédula
    :param request:
    :return:
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    form2 = AgregarUsuarioForm()
    numero_documento = request.GET.get('numero_documento')

    if numero_documento:
        funcionario = Funcionario.objects.filter(usuario__persona__numero_documento=numero_documento).first()
        if funcionario:
            messages.warning(request, 'El funcionario ya existe')
        else:
            funcionario = Funcionario.get_funcionario_numero_documento(numero_documento)
            if not funcionario:
                messages.warning(request, 'Funcionario no pudo crearse')
                return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario.agregar_manual'))
            else:
                messages.success(request, 'Funcionario registrado con éxito')
                funcionario.usuario.persona.actualizar_datos_bsg()
        return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))
    else:
        messages.warning(request, 'Lo sentimos no ha ingresado parametros validos')
    return render(request, 'talento_humano/funcionarios/agregar.html', locals())


@login_required
def agregar_funcionario_manual(request):
    """
    Funcionalidad que agrega un funcionario en modo inactivo, siempre y cuando se proporcione
    un correo institucional
    :param request:
    :return:
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    form = PersonaForm()
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            persona = form.save(commit=False)
            correo_electronico_institucional = form.cleaned_data['correo_electronico_institucional']
            usuario = Usuario(persona=persona, correo_electronico_institucional=correo_electronico_institucional)
            if usuario.get_nombre_de_usuario():
                persona.save()
                usuario.persona = persona
                usuario.save()
                funcionario = Funcionario(usuario=usuario)
                funcionario.save()
                return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))

    return render(request, 'talento_humano/funcionarios/agregar-manual.html', locals())


# </editor-fold>

# <editor-fold desc="Perfil">

@login_required
def funcionario(request, id_funcionario):
    """
    Presenta la información de un determinado Usuario
    :param request:
    :param id_funcionario: El identificador del funcionario
    :return: La página principal del funcionario
    """
    user = request.user
    if not user.is_member('talento humano'):
        raise PermissionDenied

    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    usuario = funcionario.usuario
    try:
        usuario.persona.expediente
    except:
        expediente = Expediente(persona=usuario.persona)
        expediente.save()

    navegacion = ('Módulo de Talento Humano',
                  [('Talento Humano', reverse('talento_humano:index')),
                   ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                   ('Perfil de %s' % (usuario.persona.get_nombres_completos()), None)])

    return render(request, 'seguridad/usuario/informacion_detallada.html', locals())


@login_required
def actualizar_informacion_bsg(request, id_funcionario):
    """
    Actualiza la información de los servicios gubarnamentales como:
    * Registro Civil
    * SENESCYT
    * CONADIS
    Adicionalmente carga la fotografía del correo electrónico
    :param request:
    :param id_funcionario: identificador del funcionario
    :return:página principal del funcionario despues de registrar la información
    """
    user = request.user
    if not user.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    try:
        persona = funcionario.usuario.persona
        persona.actualizar_datos_bsg()
        funcionario.usuario.vincular_google()
        messages.success(request, 'Datos actualizados desde el bus de servicios gubarnamentales')
    except:
        messages.warning(request, 'No se pudo actualizar la información')
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))


def vincular_usuario_funcionario(request):
    """
    Funcionalidad que agrega un funcionario en modo inactivo, siempre y cuando se proporcione
    un correo institucional
    :param request:
    :return:
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    form = CrearFuncionarioUsuarioForm()
    if request.method == 'POST':
        form = CrearFuncionarioUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(usuario.persona.numero_documento)
            usuario.nombre_de_usuario = usuario.get_nombre_de_usuario()
            usuario.save()
            if usuario.get_nombre_de_usuario():
                funcionario = Funcionario(usuario=usuario)
                funcionario.save()
                messages.success(request, "Datos agregados correctamente")
                return render(request, 'talento_humano/index.html', locals())
        else:
            print('error')
    return render(request, 'talento_humano/funcionarios/vincular.html', locals())


@login_required
def funcionario_ver_uaa(request, id_funcionario):
    """
    Muestra uaa
    """
    user = request.user
    if not user.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    uaas = UAA.objects.filter(uaa=None)
    return render(request, 'talento_humano/funcionarios/funcionario/uaa.html', locals())


@login_required
def funcionario_uaa_puesto(request, id_funcionario, id_uaa_puesto):
    """
    Formulario para agregar un funcionario a determinado puesto
    """
    user = request.user
    if not user.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uaa_puesto)
    form = AsignacionPuestoUAAPuestoPuroForm()
    if request.method == 'POST':
        form = AsignacionPuestoUAAPuestoPuroForm(request.POST)
        if form.is_valid():
            asignacion_puesto = form.save(commit=False)
            asignacion_puesto.funcionario = funcionario
            asignacion_puesto.uaa_puesto = uaa_puesto
            codigo_duplicado = AsignacionPuesto.objects.filter(Q(funcionario=asignacion_puesto.funcionario) &
                                                               Q(codigo=asignacion_puesto.codigo)).first()
            if not codigo_duplicado:
                asignacion_puesto.save()
                asignacion_puesto.verificar_vigencia()
                messages.success(request, 'Asignación de puesto a funcionario')
                return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))
            else:
                messages.success(request, 'Código de la Asignación de Puesto ya existe')
        else:
            messages.warning(request, 'Por revise  los datos ingresados')
    return render(request, 'talento_humano/funcionarios/funcionario/funcionario-uaa-puesto.html', locals())


# </editor-fold>

# <editor-fold desc="Puestos">

@login_required
def puestos(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    lista_de_puestos = Puesto.objects.all()
    paginator = Paginator(lista_de_puestos, 25)  # Show 25 contacts per page
    page = request.GET.get('pagina')

    try:
        puestos = paginator.page(page)
    except PageNotAnInteger:
        puestos = paginator.page(1)
    except EmptyPage:
        puestos = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/puestos/index.html', locals())


@login_required
def buscar_puestos(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_de_puestos = Puesto.buscar(filtro)
    else:
        lista_de_puestos = Puesto.objects.all()
    paginator = Paginator(lista_de_puestos, numero_items)

    try:
        puestos = paginator.page(page)
    except PageNotAnInteger:
        puestos = paginator.page(1)
    except EmptyPage:
        puestos = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/puestos/index.html', locals())


@login_required
def puesto(request, id_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = get_object_or_404(Puesto, id=id_puesto)
    form_actividad = ActividadEsencialForm()
    form_destreza = DestrezaForm()
    form_conocimiento = ConocimientoForm()
    return render(request, 'talento_humano/puestos/ver.html', locals())


@login_required
def agregar_puesto(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    form = PuestoForm()
    if request.method == 'POST':
        form = PuestoForm(request.POST)
        if form.is_valid():
            puesto = form.save()
            return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(puesto.id,)))
    return render(request, 'talento_humano/puestos/agregar.html', locals())


@login_required
def editar_puesto(request, id_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = get_object_or_404(Puesto, id=id_puesto)
    form = PuestoForm(instance=puesto)
    if request.method == 'POST':
        form = PuestoForm(request.POST, instance=puesto)
        if form.is_valid():
            puesto = form.save()
            return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(puesto.id,)))
    return render(request, 'talento_humano/puestos/agregar.html', locals())


@login_required
def agregar_actividad(request, id_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = get_object_or_404(Puesto, id=id_puesto)
    if request.method == 'POST':
        form_actividad = ActividadEsencialForm(request.POST)
        if form_actividad.is_valid():
            actividad = form_actividad.save(commit=False)
            actividad.puesto = puesto
            actividad.save()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def agregar_destreza(request, id_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = get_object_or_404(Puesto, id=id_puesto)
    if request.method == 'POST':
        form_destreza = DestrezaForm(request.POST)
        if form_destreza.is_valid():
            destreza = form_destreza.save(commit=False)
            destreza.puesto = puesto
            destreza.save()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def agregar_conocimiento(request, id_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = get_object_or_404(Puesto, id=id_puesto)
    if request.method == 'POST':
        form_conocimiento = ConocimientoForm(request.POST)
        if form_conocimiento.is_valid():
            conocimiento = form_conocimiento.save(commit=False)
            conocimiento.puesto = puesto
            conocimiento.save()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def eliminar_actividad(request, id_actividad):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    actividad = get_object_or_404(ActividadEsencial, id=id_actividad)
    id_puesto = actividad.puesto.id
    actividad.delete()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def eliminar_conocimiento(request, id_actividad):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    conocimiento = get_object_or_404(Conocimiento, id=id_actividad)
    id_puesto = conocimiento.puesto.id
    conocimiento.delete()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def eliminar_destreza(request, id_actividad):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    destreza = get_object_or_404(Destreza, id=id_actividad)
    id_puesto = destreza.puesto.id
    destreza.delete()
    return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,)))


@login_required
def asignar_puesto(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = Puesto()
    if request.method == 'POST':
        asigna_puesto = AsignacionPuesto()
        form_asignap = AsignacionDePuestoForm(request.POST, instance=asigna_puesto)
        if form_asignap.is_valid():
            asigna_puesto = form_asignap.save(commit=False)
            # asigna_puesto.puesto = puesto
            # asigna_puesto.funcionario = funcionario
            asigna_puesto.save()
            # return HttpResponseRedirect(reverse('talento_humano:puestos.puesto', args=(id_puesto,id_funcionario)))
    else:
        form_asignap = AsignacionDePuestoForm()
    return render(request,
                  'talento_humano/asignacion_puestos/asignar_puesto.html', locals())


@login_required
def editar_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    form = AsignacionDePuestoEditarForm(instance=asignacion_puesto)
    if request.method == 'POST':
        form = AsignacionDePuestoEditarForm(request.POST, instance=asignacion_puesto)
        if form.is_valid():
            asigna_puesto = form.save(commit=False)
            codigo_duplicado = AsignacionPuesto.objects.filter(Q(funcionario=asignacion_puesto.funcionario) &
                                                               Q(codigo=asignacion_puesto.codigo) &
                                                               ~Q(id=asignacion_puesto.id)).first()
            if not codigo_duplicado:
                asigna_puesto.save()
                messages.success(request, 'Asignación de puesto editada con éxito')
                return HttpResponseRedirect(
                    reverse('talento_humano:asignacion_puestos.funcionario', args=(asignacion_puesto.funcionario.id,)))
            else:
                messages.success(request, 'Código de la Asignación de Puesto ya existe')
    else:
        form_asignap = AsignacionDePuestoForm()
    return render(request,
                  'talento_humano/asignacion_puestos/editar_asignacion_puesto.html', locals())

# realiza la asignacion de un puesto a un funcionario especifico
@login_required
def asignar_puesto_funcionario(request, id_funcionario):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    puesto = Puesto()
    print(id_funcionario)
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    print('consulta', id_funcionario)
    if request.method == 'POST':
        asigna_puesto = AsignacionPuesto()
        form_asignap = AsignacionDePuestoFuncionarioForm(request.POST, instance=asigna_puesto)
        if form_asignap.is_valid():
            asigna_puesto = form_asignap.save(commit=False)
            # asigna_puesto.puesto = puesto
            asigna_puesto.funcionario = funcionario
            asigna_puesto.save()
            funcionario.activo = True
            funcionario.save()
            messages.success(request, "Funcionario activado correctamente")
            asigna_puesto.ubicar_funcionario()
            return render(request, 'talento_humano/funcionarios/index.html', locals())
    else:
        form_asignap = AsignacionDePuestoFuncionarioForm()
    return render(request,
                  'talento_humano/asignacion_puestos/asignar_puesto_funcionario.html', locals())


# </editor-fold>

# <editor-fold desc="Actividad científica">
@login_required
def agregar_produccion_cientifica(request, id_funcionario):
    """
        Agrega registro de producción científica para un funcionario
        :param request:
        :param id_funcionario: identificador del funcionario
        :return: Página porincipal del funcionario una vez registrado la producción científica
        """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    usuario = funcionario.usuario
    try:
        expediente = usuario.persona.expediente
    except:
        expediente = Expediente()
        expediente.persona = usuario.persona
        expediente.save()
    try:
        produccion_cientifica = expediente.produccioncientifica
    except:
        produccion_cientifica = ProduccionCientifica()
        produccion_cientifica.expediente = expediente
        produccion_cientifica.save()
        messages.success(request, 'Producción científica creada con éxito')
    return HttpResponseRedirect(reverse('talento_humano:funcionarios.funcionario', args=(funcionario.id,)))
    # return render(request, 'talento_humano/funcionarios/funcionario/crear_capacitacion.html',
    #               locals())


# </editor-fold>

# <editor-fold desc="Asignación de puestos">
@login_required
def asignacion_de_puestos(request, id_funcionario):
    """
    Lista los puestos asignados a un funcionario
    :param request:
    :param id_funcionario: El identificador del funcionario
    :return:
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    try:
        funcionario = get_object_or_404(Funcionario, id=id_funcionario)
        lista_puestos = funcionario.asignaciones_puestos.all()
        paginator = Paginator(lista_puestos, 25)
        terminacion_form = AsignacionDePuestoTerminacionForm(prefix='terminacion')
        renovacion_form = AsignacionDePuestoRenovacionForm(prefix='renovacion')

        page = request.GET.get('pagina')

        try:
            puestos = paginator.page(page)
        except PageNotAnInteger:
            puestos = paginator.page(1)
        except EmptyPage:
            puestos = paginator.page(paginator.num_pages)

        print('puestos ' + puestos.get_duracion)

    except:
        print('no existen datos')
        # lista_de_puestos = AsginacionDePuesto()

    return render(request, 'talento_humano/asignacion_puestos/index.html', locals())


@login_required
def buscar_asignacion_puestos(request):
    """
    Busca un puesto asignado de acuerdo a un criterio ingresado
    :param request:
    :return: la página con el listado de asignación de puestos
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_asignacion_puestos = AsignacionPuesto.buscar(filtro)
    else:
        lista_asignacion_puestos = AsignacionPuesto.objects.all()
    paginator = Paginator(lista_asignacion_puestos, numero_items)

    try:
        asignacion_puestos = paginator.page(page)
    except PageNotAnInteger:
        asignacion_puestos = paginator.page(1)
    except EmptyPage:
        asignacion_puestos = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/asignacion_puestos/lista_asignacion_puestos.html', locals())


@login_required
def eliminar_asignacion_puesto(request, id_asignacion_puesto):
    """
    Elimina la asignación de un puesto
    :param request:
    :param id_asignacion_puesto: El identificador del puesto a eliminar
    :return: La página de listado de funcionarios
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    id_funcionario = asignacion_puesto.funcionario.id
    asignacion_puesto.delete()
    return HttpResponseRedirect(reverse('talento_humano:asignacion_puestos.funcionario', args=(id_funcionario,)))


@login_required
def listar_asignar_puesto(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    lista_asignacion_puestos = AsignacionPuesto.objects.all()
    paginator = Paginator(lista_asignacion_puestos, 25)  # Show 25 contacts per page
    page = request.GET.get('pagina')

    try:
        asignacion_puestos = paginator.page(page)
    except PageNotAnInteger:
        asignacion_puestos = paginator.page(1)
    except EmptyPage:
        asignacion_puestos = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/asignacion_puestos/lista_asignacion_puestos.html', locals())


@login_required
def verificar_vigencia_listar_asignar_puesto(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    lista_asignacion_puestos = AsignacionPuesto.objects.all()
    for asignacion_puestos in lista_asignacion_puestos:
        asignacion_puestos.verificar_vigencia()
    return HttpResponseRedirect(reverse('talento_humano:asignacion_puestos.lista'))


@login_required
def validar_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    asignacion_puesto.verificar_vigencia()
    # asignacion_puesto.funcionario.es_funcionario_activo()
    messages.success(request, 'Validación de asignación correcta')
    return HttpResponseRedirect(
        reverse('talento_humano:asignacion_puestos.funcionario', args=(asignacion_puesto.funcionario.id,)))


@login_required
def fijar_vigente_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    asignacion_puesto.fijar_vigente()
    messages.success(request, 'Validacion de asignación de puesto')
    return HttpResponseRedirect(
        reverse('talento_humano:asignacion_puestos.funcionario', args=(asignacion_puesto.funcionario.id,)))


@login_required
def terminacion_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    observacion_anterior = asignacion_puesto.observacion
    print('asignacion_puesto 2: ',asignacion_puesto.observacion)
    terminacion_form = AsignacionDePuestoTerminacionForm(instance=asignacion_puesto, prefix='terminacion')
    if request.method == 'POST':
        terminacion_form = AsignacionDePuestoTerminacionForm(request.POST, instance=asignacion_puesto,
                                                             prefix='terminacion')
        if terminacion_form.is_valid():
            asignacion_puesto = terminacion_form.save()
            if observacion_anterior:
                asignacion_puesto.observacion = observacion_anterior + " - " + asignacion_puesto.observacion
            asignacion_puesto.terminacion_asignacion_puesto()
    return HttpResponseRedirect(
        reverse('talento_humano:asignacion_puestos.funcionario', args=(asignacion_puesto.funcionario.id,)))


@login_required
def renovacion_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    renovacion_form = AsignacionDePuestoRenovacionForm(instance=asignacion_puesto, prefix='renovacion')
    if request.method == 'POST':
        renovacion_form = AsignacionDePuestoRenovacionForm(request.POST, prefix='renovacion')
        if renovacion_form.is_valid():
            print('=============================================')
            asignacion_puesto_renovado = renovacion_form.save(commit=False)
            asignacion_puesto_renovado.codigo = asignacion_puesto.codigo
            asignacion_puesto_renovado.tipo_relacion_laboral = asignacion_puesto.tipo_relacion_laboral
            asignacion_puesto_renovado.partida_presupuestaria = asignacion_puesto.partida_presupuestaria
            asignacion_puesto_renovado.partida_individual = asignacion_puesto.partida_individual
            asignacion_puesto_renovado.partida_individual_th = asignacion_puesto.partida_individual_th
            asignacion_puesto_renovado.uaa_puesto = asignacion_puesto.uaa_puesto
            asignacion_puesto_renovado.funcionario = asignacion_puesto.funcionario
            asignacion_puesto_renovado.ingreso_concurso = asignacion_puesto.ingreso_concurso
            asignacion_puesto_renovado.encargado = asignacion_puesto.encargado
            asignacion_puesto_renovado.save()
            asignacion_puesto_renovado.verificar_vigencia()
        else:
            messages.warning('Datos de formulario no validos')
    return HttpResponseRedirect(
        reverse('talento_humano:asignacion_puestos.funcionario', args=(asignacion_puesto.funcionario.id,)))


@login_required
def cambio_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    uaa_puestos = UAAPuesto.objects.filter(puesto=asignacion_puesto.uaa_puesto.puesto)
    return render(request, 'talento_humano/asignacion_puestos/cambio.html', locals())


@login_required
def registrar_cambio_asignacion_puesto(request, id_asignacion_puesto, id_uua_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion_puesto = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uua_puesto)
    asignacion_puesto.uaa_puesto = uaa_puesto
    asignacion_puesto.save()
    messages.success(request, 'Se cambio exitosamente de unidad académica administrativa')
    return HttpResponseRedirect(
        reverse('talento_humano:asignacion_puestos.funcionario.cambio', args=(id_asignacion_puesto,)))


# </editor-fold>

# <editor-fold desc="Vacaciones">

@login_required
def buscar_vacaciones(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_vacaciones = Vacaciones.buscar(filtro)
    else:
        lista_vacaciones = Vacaciones.objects.filter()
    paginator = Paginator(lista_vacaciones, numero_items)

    try:
        vacaciones = paginator.page(page)
    except PageNotAnInteger:
        vacaciones = paginator.page(1)
    except EmptyPage:
        vacaciones = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/vacaciones/index.html', locals())


@login_required
def listar_vacaciones(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    lista_vacaciones = Vacaciones.objects.filter()
    paginator = Paginator(lista_vacaciones, 25)
    page = request.GET.get('pagina')

    try:
        vacaciones = paginator.page(page)
    except PageNotAnInteger:
        vacaciones = paginator.page(1)
    except EmptyPage:
        vacaciones = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/vacaciones/index.html', locals())


@login_required
def generar_vacaciones(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    Vacaciones.generar_vacaciones()
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.index'))


@login_required
def periodo_vacaciones(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    periodo_fiscal = PeriodoFiscal.get_periodo_fiscal_actual()
    if periodo_fiscal:
        planificacion = Planificacion.objects.filter(codigo='VACACIONES_' + periodo_fiscal.nombre).first()
        if planificacion:
            form = DetallePlanificacionForm()
            if request.POST:
                form = DetallePlanificacionForm(request.POST)
                if form.is_valid():
                    detalle_planificacion = form.save(commit=False)
                    if detalle_planificacion.fecha_desde > detalle_planificacion.fecha_hasta:
                        messages.warning(request, 'La fecha desde no puede ser mayor que la fecha hasta')
                    else:
                        detalle_planificacion.codigo = detalle_planificacion.nombre
                        detalle_planificacion.planificacion = planificacion
                        detalle_planificacion.save()
                        form = DetallePlanificacionForm()
                        messages.success(request, 'Datos del detalle de planificación registrados con éxito')
                        return HttpResponseRedirect(reverse('talento_humano:vacaciones.periodo'))
                else:
                    messages.warning(request, 'Datos del detalle de la planificación no validos')
    return render(request, 'talento_humano/vacaciones/periodos.html', locals())


@login_required
def crear_periodo_vacaciones(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    periodo_fiscal = PeriodoFiscal.get_periodo_fiscal_actual()
    if periodo_fiscal:
        planificacion = Planificacion.objects.filter(codigo='VACACIONES_' + periodo_fiscal.nombre).first()
        if not planificacion:
            planificacion = Planificacion(codigo='VACACIONES_' + periodo_fiscal.nombre,
                                          nombre='Vacaciones ' + periodo_fiscal.nombre,
                                          descripcion='Periodo vacional del año ' + periodo_fiscal.nombre,
                                          fecha_desde=periodo_fiscal.fecha_inicio,
                                          fecha_hasta=periodo_fiscal.fecha_fin,
                                          activo=True)
            planificacion.save()
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.periodo'))


@login_required
def eliminar_detalle_periodo_vacaciones(request, id_detalle):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    detalle_planificacion = get_object_or_404(DetallePlanificacion, id=id_detalle)
    detalle_planificacion.delete()
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.periodo'))


@login_required
def vacaciones_detalle(request, id_vacaciones):
    fecha_hasta_mes = None
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    vacaciones = get_object_or_404(Vacaciones, id=id_vacaciones)
    funcionario = vacaciones.funcionario

    # periodo_vacaciones = funcionario.get_periodo_vacaciones(True)
    periodo_vacaciones = vacaciones.periodo_vacaciones
    periodo_fiscal = PeriodoFiscal.get_periodo_fiscal(today=periodo_vacaciones.fecha_inicio)
    planificacion = Planificacion.objects.filter(codigo='VACACIONES_' + periodo_fiscal.nombre).first()
    if planificacion:
        fecha_hasta_mes = planificacion.fecha_hasta + timedelta(days=30)
    # vacaciones = Vacaciones.get_vacaciones(funcionario=funcionario, periodo_vacaciones=periodo_vacaciones)
    if periodo_fiscal and vacaciones:
        form = RegistroVacacionesForm(prefix='registro_vacaciones')
        form_compensacion = CompensacionDiasForm(prefix='compensacion')
        if request.POST:
            form = RegistroVacacionesForm(request.POST, prefix='registro_vacaciones')
            form_compensacion = CompensacionDiasForm(request.POST, prefix='compensacion')
            if form.is_valid():
                registro_vacaciones = form.save(commit=False)
                registro_vacaciones.vacaciones = vacaciones
                detalle_planificacion_id = form.cleaned_data['detalle_planificacion']
                detalle_planificacion = None
                if detalle_planificacion_id:
                    detalle_planificacion = DetallePlanificacion.objects.get(id=int(detalle_planificacion_id.id))
                    registro_vacaciones.detalle_planificacion = detalle_planificacion

                if registro_vacaciones.fecha_inicio > registro_vacaciones.fecha_fin:
                    messages.warning(request, 'La fecha de fin no puede ser mayor que la fecha de inicio')
                else:
                    if registro_vacaciones.se_puede_generar_vacaciones(registro_vacaciones.fecha_inicio,
                                                                       registro_vacaciones.fecha_fin):
                        if registro_vacaciones.get_numero_dias() <= vacaciones.dias_pendientes:
                            if detalle_planificacion is None or (detalle_planificacion
                                                                 and registro_vacaciones.fecha_inicio.date() >= detalle_planificacion.fecha_desde
                                                                 and (
                                                                         registro_vacaciones.fecha_fin.date() <= detalle_planificacion.fecha_hasta or
                                                                         (
                                                                                 fecha_hasta_mes and registro_vacaciones.fecha_fin.date() <= fecha_hasta_mes))):
                                registro_vacaciones.fecha_fin = registro_vacaciones.fecha_fin + timedelta(hours=23,
                                                                                                          minutes=59,
                                                                                                          seconds=59)
                                registro_vacaciones.save()
                                vacaciones.reducir_dias_vacaciones(registro_vacaciones.get_numero_dias())
                                messages.success(request, 'Vacaciones registradas con éxito ')
                                return HttpResponseRedirect(
                                    reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))
                            else:
                                messages.warning(request,
                                                 'Las fechas ingresadas no están acordes al periodo seleccionado')
                        else:
                            messages.warning(request, 'No puede agregar dias de vacaciones, supero el máximo permitido')
                    else:
                        messages.warning(request,
                                         'No se puede generar vacaciones en las fechas seleccionadas. Ya existe un registro que incluye éstas fechas.')
            # registro de compensación de dias
            if form_compensacion.is_valid():
                compensacion_dias = form_compensacion.save(commit=False)
                compensacion_dias.vacaciones = vacaciones
                compensacion_dias.recalcular()
                compensacion_dias.save()
                vacaciones.recalcular_dias_pendientes()
                messages.success(request, 'Cmpensación de dias registradas con éxito ')
                return HttpResponseRedirect(
                    reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))
            messages.warning(request, 'Formulario no valido, revisar la información ingresada')
    return render(request, 'talento_humano/vacaciones/detalle.html', locals())


@login_required
def generar_vacacion_detalle_planificacion(request, id_detalle, id_vacacion):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    vacaciones = get_object_or_404(Vacaciones, id=id_vacacion)
    detalle_planificacion = get_object_or_404(DetallePlanificacion, id=id_detalle)
    registro_vacaciones = RegistroVacaciones(vacaciones=vacaciones)
    if registro_vacaciones.generar_vacacion_detalle_planificacion(detalle_planificacion):
        messages.success(request, 'Registro de vacaciones exitoso')
    else:
        messages.warning(request, 'Fallo al registrar vacaciones')
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))


@login_required
def recalcular_vacacion(request, id_vacaciones):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    vacaciones = get_object_or_404(Vacaciones, id=id_vacaciones)
    vacaciones.recalcular_vacaciones()
    messages.success(request, 'Se recalcularón los valores de las vacaciones')
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))


@login_required
def recalcular_dias_vacacion(request, id_vacaciones):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    vacaciones = get_object_or_404(Vacaciones, id=id_vacaciones)
    funcionario = vacaciones.funcionario
    periodo_vacaciones = vacaciones.periodo_vacaciones

    vacaciones.recalcular_dias_pendientes()
    messages.success(request, 'Se recalcularón los dias pendientes de las vacaciones')
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))


@login_required
def eliminar_compensacion_dias(request, id_compensacion, id_funcionario):
    """
    Elimina registro de compensacnó de dias de unfuncionario
    :param request:
    :param id_compensacion: identificador de la compensación de días
    :param id_funcionario: identificador del funcionario
    :return: página principal de vaciones  del funcionario una vez eliminado el registro 
    """
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    compensacion = get_object_or_404(CompensacionDias, id=id_compensacion)
    vacaciones = compensacion.vacaciones
    compensacion.delete()
    vacaciones.recalcular_dias_pendientes()
    messages.success(request, "Datos eliminados correctamente... ")
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))


@login_required
def eliminar_registro_vacacion(request, id_registro_vacacion, id_funcionario):
    """
    Elimina registro de regisrtro de vacaciones
    :param request:
    :param id_registro_vacacion: identificador de tregistro de vacación
    :param id_funcionario: identificador del funcionario
    :return: página principal de vaciones  del funcionario una vez eliminado el registro 
    """
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    registro_vacacion = get_object_or_404(RegistroVacaciones, id=id_registro_vacacion)
    vacaciones = registro_vacacion.vacaciones
    registro_vacacion.delete()
    vacaciones.recalcular_dias_pendientes()
    messages.success(request, "Datos eliminados correctamente... ")
    return HttpResponseRedirect(reverse('talento_humano:vacaciones.detalle', args=(vacaciones.id,)))


# </editor-fold>

# <editor-fold desc="UAA por puesto">


@login_required
def index_uaa_puesto(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaas = UAA.objects.filter(uaa=None)
    return render(request, 'talento_humano/uaa-puesto/index.html', locals())


@login_required
def ver_uaa(request, id_uaa):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaa = get_object_or_404(UAA, id=id_uaa)
    uaa_puestos = UAAPuesto.get_uaa_puestos_activos(uaa=uaa)
    form = UAAPuestoForm()
    if request.method == 'POST':
        form = UAAPuestoForm(request.POST)
        if form.is_valid():
            uaa_puesto = form.save(False)
            uaa_puesto.uaa = uaa
            uaa_puesto.es_activo = True
            uaa_puesto.save()
    return render(request, 'talento_humano/uaa-puesto/ver_uaa.html', locals())


@login_required
def mover_uaa_puesto(request, id_uaa_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uaa_puesto)
    uaas = UAA.objects.filter(uaa=None)
    return render(request, 'talento_humano/uaa-puesto/mover.html', locals())


@login_required
def ejecutar_mover_uaa_puesto(request, id_uaa_puesto, id_uaa):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uaa_puesto)
    uaa = get_object_or_404(UAA, id=id_uaa)
    uaa_puesto.uaa = uaa
    uaa_puesto.save()
    return HttpResponseRedirect(reverse('talento_humano:uaa-puesto.ver_uaa', args=(uaa.id,)))


@login_required
def inactivar_uaa_puesto(request, id_uaa_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uaa_puesto)
    uaa_puesto.inactivar_uaa_puesto()
    messages.success(request, "Puesto inactivado correctamente")
    return HttpResponseRedirect(reverse('talento_humano:uaa-puesto.ver_uaa', args=(uaa_puesto.uaa.id,)))


@login_required
def agregar_funcionario_uaa_puesto(request, id_uaa_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    uaa_puesto = get_object_or_404(UAAPuesto, id=id_uaa_puesto)
    form = AsignacionPuestoUAAPuestoForm()
    if request.method == 'POST':
        form = AsignacionPuestoUAAPuestoForm(request.POST)
        if form.is_valid():
            asignacion_puesto = form.save(commit=False)
            asignacion_puesto.uaa_puesto = uaa_puesto
            codigo_duplicado = AsignacionPuesto.objects.filter(Q(funcionario=asignacion_puesto.funcionario) &
                                                               Q(codigo=asignacion_puesto.codigo)).first()
            if not codigo_duplicado:
                asignacion_puesto.save()
                asignacion_puesto.verificar_vigencia()
                messages.success(request, 'Asignación de puesto creada con éxito')
                return HttpResponseRedirect(reverse('talento_humano:uaa-puesto.ver_uaa', args=(uaa_puesto.uaa.id,)))
            else:
                messages.success(request, 'Código de la Asignación de Puesto ya existe')

    return render(request, 'talento_humano/uaa-puesto/asignar-funcionario-uaa-puesto.html', locals())

# <editor-fold desc="Ausentismo">

@login_required
def listar_ausentismos(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    lista_asignacion_puestos = AsignacionPuesto.objects.filter(activo=True)
    paginator = Paginator(lista_asignacion_puestos, 25)
    page = request.GET.get('pagina')

    try:
        asignacion_puestos = paginator.page(page)
    except PageNotAnInteger:
        asignacion_puestos = paginator.page(1)
    except EmptyPage:
        asignacion_puestos = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/ausentismos/index.html', locals())


@login_required
def buscar_ausentismos(request):
    """
    Busca un funcionario activo con asignación de puesto
    :param request:
    :return: la página con el listado de asignación de puestos
    """
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_asignacion_puestos = AsignacionPuesto.buscar(filtro, activo=True)
    else:
        lista_asignacion_puestos = AsignacionPuesto.objects.filter(activo=True)
    paginator = Paginator(lista_asignacion_puestos, numero_items)

    try:
        asignacion_puestos = paginator.page(page)
    except PageNotAnInteger:
        asignacion_puestos = paginator.page(1)
    except EmptyPage:
        asignacion_puestos = paginator.page(paginator.num_pages)

    return render(request, 'talento_humano/ausentismos/index.html', locals())


@login_required
def ausentismo_funcionario(request, id_funcionario):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    ausentismos = Ausentismo.objects.filter(activo=True)
    return render(request, 'talento_humano/ausentismos/funcionario.html', locals())


@login_required
def ausentismo_funcionario_registrar(request, id_funcionario, id_ausentismo):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    ausentismo = get_object_or_404(Ausentismo, id=id_ausentismo)
    form = AusentismoFuncionarioForm()

    if request.POST:
        form = AusentismoFuncionarioForm(request.POST)
        if form.is_valid():
            ausentismo_funcionario = form.save(commit=False)
            ausentismo_funcionario.funcionario = funcionario
            ausentismo_funcionario.ausentismo = ausentismo
            ausentismo_funcionario.activo = True
            if ausentismo_funcionario.fecha_inicio > ausentismo_funcionario.fecha_fin:
                messages.warning(request, 'La fecha de inicio no puede ser mayor a la fecha de fin')
            else:
                if ausentismo.limite_tiempo:
                    dias = ausentismo.limite_dias
                    meses = ausentismo.limite_meses
                    anios = ausentismo.limite_anios
                    if ausentismo_funcionario.cumple_limite(anio=anios, meses=meses, dias=dias):
                        if not ausentismo.imputable_vacaciones:
                            ausentismo_funcionario.save()
                            messages.success(request, 'Ausentismo registrado con éxito')
                            return HttpResponseRedirect(
                                reverse('talento_humano:ausentismos.funcionario', args=(funcionario.id,)))
                        else:
                            if funcionario.get_disponibles_vacacion() >= ausentismo_funcionario.get_total_ausentismo():
                                # Metodo que funciona con aquellos funcionarios que no tienen un puesto vigente
                                asignacion_puesto = funcionario.get_asignacion_puesto_vigente()
                                if asignacion_puesto is None:
                                    asignacion_puesto = funcionario.get_ultimo_asignacion_puesto()
                                    vacaciones = Vacaciones.objects.filter(asignacion_puesto=asignacion_puesto,
                                                                           activo=True).first()
                                # Metodo que funciona con aquellos funcionarios vigentes
                                else:
                                    vacaciones = funcionario.get_vacaciones()

                                if vacaciones:
                                    ausentismo_funcionario.vacaciones = vacaciones
                                    ausentismo_funcionario.save()
                                    vacaciones.recalcular_dias_pendientes()
                                    messages.success(request, 'Ausentismo registrado con éxito')
                                    return HttpResponseRedirect(
                                        reverse('talento_humano:ausentismos.funcionario', args=(funcionario.id,)))
                                else:
                                    messages.warning(request,
                                                     'La última asignación de puesto no posee un registro de vacaciones en estado activo ' + str(
                                                         asignacion_puesto.uaa_puesto.puesto))
                            else:
                                messages.warning(request,
                                                 'El ausentismo supera el número de dias de vacaciones disponibles:' + str(
                                                     funcionario.get_disponibles_vacacion()))
                    else:
                        messages.warning(request,
                                         'Por favor revisar las fechas. No cumple el límite de tiempo permitido')
                else:
                    if not ausentismo.imputable_vacaciones:
                        ausentismo_funcionario.save()
                        messages.success(request, 'Ausentismo registrado con éxito')
                        return HttpResponseRedirect(
                            reverse('talento_humano:ausentismos.funcionario', args=(funcionario.id,)))
                    else:
                        if funcionario.get_disponibles_vacacion() >= ausentismo_funcionario.get_total_ausentismo():
                            # Metodo que funciona con aquellos funcionarios que no tienen un puesto vigente
                            asignacion_puesto = funcionario.get_asignacion_puesto_vigente()
                            if asignacion_puesto is None:
                                asignacion_puesto = funcionario.get_ultimo_asignacion_puesto()
                                vacaciones = Vacaciones.objects.filter(asignacion_puesto=asignacion_puesto,
                                                                       activo=True).first()
                            # Metodo que funciona con aquellos funcionarios vigentes
                            else:
                                vacaciones = funcionario.get_vacaciones()

                            if vacaciones:
                                ausentismo_funcionario.vacaciones = vacaciones
                                ausentismo_funcionario.save()
                                vacaciones.recalcular_dias_pendientes()
                                messages.success(request, 'Ausentismo registrado con éxito')
                                return HttpResponseRedirect(
                                    reverse('talento_humano:ausentismos.funcionario', args=(funcionario.id,)))
                            else:
                                messages.warning(request,
                                                 'La última asignación de puesto no posee un registro de vacaciones en estado activo ' + str(
                                                     asignacion_puesto.uaa_puesto.puesto))
                        else:
                            messages.warning(request,
                                             'El ausentismo supera el número de dias de vacaciones disponibles')

    return render(request, 'talento_humano/ausentismos/registrar.html', locals())


@login_required
def eliminar_ausentismo(request, id_ausentismo_funcionario, id_funcionario):
    """
    Elimina registro de ausentismos de funcionarios
    :param request:
    :param id_ausentismo_funcionario: identificador de del ausentismo del funcionario
    :param id_funcionario: identificador del funcionario
    :return: página principal del ausentismo  del funcionario una vez eliminado el registro 
    """
    funcionario = get_object_or_404(Funcionario, id=id_funcionario)
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    ausentismo_funcionario = get_object_or_404(AusentismoFuncionario, id=id_ausentismo_funcionario)
    vacaciones = ausentismo_funcionario.vacaciones
    ausentismo_funcionario.delete()
    if vacaciones is not None:
        vacaciones.recalcular_dias_pendientes()
    messages.success(request, "Datos eliminados correctamente... ")
    return HttpResponseRedirect(reverse('talento_humano:ausentismos.funcionario', args=(funcionario.id,)))


# </editor-fold>

# <editor-fold desc="Régimen Laboral">


@login_required
def regimen_laboral(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro', '')
    page = request.GET.get('pagina')

    regimenes = RegimenLaboral.objects.all()
    if filtro:
        lista_asignacion_puestos = AsignacionPuesto.buscar(filtro, vigente=True)
    else:
        lista_asignacion_puestos = AsignacionPuesto.objects.filter(vigente=True)
    paginator = Paginator(lista_asignacion_puestos, 25)

    try:
        asignaciones = paginator.page(page)
    except PageNotAnInteger:
        asignaciones = paginator.page(1)
    except EmptyPage:
        asignaciones = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/regimen_laboral/index.html', locals())


@login_required
def regimen_laboral_buscar(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_asignacion_puestos = AsignacionPuesto.buscar(filtro, vigente=True)
    else:
        lista_asignacion_puestos = AsignacionPuesto.objects.filter(vigente=True)
    paginator = Paginator(lista_asignacion_puestos, numero_items)

    try:
        asignaciones = paginator.page(page)
    except PageNotAnInteger:
        asignaciones = paginator.page(1)
    except EmptyPage:
        asignaciones = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/regimen_laboral/index.html', locals())


@login_required
def regimen_laboral_filtro(request, id_regimen_laboral):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    regimen = get_object_or_404(RegimenLaboral, id=id_regimen_laboral)
    regimenes = RegimenLaboral.objects.all()
    if filtro:
        lista_asignacion_puestos = AsignacionPuesto.buscar(filtro, vigente=True, regimen_laboral=regimen)
    else:
        lista_asignacion_puestos = AsignacionPuesto.get_por_regimen_laboral(regimen_laboral=regimen, vigente=True)
    paginator = Paginator(lista_asignacion_puestos, numero_items)

    try:
        asignaciones = paginator.page(page)
    except PageNotAnInteger:
        asignaciones = paginator.page(1)
    except EmptyPage:
        asignaciones = paginator.page(paginator.num_pages)
    return render(request, 'talento_humano/regimen_laboral/filtro.html', locals())


# </editor-fold>


# <editor-fold desc="Reportes">

@login_required
def reporte_asignacion_puesto(request, id_asignacion_puesto):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    asignacion = get_object_or_404(AsignacionPuesto, id=id_asignacion_puesto)
    html_template = get_template('talento_humano/reporte/reporte_asignacion_puesto_pdf.html')
    rendered_html = html_template.render(RequestContext(request,
                                                        {'asignacion': asignacion,
                                                         'generado': request.user,
                                                         })).encode(encoding="UTF-8")
    ARCHIVO = BASE_DIR + "/static/css/reporte/reporte-vertical.css"
    pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(ARCHIVO)])
    http_response = HttpResponse(pdf_file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename="report.pdf"'
    return http_response


@login_required
def index_reporte(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    lista_asignacion_puestos = AsignacionPuesto.reporte()
    total = lista_asignacion_puestos.count()
    form = ReporteForm()
    page = None
    if request.method == 'GET':
        form = ReporteForm(request.GET)

        if form.is_valid():
            if 'pagina_siguiente' in request.GET:
                page = request.GET.get('siguiente')
            if 'pagina_anterior' in request.GET:
                page = request.GET.get('anterior')
            activo = form.cleaned_data['activo']
            criterio = form.cleaned_data['criterio']
            encargado = form.cleaned_data['encargado']
            fecha_fin_desde = form.cleaned_data['fecha_fin_desde']
            fecha_fin_hasta = form.cleaned_data['fecha_fin_hasta']
            fecha_inicio_desde = form.cleaned_data['fecha_inicio_desde']
            fecha_inicio_hasta = form.cleaned_data['fecha_inicio_hasta']
            fecha_termino_desde = form.cleaned_data['fecha_termino_desde']
            fecha_termino_hasta = form.cleaned_data['fecha_termino_hasta']
            grupo_ocupacional_id = form.cleaned_data['grupo_ocupacional']
            ingreso_concurso = form.cleaned_data['ingreso_concurso']
            puesto_id = form.cleaned_data['puesto']
            regimen_laboral_id = form.cleaned_data['regimen_laboral']
            responsable_uaa = form.cleaned_data['responsable_uaa']
            termino = form.cleaned_data['termino']
            tipo_relacion_laboral_id = form.cleaned_data['tipo_relacion_laboral']
            tipo_terminacion_id = form.cleaned_data['tipo_terminacion']
            uaa_id = form.cleaned_data['uaa']
            uaa_hijas = form.cleaned_data['uaa_hijas']
            vigente = form.cleaned_data['vigente']
            sexo_id = form.cleaned_data['sexo']
            tipo_etnia_id = form.cleaned_data['tipo_etnia']
            tipo_discapacidad_id = form.cleaned_data['tipo_discapacidad']
            estado_civil_id = form.cleaned_data['estado_civil']

            grupo_ocupacional = None
            puesto = None
            regimen_laboral = None
            tipo_relacion_laboral = None
            tipo_terminacion = None
            uaa = None
            sexo = None
            tipo_etnia = None
            tipo_discapacidad = None
            estado_civil = None

            if puesto_id:
                puesto = Puesto.objects.filter(id=puesto_id).first()
            if tipo_relacion_laboral_id:
                tipo_relacion_laboral = CatalogoItem.objects.filter(id=tipo_relacion_laboral_id).first()
            if tipo_terminacion_id:
                tipo_terminacion = CatalogoItem.objects.filter(id=tipo_terminacion_id).first()
            if regimen_laboral_id:
                regimen_laboral = RegimenLaboral.objects.filter(id=regimen_laboral_id).first()
            if grupo_ocupacional_id:
                grupo_ocupacional = GrupoOcupacional.objects.filter(id=grupo_ocupacional_id).first()
            if uaa_id:
                uaa = UAA.objects.filter(id=uaa_id).first()
            if sexo_id:
                sexo = CatalogoItem.objects.filter(id=sexo_id).first()
            if tipo_etnia_id:
                tipo_etnia = CatalogoItem.objects.filter(id=tipo_etnia_id).first()
            if tipo_discapacidad_id:
                if tipo_discapacidad_id == 'ninguna':
                    tipo_discapacidad = tipo_discapacidad_id
                else:
                    tipo_discapacidad = CatalogoItem.objects.filter(id=tipo_discapacidad_id).first()
            if estado_civil_id:
                estado_civil = CatalogoItem.objects.filter(id=estado_civil_id).first()

            lista_asignacion_puestos = AsignacionPuesto.reporte(activo=activo,
                                                                criterio=criterio,
                                                                encargado=encargado,
                                                                fecha_fin_desde=fecha_fin_desde,
                                                                fecha_fin_hasta=fecha_fin_hasta,
                                                                fecha_inicio_desde=fecha_inicio_desde,
                                                                fecha_inicio_hasta=fecha_inicio_hasta,
                                                                fecha_termino_desde=fecha_termino_desde,
                                                                fecha_termino_hasta=fecha_termino_hasta,
                                                                grupo_ocupacional=grupo_ocupacional,
                                                                ingreso_concurso=ingreso_concurso,
                                                                puesto=puesto,
                                                                regimen_laboral=regimen_laboral,
                                                                responsable_uaa=responsable_uaa,
                                                                termino=termino,
                                                                tipo_relacion_laboral=tipo_relacion_laboral,
                                                                tipo_terminacion=tipo_terminacion,
                                                                uaa=uaa,
                                                                uaa_hijas=uaa_hijas,
                                                                vigente=vigente,
                                                                sexo=sexo,
                                                                tipo_etnia=tipo_etnia,
                                                                tipo_discapacidad=tipo_discapacidad,
                                                                estado_civil=estado_civil
                                                                )
            total = lista_asignacion_puestos.count()
            filtros = []
            for item in form.cleaned_data:
                if form.cleaned_data.get(item):
                    fdata = [form[item].label if form[item].label else item, str(form.cleaned_data.get(item))]
                    if item in ['sexo', 'tipo_etnia', 'tipo_discapacidad', 'estado_civil', 'tipo_relacion_laboral',
                                'tipo_terminacion']:
                        fdata[1] = str(CatalogoItem.objects.filter(id=form.cleaned_data.get(item)).first())
                    elif item == 'grupo_ocupacional':
                        fdata[1] = str(grupo_ocupacional)
                    elif item == 'puesto':
                        fdata[1] = str(puesto)
                    elif item == 'regimen_laboral':
                        fdata[1] = str(regimen_laboral)
                    elif item == 'uaa':
                        fdata[1] = str(uaa)
                    filtros.append(fdata)

            if 'detalle_pdf' in request.GET:
                filtros = [{'criterio': f[0], 'valor': f[1]} for f in filtros]
                return _reporte_asignaciones_detalle(lista_asignacion_puestos, filtros, tipo='pdf', request=request)
            if 'detalle_excel' in request.GET:
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="%s%s.xls"' % (
                    "reporte_funcionarios", datetime.now().strftime("%Y%m%d_%H%M%S"))
                cabeceras = ["Nro.", "Cédula", "Apellidos", "Nombres", "Detalle"]
                tamanios = [256 * 6, 256 * 12, 256 * 18, 256 * 18, 256 * 85]

                lista = lista_asignacion_puestos.values('funcionario__usuario__persona__numero_documento',
                                                        'funcionario__usuario__persona__primer_apellido',
                                                        'funcionario__usuario__persona__segundo_apellido',
                                                        'funcionario__usuario__persona__primer_nombre',
                                                        'funcionario__usuario__persona__segundo_nombre',
                                                        'uaa_puesto__uaa__nombre',
                                                        'uaa_puesto__uaa__uaa__nombre',
                                                        'uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre',
                                                        'uaa_puesto__puesto__grupo_ocupacional__nombre',
                                                        'uaa_puesto__puesto__denominacion',
                                                        'uaa_puesto__puesto__grupo_ocupacional__rmu',
                                                        'activo',
                                                        'vigente',
                                                        'fecha_inicio',
                                                        'fecha_fin'
                                                        )
                asignaciones_list = [(numero + 1,
                                      item.get('funcionario__usuario__persona__numero_documento'),
                                      '%s %s' % (
                                          item.get('funcionario__usuario__persona__primer_apellido'),
                                          item.get('funcionario__usuario__persona__segundo_apellido')),
                                      '%s %s' % (item.get('funcionario__usuario__persona__primer_nombre'),
                                                 item.get('funcionario__usuario__persona__segundo_nombre')),
                                      "UAA: %s \nRégimen laboral: %s \nGrupo ocupacional: %s "
                                      "\nPuesto: %s \nActivo: %s \nVigente: %s \nInicio: %s %s"
                                      % ('%s-%s' % (item.get('uaa_puesto__uaa__nombre'),
                                                    item.get('uaa_puesto__uaa__uaa__nombre')),
                                         item.get(
                                             'uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre'),
                                         item.get('uaa_puesto__puesto__grupo_ocupacional__nombre'),
                                         '%s - $ %s' % (item.get('uaa_puesto__puesto__denominacion'),
                                                        item.get(
                                                            'uaa_puesto__puesto__grupo_ocupacional__rmu')),
                                         'Si' if item.get('activo') else 'No',
                                         'Si' if item.get('vigente') else 'No',
                                         item.get('fecha_inicio'),
                                         ('\nFin: %s' % item.get('fecha_fin')) if item.get(
                                             'fecha_fin') else ''
                                         )
                                      ) for numero, item in enumerate(lista)]
                workbook = generar_excel(filas=asignaciones_list, cabeceras=cabeceras, filtros=filtros,
                                         titulo="Reporte detallado de Asignación de puestos",
                                         tamanio_columnas=tamanios, alto_filas=7)
                workbook.save(response)
                return response
            if 'imprimir_sencillo_pdf' in request.GET:
                filtros = [{'criterio': f[0], 'valor': f[1]} for f in filtros]
                return _reporte_asignaciones_sencillo({'asignaciones': lista_asignacion_puestos,
                                                       'filtros': filtros}, tipo='pdf', request=request)
            if 'imprimir_sencillo_excel' in request.GET:
                titulo = "Reporte de Funcionarios"
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="%s%s.xls"' % (
                    "reporte_funcionarios", datetime.now().strftime("%Y%m%d_%H%M%S"))
                cabeceras = ["Nro.", "Cédula", "Apellidos", "Nombres", "DirecciónDomicilio", "Telefono", "Celular",
                             "CorreoInstitucional", "CorreoPersonal", "FechaNacimiento",
                             "Sexo", "Etnia", "EstadoCivil", "TipoDiscapacidad",
                             "TercerNivel", "CuartoNivel", "ObservacionTitulos",
                             "UAA", "UAAPadre", "Puesto", "Activo", "PuestoDenominacion", "RegimenLaboral",
                             "GrupoOcupacional", "TipoRelacionLaboral",
                             "RMU", "HorasDedicacion", "NroRegistroContraro/Nombramiento", "FechaDesde", "FechaHasta",
                             "FechaTermino", "Observacion"]
                tamanios = [256 * 5, 256 * 15, 256 * 30, 256 * 30, 256 * 50, 256 * 30, 256 * 30, 256 * 30, 256 * 30,
                            256 * 15,
                            256 * 15, 256 * 15, 256 * 15, 256 * 15,
                            256 * 50, 256 * 50, 256 * 50,
                            256 * 40, 256 * 40, 256 * 40, 256 * 40, 256 * 15, 256 * 30, 256 * 30, 256 * 30,
                            256 * 15, 256 * 15, 256 * 30, 256 * 15, 256 * 15, 256 * 15, 256 * 15]
                filtros = [("Desde", fecha_inicio_desde.strftime("%Y/%m/%d") if fecha_inicio_desde else ''),
                           ("Hasta", fecha_inicio_hasta.strftime("%Y/%m/%d") if fecha_inicio_hasta else '')]

                filas = []
                for numero, asignacion in enumerate(lista_asignacion_puestos):
                    domicilio = Direccion.objects.filter(persona=asignacion.funcionario.usuario.persona,
                                                         tipo_direccion__codigo_th=2).first()

                    if Expediente.objects.filter(persona=asignacion.funcionario.usuario.persona).first() is not None:
                        titulos_tercer_nivel = FormacionAcademica.objects.filter(
                            expediente=asignacion.funcionario.usuario.persona.expediente,
                            nivel_instruccion__codigo_th__in=[12, 13]).order_by(
                            'fecha_registro').all()  # Tecnología, Tercer nivel
                        tercer_nivel = ["T%s:%s" % (sec + 1, titulo.titulo_obtenido) for sec, titulo in
                                        enumerate(titulos_tercer_nivel)]
                        tercer_nivel = ' '.join(tercer_nivel)

                        titulos_cuarto_nivel = FormacionAcademica.objects.filter(
                            expediente=asignacion.funcionario.usuario.persona.expediente,
                            nivel_instruccion__codigo_th__in=[2, 3, 4, 5]).order_by(
                            'fecha_registro').all()  # Diplomado, Especialidad, Maestria, # Doctorado
                        cuarto_nivel = ["T%s:%s" % (sec + 1, titulo.titulo_obtenido) for sec, titulo in
                                        enumerate(titulos_cuarto_nivel)]
                        cuarto_nivel = ' '.join(cuarto_nivel)

                        cuarto_nivel_obs = ["%s" % (str(titulo.observacion)) for titulo in titulos_cuarto_nivel if
                                            titulo.observacion is not None]
                        cuarto_nivel_obs = ' '.join(cuarto_nivel_obs)
                    else:
                        tercer_nivel = ''
                        cuarto_nivel = ''
                        cuarto_nivel_obs = ''

                    fila = (numero + 1,
                              asignacion.funcionario.usuario.persona.numero_documento,
                              asignacion.funcionario.usuario.persona.get_apellidos(),
                              asignacion.funcionario.usuario.persona.get_nombres(),
                              "%s %s %s %s" % (domicilio.calle_principal, domicilio.calle_secundaria, domicilio.numero, domicilio.referencia) if domicilio else "",
                              domicilio.telefono if domicilio else "",
                              domicilio.celular if domicilio else "",
                              asignacion.funcionario.usuario.correo_electronico_institucional,
                              asignacion.funcionario.usuario.persona.correo_electronico_alternativo,
                              asignacion.funcionario.usuario.persona.fecha_nacimiento if asignacion.funcionario.usuario.persona.fecha_nacimiento else '',
                              asignacion.funcionario.usuario.persona.sexo.nombre if asignacion.funcionario.usuario.persona.sexo else '',
                              asignacion.funcionario.usuario.persona.tipo_etnia.nombre if asignacion.funcionario.usuario.persona.tipo_etnia else '',
                              asignacion.funcionario.usuario.persona.estado_civil.nombre if asignacion.funcionario.usuario.persona.estado_civil else '',
                              asignacion.funcionario.usuario.persona.tipo_discapacidad.nombre if asignacion.funcionario.usuario.persona.tipo_discapacidad else '',
                              tercer_nivel,
                              cuarto_nivel,
                              cuarto_nivel_obs,
                              asignacion.uaa_puesto.uaa.nombre,
                              str(asignacion.uaa_puesto.uaa.get_uaa_padre_tipo()) if asignacion.uaa_puesto.uaa.get_uaa_padre_tipo() else '' ,
                              str(asignacion.uaa_puesto.puesto),
                              'Activo' if asignacion.activo is True else 'Inactivo',
                              asignacion.uaa_puesto.puesto.denominacion,
                              asignacion.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre,
                              asignacion.uaa_puesto.puesto.grupo_ocupacional.nombre,
                              asignacion.tipo_relacion_laboral.nombre,
                              asignacion.get_sueldo(),
                              asignacion.uaa_puesto.puesto.horas_dedicacion,
                              asignacion.codigo,
                              asignacion.fecha_inicio,
                              asignacion.fecha_fin if asignacion.fecha_fin else '',
                              asignacion.fecha_termino if asignacion.fecha_termino else '',
                              asignacion.observacion if asignacion.observacion else '')

                    filas.append(fila)

                workbook = generar_excel(filas=filas, cabeceras=cabeceras, filtros=filtros,
                                         titulo="Reporte sencillo de Asignación de puestos", tamanio_columnas=tamanios)
                workbook.save(response)
                return response
            if 'imprimir_vacaciones' in request.GET:
                html_template = get_template('talento_humano/reporte/reporte_vacaciones_pdf.html')
                rendered_html = html_template.render(RequestContext(request,
                                                                    {'asignaciones': lista_asignacion_puestos,
                                                                     'total': total,
                                                                     'generado': request.user,
                                                                     })).encode(encoding="UTF-8")
                ARCHIVO = BASE_DIR + "/static/css/reporte/reporte-horizontal.css"
                pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(ARCHIVO)])
                http_response = HttpResponse(pdf_file, content_type='application/pdf')
                http_response['Content-Disposition'] = 'filename="report_funcionarios_vacaciones.pdf"'
                return http_response

    paginator = Paginator(lista_asignacion_puestos, 25)

    try:
        asignaciones = paginator.page(page)
    except PageNotAnInteger:
        asignaciones = paginator.page(1)
    except EmptyPage:
        asignaciones = paginator.page(paginator.num_pages)
    # asignaciones = lista_asignacion_puestos
    return render(request, 'talento_humano/reporte/form.html', locals())


def _reporte_asignaciones_sencillo(datos, tipo='pdf', request=None):
    lista = datos.get('asignaciones').values('funcionario__usuario__persona__numero_documento',
                                             'funcionario__usuario__persona__primer_apellido',
                                             'funcionario__usuario__persona__segundo_apellido',
                                             'funcionario__usuario__persona__primer_nombre',
                                             'funcionario__usuario__persona__segundo_nombre',
                                             'uaa_puesto__uaa__nombre',
                                             'uaa_puesto__puesto__denominacion',
                                             'uaa_puesto__puesto__grupo_ocupacional__rmu',
                                             'uaa_puesto__uaa__uaa__nombre',
                                             'fecha_inicio',
                                             'fecha_fin'
                                             )

    asignaciones_list = [dict(numero=numero + 1,
                              cedula=item.get('funcionario__usuario__persona__numero_documento'),
                              apellidos='%s %s' % (item.get('funcionario__usuario__persona__primer_apellido'),
                                                   item.get('funcionario__usuario__persona__segundo_apellido')),
                              nombres='%s %s' % (item.get('funcionario__usuario__persona__primer_nombre'),
                                                 item.get('funcionario__usuario__persona__segundo_nombre')),
                              uaa='%s-%s' % (
                                  item.get('uaa_puesto__uaa__nombre'), item.get('uaa_puesto__uaa__uaa__nombre')),
                              puesto='%s - $ %s' % (item.get('uaa_puesto__puesto__denominacion'),
                                                    item.get('uaa_puesto__puesto__grupo_ocupacional__rmu')),
                              inicio=item.get('fecha_inicio'),
                              fin=(item.get('fecha_fin'))
                              )
                         for numero, item in enumerate(lista)]

    parametros = dict(
        asignaciones=asignaciones_list,
        total=len(asignaciones_list),
        filtros=datos.get('filtros'),
        filename='ReporteAsignacionesSencillo'
    )
    return pdfUtil.generar_reporte('talento_humano_asignacion_sencillo', parametros, tipo, request)


def _reporte_asignaciones_detalle(asignaciones, filtros=[], tipo='pdf', request=None):
    lista = asignaciones.values('funcionario__usuario__persona__numero_documento',
                                'funcionario__usuario__persona__primer_apellido',
                                'funcionario__usuario__persona__segundo_apellido',
                                'funcionario__usuario__persona__primer_nombre',
                                'funcionario__usuario__persona__segundo_nombre',
                                'uaa_puesto__uaa__nombre',
                                'uaa_puesto__uaa__uaa__nombre',
                                'uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre',
                                'uaa_puesto__puesto__grupo_ocupacional__nombre',
                                'uaa_puesto__puesto__denominacion',
                                'uaa_puesto__puesto__grupo_ocupacional__rmu',
                                'activo',
                                'vigente',
                                'fecha_inicio',
                                'fecha_fin'
                                )
    asignaciones_list = [dict(numero=numero + 1,
                              cedula=item.get('funcionario__usuario__persona__numero_documento'),
                              apellidos='%s %s' % (item.get('funcionario__usuario__persona__primer_apellido'),
                                                   item.get('funcionario__usuario__persona__segundo_apellido')),
                              nombres='%s %s' % (item.get('funcionario__usuario__persona__primer_nombre'),
                                                 item.get('funcionario__usuario__persona__segundo_nombre')),
                              detalle="UAA: %s \nRégimen laboral: %s \nGrupo ocupacional: %s "
                                      "\nPuesto: %s \nActivo: %s \nVigente: %s \nInicio: %s %s"
                                      % ('%s-%s' % (
                                  item.get('uaa_puesto__uaa__nombre'), item.get('uaa_puesto__uaa__uaa__nombre')),
                                         item.get('uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre'),
                                         item.get('uaa_puesto__puesto__grupo_ocupacional__nombre'),
                                         '%s - $ %s' % (item.get('uaa_puesto__puesto__denominacion'),
                                                        item.get('uaa_puesto__puesto__grupo_ocupacional__rmu')),
                                         'Si' if item.get('activo') else 'No',
                                         'Si' if item.get('vigente') else 'No',
                                         item.get('fecha_inicio'),
                                         ('\nFin: %s' % item.get('fecha_fin')) if item.get('fecha_fin') else ''
                                         )
                              ) for numero, item in enumerate(lista)]

    parametros = dict(
        asignaciones=asignaciones_list,
        total=len(asignaciones_list),
        filtros=filtros,
        filename='ReporteAsignacionesDetallado'
    )
    return pdfUtil.generar_reporte('talento_humano_asignacion_detalle', parametros, tipo, request)


@login_required
def reporte_vacaciones_periodo(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    qfilter = RegistroVacaciones.reporte_vacaciones_detalle()

    form = ReporteVacacionesPeriodoForm()
    page = None
    if request.method == 'GET':
        form = ReporteVacacionesPeriodoForm(request.GET)
        if form.is_valid():
            if 'pagina_siguiente' in request.GET:
                page = request.GET.get('siguiente')
            if 'pagina_anterior' in request.GET:
                page = request.GET.get('anterior')

            detalle_planificacion = None

            detalle_planificacion_id = form.cleaned_data['detalle_planificacion']

            if detalle_planificacion_id:
                detalle_planificacion = DetallePlanificacion.objects.filter(id=detalle_planificacion_id).first()

            # Imprimir por facultades
            if 'exportar_facultad' in request.GET:
                # Construyo los datos
                response = HttpResponse(content_type='text/csv')
                response[
                    'Content-Disposition'] = 'attachment; filename="reporte_vacaciones_periodo_%s.csv"' % detalle_planificacion_id
                writer = csv.writer(response)

                # Obtengo las uaas de las facultades y MED
                uaas_facultades = UAA.objects.filter(id__in=(20, 21, 22, 23, 24, 25)).all()
                uaa_ids_facultades_all = []
                for uaa_fac in uaas_facultades:
                    uaa_ids_facultad = [uaa_hija.id for uaa_hija in uaa_fac.get_uaa_hijas_todas()]
                    uaa_ids_facultad.append(uaa_fac.id)
                    uaa_ids_facultades_all.extend(uaa_ids_facultad)
                    # Ontengo las vacaciones de esta facultad y de todas las uaas hijas
                    registro_vacaciones = RegistroVacaciones.reporte_vacaciones_detalle_facultad(
                        detalle_planificacion=detalle_planificacion,
                        uaas_ids_facultad=uaa_ids_facultad)

                    if registro_vacaciones:
                        writer.writerow([uaa_fac.nombre])
                        writer.writerow(
                            [u'Identificación', 'Apellidos', 'Nombres', 'Detalle',
                             'Desde',
                             'Hasta', u'N° Días',
                             u'Días pendientes', 'Horas pendientes', 'Minutos pendientes'])

                    for item in registro_vacaciones:
                        row = [item.vacaciones.funcionario.usuario.persona.numero_documento,
                               item.vacaciones.funcionario.get_apellidos(),
                               item.vacaciones.funcionario.get_nombres(),
                               item.detalle_planificacion.codigo if item.detalle_planificacion else '',
                               item.fecha_inicio.strftime('%d-%m-%Y'),
                               item.fecha_fin.strftime('%d-%m-%Y'),
                               (item.fecha_fin - item.fecha_inicio).days + 1,
                               item.vacaciones.dias_pendientes,
                               item.vacaciones.horas_pendientes,
                               item.vacaciones.minutos_pendientes]
                        writer.writerow(row)

                # Todas los quee estan fuera de las Areas
                registro_vacaciones = RegistroVacaciones.reporte_vacaciones_detalle_excludefacultad(
                    detalle_planificacion=detalle_planificacion, uaas_ids_facultad=uaa_ids_facultades_all)
                if registro_vacaciones:
                    writer.writerow(["Administración central"])
                    writer.writerow(
                        [u'Identificación', 'Apellidos', 'Nombres', 'Detalle',
                         'Desde',
                         'Hasta', u'N° Días',
                         u'Días pendientes', 'Horas pendientes', 'Minutos pendientes'])

                for item in registro_vacaciones:
                    row = [item.vacaciones.funcionario.usuario.persona.numero_documento,
                           item.vacaciones.funcionario.get_apellidos(),
                           item.vacaciones.funcionario.get_nombres(),
                           item.detalle_planificacion.codigo if item.detalle_planificacion else '',
                           item.fecha_inicio.strftime('%d-%m-%Y'),
                           item.fecha_fin.strftime('%d-%m-%Y'),
                           (item.fecha_fin - item.fecha_inicio).days + 1,
                           item.vacaciones.dias_pendientes,
                           item.vacaciones.horas_pendientes,
                           item.vacaciones.minutos_pendientes]
                    writer.writerow(row)

                return response

            qfilter = RegistroVacaciones.reporte_vacaciones_detalle(detalle_planificacion=detalle_planificacion)

            if 'exportar_pdf' in request.GET or 'exportar_csv' in request.GET:

                values = qfilter.values('vacaciones__funcionario__usuario__persona__numero_documento',
                                        'vacaciones__funcionario__usuario__persona__primer_apellido',
                                        'vacaciones__funcionario__usuario__persona__segundo_apellido',
                                        'vacaciones__funcionario__usuario__persona__primer_nombre',
                                        'vacaciones__funcionario__usuario__persona__segundo_nombre',
                                        'detalle_planificacion__codigo',
                                        'fecha_inicio',
                                        'fecha_fin',
                                        'id',
                                        'vacaciones__dias_pendientes',
                                        'vacaciones__horas_pendientes',
                                        'vacaciones__minutos_pendientes')

                for v in values:
                    dias = (v['fecha_fin'] - v['fecha_inicio']).days + 1
                    v['dias'] = dias
                    for v in values:
                        dias = (v['fecha_fin'] - v['fecha_inicio']).days + 1
                        v['dias'] = dias

                if 'exportar_csv' in request.GET:
                    response = HttpResponse(content_type='text/csv')
                    response[
                        'Content-Disposition'] = 'attachment; filename="reporte_vacaciones_periodo_%s.csv"' % detalle_planificacion_id

                    writer = csv.writer(response)
                    writer.writerow([u'Identificación', 'Apellidos', 'Nombres', 'Detalle', 'Desde', 'Hasta', 'N° Das',
                                     'Dias pendientes', 'Horas pendientes', 'Minutos pendientes'])
                    for v in values:
                        row = [v['vacaciones__funcionario__usuario__persona__numero_documento'],
                               '%s %s' % (v['vacaciones__funcionario__usuario__persona__primer_apellido'],
                                          v['vacaciones__funcionario__usuario__persona__segundo_apellido']),
                               '%s %s' % (v['vacaciones__funcionario__usuario__persona__primer_nombre'],
                                          v['vacaciones__funcionario__usuario__persona__segundo_nombre']),
                               v['detalle_planificacion__codigo'],
                               v['fecha_inicio'].strftime('%d-%m-%Y'), v['fecha_fin'].strftime('%d-%m-%Y'), v['dias'],
                               v['vacaciones__dias_pendientes'], v['vacaciones__horas_pendientes'],
                               v['vacaciones__minutos_pendientes']
                               ]
                        writer.writerow(row)
                    return response

                if 'exportar_pdf' in request.GET:
                    total = qfilter.count()
                    vacaciones = [dict(
                        identificacion=item.get('vacaciones__funcionario__usuario__persona__numero_documento'),
                        apellidos='%s %s' % (item.get('vacaciones__funcionario__usuario__persona__primer_apellido'),
                                             item.get('vacaciones__funcionario__usuario__persona__segundo_apellido')),
                        nombres='%s %s' % (item.get('vacaciones__funcionario__usuario__persona__primer_nombre'),
                                           item.get('vacaciones__funcionario__usuario__persona__segundo_nombre')),
                        detalle=item.get('detalle_planificacion__codigo'),
                        desde=item.get('fecha_inicio'),
                        hasta=item.get('fecha_fin'),
                        dias=item.get('dias'),
                        diasp=item.get('vacaciones__dias_pendientes'),
                        horas=item.get('vacaciones__horas_pendientes'),
                        minutos=item.get('vacaciones__minutos_pendientes')

                    ) for item in values]

                    datos = dict(vacaciones=vacaciones, total=total)

                    return pdfUtil.generar_reporte('talento_humano_vacaciones', datos, 'pdf', request)

    total = qfilter.count()
    paginator = Paginator(qfilter, 25)

    try:
        registros = paginator.page(page)
    except PageNotAnInteger:
        registros = paginator.page(1)
    except EmptyPage:
        registros = paginator.page(paginator.num_pages)
    # asignaciones = lista_asignacion_puestos
    return render(request, 'talento_humano/reporte/form_vacaciones_periodo.html', locals())


# </editor-fold>


@login_required
def reporte_vacaciones_pendientes(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    qfilter = Vacaciones.reporte_vacaciones_pendientes()

    form = ReporteVacacionesPendientesForm()
    page = None
    if request.method == 'GET':
        form = ReporteVacacionesPendientesForm(request.GET)
        if form.is_valid():
            if 'pagina_siguiente' in request.GET:
                page = request.GET.get('siguiente')
            if 'pagina_anterior' in request.GET:
                page = request.GET.get('anterior')
            if 'pagina' in request.GET:
                page = request.GET.get('numero_pagina')

            dias = form.cleaned_data['dias']
            activo = form.cleaned_data['activo']

            if dias != None or activo != None:
                if dias == 0 and (activo == None or activo == True):
                    qfilter = Vacaciones.reporte_vacaciones_pendientes()
                else:
                    qfilter = Vacaciones.reporte_vacaciones_pendientes_busqueda(activo=activo, dias_pendientes=dias)
            else:
                qfilter = Vacaciones.reporte_vacaciones_pendientes()

            if 'exportar_pdf' in request.GET or 'exportar_csv' in request.GET:

                values = qfilter.values('funcionario__usuario__persona__numero_documento',
                                        'funcionario__usuario__persona__primer_apellido',
                                        'funcionario__usuario__persona__segundo_apellido',
                                        'funcionario__usuario__persona__primer_nombre',
                                        'funcionario__usuario__persona__segundo_nombre',
                                        'dias_pendientes',
                                        'horas_pendientes',
                                        'minutos_pendientes')
                if 'exportar_csv' in request.GET:
                    response = HttpResponse(content_type='text/csv')
                    response[
                        'Content-Disposition'] = 'attachment; filename="reporte_vacaciones_pendientes_%s.csv"' % datetime.now().strftime(
                        "%Y%m%d_%H%M%S")

                    writer = csv.writer(response)
                    writer.writerow([u'Identificación', 'Apellidos', 'Nombres', 'Dias pendientes', 'Horas pendientes',
                                     'Minutos pendientes'])
                    for v in values:
                        row = [v['funcionario__usuario__persona__numero_documento'],
                               '%s %s' % (v['funcionario__usuario__persona__primer_apellido'],
                                          v['funcionario__usuario__persona__primer_apellido']),
                               '%s %s' % (v['funcionario__usuario__persona__primer_nombre'],
                                          v['funcionario__usuario__persona__segundo_nombre']),
                               v['dias_pendientes'], v['horas_pendientes'], v['minutos_pendientes']
                               ]
                        writer.writerow(row)
                    return response

                if 'exportar_pdf' in request.GET:
                    auxActivo = ''
                    if activo == None or activo == True:
                        auxActivo = 'Sí'
                    else:
                        auxActivo = "No"

                    total = qfilter.count()

                    vacacionesp = [dict(
                        identificacion=item.get('funcionario__usuario__persona__numero_documento'),
                        apellidos='%s %s' % (item.get('funcionario__usuario__persona__primer_apellido'),
                                             item.get('funcionario__usuario__persona__segundo_apellido')),
                        nombres='%s %s' % (item.get('funcionario__usuario__persona__primer_nombre'),
                                           item.get('funcionario__usuario__persona__segundo_nombre')),
                        diasp=item.get('dias_pendientes'),
                        horas=item.get('horas_pendientes'),
                        minutos=item.get('minutos_pendientes')

                    ) for item in values]

                    datos = dict(vacacionesp=vacacionesp, total=total, dias=dias, activos=auxActivo)

                    return pdfUtil.generar_reporte('talento_humano_vacaciones_pendientes', datos, 'pdf', request)

    total = qfilter.count()
    paginator = Paginator(qfilter, 25)

    try:
        registros = paginator.page(page)
    except PageNotAnInteger:
        registros = paginator.page(1)
    except EmptyPage:
        registros = paginator.page(paginator.num_pages)
    # asignaciones = lista_asignacion_puestos

    return render(request, 'talento_humano/reporte/form_vacaciones_pendientes.html', locals())


# </editor-fold>


@login_required
def reporte_general(request):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied
    lista_asignacion_puestos = AsignacionPuesto.reporte()
    total = lista_asignacion_puestos.count()
    form = ReporteGeneral()

    # form_filtros = ReporteGeneral() #

    page = None
    if request.method == 'GET':
        form = ReporteGeneral(request.GET)

        # form_filtros = ReporteGeneral(request.GET) #

        if form.is_valid():
            if 'pagina_siguiente' in request.GET:
                page = request.GET.get('siguiente')
            if 'pagina_anterior' in request.GET:
                page = request.GET.get('anterior')
            if 'pagina' in request.GET:
                page = request.GET.get('numero_pagina')

            edad = form.cleaned_data['edad']
            regimen_laboral_id = form.cleaned_data['regimen_laboral']
            regimen_laboral = None
            tipo_relacion_laboral_id = form.cleaned_data['tipo_relacion_laboral']
            tipo_relacion_laboral = None
            if regimen_laboral_id:
                regimen_laboral = RegimenLaboral.objects.filter(id=regimen_laboral_id).first()
            if tipo_relacion_laboral_id:
                tipo_relacion_laboral = CatalogoItem.objects.filter(id=tipo_relacion_laboral_id).first()
            lista_asignacion_puestos = AsignacionPuesto.reporte_general(
                activo=True,
                puesto='',
                regimen_laboral=regimen_laboral,
                tipo_relacion_laboral=tipo_relacion_laboral,
                edad=edad,
            )

            total = lista_asignacion_puestos.count()

            if 'exportar_pdf' in request.GET or 'exportar_csv' in request.GET:
                values = lista_asignacion_puestos.values('funcionario__usuario__persona__numero_documento',
                                                         'funcionario__usuario__persona__primer_apellido',
                                                         'funcionario__usuario__persona__segundo_apellido',
                                                         'funcionario__usuario__persona__primer_nombre',
                                                         'funcionario__usuario__persona__segundo_nombre',
                                                         'uaa_puesto__uaa__nombre',
                                                         'uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre',
                                                         'uaa_puesto__puesto__grupo_ocupacional__nombre',
                                                         'uaa_puesto__puesto__denominacion',
                                                         'tipo_relacion_laboral__nombre',
                                                         'fecha_inicio',
                                                         'funcionario__usuario__persona__fecha_nacimiento',
                                                         )

                for f in values:
                    f['edad'] = fecha.calcular_edad(f['funcionario__usuario__persona__fecha_nacimiento'])

                if 'exportar_csv' in request.GET:
                    response = HttpResponse(content_type='text/csv')
                    response[
                        'Content-Disposition'] = 'attachment; filename="reporte_por_edades%s.csv"' % datetime.now().strftime(
                        "%Y%m%d_%H%M%S")

                    writer = csv.writer(response)
                    for v in values:
                        writer.writerow([])
                        writer.writerow(['Nombres', '%s %s %s %s' % (
                            v['funcionario__usuario__persona__primer_apellido'],
                            v['funcionario__usuario__persona__segundo_apellido'],
                            v['funcionario__usuario__persona__primer_nombre'],
                            v['funcionario__usuario__persona__segundo_nombre'])])
                        writer.writerow([u'Identificación', 'UAA', 'Regimén laboral', 'Grupo ocupacional', 'Puesto',
                                         'Tipo relacion laboral', 'Fecha de inicio', 'Fecha de nacimiento', 'Edad'])
                        row = [v['funcionario__usuario__persona__numero_documento'],
                               v['uaa_puesto__uaa__nombre'],
                               v['uaa_puesto__puesto__grupo_ocupacional__regimen_laboral__nombre'],
                               v['uaa_puesto__puesto__grupo_ocupacional__nombre'],
                               v['uaa_puesto__puesto__denominacion'],
                               v['tipo_relacion_laboral__nombre'],
                               v['fecha_inicio'],
                               v['funcionario__usuario__persona__fecha_nacimiento'],
                               v['edad']
                               ]
                        writer.writerow(row)
                    return response

                if 'exportar_pdf' in request.GET:
                    total = lista_asignacion_puestos.count()

                    func = [dict(
                        identificacion=item.funcionario.usuario.persona.numero_documento,
                        nombres=item.funcionario.usuario.persona.get_nombres_completos_inverso(),
                        regimen=item.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre,
                        grupo=item.uaa_puesto.puesto.grupo_ocupacional.nombre,
                        puesto=item.uaa_puesto.puesto.denominacion,
                        uaa=item.uaa_puesto.uaa.nombre,
                        relacion=item.tipo_relacion_laboral.nombre,
                        inicio=item.fecha_inicio,
                        nacimiento=item.funcionario.usuario.persona.fecha_nacimiento,
                        edad=item.funcionario.usuario.persona.get_edad()

                    ) for item in lista_asignacion_puestos.order_by('uaa_puesto__uaa',
                                                                    'funcionario__usuario__persona__primer_apellido',
                                                                    'funcionario__usuario__persona__segundo_apellido')]
                    datos = dict(
                        asignaciones=func,
                        total=total

                    )
                    return pdfUtil.generar_reporte('talento_humano_funcionario_por_edad', datos, 'pdf', request)

    paginator = Paginator(lista_asignacion_puestos, 25)

    try:
        asignaciones = paginator.page(page)
    except PageNotAnInteger:
        asignaciones = paginator.page(1)
    except EmptyPage:
        asignaciones = paginator.page(paginator.num_pages)
    # asignaciones = lista_asignacion_puestos
    return render(request, 'talento_humano/reporte/formReporteGeneral.html', locals())


@login_required
def funcionario_reportes(request):
    """
    JJM 2018-10-18
    formulario para mostrar todos los links a reportes a los que tiene acceso el usuario
    :param request:
    :return:
    """
    usuario = request.user
    if not usuario.es_funcionario():
        raise PermissionDenied
    talento_humano = usuario.is_member('talento humano')
    sniese = usuario.is_member('reporte sniese')
    # seguridad_informacion = usuario.is_member('seguridad informacion')
    return render(request, 'talento_humano/funcionarios/reportes.html', locals())


@login_required
def reporte_sniese(request, tipo=0):
    """
    JJM 2018-10-18
    Formulario para mostrar los filtros y obtener reportes para el sniese de docentes y funcionarios
    :param request:
    :param tipo:
    :return:
    """
    usuario = request.user
    if not usuario.is_member('reporte sniese'):
        raise PermissionDenied
    # JJM aqui digo que reportes se pueden obtener, relacion con siguiente metodo
    tipos_reporte = ['docentes contratados', 'funcionarios']
    seleccionado = tipos_reporte[int(tipo)]
    # agrego seleccion de tipos de contrato, para no poner todas las opciones de tipos de contrato
    # solo para docentes escoje tipo de relacion, exclude nivel jerarquico,
    excluir = ['Libre nombramiento y remoción']
    tipo_relacion_laboral = CatalogoItem.objects.filter(catalogo__codigo='TIPO_RELACION_LABORAL'). \
        exclude(nombre__in=excluir).order_by('nombre').all()
    return render(request, 'talento_humano/funcionarios/reportes_sniese.html', locals())


@login_required
def generar_reporte_sniese(request):
    """
    Genero un reporte en base a las opciones seleccionadas en el formuario
    :param request: {fecha_desde, fecha_hasta, tipo_reporte:['docentes contratados','funcionarios'] }
    :return: Csv con todos as filas producto de la consulta
    """
    usuario = request.user
    if not usuario.is_member('reporte sniese'):
        raise PermissionDenied
    # datos de entrada
    fecha_desde = request.GET.get('fecha_desde', False)
    fecha_hasta = request.GET.get('fecha_hasta', False)
    tipo_reporte = request.GET.get('tipo_reporte', False)

    # dias = [c for c in list(request.POST.dict().keys()) if c.startswith('dia')]
    # archivo de respuesta excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s%s.xls"' % (
        tipo_reporte, datetime.now().strftime("%Y%m%d_%H%M%S"))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    results = []
    if fecha_desde and fecha_hasta and tipo_reporte:
        con = connection.cursor()
        try:
            con.execute("BEGIN")
            if tipo_reporte == 'docentes contratados':
                # tipos de contratos seleccionados
                tipo_relacion = results = list(map(int, request.GET.getlist('tipo_rel')))
                # LLamo a funcion creada en la base de datos.
                con.callproc("fn_matriz_docentes_contratados", (fecha_desde, fecha_hasta, False, tipo_relacion))
            elif tipo_reporte == 'funcionarios':
                con.callproc("fn_matriz_funcionarios", (fecha_desde, fecha_hasta))
            # si hay resultado escribo cabeceras
            if con.description:
                # writer.writerow([d.name for d in con.description])
                cabeceras = [d.name for d in con.description]
                for col_num in range(len(cabeceras)):
                    ws.write(row_num, col_num, cabeceras[col_num], font_style)
            results = con.fetchall()
            con.execute("COMMIT")
        except Exception as e:
            print(e)
        finally:
            con.close()

    for row in results:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num])

    wb.save(response)
    return response


# exportar PDF
@login_required
def trayectoria_laboral_pdf(request, funcionario_id):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    # html_template = get_template('talento_humano/reporte/reporte_trayectoria_laboral_pdf.html')
    # rendered_html = html_template.render(RequestContext(request,
    #                                                        {'funcionario': funcionario,
    #                                                         'generado': request.user
    #
    #                                                         })).encode(encoding="UTF-8")
    # ARCHIVO = BASE_DIR + "/static/css/reporte/reporte-vertical.css"
    # pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(ARCHIVO)])
    # http_response = HttpResponse(pdf_file, content_type='application/pdf')
    # http_response['Content-Disposition'] = 'filename="trayectoria_laboral_'+funcionario.usuario.persona.numero_documento+'.pdf"'
    # return http_response

    asignaciones_list = [dict(numero=numero + 1,
                              uaa=item.uaa_puesto.uaa.nombre,
                              fecha_inicio=item.fecha_inicio,
                              fecha_fin=item.fecha_fin,
                              fecha_termino=item.fecha_termino,
                              duracion=item.get_duracion_info(),
                              puesto='%s - %s' % (item.uaa_puesto.puesto.denominacion,
                                                  item.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral),
                              rmu=item.get_sueldo(),
                              relacion=str(item.tipo_relacion_laboral),
                              vigente='SI' if item.vigente else 'NO',
                              activo='SI' if item.activo else 'NO',
                              ) for numero, item in enumerate(funcionario.asignaciones_puestos.all())]

    parametros = dict(
        asignaciones=asignaciones_list,
        filtros=[{'criterio': 'Funcionario', 'valor': '%s - %s' % (
            funcionario.usuario.persona.numero_documento, funcionario.usuario.persona.get_nombres_completos())}],
        filename='TrayectoriaLaboral_%s' % funcionario.usuario.persona.numero_documento
    )
    return pdfUtil.generar_reporte('talento_humano_trayectoria_laboral', parametros, 'pdf', request)


@login_required
def vacacion_pdf(request, vacaciones_id):
    usuario = request.user
    if not usuario.is_member('talento humano'):
        raise PermissionDenied

    vacacion = get_object_or_404(Vacaciones, id=vacaciones_id)
    funcionario = vacacion.funcionario
    # html_template = get_template('talento_humano/reporte/reporte_vacacion_pdf.html')
    # rendered_html = html_template.render(RequestContext(request,
    #                                                        {'vacacion': vacacion,
    #                                                         'generado': request.user
    #                                                         })).encode(encoding="UTF-8")
    # ARCHIVO = BASE_DIR + "/static/css/reporte/reporte-vertical.css"
    # pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(ARCHIVO)])
    # http_response = HttpResponse(pdf_file, content_type='application/pdf')
    # http_response['Content-Disposition'] = 'filename="vacacion_'+vacacion.funcionario.usuario.persona.numero_documento+'.pdf"'
    # return http_response
    vacaciones_list = [dict(numero=numero + 1,
                            puesto='%s - $ %s - %s' % (
                                item.asignacion_puesto.uaa_puesto.puesto.denominacion,
                                item.asignacion_puesto.get_sueldo(),
                                item.asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral),
                            relacion=str(item.asignacion_puesto.tipo_relacion_laboral),
                            fecha_inicio=item.asignacion_puesto.fecha_inicio,
                            fecha_fin=item.asignacion_puesto.fecha_fin,
                            dias_pendientes=item.dias_pendientes,
                            horas_pendientes=item.horas_pendientes,
                            minutos_pendientes=item.minutos_pendientes
                            ) for numero, item in enumerate([vacacion])]

    parametros = dict(
        vacaciones=vacaciones_list,
        filtros=[{'criterio': 'Funcionario', 'valor': '%s - %s' % (
            funcionario.usuario.persona.numero_documento, funcionario.usuario.persona.get_nombres_completos())}],
        filename='Vacacion_%s_%s' % (vacaciones_id, funcionario.usuario.persona.numero_documento)
    )
    return pdfUtil.generar_reporte('talento_humano_vacacion', parametros, 'pdf', request)


@login_required
def reporte_ausentismos(request):
    if request.method == 'POST':
        ausentismos = list(map(int, request.POST.getlist('ausentismos'))) if 'ausentismos' in request.POST else None
        desde = request.POST['desde']
        hasta = request.POST['hasta']

        ausentismos_funcionarios = AusentismoFuncionario.objects.filter(fecha_inicio__range=[desde, hasta],
                                                                        fecha_fin__range=[desde, hasta])
        if ausentismos and 0 not in ausentismos:
            ausentismos_funcionarios = ausentismos_funcionarios.filter(ausentismo_id__in=ausentismos)
        ausentismos_funcionarios = ausentismos_funcionarios.all().order_by('funcionario__id', 'ausentismo__id',
                                                                           'fecha_inicio')

        if 'imprimir_pdf' in request.POST:
            ausentismo_lista = [dict(
                funcionario=item.funcionario.usuario.persona.get_nombres_completos_inverso(),
                tipo=item.ausentismo.tipo_ausentismo.nombre,
                descripcion=item.ausentismo.nombre,
                permiso=item.tipo_permiso.nombre,
                desde=item.fecha_inicio,
                hasta=item.fecha_fin,
                dias=item.dias,
                horas=item.horas,
                minutos=item.minutos,
                registro=item.fecha_registro,
                observacion=item.observacion
            ) for item in ausentismos_funcionarios]
            datos = dict(
                ausentismos=ausentismo_lista,
                desder=desde,
                hastar=hasta,
            )
            return pdfUtil.generar_reporte('talento_humano_ausentismos', datos, 'pdf', request)

        elif 'imprimir_excel' in request.POST:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="%s%s.xls"' % (
                "reporte_ausentismos", datetime.now().strftime("%Y%m%d_%H%M%S"))

            cabeceras = ["Nro.", "Funcionario", "Tipo", "Descripcion", "Permiso", "Desde", "Hasta", "Dias", "Horas",
                         "Minutos", "Registro", "Observación"]
            tamanios = [256 * 6, 256 * 30, 256 * 15, 256 * 30, 256 * 15, 256 * 15, 256 * 15, 256 * 15, 256 * 15,
                        256 * 15, 256 * 30, 256 * 30]
            filas = [(numero + 1,
                      ausentismo.funcionario.usuario.persona.get_nombres_completos_inverso(),
                      ausentismo.ausentismo.tipo_ausentismo.nombre,
                      ausentismo.ausentismo.nombre,
                      ausentismo.tipo_permiso.nombre,
                      ausentismo.fecha_inicio.strftime("%Y/%m/%d") if ausentismo.fecha_inicio else '',
                      ausentismo.fecha_fin.strftime("%Y/%m/%d") if ausentismo.fecha_fin else '',
                      ausentismo.dias,
                      ausentismo.horas,
                      ausentismo.minutos,
                      ausentismo.fecha_registro.strftime("%Y/%m/%d"),
                      ausentismo.observacion) for numero, ausentismo in enumerate(ausentismos_funcionarios)]

            workbook = generar_excel(filas=filas, cabeceras=cabeceras, tamanio_columnas=tamanios,
                                     titulo="Reporte de Ausentismos", alto_filas=7)
            workbook.save(response)
            return response

    else:
        ausentismos = Ausentismo.objects.all()

    return render(request, 'talento_humano/reporte/form_ausentismos.html', locals())

@login_required
def vacacion(request):
    try:
        usuario = request.user
    except Exception as e:
        print('ingreso')
        print(e)
    return render(request, 'talento_humano/funcionarios/funcionario/vacaciones.html', locals())


@login_required
def ausentismos(request):
    try:
        usuario = request.user
    except Exception as e:
        print(e)
    return render(request, 'talento_humano/funcionarios/funcionario/ausentismos.html', locals())

@login_required
def funcionario_usuario(request):
    usuario = request.user
    if not usuario.es_funcionario():
        raise PermissionDenied
    talento_humano = usuario.is_member('talento humano')
    seguridad_informacion = usuario.is_member('seguridad informacion')
    return render_to_response('talento_humano/funcionarios/funcionario/index.html', RequestContext(request, locals()))

##########################################################################################
# Fin para refactorizar
##########################################################################################

@login_required
def asignacion_puesto_filtro_siith(request):
    """
    Muestra el formulario para filtar la consulta de asignación de puestos e invoca a los metodos
    para exportar el reporte csv deacuerdo al formato del sistema SIITH
    :param request:
    :return:
    """
    if request.POST:
        estado = request.POST.get('estado', '0')
        regimen_laboral_id = request.POST.get('regimen_laboral', '0')
        fecha_inicio_desde = request.POST.get('fecha_inicio_desde', None)
        fecha_inicio_hasta = request.POST.get('fecha_inicio_hasta', None)
        fecha_fin_desde = request.POST.get('fecha_fin_desde', None)
        fecha_fin_hasta = request.POST.get('fecha_fin_hasta', None)
        fecha_termino_desde = request.POST.get('fecha_termino_desde', None)
        fecha_termino_hasta = request.POST.get('fecha_termino_hasta', None)
        activo = None if estado == '0' else True if estado == '1' else False
        regimen_laboral = None if regimen_laboral_id == '0' else RegimenLaboral.objects.get(id=regimen_laboral_id)

        funcionario_ids = list(set(AsignacionPuesto.reporte(activo=activo,
                                                            regimen_laboral=regimen_laboral,
                                                            fecha_inicio_desde=fecha_inicio_desde,
                                                            fecha_inicio_hasta=fecha_inicio_hasta,
                                                            fecha_fin_desde=fecha_fin_desde,
                                                            fecha_fin_hasta=fecha_fin_hasta,
                                                            fecha_termino_desde=fecha_termino_desde,
                                                            fecha_termino_hasta=fecha_termino_hasta
                                                         ).values_list('funcionario__id', flat=True)))

        if 'reporte_info_personal' in request.POST:
            return asignacion_puesto_reporte_siith_info_personal(funcionario_ids)
        elif 'reporte_info_bancaria' in request.POST:
            return asignacion_puesto_reporte_siith_info_bancaria(funcionario_ids)
        elif 'reporte_info_conyuge' in request.POST:
            return asignacion_puesto_reporte_siith_info_conyuge(funcionario_ids)
        elif 'reporte_cargas_familiares' in request.POST:
            return asignacion_puesto_reporte_siith_cargas_familiares(funcionario_ids)
        elif 'reporte_info_academica' in request.POST:
            return asignacion_puesto_reporte_siith_info_academica(funcionario_ids)
        elif 'reporte_capacitaciones' in request.POST:
            return asignacion_puesto_reporte_siith_capacitacion(funcionario_ids)
        elif 'reporte_trayectoria_laboral' in request.POST:
            return asignacion_puesto_reporte_siith_trayectoria_externa(funcionario_ids)
        elif 'reporte_fotografias' in request.POST:
            return asignacion_puesto_reporte_siith_fotografias(funcionario_ids)

    else:
        regimenes_laborales = RegimenLaboral.objects.all()

    navegacion = ('Módulo de reportes',
                  [('Inicio', reverse('index')), ('Exportación de datos para SIITH', None)])
    return render(request, 'talento_humano/asignacion_puesto/filtro_siith.html', locals())


def asignacion_puesto_reporte_siith_info_personal(funcionario_ids):
    """
    Retorna el reporte csv de la información personal de los funcionarios de acuerdo al sistema SIITH, como
    datos personales, direccion, contacto, declaración de bienes, otros
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="siith_informacion_personal_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(['numeroDocumento', 'apellido', 'nombre', 'tipoDocumento', 'servidorPasanteConvenio',
                     'numeroLibretaMilitar', 'nacionalidadId', 'aniosResidencia', 'fechaNacimiento', 'sexoId',
                     'tipoSangreId', 'estadoCivilId', 'discapacidad', 'numeroCarnetConadis', 'tipoDiscapacidadId',
                     'servidorCarrera', 'numeroRegistroCertificado', 'identificacionEtnicaId', 'nacionalidadIndigenaId',
                     'direccionCallePrincipal', 'direccionNumero', 'direccionCalleSecundaria', 'direccionReferencia',
                     'telefonoDomicilio', 'telefonoCelular', 'telefonoTrabajo', 'telefonoExtension',
                     'correoElectronico',
                     'correoElectronicoTmp', 'direccionProvinciaId', 'direccionCantonId', 'direccionParroquiaId',
                     'contactoApellido', 'contactoNombre', 'contactoTelefono', 'contactoTelefonoCelular',
                     'numeroNotariaBienes', 'lugarNotariaBienesId', 'fechaNotariaBienes'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        persona = funcionario.usuario.persona
        expediente = Expediente.objects.filter(persona=persona).first()
        direccion_domicilo = Direccion.objects.filter(persona=persona, tipo_direccion__codigo_th=2).first()
        direccion_trabajo = Direccion.objects.filter(persona=persona, tipo_direccion__codigo_th=3).first()
        contacto = Relacion.objects.filter(expediente=expediente, contacto=True).first() if expediente else None
        declaracion_bienes = DeclaracionBienes.objects.filter(expediente=expediente).first() if expediente else None

        row = [persona.numero_documento, persona.get_apellidos(), persona.get_nombres(), persona.tipo_documento.codigo_th,
               0,  # servidorPasanteConvenio
               persona.numero_libreta_militar if persona.numero_libreta_militar else '',
               persona.nacionalidad.codigo_th if persona.nacionalidad else '',
               persona.anios_residencia if persona.anios_residencia else '',
               persona.fecha_nacimiento.strftime("%d/%m/%Y"),
               persona.sexo.codigo_th if persona.sexo else '',
               persona.tipo_sangre.codigo_th if persona.tipo_sangre else '',
               persona.estado_civil.codigo_th if persona.estado_civil else '',
               1 if persona.discapacidad else 0,
               persona.numero_carnet_conadis if persona.numero_carnet_conadis else '',
               persona.tipo_discapacidad.codigo_th if persona.tipo_discapacidad else '',
               0, '',  # servidorCarrera, numeroRegistroCertificado
               persona.tipo_etnia.codigo_th if persona.tipo_etnia else '',
               persona.nacionalidad_indigena.codigo_th if persona.nacionalidad_indigena else '',
               direccion_domicilo.calle_principal if direccion_domicilo else '',
               direccion_domicilo.numero if direccion_domicilo else '',
               direccion_domicilo.calle_secundaria if direccion_domicilo else '',
               direccion_domicilo.referencia if direccion_domicilo else '',
               direccion_domicilo.telefono if direccion_domicilo else '',
               direccion_domicilo.celular if direccion_domicilo else '',
               direccion_trabajo.telefono if direccion_trabajo else '',
               direccion_trabajo.extension if direccion_trabajo else '',
               persona.correo_electronico,
               persona.correo_electronico_alternativo if persona.correo_electronico_alternativo else '',
               direccion_domicilo.parroquia.canton.provincia.codigo_th if direccion_domicilo and direccion_domicilo.parroquia else '',
               direccion_domicilo.parroquia.canton.codigo_th if direccion_domicilo and direccion_domicilo.parroquia else '',
               direccion_domicilo.parroquia.codigo_th if direccion_domicilo and direccion_domicilo.parroquia else '',
               contacto.apellidos if contacto else '',
               contacto.nombres if contacto else '',
               contacto.telefono if contacto else '',
               contacto.celular if contacto else '',
               declaracion_bienes.numero_notaria if declaracion_bienes else '',
               declaracion_bienes.lugar_notaria.codigo_th if declaracion_bienes else '',
               declaracion_bienes.fecha_declaracion.strftime("%d/%m/%Y") if declaracion_bienes else ''
               ]
        writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_info_bancaria(funcionario_ids):
    """
    Retorna el reporte csv de la información bancaria de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="siith_informacion_bancaria_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [u'numeroDocumento', 'institucionFinancieraBancariaId', 'tipoCuentaBancariaId', 'numeroCuentaBancaria'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        expediente = Expediente.objects.filter(persona=funcionario.usuario.persona).first()
        if expediente:
            informacion_bancaria = InformacionBancaria.objects.filter(expediente=expediente).first()
            if informacion_bancaria:
                row = [funcionario.usuario.persona.numero_documento,
                       informacion_bancaria.institucion_financiera.codigo_th,
                       informacion_bancaria.tipo_cuenta.codigo_th,
                       informacion_bancaria.numero_cuenta
                       ]
                writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_info_conyuge(funcionario_ids):
    """
    Retorna el reporte csv de la información de conyuge de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="siith_informacion_conyuge_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([u'tipoDocumentoId', 'numeroDocumento', 'nombre', 'apellido', 'tipoRelacionId', 'servidorId'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        expediente = Expediente.objects.filter(persona=funcionario.usuario.persona).first()
        if expediente:
            conyulle = Relacion.objects.filter(expediente=expediente, tipo_relacion__codigo_th__in=(1, 2)).first()
            if conyulle:
                row = [conyulle.tipo_documento.codigo_th,
                       conyulle.numero_documento,
                       conyulle.nombres,
                       conyulle.apellidos,
                       conyulle.tipo_relacion.codigo_th,
                       funcionario.usuario.persona.numero_documento
                       ]
                writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_cargas_familiares(funcionario_ids):
    """
    Retorna el reporte csv de la información de los hijos de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="siith_cargas_familiares_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [u'tipoDocumentoId', 'numeroDocumento', 'nombre', 'apellido', 'fechaNacimiento', 'nivelInstruccionId',
         'servidorId'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        expediente = Expediente.objects.filter(persona=funcionario.usuario.persona).first()
        if expediente:
            hijos = Relacion.objects.filter(expediente=expediente, tipo_relacion__codigo_th=6).all()
            for hijo in hijos:
                row = [hijo.tipo_documento.codigo_th,
                       hijo.numero_documento,
                       hijo.nombres,
                       hijo.apellidos,
                       hijo.fecha_nacimiento.strftime("%d/%m/%Y") if hijo.fecha_nacimiento else '',
                       hijo.nivel_instruccion.codigo_th if hijo.nivel_instruccion else '',
                       funcionario.usuario.persona.numero_documento
                       ]
                writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_info_academica(funcionario_ids):
    """
    Retorna el reporte csv de la información académica de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="siith_informacion_academica_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([u'nivelInstruccionId', 'numeroRegistroCertificado', 'institucionEducativa', 'anioEstudios',
                     'tipoPeriodoId', 'areaConocimiento', 'egresado', 'titulo', 'paisId', 'servidorId'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        expediente = Expediente.objects.filter(persona=funcionario.usuario.persona).first()
        if expediente:
            formaciones_academicas = FormacionAcademica.objects.filter(expediente=expediente).all()
            for formacion_academica in formaciones_academicas:
                row = [formacion_academica.nivel_instruccion.codigo_th,
                       formacion_academica.numero_registro,
                       formacion_academica.institucion_educativo_otro,
                       formacion_academica.periodos_aprobados,
                       formacion_academica.tipo_periodo_estudio.codigo_th if formacion_academica.tipo_periodo_estudio else '',
                       formacion_academica.area_conocimiento,
                       1 if formacion_academica.egresado else 0,
                       formacion_academica.titulo_obtenido,
                       formacion_academica.pais.codigo if formacion_academica.pais else '',
                       funcionario.usuario.persona.numero_documento
                       ]
                writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_capacitacion(funcionario_ids):
    """
    Retorna el reporte csv de las capaacitaciones de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="siith_capacitacion_%s.csv"' % datetime.now().strftime(
        "%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(['evento', 'tipoEventoCapacitacion', 'auspiciante', 'duracion',
                     'tipoCertificado', 'certificadoPor', 'fechaInicio', 'fechaFin', 'pais', 'servidor'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        expediente = Expediente.objects.filter(persona=funcionario.usuario.persona).first()
        if expediente:
            capacitaciones = Capacitacion.objects.filter(expediente=expediente).all()
            for capacitacion in capacitaciones:
                row = [capacitacion.evento,
                       capacitacion.tipo_evento.codigo_th,
                       capacitacion.auspiciante,
                       capacitacion.horas,
                       capacitacion.tipo_certificacion.codigo_th,
                       capacitacion.certificado_por,
                       capacitacion.fecha_inicio.strftime("%d/%m/%Y"),
                       capacitacion.fecha_fin.strftime("%d/%m/%Y"),
                       capacitacion.pais.codigo,
                       funcionario.usuario.persona.numero_documento
                       ]
                writer.writerow(row)
    return response


def asignacion_puesto_reporte_siith_trayectoria_externa(funcionario_ids):
    """
    Retorna el reporte csv de la trayectoria laboral externa de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="siith_trayectoria_externa_%s.csv"' % datetime.now().strftime("%Y%m%d_%H%M%S")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(['tipoInstitucion', 'institucion', 'unidadAdministrativa', 'denominacionPuesto',
                     'fechaIngreso', 'fechaSalida', 'motivoIngreso', 'motivoSalida', 'servidor'])

    for funcionario_id in funcionario_ids:
        funcionario = Funcionario.objects.get(id=funcionario_id)
        trayectoria_laboral_externas = TrayectoriaLaboralExterna.objects.filter(funcionario=funcionario).all()

        for trayectoria_externa in trayectoria_laboral_externas:
            row = [trayectoria_externa.tipo_institucion.codigo_th,
                   trayectoria_externa.institucion,
                   trayectoria_externa.unidad_academica if trayectoria_externa.unidad_academica else trayectoria_externa.institucion,
                   trayectoria_externa.puesto,
                   trayectoria_externa.fecha_inicio.strftime("%d/%m/%Y"),
                   trayectoria_externa.fecha_fin.strftime("%d/%m/%Y"),
                   trayectoria_externa.motivo_ingreso.codigo_th,
                   trayectoria_externa.motivo_salida.codigo_th,
                   funcionario.usuario.persona.numero_documento
                   ]
            writer.writerow(row)
    return response

def asignacion_puesto_reporte_siith_fotografias(funcionario_ids):
    """
    Retorna el en .zip (nombre, número de documento) todas las fotos de los funcionarios de acuerdo al sistema SIITH
    :param funcionario_ids:
    :return:
    """
    byte = BytesIO()
    zip = ZipFile(byte, "w")

    for index, funcionario_id in enumerate(funcionario_ids):
        funcionario = Funcionario.objects.get(id=funcionario_id)
        if funcionario.usuario.foto_url:
            foto_data = requests.get(funcionario.usuario.foto_url)
            if foto_data and foto_data.status_code == 200:
                foto_content = foto_data.content
                foto_nombre = "%s.jpg" % (funcionario.usuario.persona.numero_documento)
                zip.writestr(foto_nombre, foto_content)

    zip.close()
    response = HttpResponse(byte.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename="siith_fotografias_%s.zip"' % datetime.now().strftime("%Y%m%d_%H%M%S")
    return response


@login_required
def capacitacion_crear(request, persona_id):
    """
    Muestra la interfaz para registra una capacitación de la persona
    :param request:
    :param persona_id: El identificador de la persona
    :return: página principal de perfil
    """
    persona = Persona.objects.get(id=persona_id)
    next = request.GET.get('next')
    try:
        expediente = persona.expediente
    except:
        expediente = Expediente()
        expediente.persona = persona
        expediente.save()
    capacitacion_form = CapacitacionForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_capacitacion'),
                       ('Capacitación', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_capacitacion'),
                       ('Capacitación', None)])

    return render(request, 'talento_humano/capacitacion/editar.html', locals())


@login_required
def capacitacion_editar(request, id):
    """
    Modifica una capacitación del funcionario
    :param request:
    :param id: El identificador de la capacitación
    :return: página principal de perfil
    """
    next = request.GET.get('next')
    capacitacion = get_object_or_404(Capacitacion, id=id)
    capacitacion_form = CapacitacionForm(instance=capacitacion)
    persona = capacitacion.expediente.persona

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_capacitacion'),
                       ('Capacitación', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_capacitacion'),
                       ('Capacitación', None)])

    return render(request, 'talento_humano/capacitacion/editar.html', locals())


@login_required
def capacitacion_guardar(request, persona_id):
    """
    Guardar/Actualizar una evaluación de desempeño
    :param request:
    :param persona_id: El identificador de la persona
    :param id: El identificador de la capacitación
    :return: página principal del perfil
    """
    next = request.POST.get('next')
    id = request.POST.get('id')
    persona = Persona.objects.get(id=persona_id)
    try:
        capacitacion = get_object_or_404(Capacitacion, id=id)
    except:
        capacitacion = Capacitacion()

    capacitacion_form = CapacitacionForm(request.POST, instance=capacitacion)
    if capacitacion_form.is_valid():
        capacitacion = capacitacion_form.save(commit=False)
        capacitacion.expediente = persona.expediente
        capacitacion.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_capacitacion')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_capacitacion'),
                           ('Capacitación', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[persona.usuario.funcionario.id]) + '#tab_capacitacion'),
                           ('Capacitación', None)])

    return render(request, 'talento_humano/capacitacion/editar.html', locals())


@login_required
def capacitacion_eliminar(request, id):
    """
    Elimina el registro de una capacitacion
    :param request:
    :param id: identificador de la capacitación
    :return: página principal
    """
    next = request.GET.get('next')
    capacitacion = Capacitacion.objects.get(id=id)
    capacitacion.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next + '#tab_capacitacion')


@login_required
def declaracion_bienes_crear(request, persona_id):
    """
    Muestra la interfaz para crear una declaracion de bienes y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)
    declaracion_bienes_form = DeclaracionBienesForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')),
                       ('Declaración Juramentada de Bienes', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id])),
                       ('Declaración Juramentada de Bienes', None)])

    return render(request, 'talento_humano/declaracion_bienes/editar.html', locals())


@login_required
def declaracion_bienes_editar(request, id):
    """
    Muestra el registro para editar una declaracion de bienes y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    declaracion_bienes = DeclaracionBienes.objects.get(id=id)
    persona = declaracion_bienes.expediente.persona
    declaracion_bienes_form = DeclaracionBienesForm(instance=declaracion_bienes)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')),
                       ('Declaración Juramentada de Bienes', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id])),
                       ('Declaración Juramentada de Bienes', None)])

    return render(request, 'talento_humano/declaracion_bienes/editar.html', locals())


def declaracion_bienes_guardar(request, persona_id):
    """
    Crea o actualiza un registro de declaracion de bienes, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        declaracion_bienes = get_object_or_404(DeclaracionBienes, id=id)
    except:
        declaracion_bienes = DeclaracionBienes()

    persona = Persona.objects.get(id=persona_id)
    declaracion_bienes_form = DeclaracionBienesForm(request.POST, instance=declaracion_bienes)

    if declaracion_bienes_form.is_valid():
        declaracion_bienes = declaracion_bienes_form.save(commit=False)
        declaracion_bienes.expediente = persona.expediente
        declaracion_bienes.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next)
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil')),
                           ('Declaración Juramentada de Bienes', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario', args=[persona.usuario.funcionario.id])),
                           ('Declaración Juramentada de Bienes', None)])

    return render(request, 'talento_humano/declaracion_bienes/editar.html', locals())


@login_required
def declaracion_bienes_eliminar(request, id):
    """
    Elimina un registro declaracion bienes, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    declaracion_bienes = DeclaracionBienes.objects.get(id=id)
    declaracion_bienes.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)

    return HttpResponseRedirect(next)


@login_required
@permission_required('talento_humano.add_evaluaciondesempenio', raise_exception=True, )
def evaluacion_desempenio_crear(request, funcionario_id):
    """
    Muestra la interfaz para crear una evaluacion de desempeño de un contrato del funcionario
    :param request:
    :param funcionario_id: El identificador del funcionario
    :return: página principal del funcionario una vez agregada la evaluacion de desempeño
    """
    next = request.GET.get('next')
    funcionario = Funcionario.objects.get(id=funcionario_id)
    dict = {'funcionario_id': funcionario.id}
    evaluacion_desempenio_form = EvaluacionDesempenioForm(**dict)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_evaluacion_desempenio'),
                       ('Evaluación de desempeño', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (funcionario.usuario.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[funcionario.id]) + '#tab_evaluacion_desempenio'),
                       ('Evaluación de desempeño', None)])

    return render(request, 'talento_humano/evaluacion_desempenio/editar.html', locals())


@login_required
@permission_required('talento_humano.change_evaluaciondesempenio', raise_exception=True, )
def evaluacion_desempenio_editar(request, id):
    """
    Modifica una evaluacion de desempeño de un contrato del funcionario
    :param request:
    :param id: El identificador de la evaluacion de desempeño
    :return: página principal del funcionario una vez agregada la evaluacion de desempeño
    """
    next = request.GET.get('next')
    evaluacion_desempenio = get_object_or_404(EvaluacionDesempenio, id=id)
    funcionario = evaluacion_desempenio.funcionario
    dict = {'funcionario_id': funcionario.id}
    evaluacion_desempenio_form = EvaluacionDesempenioForm(instance=evaluacion_desempenio, **dict)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_evaluacion_desempenio'),
                       ('Evaluación de desempeño', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (funcionario.usuario.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[funcionario.id]) + '#tab_evaluacion_desempenio'),
                       ('Evaluación de desempeño', None)])

    return render(request, 'talento_humano/evaluacion_desempenio/editar.html', locals())


@login_required
@permission_required(('talento_humano.add_evaluaciondesempenio', 'talento_humano.change_evaluaciondesempenio'), raise_exception=True,)
def evaluacion_desempenio_guardar(request, funcionario_id):
    """
    Guardar/Actualizar una evaluación de desempeño
    :param request:
    :param: funcionario_id: El identificador del funcionario
    :return: página principal del funcionario una vez agregada la evaluación de desempeño
    """
    id = request.POST.get('id')
    next = request.POST.get('next')

    try:
        evaluacion_desempenio = get_object_or_404(EvaluacionDesempenio, id=id)
    except:
        evaluacion_desempenio = EvaluacionDesempenio()

    funcionario = Funcionario.objects.get(id=funcionario_id)
    evaluacion_desempenio_form = EvaluacionDesempenioForm(request.POST, instance=evaluacion_desempenio)

    if evaluacion_desempenio_form.is_valid():
        evaluacion_desempenio = evaluacion_desempenio_form.save(commit=False)
        evaluacion_desempenio.funcionario = funcionario
        evaluacion_desempenio.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_evaluacion_desempenio')
    else:
        dict = {'funcionario_id': funcionario.id}
        evaluacion_desempenio_form = EvaluacionDesempenioForm(request.POST, **dict)
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)

        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_evaluacion_desempenio'),
                           ('Evaluación de desempeño', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (funcionario.usuario.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[funcionario.id]) + '#tab_evaluacion_desempenio'),
                           ('Evaluación de desempeño', None)])

    return render(request, 'talento_humano/evaluacion_desempenio/editar.html', locals())


@login_required
@permission_required('talento_humano.delete_evaluaciondesempenio', raise_exception=True, )
def evaluacion_desempenio_eliminar(request, id):
    """
       Elimina el registro de una evaluación de desempeño
       :param request:
       :param id_evaluacion_desempenio: identificador de la evaluación de desempeño
       :return: paǵina principal del funcionario una vez eliminada la evaluación de desempeño
       """
    next = request.GET.get('next')
    evaluacion_desempenio = EvaluacionDesempenio.objects.get(id=id)
    evaluacion_desempenio.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next+'#tab_evaluacion_desempenio')


@login_required
def formacion_academica_senescyt(request, persona_id):
    """
    Crea o actualiza los registros de formación académica desde la senescyt  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)
    persona.actualizar_formacion_academica()
    messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    return HttpResponseRedirect(next+'#tab_formacion_academica')


@login_required
def formacion_academica_editar(request, id):
    """
    Muestra el registro de formación academica para editarlo y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    formacion_academica = FormacionAcademica.objects.get(id=id)
    persona = formacion_academica.expediente.persona
    formacion_academica_form = FormacionAcademicaForm(instance=formacion_academica)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_formacion_academica'),
                       ('Formación Académica', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_formacion_academica'),
                       ('Formación Académica', None)])

    return render(request, 'talento_humano/formacion_academica/editar.html', locals())


@login_required
def formacion_academica_guardar(request):
    """
    Actualiza un registro de formación academica, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :return:
    """

    id = request.POST.get('id')
    next = request.POST.get('next')

    formacion_academica = FormacionAcademica.objects.get(id=id)
    formacion_academica_form = FormacionAcademicaForm(request.POST, instance=formacion_academica)
    persona = formacion_academica.expediente.persona

    if formacion_academica_form.is_valid():
        formacion_academica_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_formacion_academica')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)

        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_formacion_academica'),
                           ('Formación Académica', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[persona.usuario.funcionario.id]) + '#tab_formacion_academica'),
                           ('Formación Académica', None)])

    return render(request, 'talento_humano/formacion_academica/editar.html', locals())


@login_required
@permission_required('talento_humano.delete_formacionacademica', raise_exception=True, )
def formacion_academica_eliminar(request, id):
    """
    Elimina un registro de formación académica, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    formacion = FormacionAcademica.objects.get(id=id)
    formacion.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next)


@login_required
def informacion_bancaria_crear(request, persona_id):
    """
    Muestra la interfaz para crear una informacion bancaria y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)
    informacion_bancaria_form = InformacionBancariaForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')),
                       ('Cuenta Bancaria', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id])),
                       ('Cuenta Bancaria', None)])

    return render(request, 'talento_humano/informacion_bancaria/editar.html', locals())


@login_required
def informacion_bancaria_editar(request, id):
    """
    Muestra el registro para editar una información bancaria y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    informacion_bancaria = InformacionBancaria.objects.get(id=id)
    persona = informacion_bancaria.expediente.persona
    informacion_bancaria_form = InformacionBancariaForm(instance=informacion_bancaria)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')),
                       ('Cuenta Bancaria', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id])),
                       ('Cuenta Bancaria', None)])

    return render(request, 'talento_humano/informacion_bancaria/editar.html', locals())


def informacion_bancaria_guardar(request, persona_id):
    """
    Crea o actualiza un registro de información bancaria, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        informacion_bancaria = get_object_or_404(InformacionBancaria, id=id)
    except:
        informacion_bancaria = InformacionBancaria()

    persona = Persona.objects.get(id=persona_id)
    informacion_bancaria_form = InformacionBancariaForm(request.POST, instance=informacion_bancaria)

    if informacion_bancaria_form.is_valid():
        informacion_bancaria = informacion_bancaria_form.save(commit=False)
        informacion_bancaria.expediente = persona.expediente
        informacion_bancaria.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next)
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)

        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil')),
                           ('Cuenta Bancaria', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario', args=[persona.usuario.funcionario.id])),
                           ('Cuenta Bancaria', None)])

    return render(request, 'talento_humano/informacion_bancaria/editar.html', locals())


@login_required
def informacion_bancaria_eliminar(request, id):
    """
    Elimina un registro de informacion bancaria, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    informacion_bancaria = InformacionBancaria.objects.get(id=id)
    informacion_bancaria.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)

    return HttpResponseRedirect(next)


@login_required
def trayectoria_laboral_externa_crear(request, funcionario_id):
    """
    Muestra la interfaz para crear una trayectoria laboral  externa del funcionario
    :param request:
    :param funcionario_id: El identificador del funcionario
    :return: página principal del funcionario una vez agregada la trayectoria laboral externa
    """
    next = request.GET.get('next')
    funcionario = Funcionario.objects.get(id=funcionario_id)
    trayectoria_laboral_externa_form = TrayectoriaLaboralExternaForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')+'#tab_trayectoria_laboral'),
                       ('Trayectoria laboral externa', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (funcionario.usuario.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario', args=[funcionario.id])+'#tab_trayectoria_laboral'),
                       ('Trayectoria laboral externa', None)])

    return render(request, 'talento_humano/trayectoria_laboral_externa/editar.html', locals())


@login_required
def trayectoria_laboral_externa_editar(request, id):
    """
    Modifica una trayectoria laboral externa del funcionario
    :param request:
    :param id: El identificador de la trayectoria laboral externa
    :return: página principal del funcionario una vez agregada la trayectoria laboral externa
    """
    next = request.GET.get('next')
    trayectoria_laboral_externa = get_object_or_404(TrayectoriaLaboralExterna, id=id)
    funcionario = trayectoria_laboral_externa.funcionario
    trayectoria_laboral_externa_form = TrayectoriaLaboralExternaForm(instance=trayectoria_laboral_externa)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')+'#tab_trayectoria_laboral'),
                       ('Trayectoria laboral externa', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (funcionario.usuario.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario', args=[funcionario.id])+'#tab_trayectoria_laboral'),
                       ('Trayectoria laboral externa', None)])

    return render(request, 'talento_humano/trayectoria_laboral_externa/editar.html', locals())


@login_required
def trayectoria_laboral_externa_guardar(request, funcionario_id):
    """
    Guardar/Actualizar una trayectoria laboral externa del funcionario
    :param request:
    :param funcionario_id: El identificador del funcionario
    :return: página principal del funcionario una vez agregada la trayectoria laboral externa
    """
    id = request.POST.get('id')
    next = request.POST.get('next')
    try:
        trayectoria_laboral = get_object_or_404(TrayectoriaLaboralExterna, id=id)
    except:
        trayectoria_laboral = TrayectoriaLaboralExterna()

    funcionario = Funcionario.objects.get(id=funcionario_id)
    trayectoria_laboral_form = TrayectoriaLaboralExternaForm(request.POST, instance=trayectoria_laboral)

    if trayectoria_laboral_form.is_valid():
        trayectoria = trayectoria_laboral_form.save(commit=False)
        trayectoria.funcionario = funcionario
        trayectoria.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_trayectoria_laboral')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)

        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % funcionario.usuario.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_trayectoria_laboral'),
                           ('Trayectoria laboral externa', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (funcionario.usuario.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario', args=[funcionario.id]) + '#tab_trayectoria_laboral'),
                           ('Trayectoria laboral externa', None)])

    return render(request, 'talento_humano/trayectoria_laboral_externa/editar.html', locals())


@login_required
def trayectoria_laboral_externa_eliminar(request, id):
    """
    Elimina el registro de una trayectoria laboral externa de un funcionario
    :param request:
    :param id: identificador de la trayectoria laboral externa
    :return: paǵina principal del funcionario una vez eliminada la trayectoria laboral
    """
    next = request.GET.get('next')
    trayectoria_laboral = TrayectoriaLaboralExterna.objects.get(id=id)
    trayectoria_laboral.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next+'#tab_trayectoria_laboral')

@login_required
def registro_vacaciones_filtro(request):
    """
    Muestra el filtro para la busqueda de registro vacaciones
    :param request:
    :return:
    """
    navegacion = ('Módulo de reportes',
                  [('Inicio', reverse('index')), ('Registro vacaciones', None)])
    detalles_planificacion = DetallePlanificacion.objects.filter(planificacion__codigo__istartswith='VACACIONES_').all()
    regimenes_laborales = RegimenLaboral.objects.all()

    return render(request, 'talento_humano/registro_vacaciones/filtro.html', locals())

@login_required
@require_http_methods(["POST"])
def registro_vacaciones_reporte(request):
    """
    Retorna el reporte de registro vacaciones en excel
    :param request:
    :return:
    """
    detalle_planificacion = request.POST.get('detalle_planificacion', None)
    fecha_inicio_desde = request.POST.get('fecha_inicio_desde', None)
    fecha_inicio_hasta = request.POST.get('fecha_inicio_hasta', None)
    fecha_fin_desde = request.POST.get('fecha_fin_desde', None)
    fecha_fin_hasta = request.POST.get('fecha_fin_hasta', None)
    regimen_laboral = request.POST.get('regimen_laboral', None)

    qset = Q()
    if detalle_planificacion:
        qset = qset & (~Q(detalle_planificacion=None) & Q(detalle_planificacion_id=detalle_planificacion))
    else:
        qset = qset & (Q(detalle_planificacion=None))
    if fecha_inicio_desde:
        qset = qset & (Q(fecha_inicio__gte=fecha_inicio_desde))
    if fecha_inicio_hasta:
        qset = qset & (Q(fecha_inicio__lte=fecha_inicio_hasta))
    if fecha_fin_desde:
        qset = qset & (Q(fecha_fin__gte=fecha_fin_desde))
    if fecha_fin_hasta:
        qset = qset & (Q(fecha_fin__lte=fecha_fin_hasta))
    if regimen_laboral:
        qset = qset & (Q(vacaciones__asignacion_puesto__uaa_puesto__puesto__grupo_ocupacional__regimen_laboral_id=regimen_laboral))

    registro_vacaciones = RegistroVacaciones.objects.filter(qset).all()

    if 'reporte_excel' in request.POST:

        cabeceras = ["Nro.", "Identificación", "Nombres/Apellidos", "Detalle planificación",
                     "Regimen laboral", "Desde", "Hasta", "Nro. días", 'Observación']

        lista = [(numero + 1,
                  item.vacaciones.funcionario.usuario.persona.numero_documento,
                  item.vacaciones.funcionario.usuario.persona.get_nombres_completos(),
                  item.detalle_planificacion.nombre if item.detalle_planificacion_id else '',
                  item.vacaciones.asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre,
                  item.fecha_inicio,
                  item.fecha_fin,
                  item.get_numero_dias(),
                  item.observacion,
                  ) for numero, item in enumerate(registro_vacaciones)]

        return retornar_excel(nombre_reporte='reporte_registro_vacaciones',
                              filas=lista,
                              cabeceras=cabeceras,
                              titulo="Reporte de registro vacaciones")


    if 'reporte_pdf' in request.POST:
        lista = [dict(numero= numero + 1,
                  identificacion=item.vacaciones.funcionario.usuario.persona.numero_documento,
                  nombres=item.vacaciones.funcionario.usuario.persona.get_nombres_completos(),
                  detalle=item.detalle_planificacion.nombre,
                  regimen=item.vacaciones.asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre,
                  desde=item.fecha_inicio,
                  hasta=item.fecha_fin,
                  dias=item.get_numero_dias(),
                  observacion=item.observacion,
                  ) for numero, item in enumerate(registro_vacaciones)]


        total=len(lista)
        datos=dict(
            vacaciones=lista,
            total=total,
        )
        return pdfUtil.generar_reporte('talento_humano_registro_vacaciones', datos, 'pdf', request)