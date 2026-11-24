from django.contrib import admin
from apps.imports.models import ImportHistory

@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('filename', 'exam', 'total_records', 'successful_records', 'failed_records', 'status', 'imported_at')
    list_filter = ('status', 'imported_at')
    search_fields = ('filename',)
