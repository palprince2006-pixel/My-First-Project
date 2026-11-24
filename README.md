# Student Result Analyzer

A high-performance, college-level academic data analytics web application developed with **Python 3.11+**, **Django**, **NumPy**, **Pandas**, **SQLite/SQL**, and **Chart.js**.

The application parses tabular exam marksheets from CSV and Excel formats, applies rigorous mathematical and statistical operations via Pandas and NumPy, computes institutional KPIs, identifies toppers, determines subject difficulty distributions, and exports audit-ready CSV and PDF reports.

---

## 1. Key Features & Modules

### Module 1: Institutional Analytics Dashboard
- Dynamic, real-time KPI metrics calculated directly from the database:
  - **Total Students** Enrolled
  - **Class Average** (%)
  - **Pass Percentage** (%)
  - **Highest Total Marks & Percentage**
  - **Lowest Total Marks & Percentage**
  - **Failed Students Count**
- Advanced NumPy statistical indicators:
  - **Median Percentage**
  - **Sample Standard Deviation (\(\sigma\))** using `np.std(marks, ddof=1)`
- Top student honor roll preview and subject difficulty overview.

### Module 2: Result Ingestion & Validation Engine
- Multi-format ingestion: **CSV** and **Excel (.xlsx)** score sheets.
- Automated structural and semantic validation:
  - Header column verification (`roll_number`, `student_name`, and subject columns).
  - Null and missing value detection per row and column.
  - Duplicate roll number detection within uploaded files.
  - Numeric boundary validation: rejects negative numbers or marks $> 100$.
- **Two-phase upload flow**:
  - **Dry-run validation preview**: Inspect parsed rows, total scores, and diagnostic error logs before committing to the database.
  - **Direct commit**: Transactional atomic database write with audit trail in `ImportHistory`.
- Pre-built downloadable starter templates in CSV and Excel formats.

### Module 3: Student Performance Analysis & Ledger
- Detailed student score directory:
  - Roll Number, Student Name, Subject-wise Marks.
  - Total Marks, Average Marks, Percentage.
  - Dynamic Letter Grade: `O`, `A+`, `A`, `B+`, `B`, `C`, `F`.
  - Pass/Fail Status (requires clearing individual subject minimums and overall threshold).
  - Dynamic Rank calculation.
- Live client-side and server-side filtering:
  - Instant search by roll number or student name.
  - Filter by clearance status (`Passed`, `Failed`).
  - Filter by letter grade (`O` through `F`).
  - Sort by rank, percentage, roll number, or name.
- Interactive **Student Marksheet Modal Card**.

### Module 4: Topper & Merit Analysis
- **Overall Class Topper Showcase**: Valedictorian spotlight with aggregate percentage, total score, and department.
- **Top 5 Honor Roll**: Visual badge cards for the top five ranked students.
- **Top 10 Extended Rank Ledger**: Full standing table.
- **Subject-wise Toppers**: Identifies peak mark scorers per subject, correctly handling ties where multiple students achieve the highest score.
- **Tie Handling Methodology**: Ranks are computed using `pandas.DataFrame.rank(method='min', ascending=False)`.

### Module 5: Subject Difficulty Analysis
- Statistical evaluation for every subject:
  - Average marks & average percentage.
  - Pass clearance rate & failure rate.
  - Peak and lowest marks.
  - NumPy Standard Deviation (\(\sigma\)).
- **Configurable Difficulty Categorization**:
  - **Easy**: Average $\ge 70\%$ and Pass Rate $\ge 80\%$.
  - **Moderate**: Average $\ge 50\%$ and Pass Rate $\ge 60\%$.
  - **Difficult**: Average $< 50\%$ or Pass Rate $< 60\%$.
- Includes analytical disclaimer clarifying that difficulty categorization is an empirical performance indicator.

### Module 6: Interactive Data Visualizations (Chart.js)
Live Chart.js charts served via dedicated JSON API (`/api/charts/`):
1. **Subject-wise Average Marks** (Bar Chart with 40-mark passing baseline).
2. **Pass vs Fail Ratio** (Doughnut Chart).
3. **Student Performance Distribution** (Bar Chart across percentage brackets).
4. **Letter Grade Breakdown** (Pie Chart).
5. **Subject Clearance Comparison** (Horizontal Bar Chart).

### Module 7: Reports & Document Export Center
- Exports for 4 institutional report dimensions:
  1. Overall Class Performance Summary.
  2. Student Results Marks Ledger.
  3. Subject-wise Analysis Matrix.
  4. Toppers & Distinction Leaderboard.
- One-click downloads available in both **CSV** and **ReportLab PDF** formats.

---

## 2. Technology Stack

- **Backend**: Python 3.11+, Django 5.2
- **Data Analytics**: NumPy 2.4, Pandas 3.0
- **Database**: SQLite with Django ORM
- **Document Generation**: ReportLab 5.0 (PDF) & openpyxl 3.1 (Excel)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS, Google Fonts, Material Symbols
- **Visualizations**: Chart.js 4.4

---

## 3. Project Architecture

```
sales analitic dashbord/
├── manage.py
├── requirements.txt
├── README.md
│
├── config/
│   ├── settings.py           # Configuration, academic grading thresholds
│   ├── urls.py               # Application routing table
│   └── wsgi.py
│
├── apps/
│   ├── core/                 # Base layout, context processors, templatetags
│   ├── students/             # Student model, views, marks ledger
│   ├── results/              # Subject, Exam, StudentMark models
│   ├── imports/              # Pandas file validation engine, ImportHistory
│   ├── analytics/            # NumPy & Pandas statistical computation engine
│   └── reports/              # ReportLab PDF & CSV generation service
│
├── templates/
│   ├── base.html             # Institutional sidebar, top navbar, theme fonts
│   ├── dashboard.html        # Dynamic KPIs, 5 Chart.js charts, honors preview
│   ├── upload.html           # File ingestion, dry-run preview, error diagnostics
│   ├── students.html         # Master results directory, filters, marksheet modal
│   ├── toppers.html          # Valedictorian hero, top 5 cards, subject toppers
│   ├── subjects.html         # Subject performance matrix, std dev, difficulty
│   └── reports.html          # Export hub with instant CSV & PDF download links
│
├── sample_data/              # Sample CSV & Excel datasets for testing
│   ├── cse_sem4_results.csv
│   ├── cse_sem4_results.xlsx
│   ├── invalid_missing_columns.csv
│   ├── invalid_duplicate_roll.csv
│   └── invalid_out_of_range.csv
│
└── tests/
    └── test_analyzer.py      # Automated test suite covering 11 critical test cases
```

---

## 4. Installation & Setup Instructions

### Prerequisites
- Python 3.11 or higher installed on your system.

### Step 1: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 2: Apply Database Migrations
```bash
python manage.py makemigrations students results imports
python manage.py migrate
```

### Step 3: Run the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 5. Sample Data & Testing

Sample datasets are included in the `sample_data/` folder:
- `cse_sem4_results.csv`: 35 valid students with 5 subjects.
- `cse_sem4_results.xlsx`: Excel version of the valid dataset.
- `invalid_missing_columns.csv`: Tests missing column validation.
- `invalid_duplicate_roll.csv`: Tests duplicate roll number detection.
- `invalid_out_of_range.csv`: Tests out-of-range marks ($> 100$ and negative numbers).

### Running Automated Unit Tests
To run the automated test suite:
```bash
python manage.py test tests
```

---

## 6. Configurable Academic Settings

Academic evaluation rules can be adjusted in `config/settings.py` under `ACADEMIC_SETTINGS`:
```python
ACADEMIC_SETTINGS = {
    'DEFAULT_PASSING_PERCENTAGE': 40.0,
    'DEFAULT_SUBJECT_PASSING_MARKS': 40.0,
    'DEFAULT_SUBJECT_MAX_MARKS': 100.0,
    'MAX_FILE_UPLOAD_SIZE_MB': 15,
    'GRADE_SCALE': [
        ('O', 90.0, 'Outstanding'),
        ('A+', 80.0, 'Excellent'),
        ('A', 70.0, 'Very Good'),
        ('B+', 60.0, 'Good'),
        ('B', 50.0, 'Above Average'),
        ('C', 40.0, 'Average / Pass'),
        ('F', 0.0, 'Fail'),
    ],
    'DIFFICULTY_THRESHOLDS': {
        'EASY_MIN_AVG': 70.0,
        'EASY_MIN_PASS_PCT': 80.0,
        'MODERATE_MIN_AVG': 50.0,
        'MODERATE_MIN_PASS_PCT': 60.0,
    }
}
```

---

## 7. Known Limitations

1. **Subject Max Marks Normalization**: The current version assumes standard subject marks out of 100.0 by default, though subjects with different maximum marks can be defined in the database.
2. **Database Engine**: Configured for SQLite for immediate standalone deployment; can be connected to PostgreSQL or MySQL by updating `DATABASES` in `config/settings.py`.
