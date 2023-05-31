from django.urls import path
from . import views

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
]