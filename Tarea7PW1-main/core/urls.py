from django.urls import path
from . import views

urlpatterns = [
    path('importar-pdf/', views.importar_pdf, name='importar_pdf'),
    path('import-success/', views.import_success, name='import_success'),
    path('pdf-to-html/', views.pdf_to_html, name='pdf_to_html'),
    path('carrera-pdf/', views.carrera_pdf_list, name='carrera_pdf_list'),
    path('materiasf/<str:codcarrera>', views.get_materiasf, name='get_materiasf'),
    path('menu', views.menu, name='menu'),
    path('autoridades', views.autoridades, name='autoridades'),
    path('listar-autoridades/', views.listar_autoridades, name='listar_autoridades'),
    path('obtener-autoridad/<int:autoridad_id>/', views.obtener_autoridad, name='obtener_autoridad'),
    path('editar-autoridad/', views.editar_autoridad, name='editar_autoridad'),
    path('carrera_pdf_list/', views.carrera_pdf_list, name='carrera_pdf_list'),
    path('asignar_dificultad/', views.asignar_dificultad, name='asignar_dificultad'),
]
