from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AcademicoConfig(AppConfig):
    name = 'app.academico'

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
        # Academico coordinación de docencia
        {
            'nombre': 'academico_coordinacion_docencia',
            'perm_detalle': ['add_ofertapensum','delete_ofertapensum'],
            'perm_modelos': ['autoridadfacultad', 'autoridadprogramaestudio', 'asignatura', 'asignaturacomponente',
                             'asignaturanivel', 'facultad', 'nivel', 'pensum',
                             'pensumcomplementario', 'pensumgrupo', 'programaestudio', 'titulo',
                             'ofertaacademica', 'periodoacademico', 'periodo_matricula'
                             ],
            'funcionalidades': [
                'academico_root',
                'academico_curricular_root',
                'academico_curricular_asignaturas',
                'academico_curricular_facultades',
                'academico_curricular_programas_estudio',
                'academico_curricular_pensums_grupo',
                'academico_periodos_academicos',
            ]
        },
        # Academico Gestor / Director
        {
            'nombre': 'academico_director',
            'perm_detalle': ['view_pensumgrupo', 'view_periodoacademico', 'view_periodomatricula', 'view_ofertaacademica'],
            'perm_modelos': [],
            'funcionalidades': [
                'academico_root',
                'academico_programa_estudio',
                'academico_periodos_academicos',
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "academico_root",
            "padre": None,
            "campos": {
                "nombre": "Académico",
                "formulario": "/academico",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-list-alt",
                "descripcion": "Menu Principal Modulo de académico",
                "modulo": "S"
            },
        },
        {
            "codigo": "academico_curricular_root",
            "padre": "academico_root",
            "campos": {
                "nombre": "Curricular",
                "formulario": "/academico/curricular",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-list-alt",
                "descripcion": "Menu Principal de la parte curricular del módulo académico",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_curricular_asignaturas",
            "padre": "academico_curricular_root",
            "campos": {
                "nombre": "Asignaturas",
                "formulario": "/academico/asignatura/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Listado de asignaturas",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_curricular_facultades",
            "padre": "academico_curricular_root",
            "campos": {
                "nombre": "Facultades",
                "formulario": "/academico/facultad/lista",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Listado de facultades",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_curricular_programas_estudio",
            "padre": "academico_curricular_root",
            "campos": {
                "nombre": "Programas de estudio",
                "formulario": "/academico/programa-estudio/lista",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Listado de programas de estudio",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_curricular_pensums_grupo",
            "padre": "academico_curricular_root",
            "campos": {
                "nombre": "Agrupación de Pensum",
                "formulario": "/academico/pensum-grupo/lista",
                "orden": 5,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Listado de pensums agrupados",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_periodos_academicos",
            "padre": "academico_root",
            "campos": {
                "nombre": "Periodos académicos",
                "formulario": "/academico/periodo-academico/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Listado de periodos académicos",
                "modulo": "S",
            }
        },
        {
            "codigo": "academico_programa_estudio",
            "padre": "academico_root",
            "campos": {
                "nombre": "Programas de estudio",
                "formulario": "/academico/programa-estudio/lista-perfil",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-cogs",
                "descripcion": "Programas de estudio",
                "modulo": "S",
            }
        },

    ]
