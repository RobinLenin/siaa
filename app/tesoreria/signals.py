from django.db.models.signals import post_save
from django.dispatch import receiver

from app.tesoreria.models import Abono


@receiver(post_save, sender=Abono)
def abono_postsave_handler(sender, instance, **kwargs):

    if kwargs["created"]:
        pass
       # instance.cuentacobrar metodo de calcular

