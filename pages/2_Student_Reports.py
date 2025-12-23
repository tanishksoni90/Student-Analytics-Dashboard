import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Student Reports", page_icon="🧑‍🎓", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.stop()

# ============================================
# ASSESSMENT STUDENT REPORTS
# ============================================
if data_mode == "assessment":
    st.title("🧑‍🎓 Individual Student Reports")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    # Student Selection
    st.subheader("🔍 Select Student")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name_col = 'Student_Name' if 'Student_Name' in df.columns else None
        reg_col = 'College_Reg' if 'College_Reg' in df.columns else None
        
        if name_col and reg_col:
            # Use index to handle duplicate registration numbers
            student_options = [f"{row[name_col]} ({row[reg_col]}) [#{i}]" for i, (_, row) in enumerate(df.iterrows())]
        elif name_col:
            student_options = [f"{name} [#{i}]" for i, name in enumerate(df[name_col].tolist())]
        else:
            student_options = [f"Student {i+1}" for i in range(len(df))]
        
        selected_student = st.selectbox("Choose a student:", options=student_options)
    
    if selected_student:
        # Get student data using index (handles duplicates correctly)
        # Extract index from the selection string [#index]
        if '[#' in selected_student:
            idx = int(selected_student.split('[#')[-1].replace(']', ''))
            student_data = df.iloc[idx]
        else:
            idx = student_options.index(selected_student)
            student_data = df.iloc[idx]
        
        with col2:
            if name_col:
                initials = ''.join([n[0] for n in str(student_data[name_col]).split()[:2]])
                st.markdown(f"""
                <div style="text-align: center; padding: 20px;">
                    <div style="background-color: #4CAF50; color: white; width: 80px; height: 80px; 
                               border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                               font-size: 24px; font-weight: bold; margin: 0 auto;">
                        {initials}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Performance Overview
        total_pct = student_data['Total_Percentage']
        total_max = student_data.get('Total_Max', 480)
        
        if total_pct >= 80:
            status = "🎉 Excellent Performance!"
            color = "green"
        elif total_pct >= 65:
            status = "👍 Good Performance"
            color = "blue"
        elif total_pct >= 50:
            status = "📈 Average Performance"
            color = "orange"
        else:
            status = "📚 Needs Improvement"
            color = "red"
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; background-color: {color}20; 
                    border-left: 5px solid {color}; margin: 10px 0;">
            <h3 style="color: {color}; margin: 0;">{status}</h3>
            <p style="margin: 5px 0 0 0;">Overall Score: {student_data['Score']}/{total_max} ({total_pct:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Score", f"{student_data['Score']}/{total_max}", f"{total_pct:.1f}%")
        
        with col2:
            rank = student_data['Rank']
            st.metric("Rank", f"{rank}/{len(df)}", f"Top {(rank/len(df)*100):.1f}%")
        
        with col3:
            avg_score = df['Score'].mean()
            diff = student_data['Score'] - avg_score
            st.metric("vs Class Average", f"{diff:+.1f}", f"Avg: {avg_score:.1f}")
        
        with col4:
            percentile = (df['Score'] < student_data['Score']).sum() / len(df) * 100
            st.metric("Percentile", f"{percentile:.1f}th")
        
        st.write("---")
        
        # Section-wise Performance
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Section-wise Performance")
            
            sections = []
            student_scores = []
            class_averages = []
            
            for col_name, max_val in score_columns.items():
                display_name = col_name.split('(')[0].strip()
                sections.append(display_name)
                student_scores.append((student_data[col_name] / max_val) * 100)
                class_averages.append((df[col_name].mean() / max_val) * 100)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=student_scores + [student_scores[0]],
                theta=sections + [sections[0]],
                fill='toself',
                name='Student',
                line_color='blue'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=class_averages + [class_averages[0]],
                theta=sections + [sections[0]],
                fill='toself',
                name='Class Average',
                line_color='red',
                fillcolor='rgba(255,0,0,0.1)'
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Performance vs Class Average",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Section Scores")
            
            section_data = []
            for col_name, max_val in score_columns.items():
                display_name = col_name.split('(')[0].strip()
                score = student_data[col_name]
                pct = (score / max_val) * 100
                section_data.append({
                    'Section': display_name,
                    'Score': f"{int(score)}/{max_val}",
                    'Percentage': f"{pct:.1f}%"
                })
            
            st.dataframe(pd.DataFrame(section_data), use_container_width=True)
        
        st.write("---")
        
        # Strengths and Improvements
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 Strengths")
            has_strength = False
            for col_name, max_val in score_columns.items():
                display_name = col_name.split('(')[0].strip()
                student_pct = (student_data[col_name] / max_val) * 100
                class_avg = (df[col_name].mean() / max_val) * 100
                if student_pct > class_avg:
                    st.success(f"**{display_name}**: {student_pct:.1f}% (Class avg: {class_avg:.1f}%)")
                    has_strength = True
            if not has_strength:
                st.info("Focus on improving all sections to reach class average.")
        
        with col2:
            st.subheader("📈 Areas for Improvement")
            has_improvement = False
            for col_name, max_val in score_columns.items():
                display_name = col_name.split('(')[0].strip()
                student_pct = (student_data[col_name] / max_val) * 100
                class_avg = (df[col_name].mean() / max_val) * 100
                if student_pct < class_avg:
                    gap = class_avg - student_pct
                    st.warning(f"**{display_name}**: {gap:.1f}% below class average")
                    has_improvement = True
            if not has_improvement:
                st.success("🎉 Above class average in all sections!")
        
        st.write("---")
        
        # Student Info
        st.subheader("👤 Student Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Name:** {student_data.get('Student_Name', 'N/A')}\n\n**Reg:** {student_data.get('College_Reg', 'N/A')}\n\n**Email:** {student_data.get('Email', 'N/A')}")
        
        with col2:
            st.info(f"**Batch:** {student_data.get('Batch', 'N/A')}\n\n**Branch:** {student_data.get('Branch', 'N/A')}")
        
        with col3:
            st.info(f"**Overall:** {total_pct:.1f}%\n\n**Rank:** {rank}/{len(df)}")

# ============================================
# COURSE STUDENT ANALYTICS
# ============================================
elif data_mode == "course":
    st.title("🧑‍🎓 Student-Level Analytics")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    tab1, tab2 = st.tabs(["**Student Portfolio**", "**Top Performers Leaderboard**"])
    
    with tab1:
        st.header("Student Portfolio Dashboard")
        
        if 'Registration Number' not in df.columns:
            st.error("Registration Number column not found in data.")
            st.stop()
        
        student_list = df['Registration Number'].unique()
        selected_reg_num = st.selectbox(
            "Search for a student by Registration Number:",
            options=student_list,
            placeholder="Select a student..."
        )
        
        if selected_reg_num:
            student_data = df[df['Registration Number'] == selected_reg_num].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Student Name", f"{student_data.get('First Name', '')} {student_data.get('Last Name', '')}")
            col2.metric("Branch", f"{student_data.get('Branch Name', 'N/A')}")
            col3.metric("Year of Passing", f"{int(student_data.get('Year of Passing', 0))}")
            
            st.subheader("Overall Progress")
            col1, col2, col3 = st.columns(3)
            col1.metric("Courses Started", f"{student_data.get('Courses Started', 0)}")
            col2.metric("Courses Completed", f"{student_data.get('Courses Completed', 0)}")
            col3.metric("Overall Completion %", f"{student_data.get('Overall Completion %', 0):.2f}%")
            
            completion_pct = student_data.get('Overall Completion %', 0)
            st.progress(min(completion_pct / 100, 1.0))
            
            st.subheader("Course Progress Details")
            
            if course_columns:
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
            
            if 'Branch Name' in df.columns and course_columns:
                branch_df = df[df['Branch Name'] == student_data['Branch Name']]
                branch_course_counts = (branch_df[course_columns] > 0).sum().sort_values(ascending=False)
                top_10_branch_courses = branch_course_counts.head(10).index
                
                student_courses = student_data[course_columns]
                courses_not_started = student_courses[student_courses == 0].index
                
                recommendations = list(set(top_10_branch_courses) & set(courses_not_started))
                
                if not recommendations:
                    st.info("This student is already taking most of the popular courses for their branch!")
                else:
                    st.write("Based on popular courses in their branch, here are some recommendations:")
                    for course in recommendations[:5]:
                        st.markdown(f"- **{course}** (*Taken by {branch_course_counts[course]} students in {student_data['Branch Name']}*)")
    
    with tab2:
        st.header("Top Performers Leaderboard")
        
        col1, col2, col3 = st.columns(3)
        
        branch_options = ["All"] + list(df['Branch Name'].unique()) if 'Branch Name' in df.columns else ["All"]
        selected_branch = col1.selectbox("Filter by Branch:", branch_options)
        
        year_options = ["All"] + sorted([int(y) for y in df['Year of Passing'].dropna().unique()]) if 'Year of Passing' in df.columns else ["All"]
        selected_year = col2.selectbox("Filter by Year:", year_options)
        
        top_n = col3.number_input("Show Top N Students:", min_value=5, max_value=100, value=20)
        
        filtered_df = df.copy()
        
        if selected_branch != "All":
            filtered_df = filtered_df[filtered_df['Branch Name'] == selected_branch]
        
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df['Year of Passing'] == selected_year]
        
        st.subheader(f"Top {top_n} Students by Overall Completion %")
        
        if 'Overall Completion %' in filtered_df.columns:
            leaderboard = filtered_df.sort_values(by="Overall Completion %", ascending=False)
            
            display_cols = ['First Name', 'Last Name', 'Registration Number', 
                           'Branch Name', 'Overall Completion %', 'Courses Completed']
            display_cols = [c for c in display_cols if c in leaderboard.columns]
            
            st.dataframe(leaderboard[display_cols].head(top_n), use_container_width=True)
