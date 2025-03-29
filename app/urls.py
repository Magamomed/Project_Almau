from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),                 # Главная страница = Загрузка анкет
    path('list/', views.list_view, name='list'),                # Список анкет
    path('edit/<int:candidate_id>/', views.edit_view, name='edit'),  # Редактирование анкеты
    path('success/', views.success_view, name='success'),       # Страница после сохранения
     path('delete/<int:candidate_id>/', views.delete_view, name='delete'),
]
