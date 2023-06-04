from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db import connection
from .forms import AutorForm, LibroForm, AutorFormSet
from django import forms
from django.db.models import Count
from .models import Usuario, LibroAutor, Categoria, Libro, Autor, Editorial

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

# Gestion de inventario

def gestion_inventario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    libros = Libro.objects.filter(id_usuario=id_usuario).select_related('id_categoria', 'id_editorial')
    return render(request, 'app/gestion_inventario.html', {'libros': libros, 'usuario': usuario})



def crear_libro(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    id_libro = None

    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            libro.id_usuario = usuario
            libro.save()
            id_libro = libro.id_libro  # Obtener el id_libro recién creado

            # Redireccionar a la página de CRUD de autores con los parámetros necesarios
            return redirect('crud_autores', id_usuario=id_usuario, id_libro=id_libro)
    else:
        form = LibroForm()

    contexto = {'form': form, 'id_usuario': id_usuario, 'id_libro': id_libro}
    return render(request, 'app/crear_libro.html', contexto)


def editar_libro(request,id_usuario,id_libro):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    libro = get_object_or_404(Libro, id_libro=id_libro)
    id_usuario = libro.id_usuario.id_usuario

    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            return redirect('gestion_inventario', id_usuario=usuario.id_usuario)
    else:
        form = LibroForm(instance=libro)

    return render(request, 'app/editar_libro.html', {'form': form, 'id_usuario': id_usuario})


def eliminar_libro(request, id_usuario, id_libro):
    libro = get_object_or_404(Libro, pk=id_libro, id_usuario_id=id_usuario)

    if request.method == 'POST':
        # Verificar si el autor no está en otro libro
        autores = Autor.objects.filter(libroautor__id_libro=id_libro)
        for autor in autores:
            if not Autor.objects.filter(libroautor__id_autor=autor).exclude(libroautor__id_libro=id_libro).exists():
                autor.delete()

        libro.delete()
        return redirect('gestion_inventario', id_usuario=id_usuario)

    return redirect('gestion_inventario', id_usuario=id_usuario)


# CRUD DE AUTORES

def crud_autores(request, id_usuario, id_libro):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id_autor, l.id_usuario_id, l.id_libro, l.titulo, a.nombre, la.anyo 
            FROM libro AS l
            INNER JOIN libro_autor AS la ON l.id_libro = la.id_libro_id
            INNER JOIN autor AS a ON a.id_autor = la.id_autor_id
            WHERE l.id_usuario_id = %s AND l.id_libro = %s
        """, [id_usuario, id_libro])

        results = cursor.fetchall()

    contexto = {
        'resultados': results,
        'id_usuario': id_usuario,
        'id_libro': id_libro
    }

    return render(request, 'app/crud_autores.html', contexto)


def crear_autor(request, id_usuario, id_libro):
    if request.method == 'POST':
        nombre_autor = request.POST.get('nombre')
        anyo_libro_autor = request.POST.get('anyo')

        with connection.cursor() as cursor:
            # Insertar el nuevo autor en la tabla Autor
            cursor.execute("INSERT INTO Autor (nombre, id_usuario_id) VALUES (%s, %s)", [nombre_autor, id_usuario])

            # Obtener el ID del autor recién insertado
            cursor.execute("SELECT MAX(id_autor) as id_autor from autor")
            autor_id = cursor.fetchone()[0]

            # Insertar el nuevo libro_autor en la tabla LibroAutor
            cursor.execute("INSERT INTO libro_autor (anyo, id_libro_id, id_autor_id) VALUES (%s, %s, %s)",
                           [anyo_libro_autor, id_libro, autor_id])

        return redirect('crud_autores', id_usuario=id_usuario, id_libro=id_libro)

    return render(request, 'app/crud_autores.html', {'id_usuario': id_usuario, 'id_libro': id_libro})


def editar_autor(request, id_usuario, id_libro, id_autor):
    if request.method == 'POST':
        nombre_autor = request.POST.get('nombre')
        anyo_libro_autor = request.POST.get('anyo')

        with connection.cursor() as cursor:
            # Actualizar el autor en la tabla Autor
            cursor.execute("UPDATE Autor SET nombre = %s WHERE id_autor = %s", [nombre_autor, id_autor])

            # Actualizar el año del libro_autor en la tabla LibroAutor
            cursor.execute("UPDATE libro_autor SET anyo = %s WHERE id_libro_id = %s AND id_autor_id = %s",
                           [anyo_libro_autor, id_libro, id_autor])

        return redirect('crud_autores', id_usuario=id_usuario, id_libro=id_libro)

    with connection.cursor() as cursor:
        # Obtener el autor y el año del libro_autor mediante una consulta SQL
        cursor.execute("SELECT a.nombre, la.anyo FROM Autor AS a INNER JOIN libro_autor AS la ON a.id_autor = la.id_autor_id WHERE a.id_autor = %s AND la.id_libro_id = %s",
                       [id_autor, id_libro])
        autor = cursor.fetchone()

    if autor is None:
        raise Http404

    contexto = {
        'nombre_autor': autor[0],
        'anyo_libro_autor': autor[1],
        'id_usuario': id_usuario,
        'id_libro': id_libro,
        'id_autor': id_autor
    }

    return render(request, 'app/crud_autores.html', contexto)


def eliminar_autor(request, id_usuario, id_libro, id_autor):
    autor = get_object_or_404(Autor, id_autor=id_autor)
    
    if request.method == 'POST':
        autor.delete()
        return redirect('crud_autores', id_usuario=id_usuario, id_libro=id_libro)
    
    contexto = {
        'id_usuario': id_usuario,
        'id_libro': id_libro,
        'id_autor': id_autor,
        'nombre_autor': autor.nombre
    }
    
    return render(request, 'app/eliminar_autor_modal.html', contexto)






