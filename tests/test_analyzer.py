import io
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from apps.students.models import Student
from apps.results.models import Subject, Exam, StudentMark
from apps.imports.models import ImportHistory
from apps.imports.services import ResultImportValidator
from apps.analytics.services import ResultAnalyticsEngine
from apps.reports.services import ReportExportService

class StudentResultAnalyzerTests(TestCase):
    """
    Comprehensive test suite verifying:
    1. CSV Upload & Ingestion
    2. Excel Upload & Ingestion
    3. Missing Columns Validation
    4. Duplicate Roll Numbers Validation
    5. Invalid Marks Out of Range (0-100)
    6. Class Average Calculations
    7. Topper Identification & Tie Handling
    8. Subject-wise Analysis & Difficulty Classification
    9. Pass/Fail Calculations & Letter Grading
    10. Report Generation (CSV & PDF)
    11. Web Views & API endpoints HTTP 200 responses
    """

    def setUp(self):
        self.client = Client()
        self.exam = Exam.objects.create(
            exam_name="End-Term Examination 2024",
            academic_year="2024-2025",
            semester="Sem IV",
            department="Computer Science & Engineering"
        )
        self.math = Subject.objects.create(subject_code="MATH4", subject_name="Mathematics 4", maximum_marks=100.0, passing_marks=40.0)
        self.ds = Subject.objects.create(subject_code="DS", subject_name="Data Structures", maximum_marks=100.0, passing_marks=40.0)
        self.os = Subject.objects.create(subject_code="OS", subject_name="Operating Systems", maximum_marks=100.0, passing_marks=40.0)

        # Create 3 baseline students
        # Student 1: High scorer (Topper)
        self.s1 = Student.objects.create(roll_number="CSE24-001", student_name="Aarav Sharma")
        StudentMark.objects.create(student=self.s1, subject=self.math, exam=self.exam, marks_obtained=95.0)
        StudentMark.objects.create(student=self.s1, subject=self.ds, exam=self.exam, marks_obtained=90.0)
        StudentMark.objects.create(student=self.s1, subject=self.os, exam=self.exam, marks_obtained=92.0)

        # Student 2: Average student
        self.s2 = Student.objects.create(roll_number="CSE24-002", student_name="Diya Patel")
        StudentMark.objects.create(student=self.s2, subject=self.math, exam=self.exam, marks_obtained=60.0)
        StudentMark.objects.create(student=self.s2, subject=self.ds, exam=self.exam, marks_obtained=65.0)
        StudentMark.objects.create(student=self.s2, subject=self.os, exam=self.exam, marks_obtained=70.0)

        # Student 3: Failed in one subject (OS mark = 30 < 40)
        self.s3 = Student.objects.create(roll_number="CSE24-003", student_name="Vivaan Gupta")
        StudentMark.objects.create(student=self.s3, subject=self.math, exam=self.exam, marks_obtained=50.0)
        StudentMark.objects.create(student=self.s3, subject=self.ds, exam=self.exam, marks_obtained=55.0)
        StudentMark.objects.create(student=self.s3, subject=self.os, exam=self.exam, marks_obtained=30.0)

    # 1. CSV Upload Test
    def test_csv_upload_and_save(self):
        csv_data = (
            "roll_number,student_name,subject_1,subject_2,subject_3,subject_4,subject_5\n"
            "CSE24-010,Kavya Nair,80,85,90,75,88\n"
            "CSE24-011,Rohan Sen,70,72,68,74,75\n"
        )
        file_obj = io.BytesIO(csv_data.encode('utf-8'))
        validator = ResultImportValidator(file_obj, "test_upload.csv", exam=self.exam)
        self.assertTrue(validator.validate(), "CSV with valid structure must pass validation.")
        res = validator.save_to_database()
        self.assertEqual(res['successful_records'], 2)
        self.assertTrue(Student.objects.filter(roll_number="CSE24-010").exists())

    # 2. Excel Upload Test
    def test_excel_upload_and_save(self):
        df = pd.DataFrame([
            {'roll_number': 'CSE24-020', 'student_name': 'Meera Rao', 'subj_a': 82, 'subj_b': 88},
            {'roll_number': 'CSE24-021', 'student_name': 'Kabir Das', 'subj_a': 76, 'subj_b': 79},
        ])
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        validator = ResultImportValidator(excel_buffer, "test_upload.xlsx", exam=self.exam)
        self.assertTrue(validator.validate(), "Excel file with valid records must pass validation.")
        res = validator.save_to_database()
        self.assertEqual(res['successful_records'], 2)
        self.assertTrue(Student.objects.filter(roll_number="CSE24-020").exists())

    # 3. Missing Columns Test
    def test_missing_required_columns(self):
        bad_csv = (
            "student_name,subj1,subj2\n"
            "John Doe,80,85\n"
        )
        file_obj = io.BytesIO(bad_csv.encode('utf-8'))
        validator = ResultImportValidator(file_obj, "missing_col.csv", exam=self.exam)
        self.assertFalse(validator.validate(), "CSV missing roll_number must fail validation.")
        self.assertTrue(any(e['col'] == 'roll_number' for e in validator.errors))

    # 4. Duplicate Roll Numbers Test
    def test_duplicate_roll_numbers(self):
        dup_csv = (
            "roll_number,student_name,subj1,subj2\n"
            "CSE24-100,Student One,80,85\n"
            "CSE24-100,Student Duplicate,70,75\n"
        )
        file_obj = io.BytesIO(dup_csv.encode('utf-8'))
        validator = ResultImportValidator(file_obj, "duplicate.csv", exam=self.exam)
        self.assertFalse(validator.validate(), "CSV with duplicate roll numbers must fail.")
        self.assertTrue(any("Duplicate roll number" in e['message'] for e in validator.errors))

    # 5. Invalid Marks Out of Range (0-100) Test
    def test_invalid_marks_range(self):
        oor_csv = (
            "roll_number,student_name,subj1,subj2\n"
            "CSE24-201,Student Over,150,85\n"
            "CSE24-202,Student Under,-10,70\n"
            "CSE24-203,Student NonNum,ABC,80\n"
        )
        file_obj = io.BytesIO(oor_csv.encode('utf-8'))
        validator = ResultImportValidator(file_obj, "invalid_marks.csv", exam=self.exam)
        self.assertFalse(validator.validate(), "Marks out of [0, 100] or non-numeric must fail.")
        self.assertGreaterEqual(len(validator.errors), 3)

    # 6. Class Average Calculations Test
    def test_class_average_calculations(self):
        engine = ResultAnalyticsEngine(exam=self.exam)
        kpis = engine.get_dashboard_kpis()
        self.assertEqual(kpis['total_students'], 3)
        # S1: (95+90+92)/300 = 277 / 300 = 92.33%
        # S2: (60+65+70)/300 = 195 / 300 = 65.00%
        # S3: (50+55+30)/300 = 135 / 300 = 45.00%
        # Total avg pct = (92.33 + 65.00 + 45.00) / 3 = 67.44%
        expected_avg = round((92.33 + 65.00 + 45.00) / 3.0, 1)
        self.assertAlmostEqual(kpis['class_average_pct'], expected_avg, delta=0.5)
        self.assertEqual(kpis['highest_total_marks'], 277.0)
        self.assertEqual(kpis['lowest_total_marks'], 135.0)

    # 7. Topper Identification & Tie Handling Test
    def test_topper_identification_and_ties(self):
        engine = ResultAnalyticsEngine(exam=self.exam)
        toppers = engine.get_topper_analysis()
        self.assertIsNotNone(toppers['overall_topper'])
        self.assertEqual(toppers['overall_topper']['roll_number'], "CSE24-001")
        self.assertEqual(toppers['overall_topper']['rank'], 1)

        # Subject-wise toppers
        math_topper = next(st for st in toppers['subject_toppers'] if st['subject_code'] == 'MATH4')
        self.assertEqual(math_topper['highest_marks'], 95.0)
        self.assertIn("Aarav Sharma (CSE24-001)", math_topper['topper_names'])

    # 8. Subject-wise Analysis & Difficulty Classification Test
    def test_subject_wise_analysis(self):
        engine = ResultAnalyticsEngine(exam=self.exam)
        subjects = engine.get_subject_difficulty_analysis()
        self.assertEqual(len(subjects), 3)
        math_stat = next(s for s in subjects if s['subject_code'] == 'MATH4')
        # Math marks: 95, 60, 50. Average = 68.33 (< 70), Pass% = 100% (>= 60%) => 'Moderate'
        self.assertEqual(math_stat['pass_percentage'], 100.0)
        self.assertEqual(math_stat['difficulty'], 'Moderate')

        # OS marks: 92, 70, 30. 2 passed, 1 failed => Pass% = 66.67%
        os_stat = next(s for s in subjects if s['subject_code'] == 'OS')
        self.assertAlmostEqual(os_stat['pass_percentage'], 66.67, places=1)
        self.assertEqual(os_stat['fail_percentage'], 33.33)

    # 9. Pass/Fail Calculations & Letter Grading Test
    def test_pass_fail_calculations(self):
        engine = ResultAnalyticsEngine(exam=self.exam)
        df = engine.get_student_summary_dataframe()
        s1_row = df[df['roll_number'] == 'CSE24-001'].iloc[0]
        s3_row = df[df['roll_number'] == 'CSE24-003'].iloc[0]

        self.assertEqual(s1_row['status'], 'Passed')
        self.assertEqual(s1_row['grade'], 'O')

        # S3 failed in OS (30 < 40) => Overall status must be Failed and Grade F
        self.assertEqual(s3_row['status'], 'Failed')
        self.assertEqual(s3_row['grade'], 'F')

    # 10. Report Generation (CSV & PDF) Test
    def test_report_generation(self):
        service = ReportExportService(exam=self.exam)

        # CSV Exports
        for rtype in ['class_summary', 'students_ledger', 'subjects', 'toppers']:
            csv_bytes, fname = service.export_csv(report_type=rtype)
            self.assertGreater(len(csv_bytes), 0, f"CSV {rtype} must not be empty.")
            self.assertTrue(fname.endswith('.csv'))

        # PDF Exports
        for rtype in ['class_summary', 'students_ledger', 'subjects', 'toppers']:
            pdf_bytes, fname = service.export_pdf(report_type=rtype)
            self.assertGreater(len(pdf_bytes), 0, f"PDF {rtype} must not be empty.")
            self.assertTrue(pdf_bytes.startswith(b'%PDF'), f"PDF {rtype} must be a valid PDF binary.")
            self.assertTrue(fname.endswith('.pdf'))

    # 11. Web Views HTTP 200 Status Test
    def test_web_views_and_charts_api(self):
        endpoints = [
            reverse('dashboard'),
            reverse('upload_results'),
            reverse('student_results'),
            reverse('topper_analysis'),
            reverse('subject_analysis'),
            reverse('reports'),
            reverse('chart_data_api'),
            reverse('download_sample_template', kwargs={'file_type': 'csv'}),
            reverse('download_sample_template', kwargs={'file_type': 'xlsx'}),
            reverse('export_report_csv') + '?type=class_summary',
            reverse('export_report_pdf') + '?type=class_summary',
        ]
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} failed with status {response.status_code}")
