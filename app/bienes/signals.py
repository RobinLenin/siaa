from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from app.seguridad.models import Funcionalidad, FuncionalidadGroup

def populate_models(sender, **kwargs):
    """
    Metodo para crear funcionalidades, grupos, permisos, y funcionalidades grupos por defecto del modulo bienes
    :param sender:
    :param kwargs:
    :return:
    """
    BienesConfig = sender
    app_name= 'bienes'

    # funcionalidades
    for funcionalidad_data in BienesConfig.funcionalidades:
        funcionalidad_padre = Funcionalidad.objects.get(codigo=funcionalidad_data.get('padre')) if funcionalidad_data.get('padre') else None
        campos = funcionalidad_data.get('campos')
        campos.update({'padre': funcionalidad_padre})
        funcionalidad, created = Funcionalidad.objects.update_or_create(codigo=funcionalidad_data.get('codigo'), defaults=campos)

    # grupos, permisos y funcionalidades grupos
    for grupo_data in BienesConfig.grupos:
        grupo, created = Group.objects.get_or_create(name=grupo_data.get('nombre'))
        permissions = Permission.objects.filter(Q(codename__in=grupo_data.get('perm_detalle',[])) |
                                                Q(content_type__model__in=grupo_data.get('perm_modelos', [])),
                                                content_type__app_label=app_name)
        grupo.permissions.set(permissions)
        for codigo_fun in grupo_data.get('funcionalidades'):
            funcionalidad = Funcionalidad.objects.filter(codigo=codigo_fun).first()
            if funcionalidad:
                FuncionalidadGroup.objects.get_or_create(funcionalidad=funcionalidad, group=grupo)
