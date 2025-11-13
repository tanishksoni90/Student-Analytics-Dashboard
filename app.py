import streamlit as st
import pandas as pd

# Set page config for the entire app. This must be the first Streamlit command.
st.set_page_config(
    page_title="Career247 Analytics Dashboard",
    page_icon="🚀",  # This icon will still appear in the browser tab
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Caching Function ---
@st.cache_data(show_spinner="Loading and cleaning data...")
def load_data(uploaded_file):
    """Loads data from the uploaded CSV file with robust encoding."""
    try:
        # Use 'latin1' encoding
        df = pd.read_csv(uploaded_file, encoding='latin1')
        
        # --- Data Cleaning ---
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

# --- Sidebar ---
# This section is the "control panel"
with st.sidebar:
    st.title("🚀 Career247 Analytics")
    st.write("---")
    
    uploaded_file = st.file_uploader(
        "Upload Course Spreadsheet (CSV)", 
        type="csv",
        key="main_uploader",
        help="Upload the 'course spreadsheet.csv' file to power the dashboard."
    )

    # Load data and store it in session state
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.session_state["df"] = df
            st.session_state["course_columns"] = df.columns[11:].tolist()
            st.success("File Loaded!")
            
    st.write("---")
    st.info("Navigate to a page to begin your analysis.")

# --- Main Page UI ---

# --- NEW: TOP-CENTER LOGO ---
# 1. Create columns for centering. [2,3,2] gives a wide center column.
#    You can adjust these ratios (e.g., [1,2,1]) to make the logo smaller or larger.
col1, col2, col3 = st.columns([2, 3, 2])

with col2:
    try:
        # 2. Display the logo from the file "logo.png"
        st.image("logo.png")
    except Exception:
        # 3. A fallback in case the image isn't found
        st.write("*(Company Logo)*") 
# --- END OF LOGO CODE ---


st.title("🏠 Welcome to the Student Analytics Dashboard")
st.header("Your central hub for data-driven insights.")

if "df" not in st.session_state:
    st.warning("Please upload a CSV file using the sidebar to get started.")
else:
    st.success("Data loaded successfully! Please select an analysis page from the sidebar.")

st.write("")
st.subheader("How to Use This Dashboard")
st.markdown("""
1.  **Upload Your File:** Use the file uploader in the sidebar to load your course spreadsheet.
2.  **Navigate Pages:** The sidebar on the left lists all available analysis pages. The file you upload will power all of them.
3.  **Explore Features:** Each page has multiple tabs and filters to help you find the insights you need.
""")

st.subheader("Dashboard Pages")
st.markdown("""
* **Student Analytics:** Find individual students, see their progress, and get course recommendations.
* **Course Analytics:** Analyze course popularity, completion rates, and which courses are taken together.
* **Branch Analytics:** Compare branches and academic years to see high-level performance trends.
* **Predictive Features:** Identify at-risk students and find "gaps" in a student's course plan.
* **About This Dashboard:** A full guide to all features and their logic.
""")