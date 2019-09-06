from django import forms

from app.seguridad.models import GrupoLDAP, Usuario, CuentaCorreo


class CuentaCorreoForm(forms.ModelForm):
    class Meta:
        model = CuentaCorreo
        fields = ('numero_documento', 'email_institucional', 'email_alternativo', 'tipo', 'nombres',
                  'apellidos', 'telefono', 'celular',)


class GrupoLdapForm(forms.ModelForm):
    class Meta:
        model = GrupoLDAP
        fields = ('nombre', 'descripcion',)
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control required'}),
        }

class UsuarioValidarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('correo_electronico_institucional',)
        widgets = dict(correo_electronico_institucional=forms.EmailInput(attrs={'class': 'form-control'}), )
