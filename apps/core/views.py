from django.shortcuts import render
from apps.results.models import Exam
from apps.analytics.services import ResultAnalyticsEngine

def dashboard_view(request):
    """
    Renders institutional dashboard featuring:
    - 6 core KPIs dynamically derived from database via NumPy & Pandas
    - Chart.js real-time visual analytics
    - Top student honors preview and subject difficulty overview
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    kpis = engine.get_dashboard_kpis()
    toppers = engine.get_topper_analysis()
    subjects = engine.get_subject_difficulty_analysis()

    context = {
        'active_nav': 'dashboard',
        'current_exam': current_exam,
        'kpis': kpis,
        'toppers': toppers,
        'subjects': subjects,
    }
    return render(request, 'dashboard.html', context)
