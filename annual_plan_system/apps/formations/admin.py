from django.contrib import admin
from .models import Formation


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ar', 'level', 'parent', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('name_ar', 'code')
    ordering = ('level', 'name_ar')
