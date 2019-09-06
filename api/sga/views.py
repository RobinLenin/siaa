from django.http import JsonResponse, HttpResponseBadRequest

from api.core.serializers import PersonaKohaSerializer
from api.sga.utils import WebServiceSga
from app.core.models import Persona, CatalogoItem


def consultar_usuario_koha(request, cedula):
    """
    Método que permite retornar información académica del estudiante, relacionada
    a la carrera como: mallas, matriculas de la malla y oferta academica del SGA
    :param request:
    :param cedula:
    :return: Devuelve un dict con la información del propietario de la cedula.
    """
    try:
        datos_personales = {'estudiante_activo': False,
                            'docente_activo': False}
        sga_service = WebServiceSga()
        datos_sga = sga_service.get_sgaws_datos_usuario_koha(cedula)
        datos_personales.update(datos_sga)
        persona = Persona.objects.filter(numero_documento=cedula).first()
        if datos_sga.get('numero_documento', False):
            # priorizo datos del siaaf a los del sga:
            datos_personales['sexo'] = persona and persona.sexo and persona.sexo.nombre or str(
                CatalogoItem.get_catalogo_item('TIPO_SEXO', datos_sga.get('sexo')))
            datos_personales['nacionalidad'] = persona and persona.nacionalidad and persona.nacionalidad.nombre or str(
                CatalogoItem.get_catalogo_item('NACIONALIDAD', datos_sga.get('nacionalidad')))
            datos_personales[
                'tipo_documento'] = persona and persona.tipo_documento and persona.tipo_documento.nombre or str(
                CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', datos_sga.get('tipo_documento')))
            datos_personales['estado_civil'] = str(
                CatalogoItem.get_catalogo_item('ESTADO_CIVIL', datos_sga.get('estado_civil')))
            if persona:
                datos_personales['nombres'] = persona.get_nombres()
                datos_personales['apellidos'] = persona.get_apellidos()
        elif persona:
            datos_personales.update(PersonaKohaSerializer(persona).data)
            direccion = persona.direccion_set.filter(tipo_direccion__catalogo__codigo='TIPO_DIRECCION',
                                                     tipo_direccion__nombre='Domicilio').first() or persona.direccion_set.first()
            datos_personales['nombres'] = persona.get_nombres()
            datos_personales['apellidos'] = persona.get_apellidos()
            if direccion:
                datos_personales['direccion'] = '%s, %s' % (direccion.calle_principal, direccion.calle_secundaria)
                datos_personales['direccion_referencia'] = direccion.referencia
                datos_personales['telefono'] = direccion.telefono or ''
                datos_personales['celular'] = direccion.celular
        else:
            datos_personales['mensaje'] = 'No se encontro una persona asociada al numero de identificacion'
        if hasattr(persona, 'usuario'):
            datos_personales['correo_institucional'] = persona.usuario.correo_electronico_institucional
        return JsonResponse(datos_personales, safe=False)
    except Exception as e:
        return HttpResponseBadRequest(content=str(e))
