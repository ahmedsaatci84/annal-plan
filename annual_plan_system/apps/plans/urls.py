from django.urls import path
from apps.plans import views

app_name = 'plans'

urlpatterns = [
    path('', views.plan_list, name='list'),
    path('create/', views.plan_create, name='create'),
    path('<int:pk>/', views.plan_detail, name='detail'),
    path('<int:pk>/edit/', views.plan_edit, name='edit'),
     path('<int:pk>/delete/', views.plan_delete, name='delete'),
     path('<int:pk>/change-status/', views.plan_change_status, name='change_status'),
    path('<int:pk>/submit/', views.plan_submit, name='submit'),
    path('<int:pk>/start-review/', views.plan_start_review, name='start_review'),
    path('<int:pk>/approve/', views.plan_approve, name='approve'),
    path('<int:pk>/reject/', views.plan_reject, name='reject'),
    path('<int:pk>/reopen/', views.plan_reopen, name='reopen'),
    path('<int:pk>/archive/', views.plan_archive, name='archive'),

    # SWOT
    path('<int:plan_pk>/swot/edit/', views.swot_edit, name='swot_edit'),

    # Goals
    path('<int:plan_pk>/goals/', views.goal_list, name='goals'),
    path('<int:plan_pk>/goals/create/', views.goal_create, name='goal_create'),
    path('<int:plan_pk>/goals/<int:goal_pk>/edit/', views.goal_edit, name='goal_edit'),
    path('<int:plan_pk>/goals/<int:goal_pk>/delete/', views.goal_delete, name='goal_delete'),

    # Activities
    path('<int:plan_pk>/goals/<int:goal_pk>/activities/create/',
         views.activity_create, name='activity_create'),
    path('<int:plan_pk>/goals/<int:goal_pk>/activities/<int:activity_pk>/edit/',
         views.activity_edit, name='activity_edit'),
    path('<int:plan_pk>/goals/<int:goal_pk>/activities/<int:activity_pk>/delete/',
         views.activity_delete, name='activity_delete'),
    path('<int:plan_pk>/goals/<int:goal_pk>/activities/<int:activity_pk>/progress/',
         views.activity_update_progress, name='activity_progress'),

    # Risks
    path('<int:plan_pk>/risks/create/', views.risk_create, name='risk_create'),
    path('<int:plan_pk>/risks/<int:risk_pk>/edit/', views.risk_edit, name='risk_edit'),
    path('<int:plan_pk>/risks/<int:risk_pk>/delete/', views.risk_delete, name='risk_delete'),

    # Read-only sections
    path('<int:plan_pk>/gantt/', views.gantt_view, name='gantt'),
    path('<int:plan_pk>/summary/', views.summary_view, name='summary'),
    path('<int:plan_pk>/recommendations/edit/', views.recommendations_edit, name='recommendations_edit'),
    path('<int:plan_pk>/export/pdf/', views.plan_export_pdf, name='export_pdf'),

    # API
    path('api/<int:plan_pk>/gantt-data/', views.gantt_data_api, name='gantt_data_api'),
    path('api/<int:plan_pk>/summary/', views.summary_api, name='summary_api'),
]
