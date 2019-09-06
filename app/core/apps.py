from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    name = 'app.core'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Core, se ejecuta metodo 'populate_models' para asignar
        funcionalidades, grupos, permisos, funcionalidades grupos comunes en el sistema SIAAF
        :return:
        """
        from .signals import populate_models
        #post_migrate.connect(populate_models, sender=self)


