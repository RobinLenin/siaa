from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q
from app.core.models import Persona

class Paciente(models.Model):
    """
    Clase que representa a la mascota que le hacen atender
    """
    HEMBRA = 'H'
    MACHO = 'M'
    SEXO_CHOICES = (
        (HEMBRA, 'Macho'),
        (MACHO, 'Hembra'))
    numero_historia_clinica = models.CharField(max_length=50,unique=True)
    fecha_registro_historia_clinica = models.DateField(blank=True, null=True, help_text='(aaaa-MM-dd)')
    nombre = models.CharField(max_length=50)
    persona=models.ForeignKey(Persona,verbose_name="Propietario", on_delete=models.CASCADE)
    especie = models.CharField(max_length=50, null=True, blank=True)
    edad = models.PositiveSmallIntegerField(verbose_name="Edad (meses)")
    tamanio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tamaño (cm.)",
                                  validators= [MinValueValidator(0.00)])
    procedencia = models.CharField(max_length=50, null=True, blank=True)
    raza = models.CharField(max_length=50, null =True, blank=True)
    sexo = models.CharField(max_length=2, choices=SEXO_CHOICES, default=MACHO)
    color = models.CharField(max_length=50, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (kg.)",
                               validators= [MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['persona','nombre']
		
    def __str__(self):
        return self.nombre

    
    @staticmethod
    def buscar(criterio):
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            print(p_criterio)
            for i in p_criterio:
                print("qset", qset)
                qset = qset & (
                    Q(persona__primer_apellido__icontains=i) | Q(persona__segundo_apellido__icontains=i) | 
                    Q(persona__primer_nombre__icontains=i) | Q(persona__segundo_nombre__icontains=i) | 
                    Q(persona__numero_de_documento__icontains=i))
                print(qset)
        return Paciente.objects.filter(qset).distinct()


class Consulta(models.Model):
    """
    Clase que representa la consulta del paciente(mascota)
    """
    motivo_consulta = models.CharField(max_length=400)
    medico_responsable = models.CharField(max_length=50)
    estudiante_interno = models.CharField(max_length=50)
    paciente=models.ForeignKey(Paciente,verbose_name="Paciente", on_delete=models.CASCADE)
    esta_finalizada = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['paciente','motivo_consulta']
		
    def __str__(self):
        return self.motivo_consulta


class Anamnesis(models.Model):
    """
    Clase que representa el anamnesis del paciente(mascota)
    """
    TRANQUILO = 'T'
    NERVIOSO = 'N'
    AGRESIVO = 'A'
    CONDUCTA_CHOICES = (
        (TRANQUILO, 'Tranquilo'),
        (NERVIOSO, 'Nervioso'),
        (AGRESIVO,'Agresivo'))
    
    #Para las hembras
    ultimo_celo = models.DateField(blank=True, null=True, help_text='(aaaa-MM-dd)')
    secreciones_vulvares = models.BooleanField(default=False, blank=True)
    fecha_ultimo_parto = models.DateField(blank=True, null=True, help_text='(aaaa-MM-dd)')
    complicaciones_parto = models.CharField(max_length=200, blank=True)

    #Para los machos
    numero_montas = models.PositiveSmallIntegerField(null=True, blank=True)  
    secreciones_prepuciales = models.BooleanField(default=False, blank=True)
    
    #Para ambos
    ultima_desparasitacion = models.DateField(blank=True, null=True, help_text='(aaaa-MM-dd)')
    vacunas = models.BooleanField(default=False, blank=True)
    enfermedades_anteriores = models.CharField(max_length=250, blank=True)
    tratamiento_anterior = models.CharField(max_length=250, blank=True)
    alimentacion = models.CharField(max_length=200, blank=True)
    conducta = models.CharField(max_length=2, choices=CONDUCTA_CHOICES, default=TRANQUILO)
    consulta = models.OneToOneField(Consulta, related_name='consulta_anamnesis', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['consulta','ultima_desparasitacion']
    
    def __str__(self):
        return self.conducta

class ExamenClinico(models.Model):
    """
    Clase que representa el examen clínico del paciente(mascota)
    """
    CONJUNTIVA = 'C'
    ORAL = 'O'
    GENITAL = 'G'
    MUCOSA_CHOICES = (
        (CONJUNTIVA, 'Conjuntiva'),
        (ORAL, 'Oral'),
        (GENITAL,'Genital'))
    frecuencia_cardiaca = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Frecuencia Cardíaca (Lt/min.)", validators=[MinValueValidator(0.00)])
    frecuencia_respiratoria = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Frecuencia Respiratoria (r/min.)", validators=[MinValueValidator(0.00)])
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Temperatura (°C)", validators=[MinValueValidator(0.00)])
    linfonodulos = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Linfonodulos", validators=[MinValueValidator(0.00)])
    tllc = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tiempo de llenado capilar", validators=[MinValueValidator(0.00)])
    pulso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pulso", validators=[MinValueValidator(0.00)])
    mucosa = models.CharField(max_length=50)
    tipo_mucosa = models.CharField(max_length=2, choices=MUCOSA_CHOICES, default=CONJUNTIVA)
    consulta = models.OneToOneField(Consulta, related_name='consulta_examen_clinico', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['consulta','frecuencia_cardiaca']
    
    def __str__(self):
        return self.frecuencia_cardiaca

class DatosPresuntivos(models.Model):
    """
    Clase que representa los datos que se registran en cada tipo de sistemas para el examen clinico 
    """
    TEGUMENTARIO = 'T'
    MUSCULO_ESQUELETICO = 'ME'
    RESPIRATORIO = 'R'
    CARDIOVASCULAR = 'C'
    DIGESTIVO = 'D'
    NERVIOSO = 'N'
    GENITOURINARIO = 'G'
    AUDITIVO_Y_OCULAR = 'AO'
    SISTEMAS_CHOICES = (
        (TEGUMENTARIO, 'Sistema Tegumentario'),
        (MUSCULO_ESQUELETICO, 'Sistema Músculo-Esquelético'),
        (RESPIRATORIO,'Sistema Respiratorio'),
        (CARDIOVASCULAR,'Sistema Cardiovascular'),
        (DIGESTIVO,'Sistema Digestivo'),
        (NERVIOSO,'Sistema Nervioso'),
        (GENITOURINARIO,'Sistema Genitourinario'),
        (AUDITIVO_Y_OCULAR,'Sistema Auditivo y Ocular'))

    tipo_sistema = models.CharField(max_length=3, choices=SISTEMAS_CHOICES, default=TEGUMENTARIO)
    dato_presuntivo = models.CharField(max_length=400,null=True, blank=True)
    examen_clinico = models.ForeignKey(ExamenClinico, related_name='examen_clinico_datos_presuntivos', verbose_name="Examen clinico", on_delete=models.CASCADE)

    class Meta:
        ordering = ['examen_clinico','dato_presuntivo']
    
    def __str__(self):
        return self.dato_presuntivo

    def dividir(self):
        return self.dato_presuntivo.split('\r\n')

class ListaMaestra(models.Model):
    """
    Clase que representa los datos subjetivos de la consulta a traves de la unificación datos presuntivos
    """
    dato_subjetivo = models.CharField(max_length=400,null=True, blank=True)
    consulta = models.OneToOneField(Consulta, related_name='consulta_lista_maestra', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['consulta','dato_subjetivo']
    
    def __str__(self):
        return self.dato_subjetivo

class DiagnosticoDiferencial(models.Model):
    """
    Clase que representa los datos objetivos de la lista maestra
    """
    dato_objetivo = models.CharField(max_length=400,null=True, blank=True)
    lista_maestra = models.OneToOneField(ListaMaestra, related_name='lista_maestra_d_diferencial', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lista_maestra','dato_objetivo']
    
    def __str__(self):
        return self.dato_objetivo

class DiagnosticoPresuntivo(models.Model):
    """
    Clase que representa los datos del diagnostico presuntivo del diagnostico diferencial
    """
    dato_dg_presuntivo = models.CharField(max_length=400,null=True, blank=True)
    diagnostico_diferencial = models.OneToOneField(DiagnosticoDiferencial, related_name='diagnostico_diferencial_d_presuntivo', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['diagnostico_diferencial','dato_dg_presuntivo']
    
    def __str__(self):
        return self.dato_dg_presuntivo

class ExamenesComplementarios(models.Model):
    """
    Clase que representa los examenes complementarios requeridos para el paciente
    """
    cuadro_hematico = models.BooleanField(default=False, blank=True)
    electrolitos = models.BooleanField(default=False, blank=True)
    antibiograma = models.BooleanField(default=False, blank=True)
    quimica_sanguinea = models.BooleanField(default=False, blank=True)
    emo = models.BooleanField(default=False, blank=True)
    citologia = models.BooleanField(default=False, blank=True)
    coprologico = models.BooleanField(default=False, blank=True)
    gases_sanguineos = models.BooleanField(default=False, blank=True)
    cultivos = models.BooleanField(default=False, blank=True)
    radiologia = models.BooleanField(default=False, blank=True)
    electrocardiografia = models.BooleanField(default=False, blank=True)
    ecografia = models.BooleanField(default=False, blank=True)
    otro_examen = models.CharField(max_length=250, blank=True)
    resultados_significativos = models.CharField(max_length=400)
    consulta = models.OneToOneField(Consulta, related_name='consulta_examenes_complementarios', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['consulta','resultados_significativos']
    
    def __str__(self):
        return self.resultados_significativos

class DiagnosticoFinal(models.Model):
    """
    Clase que representa el diagnostico final del paciente (mascota) por consulta
    """
    dato_dg_final = models.CharField(max_length=400)
    consulta = models.OneToOneField(Consulta, related_name='consulta_diagnostico_final', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['consulta','dato_dg_final']
    
    def __str__(self):
        return self.dato_dg_final

class Tratamiento(models.Model):
    """
    Clase que representa el tratamiento del paciente por diagnostico final
    """
    quirurgico = models.CharField(max_length=400)
    farmacologico = models.CharField(max_length=400)
    diagnostico_final = models.OneToOneField(DiagnosticoFinal, related_name='diagnostico_final_tratamiento', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['diagnostico_final','quirurgico']
    
    def __str__(self):
        return self.quirurgico

class InscripcionTratamiento(models.Model):
    """
    Clase que representa la inscripción que contiene el tratamiento
    """
    producto = models.CharField(max_length=80)
    presentacion = models.CharField(max_length=50)
    dosis_base = models.CharField(max_length=30)
    via = models.CharField(max_length=20)
    dosificacion = models.CharField(max_length=20,null=True, blank=True)
    frecuencia = models.CharField(max_length=20,null=True, blank=True)
    duracion = models.CharField(max_length=20,null=True, blank=True)
    tratamiento = models.ForeignKey(Tratamiento, related_name='tratamiento_inscripcion', verbose_name="Tratamiento", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tratamiento','producto']
    
    def __str__(self):
        return self.producto
   
