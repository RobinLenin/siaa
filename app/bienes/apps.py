from django.apps import AppConfig
from django.db.models.signals import post_migrate


class BienesConfig(AppConfig):
    name = 'app.bienes'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Bienes,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades,funcionalidades grupos
        y permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [
        # Grupo de Prestaciones
        {
            'nombre': 'bienes_prestaciones',
            'funcionalidades': [
                'bienes_laboratorios_root',
                'bienes_prestaciones',
                'bienes_prestaciones_reporte'
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "bienes_laboratorios_root",
            "padre": None,
            "campos": {
                "nombre": "Gestión de Laboratorios",
                "formulario": "bienes-laboratorios",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "folder",
                "descripcion": "Menu Principal de la funcionalidad Laboratorios",
                "modulo": "A"
            }
        },
        {
            "codigo": "bienes_prestaciones",
            "padre": "bienes_laboratorios_root",
            "campos": {
                "nombre": "Administrador de prestaciones",
                "formulario": "prestaciones",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Listada de prestaciones",
                "modulo": "A",
            }
        },
        {
            "codigo": "bienes_prestaciones_reporte",
            "padre": "bienes_laboratorios_root",
            "campos": {
                "nombre": "Administrador de reportes",
                "formulario": "prestaciones-reporte",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Reporte de las prestaciones",
                "modulo": "A",
            }
        },
    ]
