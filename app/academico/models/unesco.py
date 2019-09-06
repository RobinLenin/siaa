from django.db import models

class CampoAmplio(models.Model):
    codigo = models.CharField(max_length=25, unique=True)
    nombre = models.TextField()

    def __str__(self):
        return self.nombre


class CampoDetallado(models.Model):
    codigo = models.CharField(max_length=25)
    nombre = models.TextField()

    campo_especifico = models.ForeignKey('CampoEspecifico', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + ' - ' + str(self.campo_especifico) + ' - ' + str(self.campo_especifico.campo_amplio)


class CampoEspecifico(models.Model):
    codigo = models.CharField(max_length=25)
    nombre = models.TextField()

    campo_amplio = models.ForeignKey('CampoAmplio', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre