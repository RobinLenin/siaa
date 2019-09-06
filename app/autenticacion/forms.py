from django import forms

class EditarContrasenaForm(forms.Form):
    actual_password_verificada = False

    actual_password = forms.CharField(
        label='Contraseña actual',
        min_length=5,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control actual_password',
                                          'required': ''}))

    password = forms.CharField(
        label='Nueva contraseña',
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control password',
                                          'minlength': 8,
                                          'required': ''}))

    password2 = forms.CharField(
        label='Repetir contraseña',
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control password2',
                                          'minlength': 8,
                                          'equalTo': '.password',
                                          'required': ''}))

    def password_verificada(self):
        self.actual_password_verificada = True
        return 0

    def clean_actual_password(self):
        """
        Comprueba que el password actual sea el correcto
        :return:
        """
        actual_password = self.cleaned_data.get('actual_password')
        if not actual_password:
            raise forms.ValidationError("Debe ingresar la contraseña actual.")

        if not self.actual_password_verificada:
            raise forms.ValidationError("La contraseña actual es incorrecta.")
        return actual_password

    def clean_password(self):
        """
        Comprueba que el password actual no sea igual al nuevo password
        :return:
        """
        password = self.cleaned_data.get('password')
        actual_password = self.cleaned_data.get('actual_password')
        if password == actual_password:
            raise forms.ValidationError('La contraseña no debe ser igual a la actual.')
        return password

    def clean_password2(self):
        """
        Comprueba que password y password2 sean iguales
        :return:
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2
