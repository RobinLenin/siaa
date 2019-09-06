from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class PasswordCedulaValidator(object):

    def validate(self, password, user=None):
        if user and user.persona:
            if user.persona.numero_documento == password:
                raise ValidationError(
                    _("La contraseña no debe ser igual al numero de identificacion"),
                    code='password_no_cedula',
                )

    def get_help_text(self):
        return _(
            "Su contraseña no debe ser su numero de identificacion personal."
        )
