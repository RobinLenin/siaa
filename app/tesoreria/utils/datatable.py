from django.db.models import Q
from guardian.shortcuts import get_objects_for_user

from app.tesoreria.models import CuentaCobrar


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
                        Q(cliente__primer_apellido__icontains=sValue) |
                        Q(cliente__segundo_apellido__icontains=sValue) |
                        Q(cliente__primer_nombre__icontains=sValue) |
                        Q(cliente__numero_documento__icontains=sValue) |
                        Q(cliente__segundo_nombre__icontains=sValue))
            queryset = queryset.filter(qset)

        params.count = queryset.count()
        params.items = params.init_items(queryset)

        return params


