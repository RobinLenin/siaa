from django import forms
from django.db.models import Q

from .models import Asignatura
from .models import AsignaturaNivel
from .models import AutoridadFacultad
from .models import AutoridadProgramaEstudio
from .models import Facultad
from .models import Nivel
from .models import OfertaAcademica
from .models import OfertaAsignaturaNivel
from .models import OfertaPensum
from .models import Pensum
from .models import PensumComplementario
from .models import PensumGrupo
from .models import PeriodoAcademico
from .models import PeriodoMatricula
from .models import ProgramaEstudio
from .models import Titulo

# Bloque: Curricular
class AsignaturaNivelForm(forms.ModelForm):
    class Meta:
        model = AsignaturaNivel
        fields = '__all__'


class AsignaturaNivelPrerrequisitoForm(forms.ModelForm):
    class Meta:
        model = AsignaturaNivel
        fields = ('id', 'prerrequisitos')


class AsignaturaNivelCorrequisitoForm(forms.ModelForm):
    class Meta:
        model = AsignaturaNivel
        fields = ('id', 'correquisitos')


class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = '__all__'


class AutoridadFacultadForm(forms.ModelForm):
    class Meta:
        model = AutoridadFacultad
        fields = ('tipo', 'facultad', 'activo', 'abreviatura', 'fecha_inicio', 'fecha_fin', 'funcionario', 'referencia_ingreso', 'referencia_salida')

    def clean_activo(self):
        activo = self.cleaned_data.get('activo')
        tipo = self.cleaned_data.get('tipo')
        facultad_id = self.cleaned_data.get('facultad')
        qset = Q(tipo=tipo, facultad_id=facultad_id, activo=activo)
        if self.instance.id:
            qset = Q(qset, ~Q(id=self.instance.id))
        if activo and AutoridadFacultad.objects.filter(qset).exists():
            raise forms.ValidationError("Solamente puede haber 1 usuario activo de %s" % tipo)
        return activo

    def clean_fecha_inicio(self):
        inicio = self.cleaned_data.get('fecha_inicio')
        tipo = self.cleaned_data['tipo']
        qset = Q(Q(tipo=tipo), Q(facultad_id=self.cleaned_data['facultad']),
                 Q(Q(fecha_inicio__lte=inicio) & Q(fecha_fin__gte=inicio) |
                   Q(fecha_fin__isnull=True) & Q(fecha_inicio__lte=inicio)))
        if self.instance.id:
            qset = Q(qset, ~Q(id=self.instance.id))

        entre = AutoridadFacultad.objects.filter(qset)
        if entre.exists():
            autoridad = entre.first()
            raise forms.ValidationError("Conflicto con : %s, (desde %s %s)" % (
                autoridad.funcionario, autoridad.fecha_inicio,
                "hasta %s" % autoridad.fecha_fin if autoridad.fecha_fin else ''))
        return inicio

    def clean_fecha_fin(self):
        inicio = self.cleaned_data.get('fecha_inicio')
        tipo = self.cleaned_data['tipo']
        fin = self.cleaned_data.get('fecha_fin')
        qset = Q(tipo=tipo, facultad_id=self.cleaned_data['facultad'])
        if self.instance.id:
            qset = Q(qset, ~Q(id=self.instance.id))
        if fin:
            qset = Q(qset, Q(
                (Q(fecha_inicio__lte=fin) & Q(fecha_fin__gte=fin)) |
                Q(fecha_fin__isnull=True) & Q(fecha_inicio__lte=fin)))
        elif inicio:
            qset = Q(qset, Q(fecha_inicio__gte=inicio) |
                     Q(fecha_fin__gte=inicio) |
                     Q(fecha_fin__isnull=True))
        entre = AutoridadFacultad.objects.filter(qset)
        if entre.exists():
            autoridad = entre.first()
            raise forms.ValidationError("Conflicto con : %s, (desde %s %s)" % (
                autoridad.funcionario, autoridad.fecha_inicio,
                "hasta %s" % autoridad.fecha_fin if autoridad.fecha_fin else ''))
        return fin

    def clean_funcionario(self):
        activo = self.cleaned_data.get('activo')
        facultad_id = self.cleaned_data.get('facultad')
        funcionario_id = self.cleaned_data.get('funcionario')
        if activo:
            qset = Q(facultad_id=facultad_id, activo=activo, funcionario_id=funcionario_id)
            if self.instance.id:
                qset = Q(qset, ~Q(id=self.instance.id))
            if AutoridadFacultad.objects.filter(qset).exists():
                raise forms.ValidationError(
                    "El funcionario solo puede estar activo en un solo cargo en su %s" % Facultad._meta.verbose_name.title())
        return funcionario_id

    def clean_referencia_salida(self):
        referencia_salida = self.cleaned_data.get('referencia_salida')
        fin = self.cleaned_data.get('fecha_fin')
        if fin and (referencia_salida is None or referencia_salida==""):
            raise forms.ValidationError(
                "La fecha de fin existe (%s), por ende ingrese la referencia de salida" % fin)
        return  referencia_salida

class AutoridadProgramaEstudioForm(forms.ModelForm):
    class Meta:
        model = AutoridadProgramaEstudio
        fields = ('tipo', 'programa_estudio', 'activo', 'abreviatura', 'fecha_inicio', 'fecha_fin', 'funcionario', 'referencia_ingreso', 'referencia_salida')

    def clean_activo(self):
        activo = self.cleaned_data.get('activo')
        if activo:
            tipo = self.cleaned_data.get('tipo')
            programa_estudio_id = self.cleaned_data.get('programa_estudio')
            qset = Q(tipo=tipo, programa_estudio_id=programa_estudio_id, activo=activo)
            if self.instance.id:
                qset = Q(qset, ~Q(id=self.instance.id))
            if AutoridadProgramaEstudio.objects.filter(qset).count() >= AutoridadProgramaEstudio.NUMERO_ACTIVOS.get(
                    tipo):
                raise forms.ValidationError("Solamente puede haber %s usuario activo de %s" % (
                    AutoridadProgramaEstudio.NUMERO_ACTIVOS.get(tipo), tipo))
        return activo

    def clean_fecha_inicio(self):
        inicio = self.cleaned_data.get('fecha_inicio')
        tipo = self.cleaned_data['tipo']
        qset = Q(Q(tipo=tipo), Q(programa_estudio_id=self.cleaned_data['programa_estudio']),
                 Q(Q(fecha_inicio__lte=inicio) & Q(fecha_fin__gte=inicio) |
                   Q(fecha_fin__isnull=True) & Q(fecha_inicio__lte=inicio)))
        if self.instance.id:
            qset = Q(qset, ~Q(id=self.instance.id))

        entre = AutoridadProgramaEstudio.objects.filter(qset)
        if entre.count() >= AutoridadProgramaEstudio.NUMERO_ACTIVOS.get(tipo):
            autoridad = entre.all()
            nombres = ", ".join([str(a.funcionario) for a in autoridad])
            raise forms.ValidationError("Conflicto con : %s" % (nombres))
        return inicio

    def clean_fecha_fin(self):
        inicio = self.cleaned_data.get('fecha_inicio')
        tipo = self.cleaned_data['tipo']
        fin = self.cleaned_data.get('fecha_fin')
        qset = Q(tipo=tipo, programa_estudio_id=self.cleaned_data['programa_estudio'])
        if self.instance.id:
            qset = Q(qset, ~Q(id=self.instance.id))
        if fin:
            qset = Q(qset, Q(
                (Q(fecha_inicio__lte=fin) & Q(fecha_fin__gte=fin)) |
                Q(fecha_fin__isnull=True) & Q(fecha_inicio__lte=fin)))
        elif inicio:
            qset = Q(qset, Q(fecha_inicio__gte=inicio) |
                     Q(fecha_fin__gte=inicio) |
                     Q(fecha_fin__isnull=True))
        entre = AutoridadProgramaEstudio.objects.filter(qset)
        if entre.count() >= AutoridadProgramaEstudio.NUMERO_ACTIVOS.get(tipo):
            autoridad = entre.first()
            raise forms.ValidationError("Conflicto con : %s, (desde %s %s)" % (
                autoridad.funcionario, autoridad.fecha_inicio,
                "hasta %s" % autoridad.fecha_fin if autoridad.fecha_fin else ''))
        return fin

    def clean_funcionario(self):
        activo = self.cleaned_data.get('activo')
        programa_estudio_id = self.cleaned_data.get('programa_estudio')
        funcionario_id = self.cleaned_data.get('funcionario')
        if activo:
            qset = Q(programa_estudio_id=programa_estudio_id, activo=activo, funcionario_id=funcionario_id)
            if self.instance.id:
                qset = Q(qset, ~Q(id=self.instance.id))
            if AutoridadProgramaEstudio.objects.filter(qset).exists():
                raise forms.ValidationError(
                    "El funcionario solo puede estar activo en un solo cargo en su %s" % Facultad._meta.verbose_name.title())
        return funcionario_id

    def clean_referencia_salida(self):
        referencia_salida = self.cleaned_data.get('referencia_salida')
        fin = self.cleaned_data.get('fecha_fin')
        if fin and (referencia_salida is None or referencia_salida==""):
            raise forms.ValidationError(
                "La fecha de fin existe (%s), por ende ingrese la referencia de salida" % fin)
        return  referencia_salida


class FacultadForm(forms.ModelForm):
    class Meta:
        model = Facultad
        fields = '__all__'


class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = '__all__'


class PensumForm(forms.ModelForm):
    class Meta:
        model = Pensum
        fields = '__all__'
        exclude = ('pensums_grupo',)


class PensumPensumGrupoForm(forms.ModelForm):
    class Meta:
        model = Pensum
        fields = ('id', 'pensums_grupo')


class PensumGrupoForm(forms.ModelForm):
    class Meta:
        model = PensumGrupo
        fields = '__all__'


class PensumComplementarioForm(forms.ModelForm):
    class Meta:
        model = PensumComplementario
        fields = '__all__'


class ProgramaEstudioForm(forms.ModelForm):
    class Meta:
        model = ProgramaEstudio
        fields = '__all__'


class TituloForm(forms.ModelForm):
    class Meta:
        model = Titulo
        fields = '__all__'

# Bloque: Periódo Académico
class OfertaAcademicaForm(forms.ModelForm):
    class Meta:
        model = OfertaAcademica
        fields = '__all__'


class OfertaAsignaturaNivelForm(forms.ModelForm):
    class Meta:
        model = OfertaAsignaturaNivel
        fields = '__all__'


class OfertaPensumForm(forms.ModelForm):
    class Meta:
        model = OfertaPensum
        fields = '__all__'

class PeriodoAcademicoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcademico
        fields = '__all__'

class PeriodoMariculaForm(forms.ModelForm):
    class Meta:
        model = PeriodoMatricula
        fields = '__all__'