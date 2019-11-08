from django.apps import apps
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .general import validar_ced_ruc


@login_required
def validar_campo_unico(request):
    app = request.POST.get('app')
    model = request.POST.get('modelo')
    atributo = request.POST.get('atributo', '')
    valor = request.POST.get('valor', '')
    id = request.POST.get('id', 0)

    id = id if id else 0

    filtros = {atributo: valor}

    modelo_generico = apps.get_model(app, model)
    existe = modelo_generico.objects.filter(**filtros).exclude(id=id).exists()
    if existe:
        return HttpResponse("false")
    else:
        return HttpResponse("true")


def validar_campo_unico_extendido(request):
    app = request.POST.get('app')
    model = request.POST.get('modelo')
    filtros = request.POST.get('filtros', {})
    exclusiones = request.POST.get('exclusiones', {})

    modelo_generico = apps.get_model(app, model)
    existe = modelo_generico.objects.filter(
        **filtros).exclude(**exclusiones).exists()
    return JsonResponse(dict(existe=existe))


def validar_numero_documento(request):
    """
    Determina el tipo de documento y lo valida
    :param numero_documento:
    :return:
    """

    numero_documento = request.POST.get('numero_documento')
    
    if len(numero_documento) == 10 or len(numero_documento) == 13:  # verificar la longitud correcta
        cp = int(numero_documento[0:2])
        # verificar codigo de provincia (01-24 y 30=registrados en el exterior)
        if (cp >= 1 and cp <= 24) or cp == 30:
            tercer_dig = int(numero_documento[2])
            if tercer_dig >= 0 and tercer_dig < 6:  # numeros enter 0 y 6
                if len(numero_documento) == 10:
                    return HttpResponse('true' if validar_ced_ruc(numero_documento, 0)
                                        else u'Número de documento no válido.')
                elif len(numero_documento) == 13:
                    # se verifica que los ultimos numeros no sean 000
                    return HttpResponse('true' if validar_ced_ruc(numero_documento, 0) and numero_documento[10:13] != '000'
                                        else u'Número de documento no válido.')
            elif tercer_dig == 6:
                # sociedades publicas
                return HttpResponse(validar_ced_ruc(numero_documento, 1))
            elif tercer_dig == 9:  # si es ruc
                # sociedades privadas
                return HttpResponse(validar_ced_ruc(numero_documento, 2))
            else:
                return HttpResponse(u'Tercer digito invalido')
        else:
            return HttpResponse(u'Codigo de provincia incorrecto')
    else:
        return HttpResponse(u'Longitud incorrecta del numero ingresado')
