from django import forms

from app.organico.models import UAA


class UAAForm(forms.ModelForm):
    class Meta:
        model = UAA
        fields = '__all__'
        exclude = ('estructura_organizacional', 'localizacion')
        widgets = dict(
            estructura_organica=forms.Select(attrs={'class': 'form-control'}),
            campus=forms.Select(attrs={'class': 'form-control'}),
            tipo_uaa=forms.Select(attrs={'class': 'form-control'}),
            nombre=forms.TextInput(attrs={'class': 'form-control'}),
            extension=forms.TextInput(attrs={'class': 'form-control'}),
            telefono=forms.TextInput(attrs={'class': 'form-control'}),
            correo=forms.EmailInput(attrs={'class': 'form-control'}),
            siglas=forms.TextInput(attrs={'class': 'form-control'}),
            codigo=forms.TextInput(attrs={'class': 'form-control'}),
            uaa= forms.HiddenInput()
        )
