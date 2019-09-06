MÓDULO DE PLANIFICACIÓN
==========================================================

Proyecto desarrollado por la **Subdirección de Desarrollo de Software** que pertenece
a la **Unidad de Telecomunicaciones e Información** de la [Universidad Nacional de Loja](http://www.unl.edu.ec)

Descripción
-----------
El módulo permitira realizar las siguientes funcionalidaes:

* Administrar Planes Estratégicos de Desarrollo Institucional (crear, editar, eliminar) con sus respectivos componentes (Objetivos Estratégicos, Objetivos Operativos, Acciones, Indicadores, Metas).
* Administrar Planes Operativos Anuales (POA) con su repectiva planificación para que cada administrador de Unidad Académica Administativa (UAA) pueda administrar su propio POA.
* Administrar POA por UAA con sus respectivas actividades.

Requisitos
----------
1. Una vez con el modulo en app hacer migraciones:
    * python manage.py makemigrations pedi
    * python manage.py migrate pedi
2. Crear funcionaldiades y grupos:
    * python manage.py loaddata pedi_funcionalidades.json
3. Agregar los **usuarios al grupo Panificacion**.       
