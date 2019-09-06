from django.apps import AppConfig
from django.db.models.signals import post_migrate


class PlanificacionConfig(AppConfig):
    name = 'app.planificacion'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Planificacion,
        se ejecuta metodo 'populate_models', para crear/actualizar funcionalidades
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [{
        'nombre': 'planificacion_usuario',
        'perm_detalle': ['view_metaanual', 'change_metaanual', 'add_metaanual', 'view_planoperativo'],
        'perm_modelos': ['actividad', 'presupuesto', 'verificacion'],
        'funcionalidades': [
            'planificacion_root',
            'planificacion_planes_operativos'
        ]
    }, {
        'nombre': 'planificacion_administrador',
        'perm_modelos': ['actividad', 'estrategia', 'indicador', 'metaanual',
                         'objetivoestrategico', 'objetivooperativo', 'planestrategico',
                         'planoperativo', 'politica', 'presupuesto', 'resultado', 'verificacion'],
    # todos los models de la app
        'funcionalidades': [
            'planificacion_root',
            'planificacion_planes_estrategicos',
            'planificacion_planes_operativos'
        ]
    }
    ]
    funcionalidades = [
        {
            "campos": {
                "nombre": "Planificacion y Desarrollo",
                "formulario": "/planificacion",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "folder",
                "descripcion": "Menu Principal Modulo de planificacion",
                "modulo": "S"
            },
            "padre": None,
            "codigo": "planificacion_root",
        },
        {
            "codigo": "planificacion_planes_estrategicos",
            "padre": "planificacion_root",
            "campos": {
                "nombre": "Planes Estrategicos",
                "formulario": "/planificacion/plan-estrategico/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "assignment",
                "descripcion": "Listado de Planes Estrategicos",
                "modulo": "S",
            }
        },
        {
            "codigo": "planificacion_planes_operativos",
            "padre": "planificacion_root",
            "campos": {
                "nombre": "Planes Operativos",
                "formulario": "/planificacion/plan-operativo/lista",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Planes Operativos Anuales",
                "modulo": "S",
            }
        },
    ]
