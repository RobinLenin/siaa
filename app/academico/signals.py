from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm

from app.academico.models import AsignaturaComponente
from app.academico.models import AsignaturaNivel
from app.academico.models import AutoridadProgramaEstudio
from app.academico.models import ComponenteAprendizaje
from app.academico.models import Nivel
from app.academico.models import OfertaAsignaturaNivel
from app.academico.models import OfertaPensum
from app.academico.models import Pensum
from app.academico.models import Titulo
from app.seguridad.models import Usuario


@receiver(post_save, sender=AsignaturaNivel)
def asignatura_nivel_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse una asignatura nivel
    Si es creación creo las asignaturas componentes y agrego permisos
    :param sender:
    :param instance: Objeto tipo AsignaturaNivel
    :param kwargs:
    :return:
    """
    if kwargs["created"]:
        director = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                          funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums__niveles=instance.nivel, ).all()
        assign_perm('academico.view_asignaturanivel', director, obj=instance)
        if instance.nivel.pensum.editable:
            assign_perm('academico.change_asignaturanivel', director, obj=instance)
            assign_perm('academico.delete_asignaturanivel', director, obj=instance)

        if instance.nivel.pensum.tipo == Pensum.TIPO_COMPONENTE:
            lista_componentes = ComponenteAprendizaje.objects.filter(
                regimen=instance.nivel.pensum.programa_estudio.regimen).all()
            for item in lista_componentes:
                asignatura_componente = AsignaturaComponente()
                asignatura_componente.componente_aprendizaje = item
                asignatura_componente.asignatura_nivel = instance
                asignatura_componente.duracion = 0
                asignatura_componente.save()
                if instance.nivel.pensum.editable:
                    assign_perm('academico.change_asignaturacomponente', director, obj=asignatura_componente)


@receiver([post_save, post_delete], sender=AutoridadProgramaEstudio)
def autoridad_programa_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse una autoridad de ProgramaEstudio
    Agrego-quito a grupo academico_director, y permisos dependiente de
    atributo activo
    :param sender:
    :param instance: objeto modificado tipo AutoridadPrograma
    :param kwargs:
    :return:
    """
    try:
        g = Group.objects.get(name='academico_director')
    except Group.DoesNotExist:
        pass
    else:
        usuario = instance.funcionario.usuario
        if 'created' in kwargs and instance.activo:
            g.user_set.add(usuario)
            pensums = instance.programa_estudio.pensums.all()
            assign_perm('academico.change_programaestudio', usuario, obj=instance.programa_estudio)
            assign_perm('academico.view_programaestudio', usuario, obj=instance.programa_estudio)
            assign_perm('academico.view_pensum', usuario, obj=pensums)

            for pensum in pensums:
                niveles = pensum.niveles.all()
                ofertas_pensum = pensum.ofertas_pensum.all()
                asignaturas = AsignaturaNivel.objects.filter(nivel__pensum=pensum).all()
                asignaturas_componente = AsignaturaComponente.objects.filter(asignatura_nivel__nivel__pensum=pensum).all()
                assign_perm('academico.view_nivel', usuario, obj=niveles)
                assign_perm('academico.view_asignaturanivel', usuario, obj=asignaturas)
                assign_perm('academico.view_titulo', usuario, obj=pensum.titulos.all())
                assign_perm('academico.view_ofertapensum', usuario, obj=ofertas_pensum)
                assign_perm('academico.change_ofertapensum', usuario, obj=ofertas_pensum)
                assign_perm('academico.add_ofertaasignaturanivel', usuario, obj=ofertas_pensum)

                if pensum.editable:
                    assign_perm('academico.change_pensum', usuario, obj=pensum)
                    assign_perm('academico.add_nivel', usuario, obj=pensum)
                    assign_perm('academico.change_nivel', usuario, obj=niveles)
                    assign_perm('academico.delete_nivel', usuario, obj=niveles)
                    assign_perm('academico.add_asignaturanivel', usuario, obj=niveles)
                    assign_perm('academico.change_asignaturanivel', usuario, obj=asignaturas)
                    assign_perm('academico.delete_asignaturanivel', usuario, obj=asignaturas)
                    assign_perm('academico.change_asignaturacomponente', usuario, obj=asignaturas_componente)
        else:
            g.user_set.remove(instance.funcionario.usuario)
            pensums = instance.programa_estudio.pensums.all()
            ofertas_pensum = OfertaPensum.objects.filter(pensum__programa_estudio=instance.programa_estudio).all()
            titulos = Titulo.objects.filter(pensum__programa_estudio=instance.programa_estudio).all()
            niveles = Nivel.objects.filter(pensum__programa_estudio=instance.programa_estudio).all()
            asignaturas = AsignaturaNivel.objects.filter(nivel__pensum__programa_estudio=instance.programa_estudio).all()
            asignaturas_componente = AsignaturaComponente.objects.filter(
                asignatura_nivel__nivel__pensum__programa_estudio=instance.programa_estudio).all()

            remove_perm('academico.change_programaestudio', usuario, obj=instance.programa_estudio)
            remove_perm('academico.view_programaestudio', usuario, obj=instance.programa_estudio)

            remove_perm('academico.view_titulo', usuario, obj=titulos)

            remove_perm('academico.view_pensum', usuario, obj=pensums)
            remove_perm('academico.change_pensum', usuario, obj=pensums)
            remove_perm('academico.add_nivel', usuario, obj=pensums)

            remove_perm('academico.change_nivel', usuario, obj=niveles)
            remove_perm('academico.delete_nivel', usuario, obj=niveles)
            remove_perm('academico.view_nivel', usuario, obj=niveles)
            remove_perm('academico.add_asignaturanivel', usuario, obj=niveles)

            remove_perm('academico.change_asignaturanivel', usuario, obj=asignaturas)
            remove_perm('academico.delete_asignaturanivel', usuario, obj=asignaturas)
            remove_perm('academico.view_asignaturanivel', usuario, obj=asignaturas)

            remove_perm('academico.view_ofertapensum', usuario, obj=ofertas_pensum)
            remove_perm('academico.change_ofertapensum', usuario, obj=ofertas_pensum)
            remove_perm('academico.add_ofertaasignaturanivel', usuario, obj=ofertas_pensum)

            remove_perm('academico.change_asignaturacomponente', usuario, obj=asignaturas_componente)
        g.save()


@receiver(post_save, sender=Nivel)
def nivel_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse un nivel
    Si es creación agrego permisos a las autoridades activas de la carrera
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if kwargs["created"]:
        director = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                          funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums__niveles=instance, ).all()
        assign_perm('academico.view_nivel', director, obj=instance)
        if instance.pensum.editable:
            assign_perm('academico.change_nivel', director, obj=instance)
            assign_perm('academico.delete_nivel', director, obj=instance)
            assign_perm('academico.add_asignaturanivel', director, obj=instance)


@receiver(post_save, sender=OfertaAsignaturaNivel)
def oferta_asignatura_nivel_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse una oferta de asignatura
    Si es creación agrego permisos a autoridadees de las carreras
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if kwargs["created"]:
        directores = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                            funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums__ofertas_pensum=instance.oferta_pensum, ).all()
        assign_perm('academico.view_ofertaasignaturanivel', directores, obj=instance)
        assign_perm('academico.change_ofertaasignaturanivel', directores, obj=instance)
        assign_perm('academico.delete_ofertaasignaturanivel', directores, obj=instance)

@receiver(post_save, sender=OfertaPensum)
def oferta_pensum_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse una oferta de pensum
    Si es creación agrego permisos a autoridades de la carrera
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if kwargs["created"]:
        directores = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                            funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums__ofertas_pensum=instance, ).all()
        assign_perm('academico.view_ofertapensum', directores, obj=instance)
        assign_perm('academico.change_ofertapensum', directores, obj=instance)
        assign_perm('academico.add_ofertaasignaturanivel', directores, obj=instance)

@receiver(post_save, sender=Pensum)
def pensum_postsave_handler(sender, instance, **kwargs):
    """
    Ejecutado luego de guardarse un pensum
    Si es creación agrego permisos
    Si cambia atributo editable  agrego/quito permisos
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if kwargs["created"] and instance.editable:
        directores = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                            funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums=instance, ).all()
        assign_perm('academico.view_pensum', directores, obj=instance)
        assign_perm('academico.change_pensum', directores, obj=instance)
        assign_perm('academico.add_nivel', directores, obj=instance)
    elif instance.editable != instance._Pensum__original_editable:
        directores = Usuario.objects.filter(funcionario__autoridad__activo=True,
                                            funcionario__autoridad__autoridadprogramaestudio__programa_estudio__pensums=instance, )
        for director in directores.all():
            niveles = Nivel.objects.filter(pensum=instance).all()
            asignaturas = AsignaturaNivel.objects.filter(nivel__pensum=instance).all()
            asignaturas_componente = AsignaturaComponente.objects.filter(asignatura_nivel__nivel__pensum=instance).all()
            if instance.editable:

                assign_perm('academico.change_pensum', director, obj=instance)
                assign_perm('academico.add_nivel', director, obj=instance)
                assign_perm('academico.change_nivel', director, obj=niveles)
                assign_perm('academico.delete_nivel', director, obj=niveles)
                assign_perm('academico.add_asignaturanivel', director, obj=niveles)
                assign_perm('academico.change_asignaturanivel', director, obj=asignaturas)
                assign_perm('academico.delete_asignaturanivel', director, obj=asignaturas)
                assign_perm('academico.change_asignaturacomponente', director, obj=asignaturas_componente)

            else:

                remove_perm('academico.change_pensum', director, obj=instance)
                remove_perm('academico.add_nivel', director, obj=instance)
                remove_perm('academico.change_nivel', director, obj=niveles)
                remove_perm('academico.delete_nivel', director, obj=niveles)
                remove_perm('academico.add_asignaturanivel', director, obj=niveles)
                remove_perm('academico.change_asignaturanivel', director, obj=asignaturas)
                remove_perm('academico.delete_asignaturanivel', director, obj=asignaturas)
                remove_perm('academico.change_asignaturacomponente', director, obj=asignaturas_componente)


