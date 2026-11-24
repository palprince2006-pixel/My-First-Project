from django.shortcuts import render
from apps.results.models import Exam, Subject, StudentMark
from apps.analytics.services import ResultAnalyticsEngine

def student_results_view(request):
    """
    Renders the student results marks ledger table with search,
    status and grade filters, sort options, and modal marksheets.
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    engine = ResultAnalyticsEngine(exam=current_exam)
    summary_df = engine.get_student_summary_dataframe()
    raw_df = engine.get_raw_marks_dataframe()

    # Subjects for header columns
    subjects = []
    if current_exam:
        subjects = list(Subject.objects.filter(student_marks__exam=current_exam).distinct())

    search_query = request.GET.get('search', '').strip().lower()
    status_filter = request.GET.get('status', '').strip()
    grade_filter = request.GET.get('grade', '').strip()
    sort_by = request.GET.get('sort', 'rank').strip()

    # Build student records list
    students_list = []
    if not summary_df.empty:
        # Pre-build marks map: student_id -> {subject_code: marks}
        marks_map = {}
        if not raw_df.empty:
            for _, r in raw_df.iterrows():
                sid = r['student_id']
                if sid not in marks_map:
                    marks_map[sid] = {}
                marks_map[sid][r['subject_code']] = r['marks_obtained']

        for _, row in summary_df.iterrows():
            sid = row['student_id']
            record = row.to_dict()
            record['marks'] = marks_map.get(sid, {})
            students_list.append(record)

    # Filter by search
    if search_query:
        students_list = [
            s for s in students_list
            if search_query in s['roll_number'].lower() or search_query in s['student_name'].lower()
        ]

    # Filter by status
    if status_filter in ['Passed', 'Failed']:
        students_list = [s for s in students_list if s['status'] == status_filter]

    # Filter by grade
    if grade_filter:
        students_list = [s for s in students_list if s['grade'] == grade_filter]

    # Sorting
    if sort_by == 'percentage_desc':
        students_list.sort(key=lambda x: x['percentage'], reverse=True)
    elif sort_by == 'percentage_asc':
        students_list.sort(key=lambda x: x['percentage'])
    elif sort_by == 'roll':
        students_list.sort(key=lambda x: x['roll_number'])
    elif sort_by == 'name':
        students_list.sort(key=lambda x: x['student_name'].lower())
    else:  # default by rank
        students_list.sort(key=lambda x: (x['rank'], x['roll_number']))

    context = {
        'active_nav': 'students',
        'current_exam': current_exam,
        'subjects': subjects,
        'students': students_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'grade_filter': grade_filter,
        'sort_by': sort_by,
    }
    return render(request, 'students.html', context)
