import datetime
import json
import logging
import uuid

logger = logging.getLogger(__name__)

from timeit import default_timer as timer

from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.safestring import SafeString
from reportbro import Report, ReportBroError

from .utils.pdf import plantilla_basica
from .utils.pdf import json_default

from .models import Plantilla
from .models import PlantillaModelo


@login_required
@permission_required('reporte.add_plantilla', raise_exception=True)
def plantilla_detalle(request, plantilla_id):
    """
    Con el id de la plantilla vamos a la interfaz de edicion reportBro
    :param request:
    :param plantilla_id:
    :return:
    """
    plantilla = Plantilla.objects.get(id=plantilla_id)
    definicion = SafeString(plantilla.definicion)
    return render(request, 'reporte/plantilla_detalle.html', {'plantilla': plantilla, 'definicion': definicion})


@login_required
@permission_required('reporte.change_plantilla', raise_exception=True)
def plantilla_exportar(request, plantilla_id):
    """
    JJM  se recibe la plantilla editada desde la interfaz reportBro
    :param request:
    :return:
    """
    plantilla = Plantilla.objects.get(id=plantilla_id)
    datos = [plantilla.descripcion, plantilla.codigo, plantilla.definicion]
    response_content = '\n'.join(datos)

    response = HttpResponse(response_content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s.siaaf"' % plantilla.codigo
    return response


@login_required
@permission_required('reporte.delete_plantilla', raise_exception=True)
def plantilla_eliminar(request, plantilla_id):
    """
    Se elimina la plantilla, por ajax
    :param request:
    :param plantilla_id:
    :return:
    """
    if request.is_ajax() and request.method == 'DELETE':
        if Plantilla.objects.get(id=plantilla_id).delete():
            return HttpResponse("Eliminacion realizada")
        return HttpResponseBadRequest("No se encontro el reporte")
    return HttpResponseBadRequest("Metodo no válido")


@login_required
@permission_required('reporte.change_plantilla', raise_exception=True)
def plantilla_guardar_datos(request):
    """
    JJM solo modifica el nombre y la descripcion, llamado por ajax
    :param request:
    :return:
    """
    if request.is_ajax():
        try:
            if request.POST.get('plantilla_id'):
                plantilla = Plantilla.objects.get(id=request.POST.get('plantilla_id'))
            else:
                plantilla = Plantilla()
                plantilla_origen = Plantilla.objects.filter(id=request.POST.get('origen_id')).first()
                plantilla.definicion = (plantilla_origen and plantilla_origen.definicion) or plantilla_basica()
            plantilla.descripcion = request.POST.get('descripcion')
            plantilla.codigo = request.POST.get('codigo')
            plantilla.save()
            return JsonResponse({'id': plantilla.id})
        except Exception as ex:
            logger.error("Error al guardar Plantilla:" + str(ex))
            return HttpResponseServerError('Error al guardar la Plantilla: ' + str(ex))
    return HttpResponseBadRequest('Error de peticion')


@login_required
@permission_required('reporte.change_plantilla', raise_exception=True)
def plantilla_guardar_definicion(request):
    """
    JJM  se recibe la plantilla editada desde la interfaz reportBro
    :param request:
    :return:
    """
    json_data = json.loads(request.body.decode('utf-8'))
    if not isinstance(json_data, dict) or not isinstance(json_data.get('docElements'), list) or \
            not isinstance(json_data.get('styles'), list) or not isinstance(json_data.get('parameters'), list) or \
            not isinstance(json_data.get('documentProperties'), dict) or not isinstance(json_data.get('version'), int):
        return HttpResponseBadRequest('invalid values')

    definicion = dict(
        docElements=json_data.get('docElements'), styles=json_data.get('styles'),
        parameters=json_data.get('parameters'),
        documentProperties=json_data.get('documentProperties'), version=json_data.get('version'))
    definicion = json.dumps(definicion)
    if Plantilla.objects.filter(id=json_data.get('id')).update(
            definicion=definicion) == 0:
        return HttpResponseBadRequest("No se pudo actualizar el reporte")
    return HttpResponse('ok')


@login_required
@permission_required('reporte.change_plantilla', raise_exception=True)
def plantilla_importar(request):
    """
    JJM  se recibe la plantilla editada desde la interfaz reportBro
    :param request:
    :return:
    """
    try:
        archivo = request.FILES.get('archivo')
        lineas = archivo.readlines()
        if len(lineas) == 3:
            plantilla = Plantilla()
            plantilla.descripcion = lineas[0].decode('utf-8').rstrip()
            plantilla.codigo = lineas[1].decode('utf-8').rstrip()
            plantilla.definicion = lineas[2].decode('utf-8').rstrip()
            plantilla.save()
            messages.success(request, "Plantilla cargada")
        else:
            raise ValueError("Formato de archivo no valido")
    except IntegrityError as ex:
        logger.error("Error al importar la plantilla:  Codigo duplicado")
        messages.warning(request, "Error al importar la plantilla: codigo de plantilla duplicado ")
    except Exception as ex:
        logger.error("Error al importar la plantilla:  " + str(ex))
        messages.warning(request, "Error al importar la plantilla:  " + str(ex))
    return redirect('reporte:plantilla_lista')


@login_required
@permission_required('reporte.add_plantilla', raise_exception=True)
def plantilla_lista(request):
    """
    Presenta todos los reportes creados en el sistema
    :param request:
    :return:
    """
    plantillas = Plantilla.objects.all()
    navegacion = ('Módulo de Gestión de Reportes', [('Administración de Reportes', None)])
    return render(request, 'reporte/plantilla_lista.html', {'plantillas': plantillas, 'navegacion': navegacion})


@login_required
def plantilla_vista_previa(request):
    """
    Vista previa del reporte
    :param request:
    :return:
    """
    max_cache_size = 10 * 1024 * 1024  # keep max. 10 MB of generated pdf files in db
    now = datetime.datetime.now()

    response = HttpResponse('')
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, PUT, OPTIONS'
    response[
        'Access-Control-Allow-Headers'] = \
        'Origin, X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept, Z-Key'
    if request.method == 'OPTIONS':
        # options request is usually sent by browser for a cross-site request, we only need to set the
        # Access-Control-Allow headers in the response so the browser sends the following get/put request
        return response

    additional_fonts = []
    # add additional fonts here if additional fonts are used in ReportBro Designer

    if request.method == 'PUT':
        json_data = json.loads(request.body.decode('utf-8'))
        if not isinstance(json_data, dict) or not isinstance(json_data.get('report'), dict) or \
                not isinstance(json_data.get('data'), dict) or not isinstance(json_data.get('isTestData'), bool):
            return HttpResponseBadRequest('invalid report values')

        output_format = json_data.get('outputFormat')
        if output_format not in ('pdf', 'xlsx'):
            return HttpResponseBadRequest('outputFormat parameter missing or invalid')

        report_definition = json_data.get('report')
        data = json_data.get('data')
        is_test_data = json_data.get('isTestData')
        try:
            report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
        except Exception as e:
            return HttpResponseBadRequest('failed to initialize report: ' + str(e))

        if report.errors:
            return HttpResponse(json.dumps(dict(errors=report.errors)))
        try:
            # delete old reports (older than 3 minutes) to avoid table getting too big
            PlantillaModelo.objects.filter(created_on__lt=(now - datetime.timedelta(minutes=3))).delete()

            total_size = PlantillaModelo.objects.aggregate(Sum('pdf_file_size'))
            if total_size['pdf_file_size__sum'] and total_size['pdf_file_size__sum'] > max_cache_size:
                # delete all reports older than 10 seconds to reduce db size for cached pdf files
                PlantillaModelo.objects.filter(created_on__lt=(now - datetime.timedelta(seconds=10))).delete()

            start = timer()
            report_file = report.generate_pdf()
            end = timer()
            print('pdf generated in %.3f seconds' % (end - start))

            key = str(uuid.uuid4())
            # add report request into sqlite db, this enables downloading the report by url (the report is identified
            # by the key) without any post parameters. This is needed for pdf and xlsx preview.
            PlantillaModelo.objects.create(
                key=key, definicion=json.dumps(report_definition, default=json_default),
                data=json.dumps(data, default=json_default), is_test_data=is_test_data,
                pdf_file=report_file, pdf_file_size=len(report_file), created_on=now)

            return HttpResponse('key:' + key)
        except ReportBroError as err:
            return HttpResponse(json.dumps(dict(errors=[err.error])))
        except Exception as e:
            print(e)

    elif request.method == 'GET':
        output_format = request.GET.get('outputFormat')
        if output_format not in ('pdf', 'xlsx'):
            return HttpResponseBadRequest('outputFormat parameter missing or invalid')
        key = request.GET.get('key')

        report = None
        report_file = None
        if key and len(key) == 36:
            # the report is identified by a key which was saved
            # in an table during report preview with a PUT request
            try:
                plantilla_modelo = PlantillaModelo.objects.get(key=key)
            except PlantillaModelo.DoesNotExist:
                return HttpResponseBadRequest(
                    'report not found (preview probably too old), update report preview and try again')
            if output_format == 'pdf' and plantilla_modelo.pdf_file:
                report_file = plantilla_modelo.pdf_file
            else:
                report_definition = json.loads(plantilla_modelo.definicion)
                data = json.loads(plantilla_modelo.data)
                is_test_data = plantilla_modelo.is_test_data
                report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
                if report.errors:
                    return HttpResponseBadRequest(reason='error generating report')
        else:
            # generate and download report with a GET request
            json_data = json.loads(request.body.decode('utf-8'))
            if not isinstance(json_data, dict) or not isinstance(json_data.get('report'), dict) or \
                    not isinstance(json_data.get('data'), dict) or not isinstance(json_data.get('isTestData'),
                                                                                  bool):
                return HttpResponseBadRequest('invalid report values')
            report_definition = json_data.get('report')
            data = json_data.get('data')
            is_test_data = json_data.get('isTestData')
            if not isinstance(report_definition, dict) or not isinstance(data, dict):
                return HttpResponseBadRequest('report_definition or data missing')
            report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
            if report.errors:
                return HttpResponseBadRequest(reason='error generating report')

        try:
            if output_format == 'pdf':
                if report_file is None:
                    report_file = report.generate_pdf()
                response = HttpResponse(
                    report_file, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="{filename}"'.format(
                    filename='report-' + str(now) + '.pdf')
            else:
                report_file = report.generate_xlsx()
                response = HttpResponse(
                    report_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'inline; filename="{filename}"'.format(
                    filename='report-' + str(now) + '.xlsx')
            return response
        except ReportBroError:
            return HttpResponseBadRequest('error generating report')
        except Exception as ex:
            print(ex)
    return None
