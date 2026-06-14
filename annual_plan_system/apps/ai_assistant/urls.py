from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.assistant_home, name='home'),
    path('chat/', views.assistant_chat, name='chat'),
    path('analyze/', views.assistant_analyze_plan, name='analyze_plan'),
    path('export/json/', views.assistant_export_analysis_json, name='export_analysis_json'),
    path('export/pdf/', views.assistant_export_analysis_pdf, name='export_analysis_pdf'),
]
