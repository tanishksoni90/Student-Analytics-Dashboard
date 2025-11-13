import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Course Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Course-Level Analytics")

@st.cache_data
def calculate_course_stats(df, course_columns):
    """
    Pre-calculates statistics for all courses to speed up the dashboard.
    """
    course_stats = []
    
    for course in course_columns:
        # Ensure column is numeric
        course_series = pd.to_numeric(df[course], errors='coerce').fillna(0)
        
        # 1. Total Enrollment (students with > 0%)
        total_enrollment = (course_series > 0).sum()
        
        if total_enrollment > 0:
            # 2. Total Completed (students with == 100%)
            total_completed = (course_series == 100).sum()
            
            # 3. Completion Rate
            completion_rate = (total_completed / total_enrollment) * 100
            
            # 4. Average Completion % (of those enrolled)
            enrolled_students = course_series[course_series > 0]
            average_completion = enrolled_students.mean()
            
            course_stats.append({
                "Course Name": course,
                "Total Enrollment": total_enrollment,
                "Total Completed": total_completed,
                "Completion Rate (%)": completion_rate,
                "Average Completion %": average_completion
            })
        else:
            # Handle courses with zero enrollment
             course_stats.append({
                "Course Name": course,
                "Total Enrollment": 0,
                "Total Completed": 0,
                "Completion Rate (%)": 0,
                "Average Completion %": 0
            })

    stats_df = pd.DataFrame(course_stats)
    return stats_df

@st.cache_data
def calculate_correlation_matrix(df, course_columns):
    """
    Calculates the correlation matrix for course co-enrollment.
    """
    enrolled_df = (df[course_columns] > 0).astype(int)
    
    # Filter for courses with at least 10 enrollments
    popular_courses = enrolled_df.sum()[enrolled_df.sum() > 10].index
    enrolled_df_popular = enrolled_df[popular_courses]
    
    co_occurrence = enrolled_df_popular.T.dot(enrolled_df_popular)
    co_occurrence = co_occurrence.stack().reset_index()
    co_occurrence.columns = ['Course 1', 'Course 2', 'Student Count']
    co_occurrence = co_occurrence[co_occurrence['Course 1'] != co_occurrence['Course 2']]
    
    return co_occurrence, popular_courses.tolist()


# --- Check if data is loaded ---
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page (using the sidebar) to begin.")
else:
    # Load data from session state
    df = st.session_state["df"]
    course_columns = st.session_state["course_columns"]
    
    # Calculate all course stats once
    all_course_stats = calculate_course_stats(df, course_columns)

    # --- Create Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "**⭐ Top Enrolled Courses**",
        "**Course Deep Dive**", 
        "**Course Performance**", 
        "**Course Co-Enrollment**"
    ])

    # --- Tab 1: Top Enrolled Courses (Your Original Feature) ---
    with tab1:
        st.header("Top Courses by Student Enrollment")
        
        # Number Input for 'N'
        top_n = st.number_input(
            "How many top courses do you want to see?",
            min_value=1,
            max_value=176,
            value=5,
            step=1
        )
        
        # Get the top N courses from our pre-calculated stats
        top_n_enrolled = all_course_stats.sort_values(
            by="Total Enrollment", ascending=False
        ).head(top_n)
        
        # --- Results Display ---
        st.subheader(f"Top {top_n} Courses by Student Enrollment")
        
        # Set 'Course Name' as the index for a cleaner bar chart
        chart_data = top_n_enrolled.set_index('Course Name')['Total Enrollment']

        # Display the bar chart
        st.bar_chart(chart_data)

        # Display the data table
        st.dataframe(top_n_enrolled[[
            "Course Name", "Total Enrollment"
        ]], use_container_width=True)

    # --- Tab 2: Course Deep Dive ---
    with tab2:
        st.header("Course Deep Dive")
        
        # --- Course Selector ---
        course_list = all_course_stats["Course Name"]
        selected_course = st.selectbox(
            "Select a course to analyze:",
            options=course_list,
            placeholder="Select a course..."
        )
        
        if selected_course:
            # Get the stats for the selected course
            course_data = all_course_stats[all_course_stats['Course Name'] == selected_course].iloc[0]
            
            st.subheader(f"Metrics for: **{selected_course}**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Enrollment", f"{int(course_data['Total Enrollment'])}")
            col2.metric("Completion Rate", f"{course_data['Completion Rate (%)']:.2f}%")
            col3.metric("Avg. Completion (of enrolled)", f"{course_data['Average Completion %']:.2f}%")
            
            st.subheader("Enrollment by Branch")
            if course_data['Total Enrollment'] > 0:
                enrolled_branch_df = df[df[selected_course] > 0]['Branch Name'].value_counts().reset_index()
                enrolled_branch_df.columns = ['Branch Name', 'Student Count']
                
                chart = alt.Chart(enrolled_branch_df).mark_bar().encode(
                    x=alt.X('Branch Name', sort=None),
                    y='Student Count',
                    tooltip=['Branch Name', 'Student Count']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No students are enrolled in this course.")

    # --- Tab 3: Course Performance ---
    with tab3:
        st.header("Most & Least Completed Courses")
        st.write("Based on **Completion Rate** (students who finished / students who started)")
        
        min_enrollment = st.slider("Minimum enrollment to consider:", 1, 50, 10)
        
        stats_filtered = all_course_stats[all_course_stats['Total Enrollment'] >= min_enrollment]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 5 Most Completed Courses")
            top_5 = stats_filtered.sort_values(by="Completion Rate (%)", ascending=False).head(5)
            st.dataframe(top_5[[
                "Course Name", "Completion Rate (%)", "Total Enrollment"
            ]], use_container_width=True)
            
        with col2:
            st.subheader("📉 Top 5 Least Completed Courses")
            bottom_5 = stats_filtered.sort_values(by="Completion Rate (%)", ascending=True).head(5)
            st.dataframe(bottom_5[[
                "Course Name", "Completion Rate (%)", "Total Enrollment"
            ]], use_container_width=True)

    # --- Tab 4: Course Co-Enrollment Heatmap ---
    with tab4:
        st.header("Course Co-Enrollment Heatmap")
        st.write("This shows which courses are most frequently taken together.")
        st.info("Only courses with > 10 students are included to keep the chart readable.")
        
        co_occurrence_df, popular_courses = calculate_correlation_matrix(df, course_columns)
        
        heatmap = alt.Chart(co_occurrence_df).mark_rect().encode(
            x=alt.X('Course 1', sort=popular_courses),
            y=alt.Y('Course 2', sort=popular_courses),
            color=alt.Color('Student Count', scale=alt.Scale(range='heatmap')),
            tooltip=['Course 1', 'Course 2', 'Student Count']
        ).properties(
            title="Course Co-Enrollment (Number of Students)"
        ).interactive()
        
        st.altair_chart(heatmap, use_container_width=True)