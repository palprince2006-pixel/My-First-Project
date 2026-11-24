from django.shortcuts import render
from django.http import JsonResponse
from apps.results.models import Exam
from apps.analytics.services import ResultAnalyticsEngine

def topper_analysis_view(request):
    """
    Renders topper analysis, class honor roll, top 10 rankings,
    and subject-wise toppers handling tied marks.
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    toppers = engine.get_topper_analysis()

    context = {
        'active_nav': 'toppers',
        'current_exam': current_exam,
        'toppers': toppers,
    }
    return render(request, 'toppers.html', context)


def subject_analysis_view(request):
    """
    Renders subject-level performance metrics, standard deviation,
    and analytical difficulty classification.
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    subjects = engine.get_subject_difficulty_analysis()

    context = {
        'active_nav': 'subjects',
        'current_exam': current_exam,
        'subjects': subjects,
    }
    return render(request, 'subjects.html', context)


def chart_data_api(request):
    """
    JSON endpoint providing live Chart.js datasets:
    1. Subject-wise average marks (Bar)
    2. Pass vs Fail ratio (Doughnut)
    3. Performance score range distribution (Bar)
    4. Letter grade distribution (Pie)
    5. Subject clearance comparison (Horizontal Bar)
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    data = engine.get_chart_data()
    return JsonResponse(data)
