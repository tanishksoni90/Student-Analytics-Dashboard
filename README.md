# Student Analytics Dashboard

A unified Streamlit dashboard for analyzing student performance data - supporting both **LMS Course Progress** tracking and **Assessment/Test Results** analysis.

## Features

### 🔄 Dual Mode System
Choose your data type on the home page:
- **📈 Assessment Results** - For test/exam score analysis
- **📚 Course Progress** - For LMS completion tracking

### 📈 Assessment Results Module
For test/exam score analysis with dynamic score category detection:

**Features:**
- Auto-detects score columns (Quants, Logical, Verbal, etc.)
- Supports different max scores per category
- Overview Dashboard with key metrics
- Individual Student Reports with radar charts
- Section-wise Analysis
- Rankings & Leaderboard
- Email Reports (SMTP-based)
- Bulk Downloads (Excel, CSV, JSON)

**Expected CSV Format:**
```
Student_Name,Email,College_Reg,Batch,Branch,Quants (160),Logical (160),Verbal (160),Score
John Doe,john@example.com,REG001,2028,CSE,120,100,90,310
```

### 📚 Course Progress Module
For LMS completion tracking:

**Features:**
- Student Analytics & Portfolio
- Course Analytics (enrollment, completion, co-enrollment)
- Branch Analytics (comparisons, distributions)
- Predictive Features (at-risk students, recommendations)
- Download Center (comprehensive Excel reports)

**Expected CSV/Excel Format:**
```
Registration Number,First Name,Last Name,Email,Branch Name,Year of Passing,Courses Started,Courses Completed,Overall Completion %,Course1,Course2,...
REG001,John,Doe,john@example.com,CSE,2025,5,3,60.5,100,50,...
```

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Project Structure

```
├── app.py                           # Main entry point
├── pages/
│   ├── 1_📊_Overview_Dashboard.py   # Overview for both modes
│   ├── 2_🧑‍🎓_Student_Analytics.py   # Student reports/analytics
│   ├── 3_📈_Course_Analytics.py     # Course/Section analysis
│   ├── 4_🏛️_Branch_Rankings.py      # Branch analytics/Rankings
│   ├── 5_🔮_Predictive_Features.py  # Email (assessment) / Predictive (course)
│   └── 6_📥_Download_Center.py      # Bulk downloads
├── utils/
│   ├── __init__.py
│   └── data_helpers.py
├── requirements.txt
├── logo.png
└── README.md
```

## Deployment

For Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set `app.py` as main file
4. Deploy

## Requirements

- Python 3.8+
- streamlit
- pandas
- plotly
- altair
- numpy
- openpyxl
- xlsxwriter
