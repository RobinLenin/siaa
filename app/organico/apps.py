from django.apps import AppConfig
from django.db.models.signals import post_migrate


class OrganicoConfig(AppConfig):
    name = 'app.organico'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Organico,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades,funcionalidades grupos
        y permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [
        # Grupo Administrador del SIAAF
        {
            'nombre': 'administrador',
            'perm_modelos': ['uaa'],
            'funcionalidades': [
                'configuracion_root',
                'organico_root'
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "configuracion_root",
            "padre": None,
            "campos": {
                "nombre": "	Configuración",
                "formulario": "/configuracion",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-gear",
                "descripcion": "Menu Principal para Configuración del SIAAF",
                "modulo": "S"
            }
        },
        {
            "codigo": "organico_root",
            "padre": "configuracion_root",
            "campos": {
                "nombre": "Orgánico estructural",
                "formulario": "/organico",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-list-ul",
                "descripcion": "Estructura del orgánico estructural",
                "modulo": "S"
            }
        }
    ]
