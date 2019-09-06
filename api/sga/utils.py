import json

from suds import Client


class WebServiceSga():
    """
    Clase para obtener datos academicos desde el webservice del sga.
    estudiantes, datos_personales, carreras, ofertas, matriculas.
    """

    @staticmethod
    def crear_cliente_academica():
        """
        Metodo generico para crear una conexion con el webservice SGA - académico
        ejem datos de carreras,matriculas,ofertas...
        :return: cliente de conexion tipo suds.client.Client
        """
        from app.configuracion.models import DetalleParametrizacion
        url = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                    codigo='sgaws_url_academica').first()
        location = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                         codigo='sgaws_location_academica').first()
        port = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                     codigo='sgaws_port_academica').first()
        user = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS', codigo='sgaws_usuario').first()
        passwd = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                       codigo='sgaws_password').first()
        client = Client(url=url.valor, username=user.valor, password=passwd.valor, location=location.valor)
        client.set_options(port=port.valor)
        return client

    @staticmethod
    def crear_cliente_personal():
        """
        Metodo generico para crear una conexion con el webservice SGA - personal
        Ejem datos de estudiantes,docente,usuario
        :return: cliente de conexion tipo suds.client.Client
        """
        from app.configuracion.models import DetalleParametrizacion
        url = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                    codigo='sgaws_url_personal').first()
        location = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                         codigo='sgaws_location_personal').first()
        port = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                     codigo='sgaws_port_personal').first()
        user = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS', codigo='sgaws_usuario').first()
        passwd = DetalleParametrizacion.objects.filter(parametrizacion__codigo='SGA_WS',
                                                       codigo='sgaws_password').first()
        client = Client(url=url.valor, username=user.valor, password=passwd.valor, location=location.valor)
        client.set_options(port=port.valor)
        return client

    @staticmethod
    def es_estudiante_matriculado(cedula):
        """
        MetodO para saber si un estudiantes esta o no matriculado actualmente
        :param cedula: Cedula del estudiantes
        :return: boolean esta o no matriculado
        """
        if cedula:
            try:
                client = WebServiceSga.crear_cliente_academica()
                data = client.service.sgaws_is_matriculado(cedula)
                data = json.loads(data)
                if data is True:
                    return True
            except Exception as e:
                print('error en obtener el estudiantes webservice', e)
        return False

    @staticmethod
    def get_carreras_estudiante(cedula):
        """
        Metodo para obtener todas las carreras en las que ha estado historicamente el estudiantes
        :param cedula: cedula del estudiantes
        :return: Array de objetos app.academica.Carrera, del estudiantes
        """
        from app.curricular.models import Carrera
        if cedula:
            try:
                client = WebServiceSga.crear_cliente_academica()
                data = client.service.sgaws_carreras_estudiante_siaaf(cedula)
                data = json.loads(data)
                if data['estado'] == '200':
                    lista_ids = [dato['codigo_unl'] for dato in data['data']]
                    return Carrera.objects.filter(id__in=lista_ids).all()
                else:
                    print('error en obtener carreras desde el webservice, o no tiene carreras')
                    return []
            except Exception as e:
                print('error en obtener carreras webservice', e)
        return []

    @staticmethod
    def get_carreras_matriculadas_estudiante(cedula):
        """
        Metodo para obtener la lista de carreras que se estan cursando actualmente,
        desde el webservice sga
        :param cedula: cedula del estudiantes
        :return: Array de objetos Carrera en las que se encuentra matriculado en periodo actual
        """
        from app.curricular.models import Carrera
        try:
            client = WebServiceSga.crear_cliente_academica()
            data = client.service.sgaws_carreras_actuales_estudiante(cedula)
            data = json.loads(data)
            if data['estado'] == '200':
                lista_ids = [dato['codigo_unl'] for dato in data['data']]
                return Carrera.objects.filter(id__in=lista_ids).all()
            else:
                print('error en obtener carreras desde el webservice, o no tiene carreras')
                return []
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return []

    @staticmethod
    def get_carreras_ofertadas_sga():
        """
        Metodo para obtener la lista de carreras que se estan ofertando actualmente,
        desde el webservice sga
        :return: Array de objetos app.academica.Carrera
        """
        from app.curricular.models import Carrera
        try:
            client = WebServiceSga.crear_cliente_academica()
            data = client.service.sgaws_carreras_actuales()
            data = json.loads(data)
            if data['estado'] == '200':
                lista_ids = [dato['codigo_unl'] for dato in data['data']]
                return Carrera.objects.filter(id__in=lista_ids).all()
            else:
                print('error en obtener carreras desde el webservice')
                return []
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return []

    @staticmethod
    def get_estudiante(cedula):
        """
        Metodo para obtener la informacion personal del estudiantes
        desde el webservice sga, los datos de catalogo items, llegan con los
        codigos correspondientes en el siaaf.
        :param cedula: cedula del estudiantes
        :return: None si no existe, o json con datos basicos del estudiantes
        """
        try:
            client = WebServiceSga.crear_cliente_personal()
            data = client.service.sgaws_datos_estudiante_siaaf(cedula, 'token')
            data = json.loads(data)
            if data['estado'] == '200':
                return data
            else:
                return None
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return None

    @staticmethod
    def get_matriculas_carrera_estudiante(cedula, carrera_id):
        """
        Metodo para obtener todas las matriculas, que tiene el estudiantes
        en los estados aprobada, reprobada, matriculada
        :param cedula: cedula del estudiantes
        :param carrera_id: id (del siaaf) de la carrera
        :return: None si no existe, o json con datos basicos del estudiantes
        """
        try:
            client = WebServiceSga.crear_cliente_academica()
            data = client.service.sgaws_matriculas_carrera(cedula, carrera_id)
            data = json.loads(data)
            if data['estado'] == '200':
                return data
            else:
                return None
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return None

    @staticmethod
    def get_oferta_academica(oferta_id):
        """
        Metodo para obtener el detalle de la oferta indicada,
        nombre, fecha_inicio_clases, fecha_fin_clases
        :param oferta_id: id de la oferta en el sga
        :return: None si no existe, o json con datos de la oferta
        """
        try:
            client = WebServiceSga.crear_cliente_academica()
            data = client.service.sgaws_oferta_academica(oferta_id)
            data = json.loads(data)
            if data['estado'] == '200':
                return data
            else:
                return None
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return None

    @staticmethod
    def get_sgaws_datos_usuario_koha(cedula):
        """
        Metodo para obtener la lista de carreras que se estan cursando actualmente,
        desde el webservice sga
        :param cedula: cedula del estudiantes
        :return: Array de objetos Carrera en las que se encuentra matriculado en periodo actual
        """
        try:
            client = WebServiceSga.crear_cliente_academica()
            data = client.service.sgaws_datos_usuario_koha(cedula)
            return json.loads(data)
        except Exception as e:
            print('error en obtener carreras webservice', e)
            return []