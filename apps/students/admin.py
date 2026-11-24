from django.contrib import admin
from apps.students.models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'student_name', 'department', 'section', 'created_at')
    search_fields = ('roll_number', 'student_name')
    list_filter = ('department', 'section')
