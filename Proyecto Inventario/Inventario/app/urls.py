from django.urls import path
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns=[
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('signup/',views.signup,name="signup"),
    path('logout/', views.logout_view, name='logout'),
    path('pagina_principal/<int:id_usuario>/',views.pagina_principal, name="pagina_principal"),
    
    path('categoria/<int:id_usuario>/',views.categoria, name="categoria"),
    path('categoria/crear/<int:id_usuario>/', views.crear_categoria, name='crear_categoria'),
    path('categoria/actualizar/<int:id_usuario>/<int:id_categoria>/', views.actualizar_categoria, name='actualizar_categoria'),
    path('categoria/eliminar/<int:id_usuario>/<int:id_categoria>/', views.eliminar_categoria, name='eliminar_categoria'),

    path('editorial/<int:id_usuario>/',views.Editorial, name="editorial"),
    path('editorial/crear/<int:id_usuario>/', views.crear_editorial, name='crear_editorial'),
    path('editorial/actualizar/<int:id_usuario>/<int:id_editorial>/', views.actualizar_editorial, name='actualizar_editorial'),
    path('editorial/eliminar/<int:id_usuario>/<int:id_editorial>/', views.eliminar_editorial, name='eliminar_editorial'),

    path('gestion_inventario/<int:id_usuario>/',views.gestion_inventario, name="gestion_inventario"),
    path('crear_libro/<int:id_usuario>/', views.crear_libro, name='crear_libro'),
    path('editar_libro/<int:id_usuario>/<int:id_libro>/', views.editar_libro, name='editar_libro'),
    path('eliminar_libro/<int:id_usuario>/<int:id_libro>/', views.eliminar_libro, name='eliminar_libro'),

    path('crud_autores/<int:id_usuario>/<int:id_libro>/', views.crud_autores, name='crud_autores'),
    path('crear_autor/<int:id_usuario>/<int:id_libro>/', views.crear_autor, name='crear_autor'),
    path('editar_autor/<int:id_usuario>/<int:id_libro>/<int:id_autor>/', views.editar_autor, name='editar_autor'),
    path('eliminar_autor/<int:id_usuario>/<int:id_libro>/<int:id_autor>/', views.eliminar_autor, name='eliminar_autor'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)