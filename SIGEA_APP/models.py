import datetime
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser # Se importan las clases BaseUserManager y AbstractBaseUser de django para manejar la creación de usuarios
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

class Departamentos(models.Model):
    iddepartamento = models.AutoField(db_column='IDDEPARTAMENTO', primary_key=True)
    divisiondepartamento = models.CharField(db_column='DIVISIONDEPARTAMENTO', max_length=255)
    responsabledepartamento = models.ForeignKey('Usuario', models.SET_NULL, db_column='RESPONSABLEDEPARTAMENTO', null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'departamentos'
        
    def __str__(self):
        return self.divisiondepartamento
    
def update_responsable_departamento(sender, instance, **kwargs):
    Departamentos.objects.filter(responsabledepartamento=instance).update(responsabledepartamento=None)


class Evaluacion(models.Model):
    idevaluacion = models.AutoField(db_column='IDEVALUACION', primary_key=True)
    idplandes = models.ForeignKey('Plandesarrollo', on_delete=models.SET_NULL, db_column='IDPLANDES', blank=True, null=True)
    idusuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='IDUSUARIO', blank=True, null=True)  # Puede ser nulo en evaluación de departamento
    tipoevaluacion = models.CharField(db_column='TIPOEVALUACION', max_length=255)
    notaevaluacio = models.DecimalField(db_column='NOTAEVALUACIO', max_digits=10, decimal_places=0)
    comentarioevaluacio = models.CharField(db_column='COMENTARIOEVALUACIO', max_length=2000)
    fechaevaluacion = models.DateTimeField(db_column='FECHAEVALUACION')

    class Meta:
        managed = True
        db_table = 'evaluacion'


class Plandesarrollo(models.Model):
    idplandes = models.AutoField(db_column='IDPLANDES', primary_key=True)
    idevaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, db_column='IDEVALUACION')
    nombreplandes = models.CharField(db_column='NOMBREPLANDES', max_length=255)
    objetivosplandes = models.CharField(db_column='OBJETIVOSPLANDES', max_length=255)
    alcancesplandes = models.CharField(db_column='ALCANCESPLANDES', max_length=255)
    descripcionplandes = models.CharField(db_column='DESCRIPCIONPLANDES', max_length=2000)
    instruccionesplandes = models.CharField(db_column='INSTRUCCIONESPLANDES', max_length=2000)
    duracionmesesplandes = models.IntegerField(db_column='DURACIONMESESPLANDES')
    fortalezas = models.TextField(db_column='FORTALEZAS', blank=True, null=True)
    debilidades = models.TextField(db_column='DEBILIDADES', blank=True, null=True)
    oportunidades = models.TextField(db_column='OPORTUNIDADES', blank=True, null=True)
    amenazas = models.TextField(db_column='AMENAZAS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'plandesarrollo'


class Servicios(models.Model):
    idservicio = models.AutoField(db_column='IDSERVICIO', primary_key=True)
    iddepartamento = models.ForeignKey(Departamentos, models.DO_NOTHING, db_column='IDDEPARTAMENTO')
    nombreservicio = models.CharField(db_column='NOMBRESERVICIO', max_length=255)
    descripcionservicio = models.CharField(db_column='DESCRIPCIONSERVICIO', max_length=2000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'servicios'
        
    def __str__(self):
        return self.nombreservicio 


class TipoUsuario(models.Model):
    idtipousuario = models.AutoField(db_column='IDTIPOUSUARIO', primary_key=True)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255)

    class Meta:
        managed = True
        db_table = 'tipousuario'

    def __str__(self):
        return self.descripcion

class invitados_actividad(models.Model):
    idusuario = models.ForeignKey('Usuario', on_delete=models.CASCADE , db_column='IDUSUARIO')
    idactividad = models.ForeignKey('Actividades', on_delete=models.CASCADE, db_column='IDACTIVIDAD')

    class Meta:
        managed = True
        db_table = 'invitados_actividad'
        unique_together = (('idactividad', 'idusuario'), ('idactividad', 'idusuario'),)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, tipousuario=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        
        if tipousuario is not None:
            try:
                TipoUsuarioModel = self.model._meta.get_field('tipousuario').remote_field.model
                tipousuario = TipoUsuarioModel.objects.get(pk=tipousuario)
            except TipoUsuarioModel.DoesNotExist:
                raise ValueError('TipoUsuario no válido')

        user = self.model(email=email, tipousuario=tipousuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, tipousuario=1, **extra_fields):
        return self.create_user(email, password, tipousuario=tipousuario, **extra_fields)

class Usuario(AbstractBaseUser):
    idusuario = models.AutoField(db_column='IDUSUARIO', primary_key=True)
    idservicio = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='IDSERVICIO', blank=True, null=True)
    tipousuario = models.ForeignKey(TipoUsuario, models.DO_NOTHING, db_column='IDTIPOUSUARIO')  # Actualizado
    nombre = models.CharField(db_column='NOMBRE', max_length=255)
    apellido = models.CharField(db_column='APELLIDO', max_length=255)
    dui = models.CharField(db_column='DUI', max_length=10, unique=True)
    telefono = models.CharField(db_column='TELEFONO', max_length=9, unique=True)
    salario = models.DecimalField(db_column='SALARIO', max_digits=10, decimal_places=0)
    email = models.EmailField(db_column='EMAIL', max_length=255, unique=True)
    password = models.CharField(db_column='PASSWORD', max_length=255)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    objects = UsuarioManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'dui', 'telefono', 'salario', 'tipousuario']

    class Meta:
        managed = True
        db_table = 'usuario'

    def __str__(self):
        return self.email
    
class EstadoActividad(models.Model):
    idestado = models.AutoField(db_column='IDESTADO', primary_key=True)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255)

    class Meta:
        managed = True
        db_table = 'estadoactividad'

    def __str__(self):
        return self.descripcion
    
class Actividades(models.Model):
    idactividad = models.AutoField(db_column='IDACTIVIDAD', primary_key=True)
    idusuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, db_column='IDUSUARIO')
    idrecordatorio = models.ForeignKey('Recordatorio', on_delete=models.DO_NOTHING, db_column='IDRECORDATORIO', blank=True, null=True)
    estadoactividad = models.ForeignKey(EstadoActividad, models.DO_NOTHING, db_column='IDESTADO', default=1)  # Actualizado
    tipoactividad = models.CharField(db_column='TIPOACTIVIDAD', max_length=255)
    nombreactividad = models.CharField(db_column='NOMBREACTIVIDAD', max_length=255)
    fechaactividad = models.DateTimeField(db_column='FECHAACTIVIDAD')
    fechafin = models.DateTimeField(db_column='FECHAFIN')
    descripcionactividad = models.CharField(db_column='DESCRIPCIONACTIVIDAD', max_length=2000, blank=True, null=True)
    docanexoactividad = models.FileField(db_column='DOCANEXOACTIVIDAD', upload_to='archivoreunion/', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'actividades'

class Recordatorio(models.Model):
    idrecordatorio = models.AutoField(db_column='IDRECORDATORIO', primary_key=True)  # Field name made lowercase.
    idactividad = models.ForeignKey(Actividades, db_column='IDACTIVIDAD', on_delete=models.CASCADE)  # Field name made lowercase.
    nombrerecordatorio = models.CharField(db_column='NOMBRERECORDATORIO', max_length=255)  # Field name made lowercase.
    descripcionrecordatorio = models.CharField(db_column='DESCRIPCIONRECORDATORIO', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    fecharecordatorio = models.DateTimeField(db_column='FECHARECORDATORIO')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'recordatorio'

class TipoCliente(models.Model):
    idtipoCliente = models.AutoField(db_column='IDTIPO', primary_key=True)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255)

    class Meta:
        managed = True
        db_table = 'tipocliente'

    def __str__(self):
        return self.descripcion
    
class Cliente(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    idTipo = models.ForeignKey(TipoCliente, db_column='IDTIPOCLIENTE', on_delete=models.CASCADE)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    correo = models.CharField(db_column='CORREO', max_length=100)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=9, unique=True)

    class Meta:
        managed = True
        db_table = 'cliente'

class RegistroAsistencia(models.Model):
    idregistro = models.AutoField(db_column='ID', primary_key=True)
    empleado = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='registros_asistencia')
    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    horas_trabajadas = models.DurationField(default=datetime.timedelta)

    def calcular_horas_trabajadas(self):
        if self.hora_salida:
            entrada = datetime.datetime.combine(self.fecha, self.hora_entrada)
            salida = datetime.datetime.combine(self.fecha, self.hora_salida)
            diferencia = salida - entrada
            self.horas_trabajadas = diferencia
        else:
            self.horas_trabajadas = datetime.timedelta()

    def save(self, *args, **kwargs):
        self.calcular_horas_trabajadas()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.empleado} - {self.fecha}'

    class Meta:
        db_table = 'registro_asistencia'
        constraints = [
            models.CheckConstraint(check=models.Q(hora_salida__gte=models.F('hora_entrada')), name='check_hora_entrada_salida'),
            models.UniqueConstraint(fields=['empleado', 'fecha'], name='unique_empleado_fecha')
        ]
        
    @property
    def horas_trabajadas_formateadas(self):
        total_segundos = self.horas_trabajadas.total_seconds()
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return f'{int(horas)} horas, {int(minutos)} minutos'

        
    
#Modelo para la tabla de casos de los usuarios tipo abogado y usuarios cliente
class Caso(models.Model):
    ESTADO_CHOICES = [
        ('Iniciado', 'Iniciado'),
        ('En proceso', 'En Proceso'),
        ('Finalizado', 'Finalizado'),
    ]

    idCaso = models.AutoField(db_column='IDCASO', primary_key=True)  
    nombreCaso = models.CharField(db_column='NOMBRECASO', max_length=255)
    idCliente = models.ForeignKey('Cliente',  db_column='IDCLIENTE', on_delete=models.CASCADE)  
    descripcionCaso = models.CharField(db_column='DESCRIPCIONCASO', max_length=2000) 
    #campo para el estado del caso si esta iniciado, en progreso o finalizado
    estadoCaso = models.CharField(db_column='ESTADOCASO', max_length=255, choices=ESTADO_CHOICES) 
    
    #clase str para retornar el nombre del caso y su estado
    def __str__(self):
        return self.nombreCaso + " - " + self.descripcionCaso + " - " + self.estadoCaso
    class Meta:
        managed = True
        db_table = 'caso'    
