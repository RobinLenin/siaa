# -*- encoding: utf-8 -*-
from app.core.models import *


class Localizacion(models.Model):
    nombre = models.CharField(max_length=140)
