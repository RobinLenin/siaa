from django import forms
from django.forms import ModelForm

from app.cientifica.models import ArticuloRevista, CapituloLibro, Ponencia, Libro


class ArticuloRevistaForm(ModelForm):
    class Meta:
        model = ArticuloRevista
        fields = '__all__'
        exclude = ('produccion_cientifica',)
        labels = {
            'codigo_institucional': 'Código institucional',
            'nombre': 'Nombre',
            'issn': 'Issn',
            'nombre_revista': 'Nombre de revista',
            'fecha_publicacion': 'Fecha de publicación',
            'campo_detallado': 'Campo detallado',
            'observacion': 'Observación',
            'filiacion': 'Filiación'
        }
        help_texts = {
            'codigo_institucional': 'Código designado por la UNL. En caso de no tenerlo dejarlo en blanco',
            'nombre': 'Nombre del artículo',
            'issn': 'Número Internacional Normalizado de Publicaciones Seriadas',
            'nombre_revista': 'Nombre de la Revista donde fue publicado el artículo',
            'campo_detallado': 'Especifica el campo de la CINE de la UNESCO a la cual pertenece el artículo',
            'fecha_publicacion': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)'
        }
        widgets = dict(
            codigo_institucional=forms.TextInput(attrs={'class': 'form-control'}),
            nombre=forms.TextInput(attrs={'class': 'form-control required'}),
            issn=forms.TextInput(attrs={'class': 'form-control required'}),
            nombre_revista=forms.TextInput(attrs={'class': 'form-control required'}),
            observacion=forms.Textarea(attrs={'class': 'form-control'}),
            base_datos_indexada=forms.Select(attrs={'class': 'form-control'}),
            fecha_publicacion=forms.DateInput(format='%Y-%m-%d',
                                                 attrs={'class': 'form-control datepicker required'}),
            campo_detallado=forms.Select(attrs={'class': 'form-control select2 required'}),
            aceptado=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            publicado=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            filiacion=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            url=forms.TextInput(attrs={'class': 'form-control'}))


class CapituloLibroForm(ModelForm):
    class Meta:
        model = CapituloLibro
        fields = '__all__'
        exclude = ('produccion_cientifica',)
        labels = {
            'nombre': 'Nombre',
            'nombre_libro': 'Nombre de libro',
            'isbn': 'Isbn',
            'editor': 'Editor',
            'fecha_publicacion': 'Fecha de publicación',
            'campo_detallado': 'Campo detallado',
            'codigo_institucional': 'Código institucional',
            'observacion': 'Observación',
        }
        help_texts = {
            'fecha_publicacion': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'campo_detallado': 'Especifica el campo de la CINE de la UNESCO a la cual pertenece el artículo',
            'codigo_institucional': 'Código designado por la UNL. En caso de no tenerlo dejarlo en blanco'
        }
        widgets = dict(
            codigo_institucional=forms.TextInput(attrs={'class': 'form-control'}),
            nombre=forms.TextInput(attrs={'class': 'form-control required'}),
            nombre_libro=forms.TextInput(attrs={'class': 'form-control required'}),
            editor=forms.TextInput(attrs={'class': 'form-control required'}),
            isbn=forms.TextInput(attrs={'class': 'form-control required'}),
            fecha_publicacion=forms.DateInput(format='%Y-%m-%d',
                                                 attrs={'class': 'form-control datepicker required'}),
            observacion=forms.Textarea(attrs={'class': 'form-control'}),
            campo_detallado=forms.Select(attrs={'class': 'form-control select2 required'}),
            url=forms.TextInput(attrs={'class': 'form-control'}))


class LibroForm(ModelForm):
    class Meta:
        model = Libro
        fields = '__all__'
        exclude = ('produccion_cientifica',)
        labels = {
            'nombre': 'Nombre',
            'isbn': 'Isbn',
            'fecha_publicacion': 'Fecha de publicación',
            'campo_detallado': 'Campo detallado',
            'codigo_institucional': 'Código institucional',
            'observacion': 'Observación',
            'filiacion': 'Filiación',
            'revisado_pares': 'Revisado por pares'
        }
        help_texts = {
            'isbn': 'Número Estándar Internacional de Libros',
            'fecha_publicacion': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'campo_detallado': 'Especifica el campo de la CINE de la UNESCO a la cual pertenece el artículo',
            'codigo_institucional': 'Código designado por la UNL. En caso de no tenerlo dejarlo en blanco'
        }
        widgets = dict(
            codigo_institucional=forms.TextInput(attrs={'class': 'form-control'}),
            nombre=forms.TextInput(attrs={'class': 'form-control required'}),
            isbn=forms.TextInput(attrs={'class': 'form-control required'}),
            fecha_publicacion=forms.DateInput(format='%Y-%m-%d',
                                                 attrs={'class': 'form-control datepicker required'}),
            observacion=forms.Textarea(attrs={'class': 'form-control'}),
            campo_detallado=forms.Select(attrs={'class': 'form-control select2 required'}),
            revisado_pares=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            filiacion=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            url=forms.TextInput(attrs={'class': 'form-control'}))


class PonenciaForm(ModelForm):
    class Meta:
        model = Ponencia
        fields = '__all__'
        exclude = ('produccion_cientifica',)
        labels = {
            'nombre': 'Nombre',
            'nombre_evento': 'Nombre del evento',
            'fecha_publicacion': 'Fecha de publicación',
            'pais': 'País',
            'ciudad': 'Ciudad',
            'campo_detallado': 'Campo detallado',
            'codigo_institucional': 'Código institucional',
            'observacion': 'Observación',
            'filiacion': 'Filiación',
        }
        help_texts = {
            'fecha_publicacion': 'Ingrese la fecha en el formato AAAA-MM-DD (ejm: 2000-01-01)',
            'campo_detallado': 'Especifica el campo de la CINE de la UNESCO a la cual pertenece el artículo',
            'codigo_institucional': 'Código designado por la UNL. En caso de no tenerlo dejarlo en blanco'
        }
        widgets = dict(
            codigo_institucional=forms.TextInput(attrs={'class': 'form-control'}),
            nombre=forms.TextInput(attrs={'class': 'form-control required'}),
            nombre_evento=forms.TextInput(attrs={'class': 'form-control required'}),
            ciudad=forms.TextInput(attrs={'class': 'form-control required'}),
            observacion=forms.Textarea(attrs={'class': 'form-control'}),
            pais=forms.Select(attrs={'class': 'form-control required select2'}),
            fecha_publicacion=forms.DateInput(format='%Y-%m-%d',
                                                 attrs={'class': 'form-control datepicker required'}),
            campo_detallado=forms.Select(attrs={'class': 'form-control select2 required'}),
            filiacion=forms.CheckboxInput(attrs={'class': 'form-control checkbox'}),
            url=forms.TextInput(attrs={'class': 'form-control'}))
