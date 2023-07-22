from datetime import date
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db.models import Sum, Count
from django.db import connection
from django.contrib import messages
from django.template.loader import get_template
from .forms import LibroForm
from .models import Usuario, Categoria, Libro, Autor, Editorial, Boleta,DetalleBoleta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import BoletaForm
from django.http import JsonResponse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EditarUsuarioForm, CambiarContrasenaForm
from django.db.models import F

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
                return redirect('catalogo', id_usuario=usuario.id_usuario)  # Redirecciona a la página de inicio con el id_usuario
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


def editar_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)

    if request.method == 'POST':
        editar_form = EditarUsuarioForm(request.POST, instance=usuario)

        # Obtener los valores de las contraseñas desde el POST
        contrasena_actual = request.POST.get('contrasena_actual', '')
        nueva_contrasena = request.POST.get('nueva_contrasena', '')
        confirmar_nueva_contrasena = request.POST.get('confirmar_nueva_contrasena', '')

        # Verificar que la contraseña actual sea correcta
        if contrasena_actual != usuario.contrasena:
            messages.error(request, 'La contraseña actual es incorrecta.')
        else:
            # Contraseña actual correcta, proceder con la edición del usuario
            if editar_form.is_valid():
                editar_form.save()

                # Verificar si se ingresó una nueva contraseña y si coincide con la confirmación
                if nueva_contrasena and nueva_contrasena == confirmar_nueva_contrasena:
                    usuario.contrasena = nueva_contrasena
                    usuario.save()

                    messages.success(request, 'Usuario actualizado exitosamente.')
                else:
                    messages.error(request, 'Las contraseñas nuevas no coinciden.')
            else:
                messages.error(request, 'Error en los datos ingresados.')

    else:
        editar_form = EditarUsuarioForm(instance=usuario)

    cambiar_contrasena_form = CambiarContrasenaForm()

    return render(request, 'app/editar_usuario.html', {'usuario': usuario, 'editar_form': editar_form, 'cambiar_contrasena_form': cambiar_contrasena_form})



def catalogo(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    editoriales = Editorial.objects.filter(id_usuario_id=id_usuario)
    categorias = Categoria.objects.filter(id_usuario_id=id_usuario)
    filtro_categoria = request.GET.get('categoria')
    filtro_editorial = request.GET.get('editorial')
    filtro_titulo = request.GET.get('titulo')
    filtro_autor = request.GET.get('autor')  # Nuevo filtro por autor

    libros = Libro.objects.filter(id_usuario_id=id_usuario)

    if filtro_categoria:
        libros = libros.filter(id_categoria_id=filtro_categoria)

    if filtro_editorial:
        libros = libros.filter(id_editorial_id=filtro_editorial)

    if filtro_titulo:
        libros = libros.filter(titulo__icontains=filtro_titulo)

    if filtro_autor:  # Aplicar el filtro por autor si se ingresó uno
        libros = libros.filter(libroautor__id_autor__nombre__icontains=filtro_autor)

    libros_autores = []
    for libro in libros:
        autores_libro = libro.libroautor_set.values_list('id_autor__nombre', flat=True)
        libro_dict = {
            'id_libro': libro.id_libro,
            'titulo': libro.titulo,
            'imagen': libro.imagen,
            'precio': libro.precio,
            'stock': libro.stock,
            'autores': list(autores_libro),
            'agregado_a_boleta': False
        }
        libros_autores.append(libro_dict)

    # Implementación de paginación
    libros_por_pagina = 4

    paginator = Paginator(libros_autores, libros_por_pagina)
    page = request.GET.get('page')

    try:
        libros_paginados = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostrar la primera página
        libros_paginados = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        libros_paginados = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        libros_seleccionados = request.POST.getlist('libros_seleccionados')
        cantidades = request.POST.getlist('cantidad')

        if len(libros_seleccionados) != len(cantidades):
            messages.error(request, 'La cantidad de libros seleccionados no coincide con la cantidad ingresada.')
        else:
            # Crear una lista de libros seleccionados con sus cantidades
            libros_para_boleta = []
            total_monto = 0
            for libro_id, cantidad in zip(libros_seleccionados, cantidades):
                libro = Libro.objects.get(id_libro=libro_id)
                subtotal = libro.precio * int(cantidad)
                total_monto += subtotal
                libro_para_boleta = {
                    'id_libro': libro.id_libro,
                    'titulo': libro.titulo,
                    'cantidad': int(cantidad),
                    'precio': libro.precio,
                    'subtotal': subtotal
                }
                libros_para_boleta.append(libro_para_boleta)

            # Crear una boleta sin registrar en la base de datos
            nueva_boleta = Boleta.objects.create(
                nombre_comprador="agregar nombre",
                fecha=date.today(),
                monto_total=total_monto,
                id_usuario_id=id_usuario
            )

            # Registrar los detalles de la boleta en la base de datos
            for detalle in libros_para_boleta:
                DetalleBoleta.objects.create(
                    cantidad=detalle['cantidad'],
                    precio=detalle['precio'],
                    id_boleta=nueva_boleta,
                    id_libro_id=detalle['id_libro']
                )

            contexto = {
                'libros_autores': libros_autores,
                'usuario': usuario,
                'categorias': categorias,
                'editoriales': editoriales,
                'filtro_categoria': filtro_categoria,
                'filtro_editorial': filtro_editorial,
                'filtro_titulo': filtro_titulo,
                'filtro_autor': filtro_autor,
                'nueva_boleta': nueva_boleta  # Pasar la boleta creada sin registrar al contexto
            }
            return render(request, 'app/boleta.html', contexto)

    contexto = {
        'libros_paginados': libros_paginados,  # Lista de libros paginados
        'usuario': usuario,
        'categorias': categorias,
        'editoriales': editoriales,
        'filtro_categoria': filtro_categoria,
        'filtro_editorial': filtro_editorial,
        'filtro_titulo': filtro_titulo,
        'filtro_autor': filtro_autor  # Agregamos el filtro por autor al contexto
    }
    return render(request, 'app/catalogo.html', contexto)


# Categorias

def lista_categoria(request, id_usuario):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)

    # Obtener todas las categorías del usuario utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_categoria, nombre FROM categoria WHERE id_usuario_id = %s", [id_usuario])
        categorias = cursor.fetchall()

    # Crear una lista de diccionarios con los resultados de la consulta
    categorias_list = [{'id_categoria': categoria[0], 'nombre': categoria[1]} for categoria in categorias]

    # Definir la cantidad de categorías por página
    categorias_por_pagina = 5

    paginator = Paginator(categorias_list, categorias_por_pagina)
    page = request.GET.get('page')

    try:
        categorias_paginadas = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostrar la primera página
        categorias_paginadas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        categorias_paginadas = paginator.page(paginator.num_pages)

    return render(request, 'app/categoria.html', {'usuario': usuario, 'categorias': categorias_paginadas})

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

def Lista_Editorial(request, id_usuario):
    # Obtener el usuario
    usuario = Usuario.objects.get(id_usuario=id_usuario)

    # Obtener todas las editoriales del usuario utilizando una consulta SQL nativa
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_editorial, nombre FROM editorial WHERE id_usuario_id = %s", [id_usuario])
        editoriales = cursor.fetchall()

    # Crear una lista de diccionarios con los resultados de la consulta
    editoriales_list = [{'id_editorial': editorial[0], 'nombre': editorial[1]} for editorial in editoriales]

    # Definir la cantidad de editoriales por página
    editoriales_por_pagina = 5

    paginator = Paginator(editoriales_list, editoriales_por_pagina)
    page = request.GET.get('page')

    try:
        editoriales_paginadas = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostrar la primera página
        editoriales_paginadas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        editoriales_paginadas = paginator.page(paginator.num_pages)

    return render(request, 'app/editorial.html', {'usuario': usuario, 'editoriales': editoriales_paginadas})

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

def gestion_catalogo(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    libros = Libro.objects.filter(id_usuario=id_usuario).select_related('id_categoria', 'id_editorial')

    # Definir la cantidad de libros por página
    libros_por_pagina = 5

    paginator = Paginator(libros, libros_por_pagina)
    page = request.GET.get('page')

    try:
        libros_paginados = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostrar la primera página
        libros_paginados = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        libros_paginados = paginator.page(paginator.num_pages)

    contexto = {
        'libros': libros_paginados,
        'usuario': usuario
    }
    return render(request, 'app/gestion_catalogo.html', contexto)



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
            return redirect('gestion_catalogo', id_usuario=usuario.id_usuario)
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
        return redirect('gestion_catalogo', id_usuario=id_usuario)

    return redirect('gestion_catalogo', id_usuario=id_usuario)


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

# pip install django-plotly-dash

def estadisticas(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    editoriales = Editorial.objects.filter(id_usuario_id=id_usuario)
    categorias = Categoria.objects.filter(id_usuario_id=id_usuario)
    filtro_categoria = request.GET.get('categoria')
    filtro_editorial = request.GET.get('editorial')
    filtro_titulo = request.GET.get('titulo')

    libros = Libro.objects.filter(id_usuario_id=id_usuario, detalleboleta__isnull=False)

    if filtro_categoria:
        libros = libros.filter(id_categoria_id=filtro_categoria)

    if filtro_editorial:
        libros = libros.filter(id_editorial_id=filtro_editorial)

    if filtro_titulo:
        libros = libros.filter(titulo__icontains=filtro_titulo)

    resultados = libros.values('id_libro', 'titulo', 'id_categoria__nombre', 'id_editorial__nombre').annotate(
        total_cantidad=Sum('detalleboleta__cantidad'),
        total_monto=Sum(F('detalleboleta__cantidad') * F('detalleboleta__precio'))
    )

    # Definir la cantidad de libros por página
    libros_por_pagina = 5

    paginator = Paginator(resultados, libros_por_pagina)
    page = request.GET.get('page')

    try:
        libros_paginados = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostrar la primera página
        libros_paginados = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        libros_paginados = paginator.page(paginator.num_pages)

    contexto = {
        'usuario': usuario,
        'libros': libros_paginados,
        'categorias': categorias,
        'editoriales': editoriales,
        'filtro_categoria': filtro_categoria,
        'filtro_editorial': filtro_editorial,
        'filtro_titulo': filtro_titulo
    }
    return render(request, 'app/estadisticas.html', contexto)


def boleta(request, id_usuario, id_boleta):
    boleta = get_object_or_404(Boleta, id_boleta=id_boleta, id_usuario_id=id_usuario)

    if request.method == 'POST':
        nombre_comprador = request.POST.get('nombre_comprador')
        boleta.nombre_comprador = nombre_comprador
        boleta.save()
        # Redireccionar a la página de boleta para mostrar los cambios
        return redirect('boleta', id_usuario=id_usuario, id_boleta=id_boleta)

    contexto = {
        'boleta': boleta
    }
    return render(request, 'app/boleta.html', contexto)

def generar_boleta(request, id_usuario, id_boleta):
    boleta = get_object_or_404(Boleta, id_boleta=id_boleta, id_usuario_id=id_usuario)

    # Creamos un objeto de tipo BytesIO para almacenar el PDF en memoria
    buffer = BytesIO()

    # Creamos un objeto de tipo canvas, que nos permitirá dibujar en el PDF
    c = canvas.Canvas(buffer, pagesize=letter)

    # Agregamos contenido al PDF
    c.drawString(100, 750, f"Boleta Nº {boleta.id_boleta}")
    c.drawString(100, 730, f"Fecha: {boleta.fecha.strftime('%d/%m/%Y')}")
    c.drawString(100, 710, f"Nombre del Comprador: {boleta.nombre_comprador}")

    # Posición inicial del contenido de la tabla
    y = 650

    # Dibujamos la tabla con los detalles de la boleta
    c.drawString(100, y, "Título")
    c.drawString(250, y, "Cantidad")
    c.drawString(350, y, "Precio")
    c.drawString(450, y, "Subtotal")

    # Posición de la siguiente fila
    y -= 20

    for detalle in boleta.detalleboleta_set.all():
        c.drawString(100, y, detalle.id_libro.titulo)
        c.drawString(250, y, str(detalle.cantidad))
        c.drawString(350, y, f"${detalle.precio}")
        c.drawString(450, y, f"${detalle.cantidad * detalle.precio}")
        y -= 20

    # Agregamos el total de la boleta
    c.drawString(350, y - 40, "Total:")
    c.drawString(450, y - 40, f"${boleta.monto_total}")

    # Guardamos el PDF
    c.save()

    # Obtenemos el contenido del buffer y establecemos las cabeceras del HTTP response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=boleta_{boleta.id_boleta}.pdf'

    # Escribimos el contenido del PDF en la respuesta
    response.write(pdf)
    return response

# pip install reportlab