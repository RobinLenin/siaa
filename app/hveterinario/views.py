import datetime
import json
from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import *


# Create your views here.


# @login_required
def mi_index(request, nombre=''):
    if nombre:
        pacientes = Paciente.objects.filter(nombre__contains=nombre).all()
    else:
        pacientes = Paciente.objects.all()
    nombre = "Es es el texto"
    return render(request, 'hveterinario/index.html', locals())


def registros_paginados_propietarios(request):
    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina', 1)

    if filtro:
        lista_propietarios = Persona.buscar(filtro)
    else:
        lista_propietarios = Persona.objects.all()

    paginacion = Paginator(lista_propietarios, numero_items)
    try:
        propietarios = paginacion.page(page)
    except PageNotAnInteger:
        propietarios = paginacion.page(1)
    except EmptyPage:
        propietarios = paginacion.page(paginacion.num_pages)

    return render(request, 'hveterinario/index.html', {
        'propietarios': propietarios,
        'filtro': filtro
    })


def registros_paginados_pacientes(request, id_propietario=None):
    id_propietario_seleccionado = id_propietario;
    propietario_seleccionado = Persona.objects.get(id=id_propietario_seleccionado)
    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina', 1)
    # print(request.GET.dict())
    if filtro:
        # lista_pacientes = Paciente.objects.filter(persona__numero_de_documento__contains=filtro).all()
        # lista_pacientes = Paciente.buscar(filtro)
        lista_pacientes = Paciente.objects.filter(persona=id_propietario_seleccionado, nombre__icontains=filtro).all()
    else:
        lista_pacientes = Paciente.objects.filter(persona=id_propietario_seleccionado).all()

    paginacion = Paginator(lista_pacientes, numero_items)
    try:
        pacientes = paginacion.page(page)
    except PageNotAnInteger:
        pacientes = paginacion.page(1)
    except EmptyPage:
        pacientes = paginacion.page(paginacion.num_pages)

    return render(request, 'hveterinario/paciente/paciente_lista.html', locals())


def paciente(request, id_persona=None, id_paciente=None):
    # Para obtener el registro del propietario de las mascotas
    id_propietario_seleccionado = id_persona
    propietario_seleccionado = Persona.objects.get(id=id_propietario_seleccionado)

    # Para editar la información de la mascota/paciente
    id_paciente_seleccionado = id_paciente

    if request.method == "GET":
        if id_paciente:
            paciente = Paciente.objects.get(id=id_paciente)

    if request.method == "POST":
        if id_paciente:
            paciente = Paciente.objects.get(id=id_paciente)
            messages.success(request, "Información de la mascota editada correctamente... ")

        else:
            paciente = Paciente()
            messages.success(request, "Mascota registrada correctamente... ")

        paciente.numero_historia_clinica = request.POST.get('numero_historia_clinica')
        paciente.fecha_registro_historia_clinica = request.POST.get('fecha_registro_hc')
        paciente.nombre = request.POST.get('nombre_paciente')
        paciente.sexo = request.POST.get('sexo')
        paciente.especie = request.POST.get('especie')
        paciente.raza = request.POST.get('raza')
        paciente.edad = request.POST.get('edad')
        paciente.peso = request.POST.get('peso')
        paciente.tamanio = request.POST.get('tamanio')
        paciente.color = request.POST.get('color')
        paciente.procedencia = request.POST.get('procedencia', '')
        paciente.persona = propietario_seleccionado

        paciente.save()

        return HttpResponseRedirect(
            reverse('hveterinario:paciente.lista_pacientes_por_propietario', args=(id_propietario_seleccionado,)))

    return render(request, 'hveterinario/paciente/paciente_cru.html', locals())


def registros_paginados_consulta_por_paciente(request, id_paciente=None):
    id_paciente_seleccionado = id_paciente

    paciente_seleccionado = Paciente.objects.get(id=id_paciente_seleccionado)
    propietario = paciente_seleccionado.persona
    id_propietario_seleccionado = propietario.id

    filtro = request.GET.get('filtro', '')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina', 1)
    # print(request.GET.dict())
    if filtro:
        # lista_pacientes = Paciente.objects.filter(persona__numero_de_documento__contains=filtro).all()
        # lista_pacientes = Paciente.buscar(filtro)
        lista_consultas = Consulta.objects.filter(paciente=id_paciente_seleccionado, created_at__icontains=filtro).all()
    else:
        lista_consultas = Consulta.objects.filter(paciente=id_paciente_seleccionado).all()

    paginacion = Paginator(lista_consultas, numero_items)
    try:
        consultas = paginacion.page(page)
    except PageNotAnInteger:
        consultas = paginacion.page(1)
    except EmptyPage:
        consultas = paginacion.page(paginacion.num_pages)

    return render(request, 'hveterinario/consulta/consulta_lista.html', locals())


def consulta(request, id_paciente=None, id_consulta=None):
    # Para obtener el registro del paciente con sus respectivas consultas
    id_paciente_seleccionado = id_paciente
    paciente_seleccionado = Paciente.objects.get(id=id_paciente_seleccionado)
    propietario = paciente_seleccionado.persona
    id_propietario_seleccionado = propietario.id

    # Para editar la información de la consulta
    id_consulta_seleccionadoa = id_consulta

    if request.method == "GET":
        if id_consulta:
            consulta = Consulta.objects.get(id=id_consulta)

    if request.method == "POST":
        if id_consulta:
            consulta = Consulta.objects.get(id=id_consulta)
            messages.success(request, "Información de la consulta editada correctamente... ")

        else:
            consulta = Consulta()
            messages.success(request, "Consulta registrada correctamente... ")

        consulta.motivo_consulta = request.POST.get('motivo_consulta')
        consulta.medico_responsable = request.POST.get('medico_responsable')
        consulta.estudiante_interno = request.POST.get('estudiante_interno')
        consulta.paciente = paciente_seleccionado

        consulta.save()

        return HttpResponseRedirect(
            reverse('hveterinario:consulta.lista_consulta_por_pacientes', args=(id_paciente_seleccionado,)))

    return render(request, 'hveterinario/consulta/consulta_cru.html', locals())


def consulta_detalle(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)
    anamnesis = None
    examen_clinico = None
    lista_maestra = None

    datos_presuntivos = []
    datos_tegumentario_lista = []
    datos_musculo_esqueletico_lista = []
    datos_respiratorio_lista = []
    datos_cardiovascular_lista = []
    datos_digestivo_lista = []
    datos_nervioso_lista = []
    datos_genitourinario_lista = []
    datos_auditivo_y_ocular_lista = []

    numero_total_datos_presuntivo = 0
    datos_subjetivos_lista_db = []
    datos_subjetivos_combinados_rango = []

    diagnostico_diferencial = None
    datos_objetivos_lista_db = []
    datos_objetivos_combinados_rango = []

    diagnostico_presuntivo = None
    datos_dg_presuntivo_lista_db = []
    datos_dg_presuntivo_combinados_rango = []

    diagnostico_final_tratamiento = None
    tratamiento = None

    inscripciones_tratamiento = []

    if hasattr(consulta_seleccionada, 'consulta_anamnesis'):
        anamnesis = consulta_seleccionada.consulta_anamnesis

    if hasattr(consulta_seleccionada, 'consulta_examen_clinico'):
        examen_clinico = consulta_seleccionada.consulta_examen_clinico
        datos_presuntivos = examen_clinico.examen_clinico_datos_presuntivos.all()

        datos_tegumentario = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.TEGUMENTARIO).first()
        datos_musculo_esqueletico = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.MUSCULO_ESQUELETICO).first()
        datos_respiratorio = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.RESPIRATORIO).first()
        datos_cardiovascular = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.CARDIOVASCULAR).first()
        datos_digestivo = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.DIGESTIVO).first()
        datos_nervioso = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.NERVIOSO).first()
        datos_genitourinario = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.GENITOURINARIO).first()
        datos_auditivo_y_ocular = examen_clinico.examen_clinico_datos_presuntivos.filter(
            tipo_sistema=DatosPresuntivos.AUDITIVO_Y_OCULAR).first()

        if datos_tegumentario:
            datos_tegumentario_lista = str(datos_tegumentario).split('\r\n')

        if datos_musculo_esqueletico:
            datos_musculo_esqueletico_lista = str(datos_musculo_esqueletico).split('\r\n')

        if datos_respiratorio:
            datos_respiratorio_lista = str(datos_respiratorio).split('\r\n')

        if datos_cardiovascular:
            datos_cardiovascular_lista = str(datos_cardiovascular).split('\r\n')

        if datos_digestivo:
            datos_digestivo_lista = str(datos_digestivo).split('\r\n')

        if datos_nervioso:
            datos_nervioso_lista = str(datos_nervioso).split('\r\n')

        if datos_genitourinario:
            datos_genitourinario_lista = str(datos_genitourinario).split('\r\n')

        if datos_auditivo_y_ocular:
            datos_auditivo_y_ocular_lista = str(datos_auditivo_y_ocular).split('\r\n')

        numero_datos_primeros = len(datos_tegumentario_lista) + len(datos_musculo_esqueletico_lista) + len(
            datos_respiratorio_lista)
        numero_datos_segundos = len(datos_cardiovascular_lista) + len(datos_digestivo_lista) + len(datos_nervioso_lista)
        numero_datos_terceros = len(datos_genitourinario_lista) + len(datos_auditivo_y_ocular_lista)

        numero_total_datos_presuntivo = (numero_datos_primeros + numero_datos_segundos + numero_datos_terceros)

        for i in range(0, numero_total_datos_presuntivo):
            datos_subjetivos_combinados_rango.append("")

        print('numero total de datos', numero_total_datos_presuntivo)

    if hasattr(consulta_seleccionada, 'consulta_lista_maestra'):
        lista_maestra = consulta_seleccionada.consulta_lista_maestra
        datos_subjetivos_combinados_rango = []

        datos_subjetivos_lista_db = str(lista_maestra.dato_subjetivo).split(' & ')
        numero_total_datos = numero_total_datos_presuntivo

        for i in range(0, numero_total_datos):
            datos_objetivos_combinados_rango.append("")
            if i < len(datos_subjetivos_lista_db):
                datos_subjetivos_combinados_rango.append(datos_subjetivos_lista_db[i])
            else:
                datos_subjetivos_combinados_rango.append("")

        if hasattr(lista_maestra, 'lista_maestra_d_diferencial'):
            diagnostico_diferencial = lista_maestra.lista_maestra_d_diferencial
            datos_objetivos_combinados_rango = []

            datos_objetivos_lista_db = str(diagnostico_diferencial.dato_objetivo).split(' & ')

            for i in range(0, numero_total_datos):
                datos_dg_presuntivo_combinados_rango.append("")
                if i < len(datos_objetivos_lista_db):
                    datos_objetivos_combinados_rango.append(datos_objetivos_lista_db[i])
                else:
                    datos_objetivos_combinados_rango.append("")

            if hasattr(diagnostico_diferencial, 'diagnostico_diferencial_d_presuntivo'):
                diagnostico_presuntivo = diagnostico_diferencial.diagnostico_diferencial_d_presuntivo
                datos_dg_presuntivo_combinados_rango = []

                datos_dg_presuntivo_lista_db = str(diagnostico_presuntivo.dato_dg_presuntivo).split(' & ')

                for i in range(0, numero_total_datos):
                    if i < len(datos_dg_presuntivo_lista_db):
                        datos_dg_presuntivo_combinados_rango.append(datos_dg_presuntivo_lista_db[i])
                    else:
                        datos_dg_presuntivo_combinados_rango.append("")

    if hasattr(consulta_seleccionada, 'consulta_examenes_complementarios'):
        examenes_complementarios = consulta_seleccionada.consulta_examenes_complementarios

    if hasattr(consulta_seleccionada, 'consulta_diagnostico_final'):
        diagnostico_final = consulta_seleccionada.consulta_diagnostico_final

        if hasattr(diagnostico_final, 'diagnostico_final_tratamiento'):
            tratamiento = diagnostico_final.diagnostico_final_tratamiento
            inscripciones_tratamiento = tratamiento.tratamiento_inscripcion.all()

    return render(request, 'hveterinario/consulta/detalles/index.html', locals())


def detalles_consulta_anamnesis(request, id_consulta=None):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)
    try:
        anamnesis = Anamnesis.objects.get(consulta__pk=id_consulta)
    except Anamnesis.DoesNotExist:
        anamnesis = None

    if request.method == "POST":
        if anamnesis:
            messages.success(request, "Anamnesis actualizada correctamente... ")
        else:
            anamnesis = Anamnesis()
            anamnesis.consulta_id = id_consulta
            messages.success(request, "Anamnesis registrada correctamente... ")

        if consulta_seleccionada.paciente.sexo == "H":
            anamnesis.ultimo_celo = datetime.datetime.strptime(request.POST.get('ultimo_celo'), '%Y-%m-%d')
            anamnesis.secreciones_vulvares = json.loads(request.POST.get('secreciones_vulvares'))
            anamnesis.fecha_ultimo_parto = datetime.datetime.strptime(request.POST.get('fecha_ultimo_parto'),
                                                                      '%Y-%m-%d')
            anamnesis.complicaciones_parto = request.POST.get('complicaciones_parto')
        else:
            anamnesis.numero_montas = request.POST.get('numero_montas')
            anamnesis.secreciones_prepuciales = json.loads(request.POST.get('secreciones_prepuciales'))

        anamnesis.ultima_desparasitacion = datetime.datetime.strptime(request.POST.get('ultima_desparasitacion'),
                                                                      '%Y-%m-%d')
        anamnesis.vacunas = json.loads(request.POST.get('vacunas'))
        anamnesis.enfermedades_anteriores = request.POST.get('enfermedades_anteriores')
        anamnesis.tratamiento_anterior = request.POST.get('tratamiento_anterior')
        anamnesis.alimentacion = request.POST.get('alimentacion')
        anamnesis.conducta = request.POST.get('conducta')

        anamnesis.save()

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_examen_clinico(request, id_consulta=None):
    # Para obtener los datos de la consulta correspondiente
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    try:
        examen_clinico = ExamenClinico.objects.get(consulta__pk=id_consulta)
    except ExamenClinico.DoesNotExist:
        examen_clinico = None

    if request.method == "POST":
        # print(request.POST.dict())

        if examen_clinico:
            messages.success(request, "Examen clínico actualizado correctamente... ")
        else:
            examen_clinico = ExamenClinico()
            messages.success(request, "Examen clínico registrado correctamente... ")

        examen_clinico.frecuencia_cardiaca = request.POST.get('frecuencia_cardiaca')
        examen_clinico.frecuencia_respiratoria = request.POST.get('frecuencia_respiratoria')
        examen_clinico.temperatura = request.POST.get('temperatura')
        examen_clinico.linfonodulos = request.POST.get('linfonodulos')
        examen_clinico.tllc = request.POST.get('tllc')
        examen_clinico.pulso = request.POST.get('pulso')
        examen_clinico.mucosa = request.POST.get('mucosa')
        examen_clinico.tipo_mucosa = request.POST.get('tipo_mucosa')
        examen_clinico.consulta = consulta_seleccionada

        examen_clinico.save()
    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def agregarDatosPresuntivos(request, id_consulta=None):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    # el mismo metodo post
    datos_presuntivos_descripcion = request.POST.get('dato_presuntivo')
    tipo_sistema_cod = request.POST.get('tipo_sistema_cod')
    examen_clinico = consulta_seleccionada.consulta_examen_clinico

    dato_presuntivo_por_sis = DatosPresuntivos.objects.filter(tipo_sistema=tipo_sistema_cod,
                                                              examen_clinico__pk=examen_clinico.id).first()

    if not dato_presuntivo_por_sis:
        dato_presuntivo_por_sis = DatosPresuntivos()
        dato_presuntivo_por_sis.examen_clinico = examen_clinico
        messages.success(request, "Datos presuntivos registrados correctamente... ")
    else:
        messages.success(request, "Datos presuntivos actualizados correctamente... ")

    dato_presuntivo_por_sis.tipo_sistema = tipo_sistema_cod
    dato_presuntivo_por_sis.dato_presuntivo = datos_presuntivos_descripcion
    dato_presuntivo_por_sis.save()

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_lista_maestra(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    numero_total_datos_presuntivo = request.POST.get('numero_total_datos_presuntivo')
    numero_datos_presuntivo = int('0' + numero_total_datos_presuntivo)
    numero_datos_presuntivo = numero_datos_presuntivo + 1
    datos_subjetivos_lista = ''

    for x in range(1, numero_datos_presuntivo):
        dato_subjetivo = request.POST.get('dato_subjetivo' + str(x))
        if dato_subjetivo:
            datos_subjetivos_lista += dato_subjetivo + " & "

    lista_maestra = None
    if hasattr(consulta_seleccionada, 'consulta_lista_maestra'):
        lista_maestra = consulta_seleccionada.consulta_lista_maestra

    if datos_subjetivos_lista:
        if not lista_maestra:
            lista_maestra = ListaMaestra()
            lista_maestra.consulta = consulta_seleccionada
            messages.success(request, "Lista maestra registrada correctamente... ")
        else:
            messages.success(request, "Lista maestra actualizada correctamente... ")

        lista_maestra.dato_subjetivo = datos_subjetivos_lista
        lista_maestra.save()
    else:
        messages.warning(request, "No se creo o actualizó la lista maestra. Campos vacios")

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_diagnostico_diferencial(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    numero_total_datos_presuntivo = request.POST.get('numero_total_datos_presuntivo')
    numero_datos_presuntivo = int('0' + numero_total_datos_presuntivo)
    numero_datos_presuntivo = numero_datos_presuntivo + 1
    datos_objetivos_lista = ''

    for x in range(1, numero_datos_presuntivo):
        dato_objetivo = request.POST.get('dato_objetivo' + str(x))
        if dato_objetivo:
            datos_objetivos_lista += dato_objetivo + " & "

    diagnostico_diferencial = None

    if hasattr(consulta_seleccionada.consulta_lista_maestra, 'lista_maestra_d_diferencial'):
        diagnostico_diferencial = consulta_seleccionada.consulta_lista_maestra.lista_maestra_d_diferencial

    if datos_objetivos_lista:
        if not diagnostico_diferencial:
            diagnostico_diferencial = DiagnosticoDiferencial()
            diagnostico_diferencial.lista_maestra = consulta_seleccionada.consulta_lista_maestra
            messages.success(request, "Diagnóstico Diferencial registrado correctamente... ")
        else:
            messages.success(request, "Diagnóstico Diferencial actualizado correctamente... ")

        diagnostico_diferencial.dato_objetivo = datos_objetivos_lista
        diagnostico_diferencial.save()
    else:
        messages.warning(request, "No se creo o actualizó el diagnóstico diferencial. Campos vacios")

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_diagnostico_presuntivo(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    numero_total_datos_presuntivo = request.POST.get('numero_total_datos_presuntivo')
    numero_datos_presuntivo = int('0' + numero_total_datos_presuntivo)
    numero_datos_presuntivo = numero_datos_presuntivo + 1
    datos_dg_presuntivo_lista = ''

    for x in range(1, numero_datos_presuntivo):
        dato_dg_presuntivo = request.POST.get('dato_dg_presuntivo' + str(x))
        if dato_dg_presuntivo:
            datos_dg_presuntivo_lista += dato_dg_presuntivo + " & "

    diagnostico_presuntivo = None

    if hasattr(consulta_seleccionada.consulta_lista_maestra.lista_maestra_d_diferencial,
               'diagnostico_diferencial_d_presuntivo'):
        diagnostico_presuntivo = consulta_seleccionada.consulta_lista_maestra.lista_maestra_d_diferencial.diagnostico_diferencial_d_presuntivo

    if datos_dg_presuntivo_lista:
        if not diagnostico_presuntivo:
            diagnostico_presuntivo = DiagnosticoPresuntivo()
            diagnostico_presuntivo.diagnostico_diferencial = consulta_seleccionada.consulta_lista_maestra.lista_maestra_d_diferencial
            messages.success(request, "Diagnóstico Presuntivo registrado correctamente... ")
        else:
            messages.success(request, "Diagnóstico Presuntivo actualizado correctamente... ")

        diagnostico_presuntivo.dato_dg_presuntivo = datos_dg_presuntivo_lista
        diagnostico_presuntivo.save()
    else:
        messages.warning(request, "No se creo o actualizó el diagnóstico presuntivo. Campos vacios")

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


# if lista_datos_presuntivos:
#    regex = r"^([\w ]+)(\r\n)?"
#   subst = r"\1."
#  lista_datos_presuntivos_por_punto = re.sub(regex, subst, lista_datos_presuntivos,0, re.MULTILINE)

def detalles_consulta_examenes_complementarios(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)

    examenes_complementarios = None
    if hasattr(consulta_seleccionada, 'consulta_examenes_complementarios'):
        examenes_complementarios = consulta_seleccionada.consulta_examenes_complementarios

    if request.method == "POST":
        if examenes_complementarios:
            messages.success(request, "Examenes Complementarios actualizados correctamente... ")
        else:
            examenes_complementarios = ExamenesComplementarios()
            examenes_complementarios.consulta_id = id_consulta
            messages.success(request, "Examenes Complementarios registrados correctamente... ")

        examenes_complementarios.cuadro_hematico = json.loads(request.POST.get('cuadro_hematico', 'false'))
        examenes_complementarios.electrolitos = json.loads(request.POST.get('electrolitos', 'false'))
        examenes_complementarios.antibiograma = json.loads(request.POST.get('antibiograma', 'false'))
        examenes_complementarios.quimica_sanguinea = json.loads(request.POST.get('quimica_sanguinea', 'false'))
        examenes_complementarios.emo = json.loads(request.POST.get('emo', 'false'))
        examenes_complementarios.citologia = json.loads(request.POST.get('citologia', 'false'))
        examenes_complementarios.coprologico = json.loads(request.POST.get('coprologico', 'false'))
        examenes_complementarios.gases_sanguineos = json.loads(request.POST.get('gases_sanguineos', 'false'))
        examenes_complementarios.cultivos = json.loads(request.POST.get('cultivos', 'false'))
        examenes_complementarios.radiologia = json.loads(request.POST.get('radiologia', 'false'))
        examenes_complementarios.electrocardiografia = json.loads(request.POST.get('electrocardiografia', 'false'))
        examenes_complementarios.ecografia = json.loads(request.POST.get('ecografia', 'false'))
        examenes_complementarios.otro_examen = request.POST.get('otro_examen', 'false')
        examenes_complementarios.resultados_significativos = request.POST.get('resultados_significativos', 'false')

        examenes_complementarios.save()

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_diagnostico_final(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)
    # diagnostico_final = consulta_seleccionada.consulta_diagnostico_final

    diagnostico_final = None
    if hasattr(consulta_seleccionada, 'consulta_diagnostico_final'):
        diagnostico_final = consulta_seleccionada.consulta_diagnostico_final

    if request.method == "POST":
        if diagnostico_final:
            messages.success(request, "Diagnóstico final actualizado correctamente... ")
        else:
            diagnostico_final = DiagnosticoFinal()
            diagnostico_final.consulta_id = id_consulta
            messages.success(request, "Diagnóstico final registrado correctamente... ")

        diagnostico_final.dato_dg_final = request.POST.get('dato_dg_final')
        diagnostico_final.save()

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_tratamiento(request, id_consulta):
    consulta_seleccionada = Consulta.objects.get(id=id_consulta)
    tratamiento = None
    if hasattr(consulta_seleccionada.consulta_diagnostico_final, 'diagnostico_final_tratamiento'):
        tratamiento = consulta_seleccionada.consulta_diagnostico_final.diagnostico_final_tratamiento

    if request.method == "POST":
        if tratamiento:
            messages.success(request, "Tratamiento actualizado correctamente... ")
        else:
            tratamiento = Tratamiento()
            tratamiento.diagnostico_final = consulta_seleccionada.consulta_diagnostico_final
            messages.success(request, "Tratamiento registrado correctamente... ")

        tratamiento.quirurgico = request.POST.get('quirurgico')
        tratamiento.farmacologico = request.POST.get('farmacologico')
        tratamiento.save()

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))


def detalles_consulta_inscripcion_tratamiento(request, id_consulta):
    inscripcion_id = request.POST.get('inscripcion_id', False)

    consulta_seleccionada = Consulta.objects.get(id=id_consulta)
    inscripcion_tratamiento = None
    if request.method == 'POST':
        tratamiento = consulta_seleccionada.consulta_diagnostico_final.diagnostico_final_tratamiento

        if inscripcion_id:
            inscripcion_tratamiento = InscripcionTratamiento.objects.get(id=inscripcion_id)

        if not inscripcion_tratamiento:
            inscripcion_tratamiento = InscripcionTratamiento()
            inscripcion_tratamiento.tratamiento = tratamiento
            messages.success(request, "Inscripción registrada correctamente... ")
        else:
            messages.success(request, "Inscripción actualizada correctamente... ")

        inscripcion_tratamiento.producto = request.POST.get('inscripcion_producto')
        inscripcion_tratamiento.presentacion = request.POST.get('inscripcion_presentacion')
        inscripcion_tratamiento.dosis_base = request.POST.get('inscripcion_dosis_base')
        inscripcion_tratamiento.via = request.POST.get('inscripcion_via')
        inscripcion_tratamiento.dosificacion = request.POST.get('inscripcion_dosificacion')
        inscripcion_tratamiento.frecuencia = request.POST.get('inscripcion_frecuencia')
        inscripcion_tratamiento.duracion = request.POST.get('inscripcion_duracion')

        inscripcion_tratamiento.save()

        if request.is_ajax():
            return JsonResponse({'inscripcion_id': inscripcion_tratamiento.id})

    return HttpResponseRedirect(reverse('hveterinario:consulta.detalle', args=(id_consulta,)))
