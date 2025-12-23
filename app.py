import streamlit as st
import pandas as pd
import numpy as np
import re

# Set page config
st.set_page_config(
    page_title="Student Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading Functions ---

def detect_score_columns(df):
    """Auto-detect score columns and their max values from assessment data."""
    score_columns = {}
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['quants', 'logical', 'verbal', 'english', 'technical', 'coding', 'mcq']):
            # Check if column has any valid (non-NaN) data
            col_data = pd.to_numeric(df[col], errors='coerce')
            if col_data.isna().all():
                # Skip columns that are entirely empty/NaN
                continue
            
            match = re.search(r'\((\d+)\)', col)
            if match:
                max_score = int(match.group(1))
            else:
                max_val = col_data.max()
                # Handle case where max_val might still be NaN
                if pd.isna(max_val):
                    continue
                if max_val <= 100:
                    max_score = 100
                elif max_val <= 160:
                    max_score = 160
                else:
                    max_score = int(np.ceil(max_val / 10) * 10)
            score_columns[col] = max_score
    
    return score_columns


@st.cache_data(show_spinner="Loading assessment data...")
def load_assessment_data(uploaded_file):
    """Load and process assessment/test results data."""
    try:
        uploaded_file.seek(0)
        df = None
        
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            st.error("Could not read the CSV file with any encoding.")
            return None, None
        
        # Detect score columns
        score_columns = detect_score_columns(df)
        
        if not score_columns:
            st.warning("No score columns detected. Looking for columns with 'Quants', 'Logical', 'Verbal', etc.")
            return None, None
        
        # Convert score columns to numeric and fill NaN with 0
        for col in score_columns.keys():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate total score
        total_max = sum(score_columns.values())
        df['Score'] = df[list(score_columns.keys())].sum(axis=1).fillna(0)
        df['Total_Max'] = total_max
        
        # Calculate percentages (handle division safely)
        for col, max_val in score_columns.items():
            pct_col = col.split('(')[0].strip().replace(' ', '_') + '_Percentage'
            df[pct_col] = (df[col] / max_val * 100).fillna(0).round(2)
        
        df['Total_Percentage'] = (df['Score'] / total_max * 100).fillna(0).round(2)
        
        # Calculate rank - handle NaN by filling with 0 first, then rank
        df['Rank'] = df['Score'].rank(method='dense', ascending=False).fillna(0).astype(int)
        
        # Clean student names if column exists
        if 'Student_Name' in df.columns:
            df['Student_Name'] = df['Student_Name'].fillna('Unknown').astype(str).str.title()
        
        return df, score_columns
        
    except Exception as e:
        st.error(f"Error loading assessment data: {e}")
        return None, None


@st.cache_data(show_spinner="Loading course data...")
def load_course_data(uploaded_file):
    """Load and process LMS course progress data."""
    try:
        uploaded_file.seek(0)
        
        # Check file type
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            for encoding in ['utf-8', 'latin1', 'cp1252']:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    break
                except:
                    continue
        
        # Convert numeric columns
        numeric_cols = ['Courses Started', 'Overall Completion %', 'Courses Completed']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if 'Courses Started' in df.columns:
            df['Courses Started'] = df['Courses Started'].astype(int)
        if 'Courses Completed' in df.columns:
            df['Courses Completed'] = df['Courses Completed'].astype(int)
        
        # Get course columns (columns after standard metadata)
        course_columns = []
        if 'Overall Completion %' in df.columns:
            idx = df.columns.get_loc('Overall Completion %')
            course_columns = df.columns[idx + 1:].tolist()
        else:
            # Fallback: assume columns after index 11 are courses
            course_columns = df.columns[11:].tolist()
        
        return df, course_columns
        
    except Exception as e:
        st.error(f"Error loading course data: {e}")
        return None, None


# --- Sidebar ---
with st.sidebar:
    st.title("📊 Student Analytics")
    st.write("---")
    
    # Data Type Selection
    st.subheader("📁 Select Data Type")
    
    data_mode = st.radio(
        "What do you want to analyze?",
        options=["📈 Assessment Results", "📚 Course Progress"],
        help="Choose based on your data file type"
    )
    
    st.write("---")
    
    # File Upload based on selection
    if data_mode == "📈 Assessment Results":
        st.subheader("📈 Upload Assessment Data")
        assessment_file = st.file_uploader(
            "Upload Test Results (CSV)",
            type=["csv"],
            key="assessment_uploader",
            help="CSV with student scores (Quants, Logical, Verbal, etc.)"
        )
        
        if assessment_file is not None:
            df, score_columns = load_assessment_data(assessment_file)
            if df is not None:
                st.session_state["assessment_df"] = df
                st.session_state["score_columns"] = score_columns
                st.session_state["data_mode"] = "assessment"
                
                # Clear course data if exists
                if "df" in st.session_state:
                    del st.session_state["df"]
                if "course_columns" in st.session_state:
                    del st.session_state["course_columns"]
                
                st.success("✅ Assessment data loaded!")
                
                st.write("### Quick Stats")
                st.metric("Total Students", len(df))
                if 'Score' in df.columns:
                    st.metric("Average Score", f"{df['Score'].mean():.1f}/{df['Total_Max'].iloc[0]}")
                    st.metric("Highest Score", f"{df['Score'].max()}/{df['Total_Max'].iloc[0]}")
                
                st.write("### Detected Sections")
                for col, max_val in score_columns.items():
                    name = col.split('(')[0].strip()
                    st.write(f"• {name}: /{max_val}")
    
    else:  # Course Progress
        st.subheader("📚 Upload Course Data")
        course_file = st.file_uploader(
            "Upload Course Progress (CSV/Excel)",
            type=["csv", "xlsx"],
            key="course_uploader",
            help="LMS export with course completion data"
        )
        
        if course_file is not None:
            df, course_columns = load_course_data(course_file)
            if df is not None:
                st.session_state["df"] = df
                st.session_state["course_columns"] = course_columns
                st.session_state["data_mode"] = "course"
                
                # Clear assessment data if exists
                if "assessment_df" in st.session_state:
                    del st.session_state["assessment_df"]
                if "score_columns" in st.session_state:
                    del st.session_state["score_columns"]
                
                st.success("✅ Course data loaded!")
                
                st.write("### Quick Stats")
                st.metric("Total Students", len(df))
                st.metric("Total Courses", len(course_columns))
                if 'Overall Completion %' in df.columns:
                    st.metric("Avg Completion", f"{df['Overall Completion %'].mean():.1f}%")
    
    st.write("---")
    
    # Show current mode
    current_mode = st.session_state.get("data_mode", None)
    if current_mode == "assessment":
        st.info("📈 **Mode:** Assessment Results\n\nPages: Overview, Student Reports, Section Analysis, Rankings, Email, Downloads")
    elif current_mode == "course":
        st.info("📚 **Mode:** Course Progress\n\nPages: Student Analytics, Course Analytics, Branch Analytics, Predictive, Downloads")
    else:
        st.warning("Upload a file to get started")


# --- Main Page UI ---
col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    try:
        st.image("logo.png")
    except:
        pass

st.title("🏠 Student Analytics Dashboard")
st.header("Unified platform for student performance analysis")

current_mode = st.session_state.get("data_mode", None)

if current_mode is None:
    st.warning("👈 Please select a data type and upload your file using the sidebar.")
    
    st.write("---")
    st.subheader("📁 Supported Data Formats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Assessment Results")
        st.write("For analyzing test/exam scores")
        st.markdown("""
        **Required columns:**
        - `Student_Name` - Student's full name
        - `Email` - Email address
        - `College_Reg` - Registration number
        - Score columns like:
          - `Quants (160)` 
          - `Logical (160)`
          - `Verbal (160)`
          - Or any custom categories with max scores
        
        **Features:**
        - Overview Dashboard
        - Individual Student Reports
        - Section-wise Analysis
        - Rankings & Leaderboard
        - Email Reports
        - Bulk Downloads
        """)
        
    with col2:
        st.markdown("### 📚 Course Progress")
        st.write("For analyzing LMS course completion")
        st.markdown("""
        **Required columns:**
        - `Registration Number`
        - `First Name`, `Last Name`
        - `Email`
        - `Branch Name`
        - `Year of Passing`
        - `Courses Started`
        - `Courses Completed`
        - `Overall Completion %`
        - Course columns with completion %
        
        **Features:**
        - Student Analytics & Portfolio
        - Course Analytics
        - Branch Analytics
        - Predictive Features (At-Risk)
        - Download Center
        """)

elif current_mode == "assessment":
    df = st.session_state.get("assessment_df")
    score_columns = st.session_state.get("score_columns", {})
    
    st.success("✅ Assessment data loaded! Navigate using the sidebar.")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_max = df['Total_Max'].iloc[0] if 'Total_Max' in df.columns else 480
    
    with col1:
        st.metric("Total Students", len(df))
    
    with col2:
        avg_score = df['Score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}/{total_max}", f"{(avg_score/total_max*100):.1f}%")
    
    with col3:
        top_score = df['Score'].max()
        st.metric("Highest Score", f"{top_score}/{total_max}")
    
    with col4:
        pass_rate = len(df[df['Total_Percentage'] >= 50]) / len(df) * 100
        st.metric("Pass Rate (≥50%)", f"{pass_rate:.1f}%")
    
    st.write("---")
    
    # Detected sections
    st.subheader("📊 Detected Score Categories")
    cols = st.columns(len(score_columns))
    for i, (col_name, max_val) in enumerate(score_columns.items()):
        with cols[i]:
            display_name = col_name.split('(')[0].strip()
            avg = df[col_name].mean()
            st.metric(display_name, f"Avg: {avg:.1f}/{max_val}", f"{(avg/max_val*100):.1f}%")
    
    st.write("---")
    st.subheader("📋 Available Pages")
    st.markdown("""
    - **📊 Overview Dashboard** - Key metrics and performance distribution
    - **🧑‍🎓 Student Reports** - Individual student performance analysis
    - **📈 Section Analysis** - Detailed breakdown by score categories
    - **🏆 Rankings & Leaderboard** - Top performers and comparative analysis
    - **📧 Email Reports** - Send personalized reports to students
    - **📥 Bulk Downloads** - Export reports in Excel, CSV, JSON
    """)

elif current_mode == "course":
    df = st.session_state.get("df")
    course_columns = st.session_state.get("course_columns", [])
    
    st.success("✅ Course data loaded! Navigate using the sidebar.")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(df))
    
    with col2:
        st.metric("Total Courses", len(course_columns))
    
    with col3:
        if 'Courses Started' in df.columns:
            started = len(df[df['Courses Started'] > 0])
            st.metric("Students Started", f"{started}", f"{(started/len(df)*100):.1f}%")
    
    with col4:
        if 'Overall Completion %' in df.columns:
            avg_completion = df['Overall Completion %'].mean()
            st.metric("Avg Completion", f"{avg_completion:.1f}%")
    
    st.write("---")
    st.subheader("📋 Available Pages")
    st.markdown("""
    - **🧑‍🎓 Student Analytics** - Individual portfolios and leaderboards
    - **📊 Course Analytics** - Enrollment, completion rates, co-enrollment
    - **🏛️ Branch Analytics** - Branch/cohort comparisons
    - **🔮 Predictive Features** - At-risk students and recommendations
    - **📥 Download Center** - Comprehensive Excel reports
    """)

st.write("---")
st.caption("💡 Select your data type in the sidebar and upload your file to get started.")
