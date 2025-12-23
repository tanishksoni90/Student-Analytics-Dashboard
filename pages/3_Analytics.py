import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import numpy as np

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.stop()

# ============================================
# ASSESSMENT SECTION ANALYSIS
# ============================================
if data_mode == "assessment":
    st.title("📈 Section-wise Performance Analysis")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    if not score_columns:
        st.error("No score columns detected in the data.")
        st.stop()
    
    # Section Selection
    st.subheader("🎯 Select Section for Analysis")
    
    section_names = {col: col.split('(')[0].strip() for col in score_columns.keys()}
    selected_col = st.selectbox("Choose Section:", options=list(score_columns.keys()),
                                format_func=lambda x: section_names[x])
    
    section_name = section_names[selected_col]
    max_score = score_columns[selected_col]
    
    st.write("---")
    
    # Section Overview Metrics
    st.subheader(f"📊 {section_name} - Performance Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg = df[selected_col].mean()
        st.metric("Average Score", f"{avg:.1f}/{max_score}", f"{(avg/max_score*100):.1f}%")
    
    with col2:
        max_val = df[selected_col].max()
        topper = df[df[selected_col] == max_val]
        if 'Student_Name' in df.columns and len(topper) > 0:
            st.metric("Highest Score", f"{max_val}/{max_score}", f"by {topper['Student_Name'].iloc[0]}")
        else:
            st.metric("Highest Score", f"{max_val}/{max_score}")
    
    with col3:
        min_val = df[selected_col].min()
        st.metric("Lowest Score", f"{min_val}/{max_score}", f"{(min_val/max_score*100):.1f}%")
    
    with col4:
        std = df[selected_col].std()
        st.metric("Std Deviation", f"{std:.1f}")
    
    with col5:
        above_avg = len(df[df[selected_col] > avg])
        st.metric("Above Average", f"{above_avg}/{len(df)}", f"{(above_avg/len(df)*100):.1f}%")
    
    st.write("---")
    
    # Distribution and Categories
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 {section_name} Score Distribution")
        
        fig = px.histogram(df, x=selected_col, nbins=20,
                          title=f"Distribution of {section_name} Scores")
        
        for p, color in [(25, 'orange'), (50, 'red'), (75, 'green')]:
            val = np.percentile(df[selected_col], p)
            fig.add_vline(x=val, line_dash="dash", line_color=color,
                         annotation_text=f"{p}th: {val:.1f}")
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Performance Categories")
        
        def categorize(score):
            pct = (score / max_score) * 100
            if pct >= 80: return "Excellent (≥80%)"
            elif pct >= 65: return "Good (65-79%)"
            elif pct >= 50: return "Average (50-64%)"
            else: return "Below Average (<50%)"
        
        df['_Category'] = df[selected_col].apply(categorize)
        category_counts = df['_Category'].value_counts()
        
        fig = px.pie(values=category_counts.values, names=category_counts.index,
                     title=f"{section_name} Categories")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    # Top and Bottom Performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏆 Top 10 - {section_name}")
        
        top_10 = df.nlargest(10, selected_col).reset_index(drop=True)
        top_10['Rank'] = range(1, len(top_10) + 1)
        top_10['Percentage'] = (top_10[selected_col] / max_score * 100).round(1)
        
        display_cols = ['Rank']
        if 'Student_Name' in df.columns:
            display_cols.append('Student_Name')
        display_cols.extend([selected_col, 'Percentage'])
        
        st.dataframe(top_10[display_cols], use_container_width=True)
    
    with col2:
        st.subheader(f"📚 Need Support - {section_name}")
        
        threshold = max_score * 0.4
        low_performers = df[df[selected_col] < threshold].nsmallest(10, selected_col)
        
        if not low_performers.empty:
            low_performers = low_performers.reset_index(drop=True)
            low_performers['Percentage'] = (low_performers[selected_col] / max_score * 100).round(1)
            
            display_cols = []
            if 'Student_Name' in df.columns:
                display_cols.append('Student_Name')
            display_cols.extend([selected_col, 'Percentage'])
            
            st.dataframe(low_performers[display_cols], use_container_width=True)
        else:
            st.success("🎉 All students scored above 40%!")

# ============================================
# COURSE ANALYTICS
# ============================================
elif data_mode == "course":
    st.title("📊 Course-Level Analytics")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    if not course_columns:
        st.error("No course columns detected in the data.")
        st.stop()
    
    # Calculate course stats
    @st.cache_data
    def calculate_course_stats(_df, _course_columns):
        stats = []
        for course in _course_columns:
            course_data = pd.to_numeric(_df[course], errors='coerce').fillna(0)
            enrolled = (course_data > 0).sum()
            completed = (course_data == 100).sum()
            
            stats.append({
                'Course Name': course,
                'Total Enrollment': enrolled,
                'Total Completed': completed,
                'Completion Rate (%)': (completed / enrolled * 100) if enrolled > 0 else 0,
                'Average Completion %': course_data[course_data > 0].mean() if enrolled > 0 else 0
            })
        return pd.DataFrame(stats)
    
    all_course_stats = calculate_course_stats(df, course_columns)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "**Top Enrolled Courses**",
        "**Course Deep Dive**",
        "**Course Performance**",
        "**Course Co-Enrollment**"
    ])
    
    with tab1:
        st.header("Top Courses by Student Enrollment")
        
        top_n = st.number_input("How many top courses?", min_value=1, max_value=len(course_columns), value=10, step=1)
        
        top_enrolled = all_course_stats.sort_values('Total Enrollment', ascending=False).head(top_n)
        
        fig = px.bar(top_enrolled, x='Course Name', y='Total Enrollment',
                    title=f"Top {top_n} Courses by Enrollment")
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(top_enrolled[['Course Name', 'Total Enrollment']], use_container_width=True)
    
    with tab2:
        st.header("Course Deep Dive")
        
        selected_course = st.selectbox("Select a course to analyze:", options=course_columns)
        
        if selected_course:
            course_data = all_course_stats[all_course_stats['Course Name'] == selected_course].iloc[0]
            
            st.subheader(f"Metrics for: **{selected_course}**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Enrollment", int(course_data['Total Enrollment']))
            col2.metric("Completion Rate", f"{course_data['Completion Rate (%)']:.2f}%")
            col3.metric("Avg Completion (enrolled)", f"{course_data['Average Completion %']:.2f}%")
            
            if 'Branch Name' in df.columns and course_data['Total Enrollment'] > 0:
                st.subheader("Enrollment by Branch")
                enrolled_df = df[df[selected_course] > 0]
                branch_counts = enrolled_df['Branch Name'].value_counts().reset_index()
                branch_counts.columns = ['Branch Name', 'Student Count']
                
                chart = alt.Chart(branch_counts).mark_bar().encode(
                    x=alt.X('Branch Name', sort=None),
                    y='Student Count',
                    tooltip=['Branch Name', 'Student Count']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
    
    with tab3:
        st.header("Most & Least Completed Courses")
        st.write("Based on **Completion Rate** (students who finished / students who started)")
        
        min_enrollment = st.slider("Minimum enrollment to consider:", 1, 50, 10)
        
        stats_filtered = all_course_stats[all_course_stats['Total Enrollment'] >= min_enrollment]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 5 Most Completed")
            top_5 = stats_filtered.sort_values('Completion Rate (%)', ascending=False).head(5)
            st.dataframe(top_5[['Course Name', 'Completion Rate (%)', 'Total Enrollment']], use_container_width=True)
        
        with col2:
            st.subheader("📉 Top 5 Least Completed")
            bottom_5 = stats_filtered.sort_values('Completion Rate (%)', ascending=True).head(5)
            st.dataframe(bottom_5[['Course Name', 'Completion Rate (%)', 'Total Enrollment']], use_container_width=True)
    
    with tab4:
        st.header("Course Co-Enrollment Heatmap")
        st.write("Shows which courses are most frequently taken together.")
        st.info("Only courses with > 10 students are included.")
        
        # Calculate co-enrollment
        enrolled_df = (df[course_columns] > 0).astype(int)
        popular_courses = enrolled_df.sum()[enrolled_df.sum() > 10].index.tolist()
        
        if len(popular_courses) > 1:
            enrolled_popular = enrolled_df[popular_courses]
            co_occurrence = enrolled_popular.T.dot(enrolled_popular)
            
            co_df = co_occurrence.stack().reset_index()
            co_df.columns = ['Course 1', 'Course 2', 'Student Count']
            co_df = co_df[co_df['Course 1'] != co_df['Course 2']]
            
            heatmap = alt.Chart(co_df).mark_rect().encode(
                x=alt.X('Course 1', sort=popular_courses[:15]),
                y=alt.Y('Course 2', sort=popular_courses[:15]),
                color=alt.Color('Student Count', scale=alt.Scale(scheme='viridis')),
                tooltip=['Course 1', 'Course 2', 'Student Count']
            ).properties(
                title="Course Co-Enrollment",
                width=600,
                height=600
            ).interactive()
            
            st.altair_chart(heatmap, use_container_width=True)
        else:
            st.warning("Not enough courses with >10 enrollments for co-enrollment analysis.")
