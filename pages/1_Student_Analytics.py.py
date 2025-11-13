import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Student Analytics",
    page_icon="🧑‍🎓",
    layout="wide"
)

st.title("🧑‍🎓 Student-Level Analytics")

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page to begin.")
else:
    df = st.session_state["df"]
    course_columns = st.session_state["course_columns"]

    tab1, tab2 = st.tabs(["**Student Portfolio**", "**Top Performers Leaderboard**"])

    with tab1:
        st.header("Student Portfolio Dashboard")
        
        student_list = df['Registration Number'].unique()
        selected_reg_num = st.selectbox(
            "Search for a student by Registration Number:",
            options=student_list,
            placeholder="Select a student..."
        )

        if selected_reg_num:
            student_data = df[df['Registration Number'] == selected_reg_num].iloc[0]

            col1, col2, col3 = st.columns(3)
            col1.metric("Student Name", f"{student_data['First Name']} {student_data['Last Name']}")
            col2.metric("Branch", f"{student_data['Branch Name']}")
            col3.metric("Year of Passing", f"{int(student_data['Year of Passing'])}")

            st.subheader("Overall Progress")
            col1, col2, col3 = st.columns(3)
            col1.metric("Courses Started", f"{student_data['Courses Started']}")
            col2.metric("Courses Completed", f"{student_data['Courses Completed']}")
            col3.metric("Overall Completion %", f"{student_data['Overall Completion %']:.2f}%")
            
            st.progress(student_data['Overall Completion %'] / 100)

            st.subheader("Course Progress Details")
            
            student_courses = student_data[course_columns]
            courses_started = student_courses[student_courses > 0]
            
            if courses_started.empty:
                st.info("This student has not started any courses yet.")
            else:
                courses_df = courses_started.reset_index()
                courses_df.columns = ["Course Name", "Completion %"]
                courses_df = courses_df.sort_values(by="Completion %", ascending=False)
                st.dataframe(courses_df, use_container_width=True)

            st.subheader("Recommended Courses")
            
            branch_df = df[df['Branch Name'] == student_data['Branch Name']]
            
            branch_course_counts = (branch_df[course_columns] > 0).sum().sort_values(ascending=False)
            top_10_branch_courses = branch_course_counts.head(10).index
            
            courses_not_started = student_courses[student_courses == 0].index
            
            recommendations = list(set(top_10_branch_courses) & set(courses_not_started))
            
            if not recommendations:
                st.info("This student is already taking most of the popular courses for their branch!")
            else:
                st.write("Based on popular courses in their branch, here are some recommendations:")
                for i, course in enumerate(recommendations[:5]): 
                    st.markdown(f"- **{course}** (*Taken by {branch_course_counts[course]} students in {student_data['Branch Name']}*)")


    with tab2:
        st.header("Top Performers Leaderboard")
        
        col1, col2, col3 = st.columns(3)
        
        branch_options = ["All"] + list(df['Branch Name'].unique())
        selected_branch = col1.selectbox("Filter by Branch:", branch_options)
        
        year_options = ["All"] + list(df['Year of Passing'].unique())
        selected_year = col2.selectbox("Filter by Year:", year_options)
        
        top_n = col3.number_input("Show Top N Students:", min_value=5, max_value=100, value=20)
        
        filtered_df = df.copy()
        
        if selected_branch != "All":
            filtered_df = filtered_df[filtered_df['Branch Name'] == selected_branch]
            
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df['Year of Passing'] == selected_year]
            
        st.subheader(f"Top {top_n} Students by Overall Completion %")
        
        leaderboard = filtered_df.sort_values(by="Overall Completion %", ascending=False)
        
        display_cols = [
            'First Name', 'Last Name', 'Registration Number', 
            'Branch Name', 'Overall Completion %', 'Courses Completed'
        ]
        
        st.dataframe(leaderboard[display_cols].head(top_n), use_container_width=True)