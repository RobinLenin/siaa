from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


class IsPermission(object):
    """
    Decorador que se ejecuta al consumir el API que valida si el usuario
    tienen el permiso para ejecutar una acción sobre le modelo. Ejemplo:
    @method_decorator(IsPermission('recaudacion.view_producto'))
    @method_decorator(IsPermission(('recaudacion.view_producto', 'recaudacion.change_producto')))
    """

    def __init__(self, permission):
        self.permission = permission

    def __call__(self, funcion):
        def wrapper(request, *args, **kwargs):
            try:
                perms = (self.permission,) if isinstance(self.permission, str) else self.permission
                if request.user.has_perms(perms) is False:
                    raise PermissionDenied
            except:
                raise PermissionDenied

            return funcion(request, *args, **kwargs)

        return wrapper


def group_required(*group_names):
    """
    Para los views del app solo en caso de requerirse, valida si el usuario pertene a un/varios grupos.
    Ejemplo: @group_required('seguridad', 'talento_humano')
    :param group_names: De uno a varios grupos
    :return:
    """

    def in_groups(u):
        if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
            return True
        else:
            raise PermissionDenied

    return user_passes_test(in_groups)
