from django.apps import AppConfig
from django.db.models.signals import post_migrate

class TesoreriaConfig(AppConfig):
    name = 'app.tesoreria'


    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Académico,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades,funcionalidades grupos
        y permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)
        from . import signals

    grupos = [
        #
        {
            'nombre': 'tesoreria_abogado',
            # para permisos especificos
            'perm_detalle': ['view_cuentacobrar'],
            # permisos globales por modelo
            'perm_modelos': ['comentario'
                             ],
            'funcionalidades': [
                'tesoreria_root',
                'tesoreria_cuentas_cobrar',
            ]
        },
        {
            'nombre': 'tesoreria_administrador',
            # para permisos especificos
            'perm_detalle': ['view_cuentacobrar'],
            # permisos globales por modelo
            'perm_modelos': ['abono','cuentacobrar','comentario','tasainteres','interesmensual','cliente'
                             ],
            'funcionalidades': [
                'tesoreria_root',
                'tesoreria_cuentas_cobrar',
                'tesoreria_tasas_interes',
                'tesoreria_cliente',

            ]
        },

        {
            'nombre': 'tesoreria_asistente',
            # para permisos especificos
            'perm_detalle': ['view_cuentacobrar'],
            # permisos globales por modelo
            'perm_modelos': ['abono'
                             ],
            'funcionalidades': [
                'tesoreria_root',
                'tesoreria_cuentas_cobrar',
                'tesoreria_tasas_interes',
                'tesoreria_cliente',

            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "tesoreria_root",
            "padre": None,
            "campos": {
                "nombre": "Tesoreria",
                "formulario": "/tesoreria/index",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-list-alt",
                "descripcion": "Menu Principal Modulo de Tesoreria",
                "modulo": "S"
            },
        },
        {
            "codigo": "tesoreria_cuentas_cobrar",
            "padre": "tesoreria_root",
            "campos": {
                "nombre": "Cuentas por Cobrar",
                "formulario": "/tesoreria/cuenta_cobrar/listar",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Cuentas por cobrar",
                "modulo": "S"
            },
        },
        {
            "codigo": "tesoreria_tasas_interes",
            "padre": "tesoreria_root",
            "campos": {
                "nombre": "Tasas de Interes",
                "formulario": "/tesoreria/tasa_interes/listar",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Tasas de interes",
                "modulo": "S"
            },
        },
        {
            "codigo": "tesoreria_cliente",
            "padre": "tesoreria_root",
            "campos": {
                "nombre": "Cliente",
                "formulario": "/tesoreria/cliente/listar",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Clientes",
                "modulo": "S"
            },
        }
    ]