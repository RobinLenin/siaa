from django import forms

from .models import Actividad
from .models import Indicador
from .models import MetaAnual
from .models import ObjetivoEstrategico
from .models import ObjetivoOperativo
from .models import PlanEstrategico
from .models import PlanOperativo
from .models import Presupuesto
from .models import Resultado
from .models import Verificacion


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = (
        'nombre', 'codigo', 'indicador', 'meta_especifica', 'inicio', 'fin', 'peso_fijo', 'peso', 'meta_anual')


class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ('nombre', 'porcentaje', 'medible', 'meta_nombre', 'meta_valor', 'presupuesto', 'resultado')


class MetaAnualForm(forms.ModelForm):

    class Meta:
        model = MetaAnual
        fields = ('nombre', 'periodo', 'indicador', 'valor')


class ObjetivoEstrategicoForm(forms.ModelForm):
    class Meta:
        model = ObjetivoEstrategico
        fields = ('nombre', 'codigo', 'eje_estrategico', 'plan_estrategico')


class ObjetivoOperativoForm(forms.ModelForm):
    class Meta:
        model = ObjetivoOperativo
        fields = ('nombre', 'codigo', 'objetivo_estrategico')


class PlanEstrategicoForm(forms.ModelForm):
    class Meta:
        model = PlanEstrategico
        fields = ('nombre', 'activo', 'periodos')


class PlanOperativoForm(forms.ModelForm):
    class Meta:
        model = PlanOperativo
        fields = ('plan_estrategico', 'periodo')


class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ('tipo', 'destino', 'valor', 'actividad')
        labels = {
            'tipo': 'Tipo de presupuesto',
            'destino': 'Destino  del presupuesto',
            'valor': 'Valor',
        }
        help_texts = {
            'valor': 'Monto del presupuesto',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'destino': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'valor': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'actividad': forms.HiddenInput()
        }


class ResultadoForm(forms.ModelForm):
    class Meta:
        model = Resultado
        fields = ('nombre', 'codigo', 'objetivo_operativo', 'responsables')


class VerificacionForm(forms.ModelForm):
    class Meta:
        model = Verificacion
        fields = ('nombre', 'actividad_termino', 'actividad', 'documento')
