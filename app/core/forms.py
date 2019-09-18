from django.forms import ModelForm
from django import forms
from app.core.models import Relacion, CatalogoItem, Direccion, Persona
import re

class DireccionForm(ModelForm):

    class Meta:
        model = Direccion
        fields = ('parroquia_otro', 'tipo_direccion',
                  'calle_principal', 'calle_secundaria', 'numero', 'referencia',
                  'telefono', 'extension', 'celular')
        labels = {
            'tipo_direccion': 'Tipo de dirección',
            'calle_principal': 'Calle principal',
            'calle_secundaria': 'Calle secundaria',
            'numero': 'Número de casa',
            'referencia': 'Referencia',
            'telefono': 'Teléfono',
            'celular': 'Celular',
            'extension': 'Extensión'
        }
        help_texts = {
            'numero': 'Ingrese solo dígitos en el número de casa (ejm: 102102)',
            'extension': 'Ingrese solo dígitos en la extensión (ejm: 128)',
            'telefono': 'Mínimo 9 caracteres en el teléfono (ejm: 072547252)',
            'celular': 'Mínimo 10 caracteres en el celular (ejm: 0912345678)'
        }
        widgets = {
            'tipo_direccion': forms.Select(attrs={'class': 'form-control required'}),
            'calle_principal': forms.TextInput(attrs={'class': 'form-control required'}),
            'calle_secundaria': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'minlength': 9, 'maxlength': 15, 'required': 'true'}),
            'extension': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'minlength': 10, 'maxlength': 15, 'required': 'true'}),
            'parroquia_otro': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_telefono(self):
        """
        Valido el pattern del telefonos
        :return:
        """
        patron = re.compile('^\d{9,15}$')
        data = self.cleaned_data['telefono']
        if patron.match(data) is None:
            raise forms.ValidationError("El telefono debe contener mínimo 9 caracteres y solo digítos (072547252)")
        return data

    def clean_celular(self):
        """
        Valido el pattern del celular
        :return:
        """
        patron = re.compile('^\d{10,15}$')
        data = self.cleaned_data['celular']
        if patron.match(data) is None:
            raise forms.ValidationError("El celular debe contener mínimo 10 caracteres y solo digítos (0912345678)")
        return data

class PersonaBuscarForm(forms.Form):

    criterio = forms.CharField(label='Buscar ', max_length=200)

class PersonaForm(ModelForm):
    class Meta:
        model = Persona
        fields = ('primer_apellido','segundo_apellido','primer_nombre', 'segundo_nombre',
                  'fecha_nacimiento',  'numero_libreta_militar',
                  'discapacidad', 'tipo_discapacidad','numero_carnet_conadis', 'porcentaje_discapacidad',
                  'estado_civil', 'tipo_sangre', 'sexo', 'nacionalidad', 'anios_residencia',
                  'tipo_etnia', 'nacionalidad_indigena', 'correo_electronico', 'correo_electronico_alternativo')
        labels = {
            'primer_apellido': 'Primer apellido',
            'primer_nombre': 'Primer nombre',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'estado_civil': 'Estado civil',
            'sexo': 'Sexo',
            'nacionalidad': 'Nacionalidad',
            'tipo_etnia': 'Tipo de etnia',
            'correo_electronico': 'Correo electrónico',
            'anios_residencia': 'Años de residencia',
            'numero_libreta_militar': 'Número de libreta militar',
            'numero_carnet_conadis': 'Número de carnet del conadis',
            'nacionalidad_indigena': 'Nacional indígena',
            'correo_electronico_alternativo': 'Correo electrónico alternativo'

        }
        help_texts = {
            'fecha_nacimiento': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'anios_residencia': 'Por favor ingrese este dato solo si su Nacionalidad NO es Ecuatoriana',
            'correo_electronico': 'Por favor ingrese su correo electrónico personal'
        }
        widgets = dict(primer_apellido=forms.TextInput(attrs={'class': 'form-control required'}),
                       segundo_apellido=forms.TextInput(attrs={'class': 'form-control'}),
                       primer_nombre=forms.TextInput(attrs={'class': 'form-control required'}),
                       segundo_nombre=forms.TextInput(attrs={'class': 'form-control'}),
                       fecha_nacimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker required'}),
                       numero_libreta_militar=forms.TextInput(attrs={'class': 'form-control'}),
                       discapacidad=forms.CheckboxInput(attrs={'class': 'form-control checkbox',
                                                               'onclick': 'id_numero_carnet_conadis.disabled=!id_discapacidad.checked; '
                                                                          'id_porcentaje_discapacidad.disabled=!id_discapacidad.checked;'
                                                                          'id_tipo_discapacidad.disabled=!id_discapacidad.checked;',
                                                               'onload': 'id_numero_carnet_conadis.disabled=!id_discapacidad.checked; '
                                                                         'id_porcentaje_discapacidad.disabled=!id_discapacidad.checked;'
                                                                         'id_tipo_discapacidad.disabled=!id_discapacidad.checked;'}),
                       tipo_discapacidad=forms.Select(attrs={'class': 'form-control required', 'disabled': 'true'}),
                       numero_carnet_conadis=forms.TextInput(
                           attrs={'class': 'form-control required', 'disabled': 'true'}),
                       porcentaje_discapacidad=forms.TextInput(
                           attrs={'class': 'form-control required', 'disabled': 'true'}),
                       estado_civil=forms.Select(attrs={'class': 'form-control required'}),
                       tipo_sangre=forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
                       sexo=forms.Select(attrs={'class': 'form-control required'}),
                       nacionalidad=forms.Select(attrs={'class': 'form-control select2 required'}),
                       anios_residencia=forms.TextInput(attrs={'class': 'form-control'}),
                       tipo_etnia=forms.Select(attrs={'class': 'form-control required',
                                                         'onchange': 'etnia()', 'onload': 'etnia()'}),
                       nacionalidad_indigena=forms.Select(attrs={'class': 'form-control'}),
                        correo_electronico=forms.TextInput(attrs={'class': 'form-control required email'}),
                       correo_electronico_alternativo=forms.TextInput(attrs={'class': 'form-control email'}))

    def clean_nacionalidad_indigena(self):
        """
        Valida si el tipo de etnia es indigena, el campo nacional indigena es obligatorio
        :return:
        """
        tipo_etnia = self.cleaned_data.get('tipo_etnia','')
        nacionalidad_indigena = self.cleaned_data.get('nacionalidad_indigena','')
        if str(tipo_etnia) == 'Indígena' and nacionalidad_indigena is None:
            raise forms.ValidationError("Campo obligatorio")
        return nacionalidad_indigena

class PersonaFormClienteEditar(ModelForm):
    class Meta:
        model = Persona
        fields = ('primer_apellido','segundo_apellido','primer_nombre', 'segundo_nombre', 'correo_electronico')
        labels = {
            'primer_apellido': 'Primer apellido',
            'primer_nombre': 'Primer nombre',
            'correo_electronico': 'Correo electrónico'
        }
        help_texts = {
            'correo_electronico': 'Por favor ingrese su correo electrónico personal'
        }
        widgets = dict(primer_apellido=forms.TextInput(attrs={'class': 'form-control required'}),
                       segundo_apellido=forms.TextInput(attrs={'class': 'form-control'}),
                       primer_nombre=forms.TextInput(attrs={'class': 'form-control required'}),
                       segundo_nombre=forms.TextInput(attrs={'class': 'form-control'}),
                       correo_electronico=forms.TextInput(attrs={'class': 'form-control required email'}))



class RelacionForm(ModelForm):

    class Meta:
        model = Relacion
        fields =('tipo_relacion', 'tipo_documento', 'numero_documento',
                 'nombres', 'apellidos', 'telefono','celular',
                 'fecha_nacimiento', 'nivel_instruccion', 'contacto', 'nepotismo')
        labels = {
            'tipo_relacion': 'Tipo de relación',
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'nivel_instruccion': 'Nivel de instrucción',
            'nepotismo': 'Trabaja en la misma institución',
            'telefono': 'Teléfono',
            'contacto': 'Es contacto'
        }
        help_texts = {
            'telefono' : 'Mínimo 9 caracteres en el teléfono (ejm: 072547252)',
            'celular': 'Mínimo 10 caracteres en el celular (ejm: 0912345678)',
            'fecha_nacimiento': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = dict(tipo_relacion=forms.Select(attrs={'class': 'form-control required'}),
                       tipo_documento=forms.Select(attrs={'class': 'form-control required'}),
                       numero_documento=forms.TextInput(attrs={'class': 'form-control required'}),
                       nombres=forms.TextInput(attrs={'class': 'form-control required'}),
                       apellidos=forms.TextInput(attrs={'class': 'form-control required'}),
                       telefono=forms.TextInput(attrs={'class': 'form-control','minlength':9,'maxlength':15}),
                       celular=forms.TextInput(attrs={'class': 'form-control','minlength':10,'maxlength':15}),
                       fecha_nacimiento=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control datepicker', 'required': 'true'}),
                       nivel_instruccion=forms.Select(attrs={'class': 'form-control'}),
                       contacto=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
                       nepotismo=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}))

    def clean(self, *args, **kwargs):
        """
        Valido las reestricciones de varios campos
        :param args:
        :param kwargs:
        :return:
        """
        cleaned_data = super().clean()
        tipo_relacion = cleaned_data.get('tipo_relacion', None)
        telefono = cleaned_data.get('telefono', None)
        celular = cleaned_data.get('celular',None)
        contacto = cleaned_data.get('contacto', False)
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento', None)
        nivel_instruccion= cleaned_data.get('nivel_instruccion', None)

        patron_telefono = re.compile('^\d{9,15}$')
        patron_celular = re.compile('^\d{10,15}$')

        # Cuando es contacto, es obligatorio el telefono y celular
        if contacto is True:
            if telefono is None or telefono=='':
                self.add_error('telefono', 'Campo obligatorio')
            if celular is None or celular=='':
                self.add_error('celular', 'Campo obligatorio')

        # Cuando es información de los hijos, es obligatorio la fecha de nacimiento y nivel de instrucción
        if tipo_relacion is not None:
            tipo_relacion = CatalogoItem.objects.get(id=tipo_relacion.id)
            if tipo_relacion.codigo_th == '6':
                if fecha_nacimiento is None or fecha_nacimiento == '':
                    self.add_error('fecha_nacimiento', 'Campo obligatorio')
                if nivel_instruccion is None or nivel_instruccion == '':
                    self.add_error('nivel_instruccion', 'Campo obligatorio')

        # Valido los pattern de telefonos y celulares
        if telefono and patron_telefono.match(telefono) is None:
            self.add_error('telefono', 'El telefono debe contener mínimo 9 caracteres y solo digítos (072547252)')
        if celular and patron_celular.match(celular) is None:
            self.add_error('celular', 'El celular debe contener mínimo 10 caracteres y solo digítos (0912345678)')