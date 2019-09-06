from django import forms

from app.configuracion.models import DetallePlanificacion
from app.core.models import Persona, CatalogoItem
from app.organico.models import UAA
from app.seguridad.models import Usuario
from app.talento_humano.models import ActividadEsencial, Conocimiento, Destreza, Puesto, AsignacionPuesto, \
    TrayectoriaLaboralExterna, EvaluacionDesempenio, Funcionario, \
    UAAPuesto, RegistroVacaciones, AusentismoFuncionario, GrupoOcupacional, RegimenLaboral, CompensacionDias, \
    FormacionAcademica, DeclaracionBienes, InformacionBancaria, Capacitacion


#################################
# Inicio de Refactorizar
#################################

class ActividadEsencialForm(forms.ModelForm):
    class Meta:
        model = ActividadEsencial
        fields = ('descripcion',)


class BusquedaForm(forms.Form):
    criterio = forms.CharField(label='', max_length=200,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por...'}))


class ConocimientoForm(forms.ModelForm):
    class Meta:
        model = Conocimiento
        fields = ('descripcion',)


class DestrezaForm(forms.ModelForm):
    class Meta:
        model = Destreza
        fields = ('descripcion',)


class PuestoForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = Puesto
        fields = '__all__'
        widgets = dict(ambito_ejecucion=forms.Select(attrs={'class': 'form-control required'}),
                       anio_clasificacion_puesto=forms.Select(attrs={'class': 'form-control required'}),
                       area_conocimiento=forms.Textarea(attrs={'class': 'form-control'}),
                       denominacion=forms.TextInput(attrs={'class': 'form-control required'}),
                       denominacion_ministerio_finanzas=forms.TextInput(attrs={'class': 'form-control'}),
                       descripcion=forms.Textarea(attrs={'class': 'form-control'}),
                       especificidad_experiencia=forms.Textarea(attrs={'class': 'form-control'}),
                       grupo_ocupacional=forms.Select(attrs={'class': 'form-control select2 required'}),
                       horas_dedicacion=forms.NumberInput(attrs={'class': 'form-control'}),
                       interfaz=forms.Textarea(attrs={'class': 'form-control'}),
                       mision=forms.Textarea(attrs={'class': 'form-control'}),
                       nivel_instruccion=forms.Select(attrs={'class': 'form-control required'}),
                       observaciones=forms.Textarea(attrs={'class': 'form-control'}),
                       rol_puesto=forms.Select(attrs={'class': 'form-control required'}),
                       tiempo_experiencia=forms.NumberInput(attrs={'class': 'form-control'}),
                       )


class PersonaForm(forms.ModelForm):
    correo_electronico_institucional = forms.EmailField()

    class Meta:
        model = Persona
        fields = '__all__'


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['correo_electronico_institucional', ]


class AgregarUsuarioForm(forms.Form):
    numero_documento = forms.CharField(label='', max_length=200,
                                       widget=forms.TextInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Número de documento'}))


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'


class AsignacionDePuestoForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = AsignacionPuesto
        fields = ('uaa_puesto', 'funcionario', 'codigo', 'fecha_inicio', 'fecha_fin', 'fecha_reconocimiento',
                  'tipo_relacion_laboral',
                  'partida_presupuestaria', 'partida_individual', 'partida_individual_th', 'ingreso_concurso',
                  'factura')
        widgets = dict(funcionario=forms.Select(attrs={'class': 'form-control'}),
                       codigo=forms.TextInput(attrs={'class': 'form-control'}),
                       factura=forms.NumberInput(attrs={'class': 'form-control'}),
                       fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       fecha_reconocimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       ingreso_concurso=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
                       encargado=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
                       # puesto=forms.Select(attrs={'class': 'form-control'}),
                       partida_presupuestaria=forms.TextInput(attrs={'class': 'form-control'}),
                       partida_individual=forms.TextInput(attrs={'class': 'form-control'}),
                       partida_individual_th=forms.TextInput(attrs={'class': 'form-control'}),
                       tipo_relacion_laboral=forms.Select(attrs={'class': 'form-control'}),
                       uaa_puesto=forms.Select(attrs={'class': 'form-control'}),
                       )


class AsignacionDePuestoEditarForm(forms.ModelForm):
    class Meta:
        model = AsignacionPuesto
        fields = ('codigo', 'fecha_inicio', 'fecha_fin', 'fecha_reconocimiento', 'tipo_relacion_laboral',
                  'partida_presupuestaria', 'partida_individual', 'partida_individual_th', 'ingreso_concurso',
                  'encargado', 'factura','observacion')
        widgets = dict(codigo=forms.TextInput(attrs={'class': 'form-control'}),
                       fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       fecha_reconocimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
                       ingreso_concurso=forms.CheckboxInput(attrs={'class': 'form-control'}),
                       factura=forms.NumberInput(attrs={'class': 'form-control'}),
                       encargado=forms.CheckboxInput(attrs={'class': 'form-control'}),
                       partida_presupuestaria=forms.TextInput(attrs={'class': 'form-control'}),
                       partida_individual=forms.TextInput(attrs={'class': 'form-control'}),
                       partida_individual_th=forms.TextInput(attrs={'class': 'form-control'}),
                       tipo_relacion_laboral=forms.Select(attrs={'class': 'form-control'}),
                       observacion=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 400}),
                       )


class AsignacionDePuestoFuncionarioForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = AsignacionPuesto
        fields = ('uaa_puesto', 'codigo', 'fecha_inicio', 'fecha_fin', 'fecha_reconocimiento', 'tipo_relacion_laboral',
                  'partida_presupuestaria', 'partida_individual', 'partida_individual_th', 'ingreso_concurso',
                  'encargado', 'factura')
        widgets = dict(
            codigo=forms.TextInput(attrs={'class': 'form-control'}),
            fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            factura=forms.NumberInput(attrs={'class': 'form-control'}),
            fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            fecha_reconocimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            ingreso_concurso=forms.CheckboxInput(attrs={'class': 'form-control'}),
            encargado=forms.CheckboxInput(attrs={'class': 'form-control'}),
            partida_presupuestaria=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual_th=forms.TextInput(attrs={'class': 'form-control'}),
            tipo_relacion_laboral=forms.Select(attrs={'class': 'form-control'}),
            uaa_puesto=forms.Select(attrs={'class': 'form-control select2'}),
            # puesto=forms.Select(attrs={'class': 'form-control'}),
        )


class AsignacionPuestoUAAPuestoForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = AsignacionPuesto
        fields = ('funcionario', 'codigo', 'fecha_inicio', 'fecha_fin', 'fecha_reconocimiento', 'tipo_relacion_laboral',
                  'partida_presupuestaria', 'partida_individual', 'partida_individual_th', 'ingreso_concurso',
                  'encargado','observacion')
        widgets = dict(
            codigo=forms.TextInput(attrs={'class': 'form-control'}),
            fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            fecha_reconocimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            ingreso_concurso=forms.CheckboxInput(attrs={'class': 'form-control'}),
            encargado=forms.CheckboxInput(attrs={'class': 'form-control'}),
            partida_presupuestaria=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual_th=forms.TextInput(attrs={'class': 'form-control'}),
            tipo_relacion_laboral=forms.Select(attrs={'class': 'form-control'}),
            funcionario=forms.Select(attrs={'class': 'form-control'}),
            observacion=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 400}),
            # puesto=forms.Select(attrs={'class': 'form-control'}),
        )


class AsignacionPuestoUAAPuestoPuroForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = AsignacionPuesto
        fields = ('codigo', 'fecha_inicio', 'fecha_fin', 'fecha_reconocimiento', 'tipo_relacion_laboral',
                  'partida_presupuestaria', 'partida_individual', 'partida_individual_th', 'ingreso_concurso',
                  'encargado','observacion')
        widgets = dict(
            codigo=forms.TextInput(attrs={'class': 'form-control'}),
            fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),
            fecha_reconocimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}),

            ingreso_concurso=forms.CheckboxInput(attrs={'class': 'form-control'}),
            encargado=forms.CheckboxInput(attrs={'class': 'form-control'}),
            partida_presupuestaria=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual=forms.TextInput(attrs={'class': 'form-control'}),
            partida_individual_th=forms.TextInput(attrs={'class': 'form-control'}),
            tipo_relacion_laboral=forms.Select(attrs={'class': 'form-control'}),
            observacion=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 400}),
        )


class AsignacionDePuestoTerminacionForm(forms.ModelForm):
    # def __init__(self, grupo_ocupacional, *args,**kwargs):
    #     super (PuestoForm,self ).__init__(*args,**kwargs) # populates the post
    # self.fields['grupo_ocupacional'].queryset = grupo_ocupacional

    class Meta:
        model = AsignacionPuesto
        fields = ('observacion', 'tipo_terminacion', 'fecha_termino')
        widgets = dict(tipo_terminacion=forms.Select(attrs={'class': 'form-control','required':True}),
                       observacion=forms.Textarea(attrs={'class': 'form-control'}),
                       fecha_termino=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control','required':True}),
                       )


class AsignacionDePuestoRenovacionForm(forms.ModelForm):
    class Meta:
        model = AsignacionPuesto
        fields = ('fecha_inicio', 'fecha_fin', 'observacion')
        widgets = dict(
            observacion=forms.Textarea(attrs={'class': 'form-control'}),
            fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}),
            fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}),
        )


class CrearFuncionarioUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # exclude =('persona', 'usuario', )
        fields = ('correo_electronico_institucional', 'persona')
        widgets = dict(correo_electronico_institucional=forms.TextInput(attrs={'class': 'form-control'}),
                       # persona=forms.Select(attrs={'class': 'form-control autocompletar'}))
                       persona=forms.Select(attrs={'class': 'form-control'}))


class UAAPuestoForm(forms.ModelForm):
    class Meta:
        model = UAAPuesto
        fields = ('puesto',)
        widgets = dict(puesto=forms.Select(attrs={'class': 'form-control select2 required'}))


class DetallePlanificacionForm(forms.ModelForm):
    """
    Formulario que permite la creación de un detalle de planificación utilizado especialmente
    para periods de vacación por ejemplo
    """

    class Meta:
        model = DetallePlanificacion
        fields = ('nombre', 'descripcion', 'fecha_desde', 'fecha_hasta')
        widgets = dict(nombre=forms.TextInput(attrs={'class': 'form-control'}),
                       descripcion=forms.TextInput(attrs={'class': 'form-control'}),
                       fecha_desde=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}),
                       fecha_hasta=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}))


class RegistroVacacionesForm(forms.ModelForm):
    """
    Registro de vacaciones manualmente
    """

    detalle_planificacion = forms.ModelChoiceField(
        queryset=DetallePlanificacion.objects.filter(planificacion__codigo__istartswith='VACACIONES_',
                                                     activo=True).distinct(),
        empty_label="--No pertenece a un periodo de vacaciones--",
        required=False,
        label='Periodo vacaciones'
    )

    class Meta:
        model = RegistroVacaciones

        fields = ('fecha_inicio', 'fecha_fin', 'observacion', 'detalle_planificacion')
        widgets = dict(fecha_inicio=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}),
                       fecha_fin=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker form-control'}),
                       observacion=forms.Textarea(attrs={'class': 'form-control'}),
                       detalle_planificacion=forms.Select()
                       )


class CompensacionDiasForm(forms.ModelForm):
    """
    Formulario para ingresar la compensación de días
    """

    class Meta:
        model = CompensacionDias
        fields = ('dias', 'horas', 'minutos', 'observacion')
        widgets = dict(
            dias=forms.NumberInput(attrs={'class': 'form-control'}),
            horas=forms.NumberInput(attrs={'class': 'form-control'}),
            minutos=forms.NumberInput(attrs={'class': 'form-control'}),
            observacion=forms.Textarea(attrs={'class': 'form-control'})
        )


class AusentismoFuncionarioForm(forms.ModelForm):
    """
    Registro de ausentismos
    """

    class Meta:
        model = AusentismoFuncionario
        fields = ('tipo_permiso', 'fecha_inicio', 'fecha_fin', 'dias', 'horas', 'minutos', 'observacion')
        widgets = dict(
            tipo_permiso=forms.Select(attrs={'class': 'form-control',
                                             'onchange': 'permiso()', 'onload': 'permiso()'}),
            fecha_inicio=forms.DateTimeInput(format='%Y-%m-%d',
                                             attrs={'class': 'datepicker form-control', 'onchange': 'calculaDias()'}),
            fecha_fin=forms.DateInput(format='%Y-%m-%d',
                                      attrs={'class': 'datepicker form-control', 'onchange': 'calculaDias()'}),
            dias=forms.NumberInput(attrs={'class': 'form-control'}),
            horas=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 7}),
            minutos=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 59}),
            observacion=forms.Textarea(attrs={'class': 'form-control'})
        )


class ReporteForm(forms.Form):
    choice_tipo_relacion_laboral = [(trl.id, trl.nombre) for trl in
                                    CatalogoItem.get_catalogos_items('TIPO_RELACION_LABORAL')]
    choice_tipo_relacion_laboral.append(('', 'Todo'))

    choice_tipo_terminacion = [(trl.id, trl.nombre) for trl in
                               CatalogoItem.get_catalogos_items('TIPO_TERMINACION')]

    choice_tipo_terminacion.append(('', 'Todo'))

    choice_grupo_ocupacional = [(go.id, go.__str__()) for go in GrupoOcupacional.objects.all().order_by('nombre')]
    choice_grupo_ocupacional.append(('', 'Todo'))

    choice_regimen_laboral = [(rl.id, rl.nombre) for rl in RegimenLaboral.objects.all()]
    choice_regimen_laboral.append(('', 'Todo'))

    choice_puesto = [(rl.id, rl.denominacion) for rl in Puesto.objects.all()]
    choice_puesto.append(('', 'Todo'))

    choice_uaa = [(rl.id, rl.__str__()) for rl in UAA.objects.all()]
    choice_uaa.append(('', 'Todo'))

    criterio = forms.CharField(required=False, max_length=255)
    activo = forms.NullBooleanField(required=False, )
    encargado = forms.NullBooleanField(required=False)
    fecha_inicio_desde = forms.DateField(required=False,
                                         widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    fecha_inicio_hasta = forms.DateField(required=False,
                                         widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    fecha_fin_desde = forms.DateField(required=False,
                                      widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    fecha_fin_hasta = forms.DateField(required=False,
                                      widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    fecha_termino_desde = forms.DateField(required=False,
                                          widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    fecha_termino_hasta = forms.DateField(required=False,
                                          widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'datepicker'}))
    grupo_ocupacional = forms.ChoiceField(choices=choice_grupo_ocupacional,
                                          initial='',
                                          required=False, widget=forms.Select(attrs={'class': 'select2'}))
    ingreso_concurso = forms.NullBooleanField(required=False)
    puesto = forms.ChoiceField(choices=choice_puesto,
                               initial='',
                               required=False, )
    regimen_laboral = forms.ChoiceField(choices=choice_regimen_laboral,
                                        initial='',
                                        required=False, )
    responsable_uaa = forms.NullBooleanField(required=False)
    termino = forms.NullBooleanField(required=False)
    tipo_terminacion = forms.ChoiceField(choices=choice_tipo_terminacion,
                                         initial='',
                                         required=False, widget=forms.Select(attrs={'class': 'select2'}))
    tipo_relacion_laboral = forms.ChoiceField(choices=choice_tipo_relacion_laboral,
                                              initial='',
                                              required=False, )
    uaa = forms.ChoiceField(choices=choice_uaa,
                            initial='',
                            required=False, widget=forms.Select(attrs={'class': 'select2'}))
    uaa_hijas = forms.NullBooleanField(required=False)
    vigente = forms.NullBooleanField(required=False)

    choice_sexo = [(trl.id, trl.nombre) for trl in CatalogoItem.get_catalogos_items('TIPO_SEXO')]
    choice_sexo.append(('', 'Todo'))
    sexo = forms.ChoiceField(choices=choice_sexo,
                             initial='',
                             required=False)

    choice_tipo_etnia = [(trl.id, trl.nombre) for trl in CatalogoItem.get_catalogos_items('TIPO_ETNIA')]
    choice_tipo_etnia.append(('', 'Todo'))
    tipo_etnia = forms.ChoiceField(choices=choice_tipo_etnia,
                                   initial='',
                                   required=False)

    choice_tipo_discapacidad = [(trl.id, trl.nombre) for trl in CatalogoItem.get_catalogos_items('TIPO_DISCAPACIDAD')]
    choice_tipo_discapacidad.append(('ninguna', 'Ninguna'))
    choice_tipo_discapacidad.append(('', 'Todas'))
    tipo_discapacidad = forms.ChoiceField(choices=choice_tipo_discapacidad,
                                          initial='',
                                          required=False)

    choice_estado_civil = [(trl.id, trl.nombre) for trl in CatalogoItem.get_catalogos_items('ESTADO_CIVIL')]
    choice_estado_civil.append(('', 'Todas'))
    estado_civil = forms.ChoiceField(choices=choice_estado_civil,
                                     initial='',
                                     required=False)


class ReporteVacacionesPeriodoForm(forms.Form):
    choice_detalles = [(rl.id, rl.nombre) for rl in
                       DetallePlanificacion.objects.filter(planificacion__codigo__istartswith='VACACIONES_').all()]
    choice_detalles.append(('', '--Seleccione--'))
    detalle_planificacion = forms.ChoiceField(choices=choice_detalles, initial='', label='Periodo', required=False,
                                              widget=forms.Select(attrs={'class': 'required'}))


class ReporteVacacionesPendientesForm(forms.Form):
    dias = forms.IntegerField(required=False, min_value=0, max_value=1000, label=u'Mayor o  igual (días)',
                              widget=forms.NumberInput(attrs={'value': 0}))
    activo = forms.NullBooleanField(required=False, label=u'Funcionario activo', initial=2)


class ReporteGeneral(forms.Form):
    choice_tipo_relacion_laboral = [(trl.id, trl.nombre) for trl in
                                    CatalogoItem.get_catalogos_items('TIPO_RELACION_LABORAL')]
    choice_tipo_relacion_laboral.append(('', 'Todo'))
    choice_regimen_laboral = [(rl.id, rl.nombre) for rl in RegimenLaboral.objects.all()]
    choice_regimen_laboral.append(('', 'Todo'))
    regimen_laboral = forms.ChoiceField(choices=choice_regimen_laboral, initial='', required=False)
    tipo_relacion_laboral = forms.ChoiceField(choices=choice_tipo_relacion_laboral, initial='', required=False)
    edad = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'value': 0}), label=u'Edad', min_value=0,
                              max_value=100)


#################################
# Fin de Refactorizar
#################################

class CapacitacionForm(forms.ModelForm):
    class Meta:
        model = Capacitacion
        exclude = ('expediente', 'validado',)
        labels = {
            'evento': 'Evento',
            'tipo_evento': 'Tipo de evento',
            'auspiciante': 'Auspiciante',
            'horas': 'Horas',
            'tipo_certificacion': 'Tipo de certificación',
            'certificado_por': 'Certificado por',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'pais': 'País',
        }
        help_texts = {
            'auspiciante': 'Representa el nombre de la Institución que auspicia el evento de capacitación. En caso de no existir ingrese NINGUNO en este campo.',
            'certificado_por': 'Representa el nombre de la Institución que certifica el evento de capacitación',
            'fecha_inicio': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'fecha_fin': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = {
            'evento': forms.TextInput(attrs={'class': 'form-control required'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-control required select2'}),
            'auspiciante': forms.TextInput(attrs={'class': 'form-control required'}),
            'horas': forms.NumberInput(
                attrs={'class': 'form-control required digits', 'min': '0', 'max': '1000', 'step': '1'}),
            'tipo_certificacion': forms.Select(attrs={'class': 'form-control required'}),
            'certificado_por': forms.TextInput(attrs={'class': 'form-control required'}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
            'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
            'pais': forms.Select(attrs={'class': 'form-control select2 required'}),
        }


class DeclaracionBienesForm(forms.ModelForm):
    class Meta:
        model = DeclaracionBienes
        exclude = ('expediente',)
        labels = {
            'numero_notaria': 'Número de notaría',
            'fecha_declaracion': 'Fecha de la declaración',
            'lugar_notaria': 'Lugar de la notaría'
        }
        help_texts = {
            'numero_notaria': 'Por favor ingrese el número de la Notaría en texto (ejm: PRIMERA). Si realizó su declaración en la '
                              'página de la Contraloría General del Estado ingresar EN LINEA',
            'fecha_declaracion': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = {
            'numero_notaria': forms.TextInput(attrs={'class': 'form-control required'}),
            'fecha_declaracion': forms.DateInput(format='%Y-%m-%d',
                                                 attrs={'class': 'form-control datepicker required'}),
            'lugar_notaria': forms.Select(attrs={'class': 'form-control required select2'}),
        }


class EvaluacionDesempenioForm(forms.ModelForm):
    class Meta:
        model = EvaluacionDesempenio
        fields = '__all__'
        exclude = ('funcionario',)
        labels = {
            'asignacion_puesto': 'Puesto a evaluar',
            'fecha_evaluacion_inicio': 'Fecha de inicio de evaluación',
            'fecha_evaluacion_fin': 'Fecha de fin de evaluación',
            'puntaje': 'Puntaje',
            'calificacion': 'Calificación'
        }
        help_texts = {
            'fecha_evaluacion_inicio': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'fecha_evaluacion_fin': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = {'fecha_evaluacion_fin': forms.DateInput(
            format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
            'fecha_evaluacion_inicio': forms.DateInput(
                format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
            'puntaje': forms.NumberInput(
                attrs={'class': 'form-control required digits', 'min': '0', 'max': '100', 'step': '1'}),
            'asignacion_puesto': forms.Select(attrs={'class': 'form-control required'}, choices=[]),
            'calificacion': forms.Select(attrs={'class': 'form-control required'})
        }

    def __init__(self, *args, **kwargs):
        funcionario_id = kwargs.pop('funcionario_id', None)
        super(EvaluacionDesempenioForm, self).__init__(*args, **kwargs)
        if funcionario_id:
            self.fields['asignacion_puesto'].queryset = AsignacionPuesto.objects.filter(funcionario_id=funcionario_id)


class FormacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = FormacionAcademica
        fields = ('area_conocimiento', 'pais', 'tipo_periodo_estudio', 'periodos_aprobados')
        labels = {
            'area_conocimiento': 'Área de conocimiento',
            'pais': 'País',
            'tipo_periodo_estudio': 'Tipo de periódo de estudio',
            'periodos_aprobados': 'Número de periódos aprobados'
        }
        help_texts = {
            'tipo_periodo_estudio': 'Indica la modalida de estudio por semestres o años',
            'periodos_aprobados': 'Indica el número de periodos de estudio aprobados '
        }
        widgets = {'area_conocimiento': forms.TextInput(attrs={'class': 'form-control required'}),
                   'pais': forms.Select(attrs={'class': 'form-control select2 required'}),
                   'tipo_periodo_estudio': forms.Select(attrs={'class': 'form-control required'}, choices=()),
                   'periodos_aprobados': forms.NumberInput(
                       attrs={'class': 'form-control required digits', 'min': '0', 'max': '100', 'step': '1'})
                   }


class InformacionBancariaForm(forms.ModelForm):
    class Meta:
        model = InformacionBancaria
        exclude = ('expediente', 'codigo',)
        labels = {
            'institucion_financiera': 'Institución financiera',
            'tipo_cuenta': 'Tipo de cuenta',
            'numero_cuenta': 'Número de cuenta'
        }
        widgets = {
            'institucion_financiera': forms.Select(attrs={'class': 'form-control select2 required'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-control required'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control required', 'minlength': 5}),
        }


class TrayectoriaLaboralExternaForm(forms.ModelForm):
    class Meta:
        model = TrayectoriaLaboralExterna
        fields = '__all__'
        exclude = ('funcionario',)
        labels = {
            'institucion': 'Institución',
            'unidad_administrativa': 'Unidad administrativa',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'motivo_ingreso': 'Motivo de ingreso',
            'motivo_salida': 'Motivo de salida',
            'puesto': 'Puesto',
            'tipo_institucion': 'Tipo de institución'
        }
        help_texts = {
            'unidad_administrativa': 'Registra la unidad administrativa donde el servidor desempeño sus funciones',
            'fecha_inicio': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'fecha_fin': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = {'institucion': forms.TextInput(attrs={'class': 'form-control required'}),
                   'unidad_administrativa': forms.TextInput(attrs={'class': 'form-control required'}),
                   'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
                   'fecha_inicio': forms.DateInput(format='%Y-%m-%d',
                                                   attrs={'class': 'form-control datepicker required'}),
                   'motivo_ingreso': forms.Select(attrs={'class': 'form-control required select2'}),
                   'motivo_salida': forms.Select(attrs={'class': 'form-control required select2'}),
                   'puesto': forms.TextInput(attrs={'class': 'form-control required'}),
                   'tipo_institucion': forms.Select(attrs={'class': 'form-control required'})
                   }
