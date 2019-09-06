from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TalentoHumanoConfig(AppConfig):
    name = 'app.talento_humano'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Talento Humano,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades,funcionalidades grupos
        y permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [
        # Grupo Talento Humano Administrador
        {
            'nombre': 'talento humano',
            'perm_detalle':['add_asignacionpuesto', 'change_asignacionpuesto', 'view_asignacionpuesto', 'add_ausentismo'],
            'perm_modelos': ['evaluaciondesempenio', 'formacionacademica'],
            'funcionalidades': [
                'talento_humano_root',
                'talento_humano_puestos',
                'talento_humano_uaa_puestos',
                'talento_humano_funcionarios',
                'talento_humano_asignaciones',
                'talento_humano_vacaciones',
                'talento_humano_ausentismos',
                'talento_humano_regimen_laboral',
                'reportes_root',
                'reporte_talento_humano_root',
                'reporte_talento_humano_funcionarios',
                'reporte_talento_humano_funcionarios_edad',
                'reporte_talento_humano_vacaciones_periodo',
                'reporte_talento_humano_vacaciones_pendientes',
                'reporte_talento_humano_ausentismos',
                'reporte_talento_humano_asignacion_puesto_filtro_siith',
                'reporte_talento_humano_registro_vacaciones_filtro'
            ]
        },
        # Grupo Talento Humano Sniese
        {
            'nombre': 'talento_humano_sniese',
            'funcionalidades': [
                'reportes_root',
                'reporte_sniese_root',
                'reporte_sniese_docentes',
                'reporte_sniese_funcionarios'
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "talento_humano_root",
            "padre": None,
            "campos": {
                "nombre": "Talento Humano",
                "formulario": "/talento-humano",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-users",
                "descripcion": "Menu Principal del Modulo Talento Humano",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_puestos",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Puestos",
                "formulario": "/talento-humano/puestos",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista los puestos",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_uaa_puestos",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Puestos por UAA",
                "formulario": "/talento-humano/uaa-puesto",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista los puestos por UAA",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_funcionarios",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Funcionarios",
                "formulario": "/talento-humano/funcionarios",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista los funcionarios",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_asignaciones",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Asignaciones",
                "formulario": "/talento-humano/asignacion-puestos/lista",
                "orden": 4,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista las asignaciones de puestos",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_vacaciones",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Vacaciones",
                "formulario": "/talento-humano/vacaciones",
                "orden": 5,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista las vacaciones",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_ausentismos",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Ausentismos",
                "formulario": "/talento-humano/ausentismos",
                "orden": 6,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista los ausentismos",
                "modulo": "S"
            }
        },
        {
            "codigo": "talento_humano_regimen_laboral",
            "padre": "talento_humano_root",
            "campos": {
                "nombre": "Régimen Laboral",
                "formulario": "/talento-humano/regimen-laboral",
                "orden": 7,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Lista los funcionarios por regimen laboral",
                "modulo": "S"
            }
        },
        # Reportes Talento Humano
        {
            "codigo": "reportes_root",
            "padre": None,
            "campos": {
                "nombre": "Reportes",
                "formulario": "/reportes",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-bar-chart",
                "descripcion": "Menu principal de reportes",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_root",
            "padre": "reportes_root",
            "campos": {
                "nombre": "Talento Humano",
                "formulario": "/reportes-talento-humano",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-bar-chart",
                "descripcion": "Menu principal de reportes de Talento Humano",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_funcionarios",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "Funcionarios",
                "formulario": "/talento-humano/reporte/index",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de funcionarios con filtro avanzado",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_funcionarios_edad",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "Funcionarios por edad",
                "formulario": "/talento-humano/vacaciones/reporte_general",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de funcionarios por edad",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_vacaciones_periodo",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "Vacaciones periodo",
                "formulario": "/talento-humano/reporte/vacaciones/periodo",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de vacaciones por periodo",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_vacaciones_pendientes",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "Vacaciones pendientes",
                "formulario": "/talento-humano/reporte/vacaciones/pendientes",
                "orden": 4,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de vacaciones pendientes",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_ausentismos",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "Ausentismos",
                "formulario": "/talento-humano/reporte/reporte_ausentismos",
                "orden": 5,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de ausentismos",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_asignacion_puesto_filtro_siith",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "	Exportación SIITH",
                "formulario": "/talento-humano/asignacion-puesto/filtro-siith",
                "orden": 6,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reportes para exportar de acuerdo al formato requerido por el sistema SIITH",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_talento_humano_registro_vacaciones_filtro",
            "padre": "reporte_talento_humano_root",
            "campos": {
                "nombre": "	Registro de vacaciones",
                "formulario": "/talento-humano/registro-vacaciones/filtro",
                "orden": 7,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reportes para exportar registro vacaciones",
                "modulo": "S"
            }
        },
        # Reportes Sniese
        {
            "codigo": "reporte_sniese_root",
            "padre": "reportes_root",
            "campos": {
                "nombre": "Sniese",
                "formulario": "/reportes-sniese",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-bar-chart",
                "descripcion": "Menu principal de reportes Sniese",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_sniese_docentes",
            "padre": "reporte_sniese_root",
            "campos": {
                "nombre": "Docentes",
                "formulario": "/talento-humano/funcionario/reportes/sniese/0",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de docentes para el Sniese",
                "modulo": "S"
            }
        },
        {
            "codigo": "reporte_sniese_funcionarios",
            "padre": "reporte_sniese_root",
            "campos": {
                "nombre": "Funcionarios",
                "formulario": "/talento-humano/funcionario/reportes/sniese/1",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "fa-file",
                "descripcion": "Reporte de funcionarios para el Sniese",
                "modulo": "S"
            }
        }
    ]
