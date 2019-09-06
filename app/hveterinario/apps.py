from django.apps import AppConfig
from django.db.models.signals import post_migrate


class HveterinarioConfig(AppConfig):
    name = 'app.hveterinario'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Hveterinario,
        se ejecuta metodo 'populate_models', para crear/actualizar funcionalidades
        :return:
        """

        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [{
        'nombre': 'hveterinario_usuario',
        'perm_detalle': [],
        'perm_modelos': ['paciente','consulta','listamaestra','inscripciontratamiento'],
        'funcionalidades': [
            'hveterinario_root',
            'hveterinario_paciente',
            "hveterinario_consulta",
            "hveterinario_lista_maestra",
            "hveterinario_inscripcion_tratamiento",
            "hveterinario_propietarios",
        ]
    }]
    funcionalidades = [
        {
            "campos": {
                "nombre": "Hospital Veterinario",
                "formulario": "/hveterinario",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "hospital",
                "descripcion": "Menu Principal Modulo de Hveterinario",
                "modulo": "S"
            },
            "padre": None,
            "codigo": "hveterinario_root",
        },
        {
            "codigo": "hveterinario_propietarios",
            "padre": "hveterinario_root",
            "campos": {
                "nombre": "Propietarios",
                "formulario": "/hveterinario/propietarios/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Propietarios",
                "modulo": "S",
            }
        },
        {
            "codigo": "hveterinario_paciente",
            "padre": "hveterinario_root",
            "campos": {
                "nombre": "Pacientes",
                "formulario": "/hveterinario/paciente/lista",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Pacientes",
                "modulo": "S",
            }
        },
        {
            "codigo": "hveterinario_consulta",
            "padre": "hveterinario_root",
            "campos": {
                "nombre": "Consultas",
                "formulario": "/hveterinario/consulta/lista",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Consulta",
                "modulo": "S",
            }
        },
        {
            "codigo": "hveterinario_lista_maestra",
            "padre": "hveterinario_root",
            "campos": {
                "nombre": "Lista Maestra",
                "formulario": "/hveterinario/lista-maestra/lista",
                "orden": 4,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Lista Maestra",
                "modulo": "S",
            }
        },
        {
            "codigo": "hveterinario_inscripcion_tratamiento",
            "padre": "hveterinario_root",
            "campos": {
                "nombre": "Inscripcion Tratamiento",
                "formulario": "/hveterinario/inscripcion-tratamiento/lista",
                "orden": 5,
                "activo": True,
                "mostrar": True,
                "icon": "list",
                "descripcion": "Inscripcion Tratamiento",
                "modulo": "S",
            }
        },


    ]