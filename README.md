# Student Course Progress Analytics Dashboard

This is a Streamlit web application built to help educators and administrators analyze student progress data exported from a learning management system (LMS).

It turns a complex, wide CSV file into a simple, interactive, and actionable dashboard with drilldown capabilities and a powerful report-generation center.



## ✨ Features

The application is split into several pages, each serving a specific purpose:

### 🏠 1. Home
*   **Secure File Upload:** Upload your master student CSV file.
*   **Data Validation:** The app checks if essential columns (`Email`, `Branch Name`, `Overall Completion %`, etc.) are present.
*   **Data Caching:** The uploaded file is cached in memory, so you only need to upload it once per session.

### 📊 2. Main Dashboard
*   **High-Level KPIs:** View "at-a-glance" metrics for:
    *   Total Students
    *   Total Courses
    *   Students Who Started (at least 1 course)
    *   Students Who Completed (100% overall)
*   **Branch-wise Performance:** Two interactive bar charts show:
    *   **Course Started Status** (Started vs. Not Started) by branch.
    *   **Course Completed Status** (Completed vs. Not Completed) by branch.
*   **Overall Progress Distribution:** A histogram showing how many students fall into different completion percentage brackets (e.g., 0-10%, 10-20%, ... 90-100%).

### 🧑‍🎓 3. Student Drilldown
*   **Student Search:** Find any student by their Name or Email using a simple search box.
*   **Detailed Report Card:** Once selected, the app generates a detailed report for that student:
    *   KPIs for their personal progress (Courses Started, Completed, Overall %).
    *   A full list of all courses, showing their individual progress percentage in each.

### 📥 6. Download Center
This is the main hub for generating and exporting custom reports.
*   **Dynamic "Top k" Selection:** You can select the top 'k' most popular courses to focus the report on (e.g., Top 5, Top 10).
*   **Interactive Summary Reports:** On-screen tabs for:
    *   Course Started Summary
    *   Course Completed Summary
    *   Top 'k' Course Breakdown
*   **Data + Visualization:** Each tab provides both an interactive Altair chart and the corresponding summary data table.
*   **PNG Chart Downloads:** Download any of the summary charts as a high-quality, presentation-ready PNG file.
*   **Comprehensive Excel Downloads:**
    *   **Download Full Report (All Sheets):** This is the main download. It's a single `.xlsx` file containing *all* data:
        1.  The Master Student Report (with Top 'k' columns)
        2.  The "Course Started" summary table
        3.  The "Course Completed" summary table
        4.  A separate sheet for *each* of the Top 'k' courses.
    *   **Download Summary Tables Only:** A separate download option for just the summary tables.

## 🚀 How to Run

### 1. Prerequisites
You must have Python 3.8+ installed.

### 2. Installation
1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd student-dashboard
    ```
2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required packages:**
    Create a file named `requirements.txt` and add the contents from the section below. Then run:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the App
Make sure your file structure looks like this:
```
student-dashboard/
├── 1_Home.py
├── pages/
│   ├── 2_Main_Dashboard.py
│   ├── 3_Student_Drilldown.py
│   ├── 5_About_the_Dashboard.py
│   ├── 6_Download_Center.py
├── requirements.txt
└── README.md
```
Then, run the app from your terminal:
```bash
streamlit run 1_Home.py
```
Your app will open in your default web browser.

## 📄 `requirements.txt`
```
streamlit
pandas
altair
vl-convert
xlsxwriter
```

##  csv Data Format
Your CSV file must contain the following columns for the app to work correctly. Other columns are fine, but these are essential.

*   `First Name`
*   `Last Name`
*   `Email`
*   `Branch Name`
*   `Registration Number`
*   `Overall Completion %`
*   ...and one column for each course, formatted as: `[Course Name] - Progress %`