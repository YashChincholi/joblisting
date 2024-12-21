from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employment_type', 'posted_date', 'updated_date')
    search_fields = ('title', 'company', 'location')
    list_filter = ('employment_type', 'location_type', 'posted_date')
