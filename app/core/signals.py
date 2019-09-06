from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from app.seguridad.models import Funcionalidad, FuncionalidadGroup


def populate_models(sender, **kwargs):
    """
    Metodo para crear funcionalidades, grupos, permisos, y funcionalidades grupos por defecto del modulo Core
    comunes en el sistema SIAAF
    :param sender:
    :param kwargs:
    :return:
    """
    app_config = sender
    app_name = app_config.label

    # funcionalidades
    for funcionalidad_data in app_config.funcionalidades:
        funcionalidad_padre = Funcionalidad.objects.get(
            codigo=funcionalidad_data.get('padre')) if funcionalidad_data.get('padre') else None
        campos = funcionalidad_data.get('campos')
        campos.update({'padre': funcionalidad_padre})
        funcionalidad, created = Funcionalidad.objects.update_or_create(codigo=funcionalidad_data.get('codigo'),
                                                                        defaults=campos)

    # grupos y permisos
    for grupo_data in app_config.grupos:
        grupo, created = Group.objects.get_or_create(name=grupo_data.get('nombre'))
        permissions = Permission.objects.filter(Q(codename__in=grupo_data.get('perm_detalle', [])) |
                                                Q(content_type__model__in=grupo_data.get('perm_modelos', [])),
                                                content_type__app_label=app_name)
        grupo.permissions.remove(
            *grupo.permissions.filter(content_type__app_label=app_name).exclude(id__in=permissions.values_list('id')))
        grupo.permissions.add(*permissions)
        for codigo_fun in grupo_data.get('funcionalidades', []):
            funcionalidad = Funcionalidad.objects.filter(codigo=codigo_fun).first()
            if funcionalidad:
                FuncionalidadGroup.objects.get_or_create(funcionalidad=funcionalidad, group=grupo)
