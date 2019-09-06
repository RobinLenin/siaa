from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from app.bsg.views import consultar_por_cedula_regciv
from app.core.utils.enums import MensajesEnum
from app.core.utils.general import dividir_nombres_completos
from app.core.utils.google import nombre_usuario_disponible, get_usuario_google
from app.core.utils.ldap import crear_usuario_ldap_of_cuenta_correo, existe_usuario_by_uid
from app.seguridad.forms import GrupoLdapForm, UsuarioValidarForm, CuentaCorreoForm
from app.seguridad.models import Usuario, GrupoLDAP, CuentaCorreo

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from app.core.dto.datatable import DataTableParams

@login_required
def index(request):
    """
    Presenta la página de inicio del módulo de seguridad de la información
    :param request:
    :return:
    """
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index'))])
    return render(request, 'seguridad_informacion/index.html', locals())


@login_required
@permission_required('seguridad.view_cuentacorreo', raise_exception=True, )
def cuenta_correo_consultar_numero_documento(request, numero_documento):
    """
    Consulta si existe la cuenta de correo por el numero_documento
    :param request:
    :param numero_documento:
    :return:
    """
    mensaje = ''
    if request.is_ajax():
        if numero_documento:
            cuenta_correo = CuentaCorreo.objects.filter(numero_documento=numero_documento).first();
            if cuenta_correo:
                datos = {
                    'nombres': cuenta_correo.nombres,
                    'apellidos': cuenta_correo.apellidos,
                    'email_institucional': cuenta_correo.email_institucional,
                    'mensaje': u'Ya existe la cuenta de correo para éste número de documento',
                    'crear': False
                }

                return JsonResponse(datos)

            data = consultar_por_cedula_regciv(numero_documento, force=False)
            if data and data.CodigoError == '000':
                primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(
                    data.Nombre)
                datos = {
                    'nombres': '%s %s' % (primer_nombre, segundo_nombre),
                    'apellidos': '%s %s' % (primer_apellido, segundo_apellido),
                    'crear': True
                }
                data_disponible = nombre_usuario_disponible(primer_apellido, segundo_apellido, primer_nombre,
                                                            segundo_nombre, numero_documento)
                if data_disponible.get('estado'):
                    datos.update({'email_institucional': '%s@%s' % (
                        data_disponible.get('nombre_usuario'), settings.GOOGLE_DOMAIN)})
                else:
                    datos.update({'email_institucional': False,
                                  'mensaje': data_disponible.get('mensaje')})
                return JsonResponse(datos)
            elif data.CodigoError == '009':
                datos = {
                    'nombres': '',
                    'apellidos': '',
                    'email_institucional': False,
                    'mensaje': 'El numero de documento no se encontró, ingrese manualmente la información'}
                return JsonResponse(datos)

    return HttpResponseBadRequest(mensaje)


@login_required
@permission_required('seguridad.view_cuentacorreo', raise_exception=True, )
def cuenta_correo_detalle(request, id):
    """
    Presenta el detalle de una cuenta de correo
    :param request:
    :return:
    """
    cuenta_correo = get_object_or_404(CuentaCorreo, id=id)
    user_google = get_usuario_google(cuenta_correo.email_institucional.split('@')[0])
    user_siaaf = Usuario.objects.filter(persona__numero_documento=cuenta_correo.numero_documento).first()
    ldap = 'Si' if existe_usuario_by_uid(cuenta_correo.email_institucional) else 'No'

    cuenta_correo.conected = 'No'

    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Cuentas de correo', reverse('seguridad_informacion:cuenta_correo_lista')),
                   ('Detalle', None)])

    if user_google:
        cuenta_correo.g_conectado = u'Ok'
        cuenta_correo.email_name = user_google.get('name', {}).get('fullName', None)
        cuenta_correo.g_suspendida = user_google.get('suspended', None)
        cuenta_correo.g_cambiar_clave = user_google.get('changePasswordAtNextLogin', None)
        cuenta_correo.g_ultimo_acceso = user_google.get('lastLoginTime', None)

    TIPO_CHOICES = CuentaCorreo.TIPO_CHOICES
    return render(request, 'seguridad_informacion/cuenta_correo/detalle.html', locals())


@login_required
@permission_required(('seguridad.change_cuentacorreo', 'seguridad.add_cuentacorreo'), raise_exception=True, )
def cuenta_correo_guardar(request):
    """
    Guarda una cuenta de correo
    :param request:
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            cuenta_correo = CuentaCorreo.objects.get('id')
        else:
            cuenta_correo = CuentaCorreo()
        form = CuentaCorreoForm(request.POST, instance=cuenta_correo)
        if form.is_valid():
            cuenta_correo = form.save(commit=False)
            if cuenta_correo.crear_cuenta_google():
                if not hasattr(cuenta_correo, 'id'):
                    cuenta_correo.email_name = '%s %s' % (cuenta_correo.nombres, cuenta_correo.apellidos)
                cuenta_correo.save()
                messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
            else:
                messages.warning(request, 'No se pudo crear la cuenta Google')
        else:
            messages.warning(request, form.errors)
    else:
        messages.warning(request, 'Petición inválido')

    return redirect('seguridad_informacion:cuenta_correo_lista')


@login_required
@permission_required('seguridad.view_cuentacorreo', raise_exception=True, )
def cuenta_correo_lista(request):
    """
    Presenta el listado de las cuentas de correo existentes en el SIAAF
    :param request:
    :return:
    """
    #numero_items = request.GET.get('numero_items', '25')
    #filtro = request.GET.get('filtro', '')
    #page = request.GET.get('pagina')
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Cuentas de Correo', None)])

    #if filtro:
    #    lista_cuentas = CuentaCorreo.buscar(filtro)
    #else:
    #    lista_cuentas = CuentaCorreo.objects.all()

    TIPO_CHOICES = CuentaCorreo.TIPO_CHOICES
    #paginator = Paginator(lista_cuentas, numero_items)

    #try:
    #    cuentas = paginator.page(page)
    #except PageNotAnInteger:
    #    cuentas = paginator.page(1)
    #except EmptyPage:
    #    cuentas = paginator.page(paginator.num_pages)

    return render(request, 'seguridad_informacion/cuenta_correo/lista.html', locals())

@login_required
@permission_required('seguridad.view_cuentacorreo', raise_exception=True, )
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def cuenta_correo_lista_paginador(request):
    """
    Retorna la lista de correos por cada página solicitada por el datatable desde la vista
    :param request:
    :return:
    """

    params = DataTableParams(request, **request.POST)

    try:
        CuentaCorreo.query_cuenta_correo_by_datatable_params(params)
        # dmunoz: tambien se puede usar un serializer se no se quiere mapear a un diccionario
        # serializer = CuentaCorreoSerializer(params.items, many=True)
        # data = serializer.data
        data = [{
             'id': it.id,
             'numero_documento': it.numero_documento,
             'nombres': it.nombres,
             'apellidos': it.apellidos,
             'email_institucional': it.email_institucional,
             'tipo': it.tipo} for it in params.items]

        result = params.result(data)
        return Response(result, status=status.HTTP_200_OK, template_name=None, content_type=None)

    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)


@login_required
@permission_required('seguridad.add_cuentacorreo', raise_exception=True, )
def cuenta_correo_vincular(request, id):
    """
    Vincula la cuenta de correo al google y al servidor LDAP de acuerdo al identificador dado
    :param request:
    :param id:
    :return:
    """
    cuenta = get_object_or_404(CuentaCorreo, id=id)
    usuario = Usuario.objects.filter(persona__numero_documento=cuenta.numero_documento).first()
    msg = ''

    if usuario:
        # vincular google
        if usuario.correo_electronico_institucional != cuenta.email_institucional or usuario.google == False:
            usuario.correo_electronico_institucional = cuenta.email_institucional
            usuario.nombre_de_usuario = cuenta.email_institucional.split('@')[0]
            if usuario.vincular_google():
                msg += "Cuenta vinculada a google! "
            else:
                msg += "No se pudo vincular a google. "

        # vincular ldap
        if usuario.vincular_ldap():
            msg += "Cuenta vinculada a ldap! "
        else:
            msg += "No se pudo vincular a ldap --> Estado: %s. " % ('Si' if usuario.activo else 'No')
    else:
        if not existe_usuario_by_uid(cuenta.email_institucional):
            if crear_usuario_ldap_of_cuenta_correo(cuenta):
                msg += "Cuenta vinculada a ldap! "
            else:
                msg += "No se pudo vincular a ldap. "

    messages.success(request, msg)

    return HttpResponseRedirect(reverse('seguridad_informacion:cuenta_correo_detalle', args=(cuenta.id,)))


@login_required
def cuenta_correo_vincular_google(request):
    """
    Vincula la cuenta de correo a google
    :param request:
    :return:
    """
    if request.method == 'POST':
        email_institucional = request.POST.get('email_institucional_asociar')
        numero_documento = request.POST.get('numero_documento_asociar')
        tipo = request.POST.get('tipo_asociar')

        cuenta_correo = CuentaCorreo.objects.filter(email_institucional=email_institucional)
        cuenta_correo_ndoc = CuentaCorreo.objects.filter(numero_documento=numero_documento)

        if cuenta_correo or cuenta_correo_ndoc:
            messages.success(request, 'Ya existe una cuenta de correo')
        else:
            user_google = get_usuario_google(email_institucional.split('@')[0])
            if user_google:
                cuenta_correo = CuentaCorreo()
                cuenta_correo.email_institucional = email_institucional
                cuenta_correo.numero_documento = numero_documento
                cuenta_correo.tipo = tipo
                cuenta_correo.email_name = user_google.get('name', {}).get('fullName', None)
                cuenta_correo.apellidos = user_google.get('name', {}).get('familyName', None)
                cuenta_correo.nombres = user_google.get('name', {}).get('givenName', None)

                for ext_id in user_google.get('externalIds', []):
                    ndoc_other = ext_id.get('value', None)
                    if ndoc_other != cuenta_correo.numero_documento:
                        messages.warning(request, 'La cuenta esta asociada en google a otro documento: %s', ndoc_other)
                        cuenta_correo.email_institucional = None

                for phone in user_google.get('phones', []):
                    if phone.get('type') == 'home':
                        cuenta_correo.telefono = phone.get('value', None)
                    if phone.get('type') == 'mobile':
                        cuenta_correo.celular = phone.get('value', None)

                for email in user_google.get('emails', []):
                    if email.get('type') == 'home':
                        cuenta_correo.email_alternativo = email.get('address', None)

                if cuenta_correo.email_institucional and cuenta_correo.numero_documento == numero_documento:
                    if cuenta_correo.asociar_cuenta_google():
                        cuenta_correo.save()
                        messages.success(request, 'Datos actualizados con exito')
                        return HttpResponseRedirect(
                            reverse('seguridad_informacion:cuenta_correo_detalle', args=(cuenta_correo.id,)))
                    else:
                        messages.warning(request, 'No se pudo asociar en Google')
                else:
                    messages.warning(request, 'Ya existe una cuenta asociada al numero de document %s',
                                     cuenta_correo.numero_documento)
            else:
                messages.warning(request, 'No existe la cuenta en Google')
    else:
        messages.warning(request, 'Petición inválido')
    return redirect('seguridad_informacion:cuenta_correo_lista')


@login_required
@permission_required('seguridad.add_grupoldap', raise_exception=True, )
def grupo_ldap_crear(request):
    """
    Funcionalidad que agrega un grupo Ldap y lo sincroniza con Ldap
    :param request:
    :return:
    """
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Grupos Ldap', reverse('seguridad_informacion:grupo_ldap_lista')),
                   ('Nuevo Grupo Ldap', None)])

    if request.method == 'POST':
        grupo_ldap_form = GrupoLdapForm(request.POST)
        if grupo_ldap_form.is_valid():
            grupo = grupo_ldap_form.save()
            grupo.vincular_ldap()
            return HttpResponseRedirect(reverse('seguridad_informacion:grupo_ldap_detalle', args=(grupo.id,)))
    else:
        grupo_ldap_form = GrupoLdapForm()

    return render(request, 'seguridad_informacion/grupo_ldap/editar.html', locals())


@login_required
@permission_required('seguridad.view_grupoldap', raise_exception=True, )
def grupo_ldap_detalle(request, id):
    """
    Funcionalidad que visualiza un grupo ldap
    :param request:
    :param id: Identificador del grupo Ldap
    :return:
    """
    grupo_ldap = get_object_or_404(GrupoLDAP, id=id)
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Grupos Ldap', reverse('seguridad_informacion:grupo_ldap_lista')),
                   (grupo_ldap.nombre.upper(), None)])
    return render(request, 'seguridad_informacion/grupo_ldap/detalle.html', locals())


@login_required
@permission_required('seguridad.view_grupoldap', raise_exception=True, )
def grupo_ldap_lista(request):
    """
    Muestra el listado de todos los grupos LDAP
    :param request:
    :return:
    """
    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Grupos Ldap', None)])

    if filtro:
        lista_grupos = GrupoLDAP.objects.filter(nombre__icontains=filtro)
    else:
        lista_grupos = GrupoLDAP.objects.all()

    paginator = Paginator(lista_grupos, numero_items)
    try:
        grupos = paginator.page(page)
    except PageNotAnInteger:
        grupos = paginator.page(1)
    except EmptyPage:
        grupos = paginator.page(paginator.num_pages)

    return render(request, 'seguridad_informacion/grupo_ldap/lista.html', locals())


@login_required
@permission_required('seguridad.change_grupoldap', raise_exception=True, )
def grupo_ldap_usuario_agregar(request, id, usuario_id):
    """
    Agrega un determinado usuario a un grupo dado los respectivos identificadores
    :param request:
    :param id: Identificador de GrupoLDAP
    :param usuario_id: Identificador de Usuario
    :return:
    """
    grupo_ldap = get_object_or_404(GrupoLDAP, id=id)
    usuario = get_object_or_404(Usuario, id=usuario_id)
    grupo_ldap.usuarios.add(usuario)
    grupo_ldap.save()
    grupo_ldap.agregar_usuario_grupo_ldap(usuario)
    return HttpResponseRedirect(reverse('seguridad_informacion:grupo_ldap_detalle', args=(grupo_ldap.id,)))


@login_required
@permission_required('seguridad.change_grupoldap', raise_exception=True, )
def grupo_ldap_usuario_eliminar(request, id, usuario_id):
    """
    Agrega un determinado usuario a un grupo dado los respectivos identificadores
    :param request:
    :param id: Identificador de GrupoLDAP
    :param usuario_id: Identificador de Usuario
    :return:
    """
    grupo_ldap = get_object_or_404(GrupoLDAP, id=id)
    usuario = get_object_or_404(Usuario, id=usuario_id)
    grupo_ldap.usuarios.remove(usuario)
    grupo_ldap.save()
    grupo_ldap.eliminar_usuario_grupo_ldap(usuario)
    return HttpResponseRedirect(reverse('seguridad_informacion:grupo_ldap_detalle', args=(grupo_ldap.id,)))


@login_required
@permission_required('seguridad.change_grupoldap', raise_exception=True, )
def grupo_ldap_usuario_lista(request, id):
    """
    Busqueda de usuarios para agregarlos a grupo de acuerdo al identificador del grupo
    :param request:
    :param id: Identificador de grupo
    :return:
    """
    grupo_ldap = get_object_or_404(GrupoLDAP, id=id)
    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', 25)
    page = request.GET.get('pagina', 1)
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Grupos Ldap', reverse('seguridad_informacion:grupo_ldap_lista')),
                   (grupo_ldap.nombre.upper(),
                    reverse('seguridad_informacion:grupo_ldap_detalle', args=[grupo_ldap.id])),
                   ('Buscar usuarios', None)])

    if filtro:
        lista_de_usuarios = Usuario.buscar(filtro)
    else:
        lista_de_usuarios = Usuario.objects.all()

    paginator = Paginator(lista_de_usuarios, numero_items)

    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)

    return render(request, 'seguridad_informacion/grupo_ldap/usuario_lista.html', locals())


@login_required
@permission_required('seguridad.change_grupoldap', raise_exception=True, )
def grupo_ldap_vincular(request, id):
    """
    Vincula un grupo ldap al servidor LDAP de acuerdo al identificador
    :param request:
    :param id: Identificador de grupo
    :return:
    """
    grupo_ldap = get_object_or_404(GrupoLDAP, id=id)
    grupo_ldap.vincular_ldap()
    return HttpResponseRedirect(reverse('seguridad_informacion:grupo_ldap_detalle', args=(grupo_ldap.id,)))


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_actualizar_fotografia_all(request):
    """
    Actualiza la foto de todos los usuario del SIAAF respecto a la del gmail
    :param request:
    :return:
    """
    lista_de_usuarios = Usuario.objects.all()
    for usua in lista_de_usuarios:
        usua.vincular_google()

    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_lista'))


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_cambiar_estado(request, id):
    """
    Cambia el estado de un usuario. Si está activo le pone inactivo y si inactivo cambia a activo
    :param request:
    :param id: El identificador de Usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)

    if usuario.activo:
        usuario.activo = False
        messages.success(request, 'El usuario ha sido inactivado correctamente!')
    else:
        usuario.activo = True
        messages.success(request, 'El usuario ha sido activado correctamente!')

    usuario.save()
    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_detalle', args=(usuario.id,)))


@login_required
@permission_required('seguridad.view_usuario', raise_exception=True, )
def usuario_detalle(request, id):
    """
    Presenta la información de un determinado usuario, basado en id identificador
    :param request:
    :param id: Identificador de Usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)
    LDAP_ACTIVE = settings.LDAP_ACTIVE
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Usuarios', reverse('seguridad_informacion:usuario_lista')),
                   (usuario.persona.get_nombres_completos().upper(), None)])

    return render(request, 'seguridad_informacion/usuario/detalle.html', locals())


@login_required
@permission_required('seguridad.view_usuario', raise_exception=True, )
def usuario_lista(request):
    """
    Presenta el listado de los usuario existentes en el SIAAF
    :param request:
    :return:
    """
    filtro = request.GET.get('filtro', '')
    page = request.GET.get('pagina')
    numero_items = request.GET.get('numero_items', '25')
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Usuarios', None)])

    if filtro:
        lista_de_usuarios = Usuario.buscar(filtro)
    else:
        lista_de_usuarios = Usuario.objects.all()

    paginator = Paginator(lista_de_usuarios, numero_items)
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)

    return render(request, 'seguridad_informacion/usuario/lista.html', locals())


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_resetear_password(request, id):
    """
    Reinicia la contraseña del usuario
    :param request:
    :param id: Identificador de usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)
    usuario.resetear_contrasena()
    messages.success(request, 'Contraseña reseteada al número de identificación')

    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_detalle', args=(usuario.id,)))


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_validar(request, id):
    """
    Actualiza el usuario y la foto
    :param request:
    :param id: Identificador del usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)
    navegacion = ('Módulo de la Seguridad de la Información',
                  [('Seguridad de la Información', reverse('seguridad_informacion:index')),
                   ('Usuarios', reverse('seguridad_informacion:usuario_lista')),
                   (usuario.persona.get_nombres_completos().upper(),
                    reverse('seguridad_informacion:usuario_detalle', args=(usuario.id,))),
                   ('Validar', None)])

    if request.method == 'POST':
        usuario_validar_form = UsuarioValidarForm(request.POST, instance=usuario)
        if usuario_validar_form.is_valid():
            usuario = usuario_validar_form.save(commit=False)
            if usuario.validar_correo_institucional(correo=usuario.correo_electronico_institucional):
                usuario.nombre_de_usuario = usuario.get_nombre_de_usuario()
                usuario.vincular_google()
                usuario.save()
                messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
            else:
                messages.warning(request, 'El correo electrónico no es valido')
    else:
        usuario_validar_form = UsuarioValidarForm(instance=usuario)

    return render(request, 'seguridad_informacion/usuario/validar.html', locals())


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_vincular_google(request, id):
    """
    Vincula el usuario con google
    :param request:
    :param id: Identificador de usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)
    if usuario.vincular_google():
        messages.success(request, 'Vinculado con google')
    else:
        messages.warning(request, 'No pudo vincularse')

    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_detalle', args=(usuario.id,)))


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_vincular_ldap(request, id):
    """
    Vincula un usuaurio al servidor LDAP de acuerdo al identificador dado
    :param request:
    :param id: El identificador de Usuario
    :return:
    """
    usuario = get_object_or_404(Usuario, id=id)
    if usuario.vincular_ldap():
        messages.success(request, 'Usuario vinculado a LDAP exitosamente')
    else:
        messages.warning(request, 'No pudo vincularse a LDAP')

    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_detalle', args=(usuario.id,)))


@login_required
@permission_required('seguridad.change_usuario', raise_exception=True, )
def usuario_vincular_ldap_all(request):
    """
    Vincula todos los usuario del SIAAF a Ldap
    :param request:
    :return:
    """
    lista_de_usuarios = Usuario.objects.all()
    for usua in lista_de_usuarios:
        if not usua.ldap:
            usua.vincular_ldap()

    return HttpResponseRedirect(reverse('seguridad_informacion:usuario_lista'))
