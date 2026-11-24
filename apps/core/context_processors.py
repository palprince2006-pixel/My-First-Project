def academic_context(request):
    """
    Supplies global academic context across all template views:
    available exam terms, active exam filter, and system state.
    """
    from apps.results.models import Exam
    try:
        exams = Exam.objects.all().order_by('-created_at')
        selected_exam_id = request.GET.get('exam_id')
        current_exam = None
        if selected_exam_id:
            current_exam = exams.filter(id=selected_exam_id).first()
        if not current_exam and exams.exists():
            current_exam = exams.first()
    except Exception:
        exams = []
        current_exam = None

    return {
        'all_exams': exams,
        'current_exam': current_exam,
        'system_version': 'v2.4',
    }
