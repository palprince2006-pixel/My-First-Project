import io
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from apps.results.models import Exam
from apps.imports.models import ImportHistory
from apps.imports.services import ResultImportValidator

def upload_results_view(request):
    """
    Handles CSV and Excel score sheet uploads with two modes:
    1. Dry-run preview with schema validation and error diagnostic report.
    2. Atomic database ingestion and audit log recording.
    """
    selected_exam_id = request.GET.get('exam_id')
    current_exam = None
    if selected_exam_id:
        current_exam = Exam.objects.filter(id=selected_exam_id).first()
    if not current_exam:
        current_exam = Exam.objects.first()

    recent_imports = ImportHistory.objects.all()[:15]
    validation_errors = []
    preview_summary = None
    preview_data = []

    if request.method == 'POST':
        action = request.POST.get('action', 'import')
        uploaded_file = request.FILES.get('result_file')

        exam_name = request.POST.get('exam_name', 'Mid-Term Examination 2024-25').strip()
        academic_year = request.POST.get('academic_year', '2024-2025').strip()
        semester = request.POST.get('semester', 'Sem IV').strip()
        department = request.POST.get('department', 'Computer Science & Engineering').strip()

        target_exam, _ = Exam.objects.get_or_create(
            exam_name=exam_name,
            academic_year=academic_year,
            semester=semester,
            defaults={'department': department}
        )

        if not uploaded_file:
            messages.error(request, "Please choose a CSV or Excel file to upload.")
            return render(request, 'upload.html', {
                'active_nav': 'upload',
                'current_exam': target_exam,
                'import_history': recent_imports,
            })

        # File size check (< 15MB)
        if uploaded_file.size > 15 * 1024 * 1024:
            messages.error(request, "File size exceeds the 15MB limit.")
            return render(request, 'upload.html', {
                'active_nav': 'upload',
                'current_exam': target_exam,
                'import_history': recent_imports,
            })

        validator = ResultImportValidator(
            file_obj=uploaded_file,
            filename=uploaded_file.name,
            exam=target_exam
        )

        is_valid = validator.validate()

        if not is_valid:
            validation_errors = validator.errors
            messages.error(request, f"File validation failed with {len(validation_errors)} error(s). Review table below.")
            return render(request, 'upload.html', {
                'active_nav': 'upload',
                'current_exam': target_exam,
                'import_history': recent_imports,
                'validation_errors': validation_errors,
            })

        # If user chose 'preview'
        if action == 'preview':
            preview_summary = validator.summary
            preview_data = validator.preview_data
            messages.success(request, f"Validation successful! {validator.summary['total_rows']} student records verified. Ready to commit.")
            return render(request, 'upload.html', {
                'active_nav': 'upload',
                'current_exam': target_exam,
                'import_history': recent_imports,
                'preview_summary': preview_summary,
                'preview_data': preview_data,
            })

        # If user chose 'import' (direct commit)
        try:
            result = validator.save_to_database(exam=target_exam)
            messages.success(
                request,
                f"Successfully ingested {result['successful_records']} student records for {target_exam.exam_name}!"
            )
            return redirect(f"/?exam_id={target_exam.id}")
        except Exception as e:
            messages.error(request, f"Database commit failed: {str(e)}")

    context = {
        'active_nav': 'upload',
        'current_exam': current_exam,
        'import_history': recent_imports,
        'validation_errors': validation_errors,
        'preview_summary': preview_summary,
        'preview_data': preview_data,
    }
    return render(request, 'upload.html', context)


def download_sample_template(request, file_type='csv'):
    """Generates standard starter template in CSV or XLSX format."""
    sample_rows = [
        {'roll_number': 'CSE24-001', 'student_name': 'Aarav Sharma', 'subject_1': 88, 'subject_2': 92, 'subject_3': 85, 'subject_4': 95, 'subject_5': 90},
        {'roll_number': 'CSE24-002', 'student_name': 'Diya Patel', 'subject_1': 75, 'subject_2': 80, 'subject_3': 78, 'subject_4': 82, 'subject_5': 79},
        {'roll_number': 'CSE24-003', 'student_name': 'Vivaan Gupta', 'subject_1': 65, 'subject_2': 70, 'subject_3': 68, 'subject_4': 72, 'subject_5': 74},
        {'roll_number': 'CSE24-004', 'student_name': 'Ananya Iyer', 'subject_1': 95, 'subject_2': 94, 'subject_3': 90, 'subject_4': 98, 'subject_5': 92},
        {'roll_number': 'CSE24-005', 'student_name': 'Advait Nair', 'subject_1': 70, 'subject_2': 68, 'subject_3': 74, 'subject_4': 80, 'subject_5': 72},
    ]
    df = pd.DataFrame(sample_rows)

    if file_type.lower() == 'xlsx':
        out = io.BytesIO()
        df.to_excel(out, index=False, engine='openpyxl')
        out.seek(0)
        response = HttpResponse(
            out.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="student_results_template.xlsx"'
        return response
    else:
        out = io.StringIO()
        df.to_csv(out, index=False)
        response = HttpResponse(out.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_results_template.csv"'
        return response


def download_practice_dataset(request, filename):
    """Safely serves pre-generated practice dataset files from sample_data/."""
    safe_name = os.path.basename(filename)
    file_path = os.path.join(settings.BASE_DIR, 'sample_data', safe_name)

    if not os.path.exists(file_path):
        return HttpResponse("Practice dataset file not found.", status=404)

    ext = os.path.splitext(safe_name)[1].lower()
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if ext == '.xlsx' else 'text/csv'

    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    response = HttpResponse(file_bytes, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
    return response

