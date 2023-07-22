from django.db import models

# Create your models here.

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=512)
    contrasena = models.CharField(max_length=512)
    nombre = models.CharField(max_length=64)
    telefono = models.CharField(max_length=9)
    last_login = models.DateTimeField(auto_now=True)  # Agregar el campo last_login para controlar fecha de inicio de sesion

    USERNAME_FIELD = 'correo'

    class Meta:
        db_table = "usuario"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = "categoria"

class Boleta(models.Model):
    id_boleta = models.AutoField(primary_key=True)
    nombre_comprador = models.CharField(max_length=64)
    fecha = models.DateField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = "boleta"

class Editorial(models.Model):
    id_editorial = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = "editorial"

class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=1024)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='imagenes/',verbose_name='Imagen',null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    id_editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE)

    def __str__(self):
        fila="Titulo " + self.titulo + "-"+"Descripcion: "+self.descripcion
        return fila

    # esta funcion es para eliminar la imagen
    def delete(self,using=None,keep_parents=False):
        self.imagen.storage.delete(self.imagen.name)
        super().delete()

    class Meta:
        db_table = "libro"

class Autor(models.Model):
    id_autor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = "autor"

class LibroAutor(models.Model):
    id_libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    id_autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    anyo = models.IntegerField()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id_libro', 'id_autor'], name='libro_autor_pk')
        ]
    
    class Meta:
        db_table = "libro_autor"

class DetalleBoleta(models.Model):
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    id_libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    id_boleta = models.ForeignKey(Boleta, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id_libro', 'id_boleta'], name='detalle_boleta_pk')
        ]
    
    class Meta:
        db_table = "detalle_boleta"




