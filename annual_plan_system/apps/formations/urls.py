from django.urls import path
from . import views

app_name = 'formations'

urlpatterns = [
    # Parent Formation CRUD
    path('parent/', views.ParentFormationListView.as_view(), name='parent_list'),
    path('parent/create/', views.parent_formation_create, name='parent_create'),
    path('parent/<int:pk>/edit/', views.parent_formation_edit, name='parent_edit'),
    path('parent/<int:pk>/delete/', views.parent_formation_delete, name='parent_delete'),

    # Formation CRUD
    path('', views.FormationListView.as_view(), name='list'),
    path('create/', views.formation_create, name='create'),
    path('<int:pk>/edit/', views.formation_edit, name='edit'),
    path('<int:pk>/delete/', views.formation_delete, name='delete'),
    path('api/tree/', views.formation_tree_api, name='tree_api'),
]
