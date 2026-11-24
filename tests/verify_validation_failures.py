import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.imports.services import ResultImportValidator

def test_failures():
    # 1. Missing columns
    with open('sample_data/invalid_missing_columns.csv', 'rb') as f:
        v1 = ResultImportValidator(f, 'invalid_missing_columns.csv')
        v1_valid = v1.validate()
        print(f"Missing cols valid? {v1_valid}. Errors caught: {len(v1.errors)}. First error: {v1.errors[0]['message']}")
        assert not v1_valid

    # 2. Duplicate roll
    with open('sample_data/invalid_duplicate_roll.csv', 'rb') as f:
        v2 = ResultImportValidator(f, 'invalid_duplicate_roll.csv')
        v2_valid = v2.validate()
        print(f"Duplicate roll valid? {v2_valid}. Errors caught: {len(v2.errors)}. First error: {v2.errors[0]['message']}")
        assert not v2_valid

    # 3. Out of range marks
    with open('sample_data/invalid_out_of_range.csv', 'rb') as f:
        v3 = ResultImportValidator(f, 'invalid_out_of_range.csv')
        v3_valid = v3.validate()
        print(f"Out of range marks valid? {v3_valid}. Errors caught: {len(v3.errors)}. First error: {v3.errors[0]['message']}")
        assert not v3_valid

    # 4. Excel upload
    with open('sample_data/cse_sem4_results.xlsx', 'rb') as f:
        v4 = ResultImportValidator(f, 'cse_sem4_results.xlsx')
        v4_valid = v4.validate()
        print(f"Excel file valid? {v4_valid}. Rows count: {len(v4.df)}")
        assert v4_valid

    print("\nALL VALIDATION EDGE CASES PASSED WITH DISTINCTION!")

if __name__ == '__main__':
    test_failures()
