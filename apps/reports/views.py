from django.shortcuts import render
from django.http import HttpResponse, Http404
from apps.results.models import Exam
from apps.analytics.services import ResultAnalyticsEngine
from apps.reports.services import ReportExportService

def reports_view(request):
    """Renders the reports and data export dashboard."""
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    kpis = engine.get_dashboard_kpis()

    context = {
        'active_nav': 'reports',
        'current_exam': current_exam,
        'kpis': kpis,
    }
    return render(request, 'reports.html', context)


def export_report_csv_view(request):
    """Delivers dynamic CSV file for the requested report type."""
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    report_type = request.GET.get('type', 'students_ledger')
    service = ReportExportService(exam=current_exam)
    csv_bytes, filename = service.export_csv(report_type=report_type)

    response = HttpResponse(csv_bytes, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def export_report_pdf_view(request):
    """Delivers dynamic styled ReportLab PDF for the requested report type."""
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    report_type = request.GET.get('type', 'students_ledger')
    service = ReportExportService(exam=current_exam)
    try:
        pdf_bytes, filename = service.export_pdf(report_type=report_type)
    except Exception as e:
        return HttpResponse(f"Error generating PDF report: {str(e)}", status=500)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
