from django import forms
from app.tesoreria.models import CuentaCobrar, Comentario, Abono, TasaInteres, InteresMensual


class CuentaCobrarForm(forms.ModelForm):
    class Meta:
        model = CuentaCobrar
        fields = '__all__'


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = '__all__'


class AbonoForm(forms.ModelForm):
    class Meta:
        model = Abono
        fields = '__all__'

class TasaInteresForm(forms.ModelForm):
    class Meta:
        model = TasaInteres
        fields = '__all__'

class InteresMensualForm(forms.ModelForm):
    class Meta:
        model = InteresMensual
        fields = '__all__'
