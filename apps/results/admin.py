from django.contrib import admin
from apps.results.models import Subject, Exam, StudentMark

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'maximum_marks', 'passing_marks', 'created_at')
    search_fields = ('subject_code', 'subject_name')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'academic_year', 'semester', 'department', 'is_active', 'created_at')
    list_filter = ('academic_year', 'semester', 'is_active')

@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained', 'is_passed')
    list_filter = ('exam', 'subject')
    search_fields = ('student__roll_number', 'student__student_name', 'subject__subject_name')
