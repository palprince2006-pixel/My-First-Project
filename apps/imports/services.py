import os
import re
import pandas as pd
import numpy as np
from django.db import transaction
from django.conf import settings
from apps.students.models import Student
from apps.results.models import Subject, Exam, StudentMark
from apps.imports.models import ImportHistory

class ResultImportValidator:
    """
    Validates and processes student result files (CSV / Excel) using Pandas.
    Enforces strict data integrity, edge-range verification (0-100),
    column schemas, missing values, and duplicate roll numbers.
    """

    REQUIRED_IDENTIFIER_COLS = ['roll_number', 'student_name']

    def __init__(self, file_obj, filename, exam=None, max_marks=100.0, passing_marks=40.0):
        self.file_obj = file_obj
        self.filename = filename
        self.exam = exam
        self.max_marks = max_marks
        self.passing_marks = passing_marks
        self.df = None
        self.subject_cols = []
        self.errors = []
        self.warnings = []
        self.preview_data = []
        self.summary = {
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'duplicate_rolls': 0,
            'detected_subjects': [],
        }

    def _normalize_col_name(self, col):
        """Converts column headers to snake_case alphanumeric strings."""
        c = str(col).strip().lower()
        c = re.sub(r'[\s\-\/\.]+', '_', c)
        c = re.sub(r'[^a-z0-9_]', '', c)
        return c

    def read_dataframe(self):
        """Loads CSV or XLSX into a Pandas DataFrame."""
        ext = os.path.splitext(self.filename)[1].lower()
        if ext not in ['.csv', '.xlsx', '.xls']:
            self.errors.append({
                'row': 0,
                'col': 'file_format',
                'value': ext,
                'message': f"Unsupported file format '{ext}'. Only .csv and .xlsx files are supported."
            })
            return False

        try:
            if hasattr(self.file_obj, 'seek'):
                self.file_obj.seek(0)

            if ext == '.csv':
                # Try reading with utf-8, fallback to latin-1
                try:
                    self.df = pd.read_csv(self.file_obj, encoding='utf-8')
                except UnicodeDecodeError:
                    if hasattr(self.file_obj, 'seek'):
                        self.file_obj.seek(0)
                    self.df = pd.read_csv(self.file_obj, encoding='latin-1')
            else:
                self.df = pd.read_excel(self.file_obj, engine='openpyxl')

        except Exception as e:
            self.errors.append({
                'row': 0,
                'col': 'file_read',
                'value': 'corrupt_file',
                'message': f"Could not parse file: {str(e)}"
            })
            return False

        if self.df is None or self.df.empty:
            self.errors.append({
                'row': 0,
                'col': 'data',
                'value': 'empty',
                'message': "The uploaded file contains no data rows."
            })
            return False

        # Normalize column headers
        col_mapping = {c: self._normalize_col_name(c) for c in self.df.columns}
        self.df.rename(columns=col_mapping, inplace=True)
        return True

    def validate(self):
        """
        Executes comprehensive validation on the uploaded dataset:
        1. Required identifiers check (roll_number, student_name).
        2. Subject columns identification.
        3. Missing data check.
        4. Duplicate roll numbers check within file.
        5. Numeric range check for marks (0 to max_marks).
        """
        if not self.read_dataframe():
            return False

        raw_cols = list(self.df.columns)

        # Check required identifier columns
        for req_col in self.REQUIRED_IDENTIFIER_COLS:
            if req_col not in raw_cols:
                # Also check alternative names like 'roll_no', 'rollno', 'name'
                alt_names = {
                    'roll_number': ['roll_no', 'rollno', 'student_id', 'reg_no', 'registration_no'],
                    'student_name': ['name', 'studentname', 'candidate_name', 'full_name']
                }
                found = False
                for alt in alt_names.get(req_col, []):
                    if alt in raw_cols:
                        self.df.rename(columns={alt: req_col}, inplace=True)
                        found = True
                        break
                if not found:
                    self.errors.append({
                        'row': 1,
                        'col': req_col,
                        'value': 'missing',
                        'message': f"Required column '{req_col}' is missing from the file header."
                    })

        if any(e['col'] in self.REQUIRED_IDENTIFIER_COLS for e in self.errors):
            return False

        # Identify subject columns (all columns except roll_number, student_name, email, department, section)
        non_subject_cols = set(self.REQUIRED_IDENTIFIER_COLS + ['email', 'department', 'section', 'id', 's_no', 'sno'])
        self.subject_cols = [c for c in self.df.columns if c not in non_subject_cols]

        if not self.subject_cols:
            self.errors.append({
                'row': 1,
                'col': 'subjects',
                'value': 'missing',
                'message': "No subject columns detected. Expected columns like subject_1, subject_2, ... or specific subject names."
            })
            return False

        self.summary['detected_subjects'] = self.subject_cols
        self.summary['total_rows'] = len(self.df)

        # 1. Check duplicate roll numbers inside uploaded file
        # Clean roll_number strings
        self.df['roll_number'] = self.df['roll_number'].astype(str).str.strip()
        duplicates = self.df[self.df.duplicated(subset=['roll_number'], keep=False)]
        if not duplicates.empty:
            duplicate_rolls = duplicates['roll_number'].unique()
            self.summary['duplicate_rolls'] = len(duplicate_rolls)
            for roll in duplicate_rolls:
                dup_indices = self.df.index[self.df['roll_number'] == roll].tolist()
                row_nums = [idx + 2 for idx in dup_indices]  # 1-based + 1 for header
                self.errors.append({
                    'row': row_nums[0],
                    'col': 'roll_number',
                    'value': roll,
                    'message': f"Duplicate roll number '{roll}' found on rows {', '.join(map(str, row_nums))}."
                })

        # 2. Row by row detailed validation
        valid_count = 0
        invalid_count = 0

        for idx, row in self.df.iterrows():
            row_num = idx + 2  # Excel row number (1-based + header)
            row_has_error = False

            roll = str(row.get('roll_number', '')).strip()
            name = str(row.get('student_name', '')).strip()

            if not roll or roll.lower() == 'nan':
                self.errors.append({
                    'row': row_num,
                    'col': 'roll_number',
                    'value': roll,
                    'message': f"Row {row_num}: Missing roll number."
                })
                row_has_error = True

            if not name or name.lower() == 'nan':
                self.errors.append({
                    'row': row_num,
                    'col': 'student_name',
                    'value': name,
                    'message': f"Row {row_num}: Missing student name."
                })
                row_has_error = True

            # Validate marks for each subject
            for subj in self.subject_cols:
                raw_val = row.get(subj)
                if pd.isna(raw_val) or str(raw_val).strip() == '':
                    self.errors.append({
                        'row': row_num,
                        'col': subj,
                        'value': 'null/empty',
                        'message': f"Row {row_num}: Missing marks for subject '{subj}'."
                    })
                    row_has_error = True
                    continue

                try:
                    mark = float(raw_val)
                    if np.isnan(mark) or np.isinf(mark):
                        raise ValueError("Invalid float")
                    if mark < 0.0 or mark > self.max_marks:
                        self.errors.append({
                            'row': row_num,
                            'col': subj,
                            'value': str(raw_val),
                            'message': f"Row {row_num}: Mark '{raw_val}' in subject '{subj}' is out of range [0, {self.max_marks}]."
                        })
                        row_has_error = True
                except (ValueError, TypeError):
                    self.errors.append({
                        'row': row_num,
                        'col': subj,
                        'value': str(raw_val),
                        'message': f"Row {row_num}: Non-numeric mark '{raw_val}' in subject '{subj}'."
                    })
                    row_has_error = True

            if row_has_error:
                invalid_count += 1
            else:
                valid_count += 1

        self.summary['valid_rows'] = valid_count
        self.summary['invalid_rows'] = invalid_count

        # Build preview of first 15 rows with calculated values
        preview_rows = []
        preview_slice = self.df.head(15)
        for _, row in preview_slice.iterrows():
            item = {
                'roll_number': str(row.get('roll_number', '')).strip(),
                'student_name': str(row.get('student_name', '')).strip(),
                'marks': {},
            }
            marks_sum = 0
            count = 0
            has_invalid = False
            for subj in self.subject_cols:
                val = row.get(subj)
                try:
                    f_val = float(val)
                    item['marks'][subj] = f_val
                    marks_sum += f_val
                    count += 1
                except Exception:
                    item['marks'][subj] = str(val)
                    has_invalid = True
            
            if count > 0 and not has_invalid:
                item['total'] = round(marks_sum, 2)
                item['average'] = round(marks_sum / count, 2)
            else:
                item['total'] = '-'
                item['average'] = '-'
            preview_rows.append(item)

        self.preview_data = preview_rows
        return len(self.errors) == 0

    @transaction.atomic
    def save_to_database(self, exam=None):
        """
        Commits validated student marks to the database transactionally.
        Ensures foreign key relations with Student, Subject, and Exam.
        Logs operation in ImportHistory.
        """
        if self.df is None:
            raise ValueError("Validation must be run before saving.")

        if self.errors:
            raise ValueError("Cannot save file with validation errors.")

        active_exam = exam or self.exam
        if not active_exam:
            active_exam = Exam.objects.first()
            if not active_exam:
                active_exam = Exam.objects.create(
                    exam_name="Mid-Term Examination 2024-25",
                    academic_year="2024-2025",
                    semester="Sem IV",
                    department="Computer Science & Engineering"
                )

        # 1. Resolve or create Subject records
        subject_objects = {}
        for s_col in self.subject_cols:
            clean_name = s_col.replace('_', ' ').title()
            subject, _ = Subject.objects.get_or_create(
                subject_code=s_col.upper(),
                defaults={
                    'subject_name': clean_name,
                    'maximum_marks': self.max_marks,
                    'passing_marks': self.passing_marks,
                }
            )
            subject_objects[s_col] = subject

        successful_records = 0
        failed_records = 0
        error_msgs = []

        for idx, row in self.df.iterrows():
            roll = str(row['roll_number']).strip()
            name = str(row['student_name']).strip()
            dept = str(row.get('department', active_exam.department)).strip()
            sec = str(row.get('section', 'A')).strip()

            try:
                student, _ = Student.objects.update_or_create(
                    roll_number=roll,
                    defaults={
                        'student_name': name,
                        'department': dept,
                        'section': sec,
                    }
                )

                for s_col in self.subject_cols:
                    val = float(row[s_col])
                    subj = subject_objects[s_col]
                    StudentMark.objects.update_or_create(
                        student=student,
                        subject=subj,
                        exam=active_exam,
                        defaults={
                            'marks_obtained': val
                        }
                    )
                successful_records += 1

            except Exception as e:
                failed_records += 1
                error_msgs.append(f"Row {idx+2} ({roll}): {str(e)}")

        status = 'SUCCESS' if failed_records == 0 else ('PARTIAL' if successful_records > 0 else 'FAILED')

        history = ImportHistory.objects.create(
            filename=self.filename,
            exam=active_exam,
            total_records=len(self.df),
            successful_records=successful_records,
            failed_records=failed_records,
            status=status,
            error_summary="\n".join(error_msgs[:50]) if error_msgs else None
        )

        return {
            'history_id': history.id,
            'total_records': len(self.df),
            'successful_records': successful_records,
            'failed_records': failed_records,
            'status': status,
            'exam': active_exam
        }
