from django import forms
from django.forms import formset_factory
from .models import Libro, Autor, Categoria, Editorial, Boleta, Usuario

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'stock', 'imagen', 'precio', 'id_categoria', 'id_editorial']
    
    widgets = {
            'imagen': forms.ClearableFileInput(attrs={'accept': 'imagenes/*'}),
        }

    id_categoria = forms.ModelChoiceField(queryset=Categoria.objects.all())
    id_editorial = forms.ModelChoiceField(queryset=Editorial.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_categoria'].label_from_instance = lambda obj: obj.nombre
        self.fields['id_editorial'].label_from_instance = lambda obj: obj.nombre


class AutorForm(forms.ModelForm):
    anyo = forms.IntegerField()

    class Meta:
        model = Autor
        fields = ['nombre']

AutorFormSet = formset_factory(AutorForm, extra=1)


class BoletaForm(forms.ModelForm):
    class Meta:
        model = Boleta
        fields = ['nombre_comprador', 'monto_total']


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['correo', 'nombre', 'telefono']  # Aquí puedes incluir los campos que desees editar del modelo Usuario

class CambiarContrasenaForm(forms.Form):
    contrasena_actual = forms.CharField(widget=forms.PasswordInput, label='Contraseña Actual')
    nueva_contrasena = forms.CharField(widget=forms.PasswordInput, label='Nueva Contraseña')
    confirmar_nueva_contrasena = forms.CharField(widget=forms.PasswordInput, label='Confirmar Nueva Contraseña')


