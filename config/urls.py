from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import dashboard_view
from apps.imports.views import upload_results_view, download_sample_template, download_practice_dataset
from apps.students.views import student_results_view
from apps.analytics.views import topper_analysis_view, subject_analysis_view, chart_data_api
from apps.reports.views import reports_view, export_report_csv_view, export_report_pdf_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Module 1: Dashboard
    path('', dashboard_view, name='dashboard'),

    # Module 2: Upload Student Results
    path('upload/', upload_results_view, name='upload_results'),
    path('upload/sample-template/<str:file_type>/', download_sample_template, name='download_sample_template'),
    path('upload/practice-dataset/<str:filename>/', download_practice_dataset, name='download_practice_dataset'),

    # Module 3: Student Performance & Marks Ledger
    path('students/', student_results_view, name='student_results'),

    # Module 4: Topper Analysis
    path('toppers/', topper_analysis_view, name='topper_analysis'),

    # Module 5: Subject Difficulty Analysis
    path('subjects/', subject_analysis_view, name='subject_analysis'),

    # Module 6: Real-time Chart Data API
    path('api/charts/', chart_data_api, name='chart_data_api'),

    # Module 7: Reports & Data Exports
    path('reports/', reports_view, name='reports'),
    path('reports/export/csv/', export_report_csv_view, name='export_report_csv'),
    path('reports/export/pdf/', export_report_pdf_view, name='export_report_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
