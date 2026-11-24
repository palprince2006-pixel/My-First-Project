import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.imports.services import ResultImportValidator
from apps.analytics.services import ResultAnalyticsEngine

def test_pipeline():
    with open('sample_data/cse_sem4_results.csv', 'rb') as f:
        validator = ResultImportValidator(f, 'cse_sem4_results.csv')
        valid = validator.validate()
        print(f"Validation valid: {valid}, Errors count: {len(validator.errors)}")
        if valid:
            save_res = validator.save_to_database()
            print("Database commit outcome:", save_res)

    engine = ResultAnalyticsEngine()
    kpis = engine.get_dashboard_kpis()
    print("\n--- INSTITUTIONAL DASHBOARD KPIS ---")
    for k, v in kpis.items():
        print(f"  {k}: {v}")

    toppers = engine.get_topper_analysis()
    print("\n--- TOPPER ANALYSIS ---")
    print(f"Overall Topper: {toppers['overall_topper']['student_name']} (Roll: {toppers['overall_topper']['roll_number']}), Total: {toppers['overall_topper']['total_marks']}")
    print(f"Top 5 Count: {len(toppers['top_5_students'])}")
    for t in toppers['top_5_students']:
        print(f"  Rank {t['rank']}: {t['student_name']} - {t['percentage']}% ({t['grade']})")

    subjects = engine.get_subject_difficulty_analysis()
    print("\n--- SUBJECT DIFFICULTY ANALYSIS ---")
    for s in subjects:
        print(f"  {s['subject_name']}: Avg={s['average_marks']}, Pass%={s['pass_percentage']}%, StdDev={s['standard_deviation']}, Category={s['difficulty']}")

    charts = engine.get_chart_data()
    print("\n--- CHART DATA READY ---")
    print(f"Subjects for Chart 1: {charts['chart1_subject_averages']['labels']}")
    print(f"Pass/Fail Chart 2: {charts['chart2_pass_fail']}")
    print(f"Performance Distribution Chart 3: {charts['chart3_performance_distribution']}")
    print(f"Grade Distribution Chart 4: {charts['chart4_grade_distribution']}")

if __name__ == '__main__':
    test_pipeline()
