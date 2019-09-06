from django.apps import AppConfig
from django.db.models.signals import post_migrate


class SeguridadConfig(AppConfig):
    name = 'app.seguridad'

    def ready(self):
        """
        Metodo ejecutado en cada carga del módulo Seguridad,
        se ejecuta metodo 'populate_models', para crear/actualizar grupos, funcionalidades, funcionalidades grupos y
        asignación de permisos a los grupos
        :return:
        """
        from app.core.signals import populate_models
        post_migrate.connect(populate_models, sender=self)

    grupos = [
        # Grupo Seguridad de la Información Administrador
        {
            'nombre': 'seguridad_informacion_administrador',
            'perm_detalle': ['view_usuario', 'change_usuario', 'add_usuario',
                             'view_cuentacorreo', 'change_cuentacorreo', 'add_cuentacorreo',
                             'view_grupoldap', 'change_grupoldap', 'add_grupoldap'],
            'funcionalidades': [
                'seguridad_informacion_root',
                'seguridad_informacion_usuarios',
                'seguridad_informacion_cuentas_correo',
                'seguridad_informacion_grupos_ldap'
            ]
        }
    ]
    funcionalidades = [
        {
            "codigo": "seguridad_informacion_root",
            "padre": None,
            "campos": {
                "nombre": "Seguridad Información",
                "formulario": "/seguridad-informacion",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-unlock-alt",
                "descripcion": "Menu Principal del Modulo Seguridad de la Información",
                "modulo": "S"
            }
        },
        {
            "codigo": "seguridad_informacion_usuarios",
            "padre": "seguridad_informacion_root",
            "campos": {
                "nombre": "Usuarios",
                "formulario": "/seguridad-informacion/usuario/lista",
                "orden": 1,
                "activo": True,
                "mostrar": True,
                "icon": "fa-user",
                "descripcion": "Listada de Usuario",
                "modulo": "S",
            }
        },
        {
            "codigo": "seguridad_informacion_cuentas_correo",
            "padre": "seguridad_informacion_root",
            "campos": {
                "nombre": "Cuentas correo",
                "formulario": "/seguridad-informacion/cuenta-correo/lista",
                "orden": 2,
                "activo": True,
                "mostrar": True,
                "icon": "fa-envelope",
                "descripcion": "Lista de cuentas de correo",
                "modulo": "S",
            }
        },
        {
            "codigo": "seguridad_informacion_grupos_ldap",
            "padre": "seguridad_informacion_root",
            "campos": {
                "nombre": "Grupos Ldap",
                "formulario": "/seguridad-informacion/grupo-ldap/lista",
                "orden": 3,
                "activo": True,
                "mostrar": True,
                "icon": "fa-object-group",
                "descripcion": "Lista de grupos Ldap",
                "modulo": "S",
            }
        }
    ]
