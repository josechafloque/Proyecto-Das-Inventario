from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db import connection
from .models import Usuario, Categoria

# Create your views here.

def inicio(request):
    return render(request, 'app/inicio.html')

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']
        
        try:
            usuario = Usuario.objects.get(correo=correo)
            
            if usuario.contrasena == contrasena:
                # Autenticación exitosa, iniciar sesión
                login(request, usuario)
                return redirect('pagina_principal', id_usuario=usuario.id_usuario)  # Redirecciona a la página de inicio con el id_usuario
            else:
                error = 'Credenciales inválidas'
                return render(request, 'app/login.html', {'error': error})
        
        except Usuario.DoesNotExist:
            error = 'Credenciales inválidas'
            return render(request, 'app/login.html', {'error': error})
    else:
        return render(request, 'app/login.html')



def signup(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']
        nombre = request.POST['nombre']
        telefono = request.POST['telefono']
        
        # Crear un nuevo usuario
        usuario = Usuario(correo=correo, contrasena=contrasena, nombre=nombre, telefono=telefono)
        usuario.save()
        
    return render(request, 'app/signup.html')

def logout_view(request):
    return render(request, 'app/inicio.html')


def pagina_principal(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    return render(request, 'app/pagina_principal.html', {'usuario': usuario})

# Categorias

def categoria(request, id_usuario):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)

    # Obtener todas las categorías del usuario utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_categoria, nombre FROM categoria WHERE id_usuario_id = %s", [id_usuario])
        categorias = cursor.fetchall()

    # Crear una lista de diccionarios con los resultados de la consulta
    categorias_list = [{'id_categoria': categoria[0], 'nombre': categoria[1]} for categoria in categorias]

    return render(request, 'app/categoria.html', {'usuario': usuario, 'categorias': categorias_list})

def crear_categoria(request, id_usuario):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        
        # Obtener el usuario
        usuario = Usuario.objects.get(id_usuario=id_usuario)
        
        # Insertar la nueva categoría utilizando una consulta SQL nativa
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO categoria (nombre, id_usuario_id) VALUES (%s, %s)", [nombre, usuario.id_usuario])
        
        # Redireccionar a la página de categorías
        return redirect('categoria', id_usuario=id_usuario)
    
    return render(request, 'app/categoria.html')

def actualizar_categoria(request, id_usuario, id_categoria):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        
        # Obtener el usuario
        usuario = Usuario.objects.get(id_usuario=id_usuario)
        
        # Actualizar la categoría utilizando una consulta SQL nativa
        with connection.cursor() as cursor:
            cursor.execute("UPDATE categoria SET nombre = %s WHERE id_categoria = %s AND id_usuario_id = %s", [nombre, id_categoria, usuario.id_usuario])
        
        # Redireccionar a la página de categorías
        return redirect('categoria', id_usuario=id_usuario)
    
    return render(request, 'app/categoria.html')

def eliminar_categoria(request, id_usuario, id_categoria):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    
    # Eliminar la categoría utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM categoria WHERE id_categoria = %s AND id_usuario_id = %s", [id_categoria, usuario.id_usuario])
    
    # Redireccionar a la página de categorías
    return redirect('categoria', id_usuario=id_usuario)

#Editoriales

def Editorial(request, id_usuario):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)

    # Obtener todas las categorías del usuario utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_editorial, nombre FROM editorial WHERE id_usuario_id = %s", [id_usuario])
        editoriales = cursor.fetchall()

    # Crear una lista de diccionarios con los resultados de la consulta
    editoriales_list = [{'id_editorial': editorial[0], 'nombre': editorial[1]} for editorial in editoriales]

    return render(request, 'app/editorial.html', {'usuario': usuario, 'editoriales': editoriales_list})

def crear_editorial(request, id_usuario):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        
        # Obtener el usuario
        usuario = Usuario.objects.get(id_usuario=id_usuario)
        
        # Insertar la nueva categoría utilizando una consulta SQL nativa
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO editorial (nombre, id_usuario_id) VALUES (%s, %s)", [nombre, usuario.id_usuario])
        
        # Redireccionar a la página de categorías
        return redirect('editorial', id_usuario=id_usuario)
    
    return render(request, 'app/editorial.html')

def actualizar_editorial(request, id_usuario, id_editorial):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        
        # Obtener el usuario
        usuario = Usuario.objects.get(id_usuario=id_usuario)
        
        # Actualizar la categoría utilizando una consulta SQL nativa
        with connection.cursor() as cursor:
            cursor.execute("UPDATE editorial SET nombre = %s WHERE id_editorial = %s AND id_usuario_id = %s", [nombre, id_editorial, usuario.id_usuario])
        
        # Redireccionar a la página de categorías
        return redirect('editorial', id_usuario=id_usuario)
    
    return render(request, 'app/editorial.html')

def eliminar_editorial(request, id_usuario, id_editorial):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    
    # Eliminar la categoría utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM editorial WHERE id_editorial = %s AND id_usuario_id = %s", [id_editorial, usuario.id_usuario])
    
    # Redireccionar a la página de categorías
    return redirect('editorial', id_usuario=id_usuario)

