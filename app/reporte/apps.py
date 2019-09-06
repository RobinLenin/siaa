from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ReporteConfig(AppConfig):
    name = 'app.reporte'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Reporte,
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
            'perm_modelos': ['plantilla'],
            'funcionalidades': [
                'configuracion_root',
                'reporte_root'
            ],

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
            "codigo": "reporte_root",
            "padre": "configuracion_root",
            "campos": {
                "nombre": "Reportes plantillas",
                "formulario": "/reporte/plantilla/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file-pdf-o",
                "descripcion": "Lista las plantillas de reportes",
                "modulo": "S"
            }
        }
    ]
