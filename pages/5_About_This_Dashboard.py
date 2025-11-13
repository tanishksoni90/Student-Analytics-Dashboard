import streamlit as st

st.set_page_config(
    page_title="About the Dashboard",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ About the Dashboard")

st.markdown("""
This is a Streamlit web application designed to help you analyze and understand your student course progress data. 
The app is divided into several pages, each with a specific function.

You must first upload your CSV file on the **🏠 Home** page to use the dashboard.
""")

st.write("---")

# --- Home ---
st.header("🏠 Home")
st.markdown("""
The **Home** page is the starting point.
*   **File Uploader:** This is where you upload your master student `.csv` file.
*   **Data Validation:** Upon upload, the app immediately checks if essential columns (like `Email`, `Branch Name`, `Overall Completion %`) are present.
*   **Session Caching:** Your data is stored in the app's session state, so you only need to upload it once. You can navigate between pages without losing your data.
""")

st.write("---")

# --- Main Dashboard ---
st.header("📊 Main Dashboard")
st.markdown("""
The **Main Dashboard** provides a high-level, 30,000-foot view of your entire student body.
*   **Key Metrics (KPIs):** See the most important numbers at a glance: Total Students, Total Courses, % of Students who have started, and % of Students who have fully completed.
*   **Branch-wise Performance:** Two charts break down student engagement by branch, showing:
    1.  The number of students who have **Started vs. Not Started**.
    2.  The number of students who have **Completed vs. Not Completed**.
*   **Overall Progress Distribution:** A histogram shows the "shape" of your student cohort, letting you see how many students are at 0%, 50%, or 100% completion.
""")

st.write("---")

# --- Student Drilldown ---
st.header("🧑‍🎓 Student Drilldown")
st.markdown("""
This page allows you to **find any individual student** and view their personal progress report.
*   **Search Function:** Use the search box to find a student by their Name or Email.
*   **Detailed Report Card:** Once you select a student, you'll see:
    1.  Their personal KPIs (Courses Started, Completed, etc.).
    2.  A complete list of all courses and their specific progress percentage in each one.
""")

st.write("---")

# --- NEW SECTION ---
st.header("📥 Download Center")
st.markdown("""
The **Download Center** is the most powerful page for exporting your analysis. It's where you can generate and download custom reports.
*   **Select Top 'k' Courses:** You can dynamically choose how many of the most-enrolled courses to focus your analysis on (e.g., Top 5, Top 10).
*   **Interactive Report Tabs:** View on-screen summaries for:
    1.  **Course Started Status:** A chart and table showing started vs. not started by branch.
    2.  **Course Completed Status:** A chart and table for completed vs. not completed by branch.
    3.  **Top 'k' Course Breakdown:** A detailed chart and table for each of your selected top courses.
*   **Download Visuals:** Every chart on this page can be individually downloaded as a high-quality **PNG** file for use in presentations.
*   **Download Full Report:** This is the primary download. It generates a single, multi-sheet **Excel file** that contains:
    1.  The complete "Master Student Report".
    2.  The "Course Started" summary table.
    3.  The "Course Completed" summary table.
    4.  A separate sheet for *each* of your "Top k" courses.
*   **Download Summary Tables:** A second download option to get an Excel file containing *only* the summary tables.
""")