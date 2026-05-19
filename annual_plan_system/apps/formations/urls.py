from django.urls import path
from . import views

app_name = 'formations'

urlpatterns = [
    path('', views.FormationListView.as_view(), name='list'),
    path('create/', views.formation_create, name='create'),
    path('<int:pk>/edit/', views.formation_edit, name='edit'),
    path('api/tree/', views.formation_tree_api, name='tree_api'),
]
