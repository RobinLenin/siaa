from django.db.models import Q
from guardian.shortcuts import get_objects_for_user

from app.tesoreria.models import CuentaCobrar
from app.academico.models import ProgramaEstudio


class DatatableBuscar():
    """
    Busca por los parámetros indicados para el datatable para un modelo
    :param params:
    :return:
    """

    @staticmethod
    def cuenta_cobrar(params):
        queryset = CuentaCobrar.objects
        params.total = queryset.count()

        if params.search_value:
            qset = Q()
            for sValue in params.get_search_values():
                qset = qset & (
                        Q(id__icontains=sValue) |
                        Q(cliente__icontains=sValue) |
                        Q(monto__icontains=sValue) |
                        Q(saldo__icontains=sValue))
            queryset = queryset.filter(qset)

        params.count = queryset.count()
        params.items = params.init_items(queryset)

        return params

    @staticmethod
    def programa_estudio(params):
        if params.request and params.request.user:
            queryset = get_objects_for_user(params.request.user, 'academico.view_programaestudio',
                                            accept_global_perms=True)
        else:
            queryset = ProgramaEstudio.objects
        params.total = queryset.count()

        if params.search_value:
            qset = Q()
            for sValue in params.get_search_values():
                qset = qset & (Q(nombre__icontains=sValue) |
                               Q(modalidad__icontains=sValue) |
                               Q(facultad__siglas__icontains=sValue))
            queryset = queryset.filter(qset)

        params.count = queryset.count()
        params.items = params.init_items(queryset)

        return params
