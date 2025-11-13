import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Career247 Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data(uploaded_file):
    """Loads data from the uploaded CSV file with robust encoding."""
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        
        df['Courses Started'] = pd.to_numeric(df['Courses Started'], errors='coerce')
        df['Overall Completion %'] = pd.to_numeric(df['Overall Completion %'], errors='coerce')
        df['Courses Completed'] = pd.to_numeric(df['Courses Completed'], errors='coerce')

        df['Courses Started'] = df['Courses Started'].fillna(0).astype(int)
        df['Courses Completed'] = df['Courses Completed'].fillna(0).astype(int)
        df['Overall Completion %'] = df['Overall Completion %'].fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading or cleaning file: {e}")
        return None

with st.sidebar:
    st.title("🚀 Analytics Dashboard")
    st.write("---")
    
    uploaded_file = st.file_uploader(
        "Upload your course spreadsheet (CSV)", 
        type="csv",
        key="main_uploader"
    )

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            st.session_state["df"] = df
            st.session_state["course_columns"] = df.columns[11:].tolist()
            st.success("File Loaded!")
            
    st.write("---")
    st.info("Navigate to a page to begin your analysis.")

st.title("Welcome to the Student Analytics Dashboard")
st.header("Your central hub for data-driven insights.")

if "df" not in st.session_state:
    st.warning("Please upload a CSV file using the sidebar to get started.")
else:
    st.success("Data loaded successfully! Please select an analysis page from the sidebar.")
    
    st.subheader("Dashboard Features:")
    st.markdown("""
    * **1_Student_Analytics:** Search for individual students and view their complete portfolio and course recommendations.
    * **2_Course_Analytics:** Get a deep dive into course performance, including enrollment, completion rates, and popularity.
    * **3_Branch_Analytics:** Compare performance across different branches and academic years.
    * **4_Predictive_Features:** Identify at-risk students and use the recommendation engine.
    """)