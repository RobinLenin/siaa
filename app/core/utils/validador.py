from django.apps import apps
from django.http import JsonResponse, HttpResponse


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

    print('filtros', filtros)
    print('exculusiones', exclusiones)

    modelo_generico = apps.get_model(app, model)
    existe = modelo_generico.objects.filter(**filtros).exclude(**exclusiones).exists()
    return JsonResponse(dict(existe=existe))

