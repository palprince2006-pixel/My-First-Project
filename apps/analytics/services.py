import numpy as np
import pandas as pd
from django.conf import settings
from apps.results.models import StudentMark, Subject, Exam
from apps.students.models import Student

class ResultAnalyticsEngine:
    """
    High-performance statistical analytics engine using Pandas and NumPy.
    Processes relational SQL marks and computes institution-grade metrics,
    grade distributions, rankings, and subject difficulty indicators.
    """

    def __init__(self, exam=None):
        self.exam = exam or Exam.objects.first()
        self.grading_scale = getattr(settings, 'ACADEMIC_SETTINGS', {}).get('GRADE_SCALE', [
            ('O', 90.0, 'Outstanding'),
            ('A+', 80.0, 'Excellent'),
            ('A', 70.0, 'Very Good'),
            ('B+', 60.0, 'Good'),
            ('B', 50.0, 'Above Average'),
            ('C', 40.0, 'Average / Pass'),
            ('F', 0.0, 'Fail'),
        ])
        self.passing_percentage = getattr(settings, 'ACADEMIC_SETTINGS', {}).get('DEFAULT_PASSING_PERCENTAGE', 40.0)
        self.difficulty_thresholds = getattr(settings, 'ACADEMIC_SETTINGS', {}).get('DIFFICULTY_THRESHOLDS', {
            'EASY_MIN_AVG': 70.0,
            'EASY_MIN_PASS_PCT': 80.0,
            'MODERATE_MIN_AVG': 50.0,
            'MODERATE_MIN_PASS_PCT': 60.0,
        })
        self._raw_marks_df = None
        self._student_summary_df = None
        self._subject_summary_df = None

    def get_raw_marks_dataframe(self):
        """
        Extracts all student marks for the active exam into a Pandas DataFrame.
        """
        if self._raw_marks_df is not None:
            return self._raw_marks_df

        if not self.exam:
            self._raw_marks_df = pd.DataFrame(columns=[
                'student_id', 'roll_number', 'student_name', 'department', 'section',
                'subject_id', 'subject_code', 'subject_name', 'passing_marks', 'maximum_marks', 'marks_obtained'
            ])
            return self._raw_marks_df

        marks_qs = StudentMark.objects.filter(exam=self.exam).select_related('student', 'subject')
        
        records = []
        for m in marks_qs:
            records.append({
                'student_id': m.student_id,
                'roll_number': m.student.roll_number,
                'student_name': m.student.student_name,
                'department': m.student.department,
                'section': m.student.section,
                'subject_id': m.subject_id,
                'subject_code': m.subject.subject_code,
                'subject_name': m.subject.subject_name,
                'passing_marks': float(m.subject.passing_marks),
                'maximum_marks': float(m.subject.maximum_marks),
                'marks_obtained': float(m.marks_obtained),
                'is_subject_passed': float(m.marks_obtained) >= float(m.subject.passing_marks)
            })

        self._raw_marks_df = pd.DataFrame(records)
        return self._raw_marks_df

    def assign_grade(self, percentage):
        """Maps percentage to academic letter grade based on configurable scale."""
        for grade, threshold, _ in self.grading_scale:
            if percentage >= threshold:
                return grade
        return 'F'

    def get_student_summary_dataframe(self):
        """
        Generates comprehensive student-level performance analysis:
        Total marks, Max possible, Average, Percentage, Grade, Pass/Fail, and Rank.
        """
        if self._student_summary_df is not None:
            return self._student_summary_df

        df = self.get_raw_marks_dataframe()
        if df.empty:
            self._student_summary_df = pd.DataFrame(columns=[
                'student_id', 'roll_number', 'student_name', 'department', 'section',
                'total_marks', 'max_possible_marks', 'average_marks', 'percentage',
                'passed_all_subjects', 'status', 'grade', 'rank'
            ])
            return self._student_summary_df

        # Group by student
        grouped = df.groupby(['student_id', 'roll_number', 'student_name', 'department', 'section'])

        student_rows = []
        for (sid, roll, name, dept, sec), group in grouped:
            total_marks = group['marks_obtained'].sum()
            max_marks = group['maximum_marks'].sum()
            subj_count = len(group)
            avg_marks = group['marks_obtained'].mean() if subj_count > 0 else 0.0
            pct = (total_marks / max_marks * 100.0) if max_marks > 0 else 0.0

            # Pass condition: Passed every subject individual passing criteria AND overall % >= threshold
            passed_all = bool(group['is_subject_passed'].all())
            overall_pass = passed_all and (pct >= self.passing_percentage)

            grade = self.assign_grade(pct) if overall_pass else 'F'

            student_rows.append({
                'student_id': sid,
                'roll_number': roll,
                'student_name': name,
                'department': dept,
                'section': sec,
                'subject_count': subj_count,
                'total_marks': round(total_marks, 2),
                'max_possible_marks': round(max_marks, 2),
                'average_marks': round(avg_marks, 2),
                'percentage': round(pct, 2),
                'passed_all_subjects': passed_all,
                'status': 'Passed' if overall_pass else 'Failed',
                'grade': grade
            })

        summary_df = pd.DataFrame(student_rows)

        if not summary_df.empty:
            # Rank students dynamically by total_marks descending
            # Using method='min' to handle tied marks properly (e.g. 1, 2, 2, 4)
            summary_df['rank'] = summary_df['total_marks'].rank(ascending=False, method='min').astype(int)
            summary_df = summary_df.sort_values(by=['rank', 'roll_number'])

        self._student_summary_df = summary_df
        return self._student_summary_df

    def get_dashboard_kpis(self):
        """
        Computes dynamic institution KPIs for dashboard cards:
        Total Students, Class Average, Pass Percentage, Highest Marks,
        Lowest Marks, Failed Students, Passed Students, Median, and Std Dev.
        """
        student_df = self.get_student_summary_dataframe()
        raw_df = self.get_raw_marks_dataframe()

        if student_df.empty:
            return {
                'total_students': 0,
                'passed_students': 0,
                'failed_students': 0,
                'pass_percentage': 0.0,
                'class_average_pct': 0.0,
                'class_average_total': 0.0,
                'highest_total_marks': 0.0,
                'lowest_total_marks': 0.0,
                'highest_percentage': 0.0,
                'lowest_percentage': 0.0,
                'median_percentage': 0.0,
                'std_deviation': 0.0,
                'total_subjects': 0,
            }

        total_students = len(student_df)
        passed_students = int((student_df['status'] == 'Passed').sum())
        failed_students = int((student_df['status'] == 'Failed').sum())
        pass_pct = round((passed_students / total_students * 100.0), 2) if total_students > 0 else 0.0

        pct_array = student_df['percentage'].to_numpy()
        tot_array = student_df['total_marks'].to_numpy()

        class_avg_pct = round(float(np.mean(pct_array)), 2)
        class_avg_tot = round(float(np.mean(tot_array)), 2)
        highest_tot = round(float(np.max(tot_array)), 2)
        lowest_tot = round(float(np.min(tot_array)), 2)
        highest_pct = round(float(np.max(pct_array)), 2)
        lowest_pct = round(float(np.min(pct_array)), 2)

        median_pct = round(float(np.median(pct_array)), 2)
        # Sample standard deviation (ddof=1) if N > 1, else 0
        std_dev = round(float(np.std(pct_array, ddof=1)), 2) if len(pct_array) > 1 else 0.0

        unique_subjects = raw_df['subject_id'].nunique() if not raw_df.empty else 0

        return {
            'total_students': total_students,
            'passed_students': passed_students,
            'failed_students': failed_students,
            'pass_percentage': pass_pct,
            'class_average_pct': class_avg_pct,
            'class_average_total': class_avg_tot,
            'highest_total_marks': highest_tot,
            'lowest_total_marks': lowest_tot,
            'highest_percentage': highest_pct,
            'lowest_percentage': lowest_pct,
            'median_percentage': median_pct,
            'std_deviation': std_dev,
            'total_subjects': unique_subjects,
        }

    def get_topper_analysis(self):
        """
        Identifies overall class toppers (Top 1, Top 5, Top 10)
        and subject-wise toppers handling mark ties accurately.
        """
        student_df = self.get_student_summary_dataframe()
        raw_df = self.get_raw_marks_dataframe()

        if student_df.empty:
            return {
                'overall_topper': None,
                'top_5_students': [],
                'top_10_students': [],
                'subject_toppers': [],
            }

        # Overall Class Topper
        topper_row = student_df.iloc[0].to_dict()

        # Top 5 students
        top_5 = student_df.head(5).to_dict(orient='records')
        top_10 = student_df.head(10).to_dict(orient='records')

        # Subject-wise toppers
        subject_toppers = []
        if not raw_df.empty:
            for (subj_id, code, name), group in raw_df.groupby(['subject_id', 'subject_code', 'subject_name']):
                max_mark = group['marks_obtained'].max()
                top_scorers = group[group['marks_obtained'] == max_mark]
                topper_names = [f"{r['student_name']} ({r['roll_number']})" for _, r in top_scorers.iterrows()]
                
                subject_toppers.append({
                    'subject_id': subj_id,
                    'subject_code': code,
                    'subject_name': name,
                    'highest_marks': round(float(max_mark), 2),
                    'topper_names': topper_names,
                    'scorers_count': len(top_scorers),
                    'first_topper_name': top_scorers.iloc[0]['student_name'],
                    'first_topper_roll': top_scorers.iloc[0]['roll_number'],
                })

        return {
            'overall_topper': topper_row,
            'top_5_students': top_5,
            'top_10_students': top_10,
            'subject_toppers': subject_toppers,
        }

    def classify_difficulty(self, avg_pct, pass_pct):
        """
        Classifies subject difficulty analytically based on configured thresholds.
        Analytical indicator, not a definitive measurement.
        """
        t = self.difficulty_thresholds
        if avg_pct >= t['EASY_MIN_AVG'] and pass_pct >= t['EASY_MIN_PASS_PCT']:
            return 'Easy', 'text-tertiary bg-tertiary-fixed/30 border-tertiary-fixed'
        elif avg_pct >= t['MODERATE_MIN_AVG'] and pass_pct >= t['MODERATE_MIN_PASS_PCT']:
            return 'Moderate', 'text-secondary-fixed-dim bg-secondary-container border-secondary'
        else:
            return 'Difficult', 'text-error bg-error-container border-error'

    def get_subject_difficulty_analysis(self):
        """
        Computes statistical analysis for each subject:
        Average, Pass %, Fail %, Highest, Lowest, NumPy Std Dev, and Difficulty Category.
        """
        if self._subject_summary_df is not None:
            return self._subject_summary_df.to_dict(orient='records')

        raw_df = self.get_raw_marks_dataframe()
        if raw_df.empty:
            return []

        subjects_data = []
        for (subj_id, code, name, max_m, pass_m), group in raw_df.groupby(
            ['subject_id', 'subject_code', 'subject_name', 'maximum_marks', 'passing_marks']
        ):
            marks = group['marks_obtained'].to_numpy()
            total_students = len(marks)
            passed_count = int(np.sum(marks >= pass_m))
            failed_count = total_students - passed_count

            pass_pct = round((passed_count / total_students * 100.0), 2) if total_students > 0 else 0.0
            fail_pct = round((failed_count / total_students * 100.0), 2) if total_students > 0 else 0.0

            avg_marks = round(float(np.mean(marks)), 2)
            avg_pct = round((avg_marks / max_m * 100.0), 2) if max_m > 0 else 0.0
            std_dev = round(float(np.std(marks, ddof=1)), 2) if len(marks) > 1 else 0.0
            highest = round(float(np.max(marks)), 2)
            lowest = round(float(np.min(marks)), 2)

            difficulty_label, difficulty_class = self.classify_difficulty(avg_pct, pass_pct)

            subjects_data.append({
                'subject_id': subj_id,
                'subject_code': code,
                'subject_name': name,
                'maximum_marks': max_m,
                'passing_marks': pass_m,
                'total_students': total_students,
                'passed_students': passed_count,
                'failed_students': failed_count,
                'pass_percentage': pass_pct,
                'fail_percentage': fail_pct,
                'average_marks': avg_marks,
                'average_percentage': avg_pct,
                'highest_marks': highest,
                'lowest_marks': lowest,
                'standard_deviation': std_dev,
                'difficulty': difficulty_label,
                'difficulty_badge_class': difficulty_class,
            })

        self._subject_summary_df = pd.DataFrame(subjects_data)
        return subjects_data

    def get_chart_data(self):
        """
        Produces clean JSON datasets strictly formatted for Chart.js:
        1. Subject-wise average marks – Bar Chart
        2. Pass vs Fail – Doughnut Chart
        3. Student performance distribution – Bar Chart
        4. Grade distribution – Pie Chart
        5. Subject comparison – Horizontal Bar Chart
        """
        student_df = self.get_student_summary_dataframe()
        subject_stats = self.get_subject_difficulty_analysis()

        # Chart 1: Subject-wise average marks
        subj_labels = [s['subject_name'] for s in subject_stats]
        subj_averages = [s['average_marks'] for s in subject_stats]
        subj_passing = [s['passing_marks'] for s in subject_stats]

        # Chart 2: Pass vs Fail
        passed_count = int((student_df['status'] == 'Passed').sum()) if not student_df.empty else 0
        failed_count = int((student_df['status'] == 'Failed').sum()) if not student_df.empty else 0

        # Chart 3: Performance distribution (Score ranges)
        # Buckets: 0-39 (Fail), 40-59 (Pass/Avg), 60-74 (Good), 75-89 (Distinction), 90-100 (Outstanding)
        buckets = {
            '< 40%': 0,
            '40% - 59%': 0,
            '60% - 74%': 0,
            '75% - 89%': 0,
            '90% - 100%': 0
        }
        if not student_df.empty:
            pcts = student_df['percentage'].tolist()
            for p in pcts:
                if p < 40:
                    buckets['< 40%'] += 1
                elif p < 60:
                    buckets['40% - 59%'] += 1
                elif p < 75:
                    buckets['60% - 74%'] += 1
                elif p < 90:
                    buckets['75% - 89%'] += 1
                else:
                    buckets['90% - 100%'] += 1

        # Chart 4: Grade distribution
        grades_count = {'O': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'F': 0}
        if not student_df.empty:
            for g in student_df['grade'].tolist():
                if g in grades_count:
                    grades_count[g] += 1
                else:
                    grades_count[g] = 1

        # Chart 5: Subject comparison (Pass % vs Fail %)
        subj_pass_pcts = [s['pass_percentage'] for s in subject_stats]
        subj_fail_pcts = [s['fail_percentage'] for s in subject_stats]

        return {
            'chart1_subject_averages': {
                'labels': subj_labels,
                'averages': subj_averages,
                'passing_marks': subj_passing
            },
            'chart2_pass_fail': {
                'labels': ['Passed Students', 'Failed Students'],
                'data': [passed_count, failed_count],
            },
            'chart3_performance_distribution': {
                'labels': list(buckets.keys()),
                'data': list(buckets.values()),
            },
            'chart4_grade_distribution': {
                'labels': list(grades_count.keys()),
                'data': list(grades_count.values()),
            },
            'chart5_subject_comparison': {
                'labels': subj_labels,
                'pass_percentages': subj_pass_pcts,
                'fail_percentages': subj_fail_pcts,
            }
        }
