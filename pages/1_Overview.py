import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.info("Go to the Home page, select your data type, and upload your file.")
    st.stop()

# ============================================
# ASSESSMENT OVERVIEW DASHBOARD
# ============================================
if data_mode == "assessment":
    st.title("📊 Assessment Overview Dashboard")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    # Key Metrics Row
    st.subheader("📈 Key Performance Metrics")
    
    total_max = df['Total_Max'].iloc[0] if 'Total_Max' in df.columns else 480
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", len(df))
    
    with col2:
        avg_score = df['Score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}/{total_max}", f"{(avg_score/total_max*100):.1f}%")
    
    with col3:
        top_score = df['Score'].max()
        if 'Student_Name' in df.columns:
            top_student = df[df['Score'] == top_score]['Student_Name'].iloc[0]
            st.metric("Highest Score", f"{top_score}/{total_max}", f"by {top_student}")
        else:
            st.metric("Highest Score", f"{top_score}/{total_max}")
    
    with col4:
        pass_students = len(df[df['Total_Percentage'] >= 50])
        pass_rate = (pass_students / len(df)) * 100
        st.metric("Pass Rate (≥50%)", f"{pass_rate:.1f}%", f"{pass_students} students")
    
    with col5:
        excellent_students = len(df[df['Total_Percentage'] >= 80])
        excellent_rate = (excellent_students / len(df)) * 100
        st.metric("Excellence (≥80%)", f"{excellent_rate:.1f}%", f"{excellent_students} students")
    
    st.write("---")
    
    # Section-wise Performance
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Section-wise Performance")
        
        section_data = {'Section': [], 'Average Score': [], 'Max Score': []}
        
        for col_name, max_val in score_columns.items():
            display_name = col_name.split('(')[0].strip()
            section_data['Section'].append(display_name)
            section_data['Average Score'].append(df[col_name].mean())
            section_data['Max Score'].append(max_val)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Average Score',
            x=section_data['Section'],
            y=section_data['Average Score'],
            text=[f"{score:.1f}" for score in section_data['Average Score']],
            textposition='auto',
        ))
        
        fig.add_trace(go.Scatter(
            name='Max Possible',
            x=section_data['Section'],
            y=section_data['Max Score'],
            mode='lines+markers',
            line=dict(color='red', dash='dash'),
        ))
        
        fig.update_layout(title="Average Scores by Section", height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Section Summary")
        
        for col_name, max_val in score_columns.items():
            display_name = col_name.split('(')[0].strip()
            avg_pct = (df[col_name].mean() / max_val) * 100
            st.metric(f"{display_name}", f"{avg_pct:.1f}%", f"Avg: {df[col_name].mean():.1f}/{max_val}")
    
    st.write("---")
    
    # Distribution Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Score Distribution")
        fig = px.histogram(df, x='Score', nbins=20, title="Distribution of Total Scores")
        fig.add_vline(x=df['Score'].mean(), line_dash="dash", line_color="red",
                      annotation_text=f"Avg: {df['Score'].mean():.1f}")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Performance Categories")
        
        def categorize(pct):
            if pct >= 80: return "Excellent (≥80%)"
            elif pct >= 65: return "Good (65-79%)"
            elif pct >= 50: return "Average (50-64%)"
            else: return "Below Average (<50%)"
        
        df['Category'] = df['Total_Percentage'].apply(categorize)
        category_counts = df['Category'].value_counts()
        
        fig = px.pie(values=category_counts.values, names=category_counts.index,
                     title="Students by Performance Category")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    # Top Performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Performers")
        display_cols = ['Rank', 'Student_Name', 'Score', 'Total_Percentage'] if 'Student_Name' in df.columns else ['Rank', 'Score', 'Total_Percentage']
        available_cols = [c for c in display_cols if c in df.columns]
        top_10 = df.nlargest(10, 'Score')[available_cols].reset_index(drop=True)
        st.dataframe(top_10, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Section Toppers")
        toppers_data = []
        for col_name, max_val in score_columns.items():
            display_name = col_name.split('(')[0].strip()
            top_idx = df[col_name].idxmax()
            top_row = df.loc[top_idx]
            toppers_data.append({
                'Section': display_name,
                'Student': top_row.get('Student_Name', 'N/A'),
                'Score': f"{top_row[col_name]}/{max_val}",
                'Percentage': f"{(top_row[col_name]/max_val*100):.1f}%"
            })
        st.dataframe(pd.DataFrame(toppers_data), use_container_width=True)

# ============================================
# COURSE OVERVIEW DASHBOARD
# ============================================
elif data_mode == "course":
    st.title("📊 Course Progress Dashboard")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    # Key Metrics
    st.subheader("📈 Key Metrics")
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
        if 'Courses Completed' in df.columns:
            completed = len(df[df['Courses Completed'] > 0])
            st.metric("Students Completed", f"{completed}", f"{(completed/len(df)*100):.1f}%")
    
    st.write("---")
    
    # Branch-wise Performance
    if 'Branch Name' in df.columns:
        st.subheader("🏛️ Branch-wise Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Course Started Status by Branch (≥10%)**")
            df['Started_Status'] = df['Courses Started'].apply(lambda x: 'Started' if x > 0 else 'Not Started')
            started_by_branch = df.groupby(['Branch Name', 'Started_Status']).size().reset_index(name='Count')
            
            chart = alt.Chart(started_by_branch).mark_bar().encode(
                x=alt.X('Branch Name', sort=None),
                y='Count',
                color='Started_Status',
                tooltip=['Branch Name', 'Started_Status', 'Count']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            st.write("**Course Completed Status by Branch (≥90%)**")
            if 'Courses Completed' in df.columns:
                df['Completed_Status'] = df['Courses Completed'].apply(lambda x: 'Completed' if x > 0 else 'Not Completed')
                completed_by_branch = df.groupby(['Branch Name', 'Completed_Status']).size().reset_index(name='Count')
                
                chart = alt.Chart(completed_by_branch).mark_bar().encode(
                    x=alt.X('Branch Name', sort=None),
                    y='Count',
                    color='Completed_Status',
                    tooltip=['Branch Name', 'Completed_Status', 'Count']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
    
    st.write("---")
    
    # Overall Progress Distribution
    st.subheader("📈 Overall Progress Distribution")
    
    if 'Overall Completion %' in df.columns:
        fig = px.histogram(df, x='Overall Completion %', nbins=20,
                          title="Distribution of Student Completion Percentages")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    # Top Enrolled Courses (>=10% considered as started/enrolled)
    st.subheader("📚 Top 10 Enrolled Courses (≥10%)")
    
    if course_columns:
        enrollment = (df[course_columns] >= 10).sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(x=enrollment.index, y=enrollment.values,
                    labels={'x': 'Course', 'y': 'Students Enrolled'},
                    title="Top 10 Courses by Enrollment (≥10%)")
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
