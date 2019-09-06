from django.apps import AppConfig
from django.db.models.signals import post_migrate


class RecaudacionConfig(AppConfig):
    name = 'app.recaudacion'

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
            'perm_detalle': ['view_puntoemisionuaa', 'add_comprobante', 'change_comprobante', 'view_comprobante',
                             'add_ordenpago', 'change_ordenpago', 'view_ordenpago'],
            'perm_modelos': ['producto', 'puntoemision'],
            'funcionalidades': [
                'recaudacion_root',
                'recaudacion_puntos_emision',
                'recaudacion_productos',
                'recaudacion_ordenes_pago',
                'recaudacion_emision_comprobantes',
                'recaudacion_reportes_administrador'
            ]
        },
        # Grupo Recaudacion Usuario
        {
            'nombre': 'recaudacion_usuario',
            'perm_detalle': ['view_ordenpago', 'add_ordenpago', 'change_ordenpago',
                             'view_producto', 'view_puntoemision', 'view_puntoemisionuaa'],
            'funcionalidades': [
                'recaudacion_root',
                'recaudacion_ordenes_pago',
                'recaudacion_reportes_usuario',
                'recaudacion_ordenes_pago_validar'
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "recaudacion_root",
            "padre": None,
            "campos": {
                "nombre": "Recaudación",
                "formulario": "recaudacion",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "folder",
                "descripcion": "Menu Principal del Modulo Recaudación",
                "modulo": "A"
            }
        },
        {
            "codigo": "recaudacion_puntos_emision",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Puntos de Emisión",
                "formulario": "recaudacion-punto-emision-list",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Listada de Puntos de Emicsión",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_productos",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Productos",
                "formulario": "recaudacion-producto-list",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Lista de productos",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_ordenes_pago",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Ordenes de Pago",
                "formulario": "recaudacion-orden-pago-list",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Lista de Ordenes de Pago",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_emision_comprobantes",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Emisión de Facturas",
                "formulario": "recaudacion-factura-emision-list",
                "orden": 5,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Emisión y anulación de comprobantes (facturas electrónicas)",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_reportes_usuario",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Reportes Recaudadora",
                "formulario": "recaudacion-reportes-uaa",
                "orden": 6,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Reportes asignados a los recaudadores",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_reportes_administrador",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Reportes Tesorería",
                "formulario": "recaudacion-reportes-admin",
                "orden": 7,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Reportes asignado a la tesorera",
                "modulo": "A",
            }
        },
        {
            "codigo": "recaudacion_ordenes_pago_validar",
            "padre": "recaudacion_root",
            "campos": {
                "nombre": "Ordenes pendientes",
                "formulario": "recaudacion-orden-pago-validar-list",
                "orden": 8,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Lista de ordenes de pago a validar",
                "modulo": "A",
            }
        }
    ]
