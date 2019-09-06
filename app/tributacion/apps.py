from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TributacionConfig(AppConfig):
    name = 'app.tributacion'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Recaudación,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades,funcionalidades grupos
        y permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [
        # Grupo Recaudacion Administrador
        {
            'nombre': 'recaudacion_administrador',
            'perm_detalle': ['add_comprobante', 'change_comprobante', 'view_comprobante'],
        },
        ]
    funcionalidades = []
