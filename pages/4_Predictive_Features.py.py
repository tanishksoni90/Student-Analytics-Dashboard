import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Predictive Features",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 Predictive Features & Reports")

@st.cache_data
def get_at_risk_students(df, min_courses, max_completion):
    """Filters the DataFrame for at-risk students based on parameters."""
    criteria = (df['Courses Started'] >= min_courses) & (df['Overall Completion %'] <= max_completion)
    at_risk_df = df[criteria]
    return at_risk_df

@st.cache_data
def get_recommendations(df, course_columns, student_reg_num, top_n_courses=10):
    """Generates course recommendations for a single student."""
    
    student_data = df[df['Registration Number'] == student_reg_num].iloc[0]
    student_branch = student_data['Branch Name']
    
    student_courses_series = student_data[course_columns]
    courses_started_by_student = set(student_courses_series[student_courses_series > 0].index)
    
    branch_df = df[df['Branch Name'] == student_branch]
    
    branch_course_counts = (branch_df[course_columns] > 0).sum().sort_values(ascending=False)
    
    top_n_branch_courses = set(branch_course_counts.head(top_n_courses).index)
    
    recommendations = list(top_n_branch_courses - courses_started_by_student)
    
    recommended_courses_with_counts = branch_course_counts[recommendations].reset_index()
    recommended_courses_with_counts.columns = ['Course Name', 'Enrollment in Branch']
    
    return recommended_courses_with_counts.sort_values(by='Enrollment in Branch', ascending=False)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page to begin.")
else:
    df = st.session_state["df"]
    course_columns = st.session_state["course_columns"]

    tab1, tab2 = st.tabs([
        "**At-Risk Student Identifier**", 
        "**Course Recommendation Engine**"
    ])

    with tab1:
        st.header("At-Risk Student Identifier")
        st.write("Find students who may need extra support based on their progress.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_courses = st.slider(
                "Minimum 'Courses Started':", 
                min_value=1, 
                max_value=20, 
                value=5
            )
            
        with col2:
            max_completion = st.slider(
                "Maximum 'Overall Completion %' less than:", 
                min_value=10, 
                max_value=100, 
                value=30
            )
            
        at_risk_df = get_at_risk_students(df, min_courses, max_completion)
        
        st.subheader(f"Found {len(at_risk_df)} students matching criteria")
        
        if not at_risk_df.empty:
            display_cols = [
                'First Name', 'Last Name', 'Registration Number', 
                'Branch Name', 'Courses Started', 'Courses Completed', 'Overall Completion %'
            ]
            
            at_risk_df_sorted = at_risk_df[display_cols].sort_values(by='Overall Completion %', ascending=True)
            
            st.dataframe(at_risk_df_sorted, use_container_width=True)
            
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_df_to_csv(at_risk_df_sorted)

            st.download_button(
                label="📥 Download Full Report as CSV",
                data=csv_data,
                file_name=f"at_risk_report_(started_{min_courses}_completion_{max_completion}).csv",
                mime="text/csv",
            )
        else:
            st.success("Great news! No students found matching these criteria.")

    with tab2:
        st.header("Simple Course Recommendation Engine")
        st.write("Select a student to see recommended courses based on popularity in their branch.")
        
        student_list = df['Registration Number'].unique()
        selected_reg_num = st.selectbox(
            "Select a student by Registration Number:",
            options=student_list,
            placeholder="Select a student...",
            key="recommendation_selectbox"
        )
        
        if selected_reg_num:
            recommendations_df = get_recommendations(df, course_columns, selected_reg_num)
            
            student_data = df[df['Registration Number'] == selected_reg_num].iloc[0]
            st.info(f"Showing recommendations for **{student_data['First Name']} {student_data['Last Name']}** (Branch: {student_data['Branch Name']})")
            
            if recommendations_df.empty:
                st.success("This student is already enrolled in most of the top courses for their branch!")
            else:
                st.write("Here are the top courses from their branch that they haven't started yet:")
                st.dataframe(recommendations_df, use_container_width=True)