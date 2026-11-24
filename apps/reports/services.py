import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from apps.analytics.services import ResultAnalyticsEngine
from apps.results.models import Exam, Subject

class ReportExportService:
    """
    Generates institutional CSV and PDF exports for:
    - Overall Class Performance Summary
    - Student Performance Ledger
    - Subject-wise Analysis Matrix
    - Toppers and Merit Leaderboard
    """

    def __init__(self, exam=None):
        self.exam = exam or Exam.objects.first()
        self.engine = ResultAnalyticsEngine(exam=self.exam)

    def export_csv(self, report_type='students_ledger'):
        """Generates CSV bytes and filename for the requested report type."""
        output = io.StringIO()
        writer = csv.writer(output)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exam_slug = (self.exam.exam_name if self.exam else 'general').replace(' ', '_').lower()

        if report_type == 'class_summary':
            filename = f"class_performance_{exam_slug}_{timestamp}.csv"
            kpis = self.engine.get_dashboard_kpis()
            writer.writerow(['STUDENT RESULT ANALYZER - INSTITUTIONAL CLASS PERFORMANCE SUMMARY'])
            writer.writerow(['Exam Name', self.exam.exam_name if self.exam else 'N/A'])
            writer.writerow(['Academic Year', self.exam.academic_year if self.exam else 'N/A'])
            writer.writerow(['Semester', self.exam.semester if self.exam else 'N/A'])
            writer.writerow(['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            writer.writerow(['Metric', 'Calculated Value'])
            writer.writerow(['Total Students Enrolled', kpis['total_students']])
            writer.writerow(['Students Cleared / Passed', kpis['passed_students']])
            writer.writerow(['Failed Students', kpis['failed_students']])
            writer.writerow(['Overall Pass Percentage', f"{kpis['pass_percentage']}%"])
            writer.writerow(['Class Average Percentage', f"{kpis['class_average_pct']}%"])
            writer.writerow(['Class Average Total Marks', kpis['class_average_total']])
            writer.writerow(['Highest Total Marks', kpis['highest_total_marks']])
            writer.writerow(['Lowest Total Marks', kpis['lowest_total_marks']])
            writer.writerow(['Median Percentage (NumPy)', f"{kpis['median_percentage']}%"])
            writer.writerow(['Standard Deviation (NumPy)', kpis['std_deviation']])
            writer.writerow(['Evaluated Subjects Count', kpis['total_subjects']])

        elif report_type == 'subjects':
            filename = f"subject_difficulty_{exam_slug}_{timestamp}.csv"
            subjects = self.engine.get_subject_difficulty_analysis()
            writer.writerow(['Subject Code', 'Subject Name', 'Class Average', 'Pass %', 'Fail %', 'Highest', 'Lowest', 'Std Dev', 'Difficulty'])
            for s in subjects:
                writer.writerow([
                    s['subject_code'], s['subject_name'], s['average_marks'],
                    f"{s['pass_percentage']}%", f"{s['fail_percentage']}%",
                    s['highest_marks'], s['lowest_marks'], s['standard_deviation'], s['difficulty']
                ])

        elif report_type == 'toppers':
            filename = f"toppers_leaderboard_{exam_slug}_{timestamp}.csv"
            toppers = self.engine.get_topper_analysis()
            writer.writerow(['TOP 10 CLASS RANKINGS'])
            writer.writerow(['Rank', 'Roll Number', 'Student Name', 'Total Marks', 'Percentage', 'Grade', 'Status'])
            for s in toppers['top_10_students']:
                writer.writerow([
                    s['rank'], s['roll_number'], s['student_name'],
                    s['total_marks'], f"{s['percentage']}%", s['grade'], s['status']
                ])
            writer.writerow([])
            writer.writerow(['SUBJECT-WISE HIGHEST SCORERS'])
            writer.writerow(['Subject Code', 'Subject Name', 'Highest Mark', 'Topper(s)'])
            for st in toppers['subject_toppers']:
                writer.writerow([
                    st['subject_code'], st['subject_name'], st['highest_marks'], ", ".join(st['topper_names'])
                ])

        else:  # students_ledger
            filename = f"students_marks_ledger_{exam_slug}_{timestamp}.csv"
            students_df = self.engine.get_student_summary_dataframe()
            raw_df = self.engine.get_raw_marks_dataframe()
            
            subjects = list(raw_df[['subject_code', 'subject_name']].drop_duplicates().to_dict(orient='records')) if not raw_df.empty else []
            subj_codes = [s['subject_code'] for s in subjects]

            # Header
            header = ['Rank', 'Roll Number', 'Student Name'] + [s['subject_name'] for s in subjects] + ['Total Marks', 'Percentage', 'Grade', 'Status']
            writer.writerow(header)

            marks_pivot = {}
            if not raw_df.empty:
                for _, r in raw_df.iterrows():
                    marks_pivot[(r['student_id'], r['subject_code'])] = r['marks_obtained']

            for _, s in students_df.iterrows():
                row = [s['rank'], s['roll_number'], s['student_name']]
                for code in subj_codes:
                    row.append(marks_pivot.get((s['student_id'], code), '-'))
                row.extend([s['total_marks'], f"{s['percentage']}%", s['grade'], s['status']])
                writer.writerow(row)

        output.seek(0)
        return output.getvalue().encode('utf-8'), filename

    def export_pdf(self, report_type='students_ledger'):
        """Generates a professional ReportLab PDF for the requested report type."""
        buffer = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exam_slug = (self.exam.exam_name if self.exam else 'general').replace(' ', '_').lower()

        # Landscape orientation for wide tabular data, Portrait for summaries
        if report_type in ['students_ledger', 'subjects']:
            doc = SimpleDocTemplate(
                buffer, pagesize=landscape(letter),
                leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
            )
        else:
            doc = SimpleDocTemplate(
                buffer, pagesize=letter,
                leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
            )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#00236f'),
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#565e74'),
            spaceAfter=12
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0b1c30')
        )
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        elements = []

        # Common Institutional Header
        exam_name = self.exam.exam_name if self.exam else "General Academic Assessment"
        acad_year = self.exam.academic_year if self.exam else "2024-2025"
        sem = self.exam.semester if self.exam else "Sem IV"
        dept = self.exam.department if self.exam else "Computer Science & Engineering"

        elements.append(Paragraph("STUDENT RESULT ANALYZER", title_style))
        elements.append(Paragraph(f"Institution Academic Report • Department of {dept}", subtitle_style))
        elements.append(Paragraph(f"Assessment Cycle: <b>{exam_name}</b> | Academic Year: <b>{acad_year}</b> ({sem}) | Date: <b>{datetime.now().strftime('%Y-%m-%d')}</b>", subtitle_style))
        elements.append(Spacer(1, 10))

        if report_type == 'class_summary':
            filename = f"class_summary_{exam_slug}_{timestamp}.pdf"
            kpis = self.engine.get_dashboard_kpis()

            elements.append(Paragraph("<b>INSTITUTIONAL PERFORMANCE SUMMARY</b>", styles['Heading2']))
            elements.append(Spacer(1, 6))

            kpi_data = [
                [Paragraph("<b>Metric Dimension</b>", table_header_style), Paragraph("<b>Statistical Value</b>", table_header_style)],
                [Paragraph("Total Students Enrolled", table_cell_style), Paragraph(str(kpis['total_students']), table_cell_style)],
                [Paragraph("Passed Students", table_cell_style), Paragraph(f"{kpis['passed_students']} ({kpis['pass_percentage']}%)", table_cell_style)],
                [Paragraph("Failed Students", table_cell_style), Paragraph(str(kpis['failed_students']), table_cell_style)],
                [Paragraph("Class Average Percentage", table_cell_style), Paragraph(f"{kpis['class_average_pct']}%", table_cell_style)],
                [Paragraph("Class Average Total Marks", table_cell_style), Paragraph(str(kpis['class_average_total']), table_cell_style)],
                [Paragraph("Highest Aggregate Marks", table_cell_style), Paragraph(f"{kpis['highest_total_marks']} ({kpis['highest_percentage']}%)", table_cell_style)],
                [Paragraph("Lowest Aggregate Marks", table_cell_style), Paragraph(f"{kpis['lowest_total_marks']} ({kpis['lowest_percentage']}%)", table_cell_style)],
                [Paragraph("Median Percentage (NumPy)", table_cell_style), Paragraph(f"{kpis['median_percentage']}%", table_cell_style)],
                [Paragraph("Standard Deviation (NumPy)", table_cell_style), Paragraph(str(kpis['std_deviation']), table_cell_style)],
            ]

            t = Table(kpi_data, colWidths=[280, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00236f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5c5d3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff4ff')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(t)

        elif report_type == 'subjects':
            filename = f"subject_difficulty_{exam_slug}_{timestamp}.pdf"
            subjects = self.engine.get_subject_difficulty_analysis()

            elements.append(Paragraph("<b>SUBJECT-WISE PERFORMANCE & DIFFICULTY MATRIX</b>", styles['Heading2']))
            elements.append(Spacer(1, 6))

            headers = ["Code", "Subject Title", "Average", "Pass %", "Fail %", "Peak", "Low", "StdDev", "Difficulty"]
            table_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

            for s in subjects:
                table_data.append([
                    Paragraph(s['subject_code'], table_cell_style),
                    Paragraph(s['subject_name'], table_cell_style),
                    Paragraph(str(s['average_marks']), table_cell_style),
                    Paragraph(f"{s['pass_percentage']}%", table_cell_style),
                    Paragraph(f"{s['fail_percentage']}%", table_cell_style),
                    Paragraph(str(s['highest_marks']), table_cell_style),
                    Paragraph(str(s['lowest_marks']), table_cell_style),
                    Paragraph(str(s['standard_deviation']), table_cell_style),
                    Paragraph(s['difficulty'], table_cell_style),
                ])

            t = Table(table_data, colWidths=[65, 170, 50, 50, 50, 45, 45, 55, 65])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00236f')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5c5d3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff4ff')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)

        elif report_type == 'toppers':
            filename = f"toppers_leaderboard_{exam_slug}_{timestamp}.pdf"
            toppers = self.engine.get_topper_analysis()

            elements.append(Paragraph("<b>TOP 10 MERIT LEADERBOARD</b>", styles['Heading2']))
            elements.append(Spacer(1, 6))

            headers = ["Rank", "Roll No", "Student Name", "Total Score", "Percentage", "Grade", "Status"]
            table_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

            for s in toppers['top_10_students']:
                table_data.append([
                    Paragraph(f"#{s['rank']}", table_cell_style),
                    Paragraph(s['roll_number'], table_cell_style),
                    Paragraph(s['student_name'], table_cell_style),
                    Paragraph(str(s['total_marks']), table_cell_style),
                    Paragraph(f"{s['percentage']}%", table_cell_style),
                    Paragraph(s['grade'], table_cell_style),
                    Paragraph(s['status'], table_cell_style),
                ])

            t = Table(table_data, colWidths=[40, 75, 160, 65, 65, 45, 60])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00236f')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5c5d3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff4ff')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)

        else:  # students_ledger
            filename = f"students_marks_ledger_{exam_slug}_{timestamp}.pdf"
            students_df = self.engine.get_student_summary_dataframe()
            raw_df = self.engine.get_raw_marks_dataframe()

            subjects = list(raw_df[['subject_code', 'subject_name']].drop_duplicates().to_dict(orient='records')) if not raw_df.empty else []
            subj_codes = [s['subject_code'] for s in subjects]

            elements.append(Paragraph("<b>STUDENT RESULTS MARKS LEDGER</b>", styles['Heading2']))
            elements.append(Spacer(1, 6))

            headers = ["Rank", "Roll No", "Student Name"] + [s['subject_code'] for s in subjects] + ["Total", "%", "Grade", "Status"]
            table_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

            marks_pivot = {}
            if not raw_df.empty:
                for _, r in raw_df.iterrows():
                    marks_pivot[(r['student_id'], r['subject_code'])] = r['marks_obtained']

            for _, s in students_df.iterrows():
                row = [
                    Paragraph(f"#{s['rank']}", table_cell_style),
                    Paragraph(s['roll_number'], table_cell_style),
                    Paragraph(s['student_name'][:18], table_cell_style),
                ]
                for code in subj_codes:
                    val = marks_pivot.get((s['student_id'], code), '-')
                    row.append(Paragraph(str(val), table_cell_style))
                row.extend([
                    Paragraph(str(s['total_marks']), table_cell_style),
                    Paragraph(f"{s['percentage']}%", table_cell_style),
                    Paragraph(s['grade'], table_cell_style),
                    Paragraph(s['status'], table_cell_style),
                ])
                table_data.append(row)

            # Calculate responsive column widths for landscape
            col_widths = [32, 60, 105] + [48] * len(subj_codes) + [45, 45, 38, 48]
            t = Table(table_data, colWidths=col_widths, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00236f')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5c5d3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff4ff')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(t)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue(), filename
