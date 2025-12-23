import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import numpy as np

st.set_page_config(page_title="Rankings", page_icon="🏆", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.stop()

# ============================================
# ASSESSMENT RANKINGS & LEADERBOARD
# ============================================
if data_mode == "assessment":
    st.title("🏆 Rankings & Leaderboard")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_top_n = st.selectbox("Show Top N:", options=[10, 20, 30, 50, 100, "All"], index=1)
    
    with col2:
        if 'Batch' in df.columns and df['Batch'].notna().any():
            batches = ["All"] + sorted([str(b) for b in df['Batch'].dropna().unique().tolist()])
            batch_filter = st.selectbox("Batch:", options=batches)
        else:
            batch_filter = "All"
    
    with col3:
        if 'Branch' in df.columns and df['Branch'].notna().any():
            branches = ["All"] + sorted(df['Branch'].dropna().unique().tolist())
            branch_filter = st.selectbox("Branch:", options=branches)
        else:
            branch_filter = "All"
    
    # Apply filters
    filtered_df = df.copy()
    if batch_filter != "All" and 'Batch' in df.columns:
        filtered_df = filtered_df[filtered_df['Batch'].astype(str) == batch_filter]
    if branch_filter != "All" and 'Branch' in df.columns:
        filtered_df = filtered_df[filtered_df['Branch'] == branch_filter]
    
    filtered_df['Filtered_Rank'] = filtered_df['Score'].rank(method='dense', ascending=False).fillna(0).astype(int)
    
    display_count = len(filtered_df) if show_top_n == "All" else min(show_top_n, len(filtered_df))
    
    st.write("---")
    
    # Overall Leaderboard
    st.subheader("🥇 Overall Leaderboard")
    
    leaderboard = filtered_df.nlargest(display_count, 'Score').reset_index(drop=True)
    
    display_cols = ['Filtered_Rank']
    if 'Student_Name' in df.columns:
        display_cols.append('Student_Name')
    if 'College_Reg' in df.columns:
        display_cols.append('College_Reg')
    display_cols.extend(['Score', 'Total_Percentage'])
    
    for col in score_columns.keys():
        if col in leaderboard.columns:
            display_cols.append(col)
    
    leaderboard_display = leaderboard[[c for c in display_cols if c in leaderboard.columns]].copy()
    
    def style_leaderboard(row):
        rank = row.iloc[0]
        if rank == 1:
            return ['background-color: #FFD700; font-weight: bold'] * len(row)
        elif rank == 2:
            return ['background-color: #C0C0C0; font-weight: bold'] * len(row)
        elif rank == 3:
            return ['background-color: #CD7F32; font-weight: bold'] * len(row)
        elif rank <= 10:
            return ['background-color: #E8F5E8'] * len(row)
        return [''] * len(row)
    
    styled = leaderboard_display.style.apply(style_leaderboard, axis=1)
    st.dataframe(styled, use_container_width=True, height=600)
    
    st.write("---")
    
    # Section-wise Rankings
    st.subheader("📊 Section-wise Top Performers")
    
    tabs = st.tabs([col.split('(')[0].strip() for col in score_columns.keys()])
    
    for i, (col_name, max_val) in enumerate(score_columns.items()):
        with tabs[i]:
            section_name = col_name.split('(')[0].strip()
            st.subheader(f"Top 15 in {section_name}")
            
            section_top = filtered_df.nlargest(15, col_name).reset_index(drop=True)
            section_top['Section_Rank'] = range(1, len(section_top) + 1)
            section_top['Percentage'] = (section_top[col_name] / max_val * 100).round(1)
            
            chart_data = section_top.head(10)
            x_col = 'Student_Name' if 'Student_Name' in df.columns else chart_data.index
            
            fig = px.bar(chart_data, x=x_col if isinstance(x_col, str) else None,
                        y=col_name, title=f"Top 10 {section_name} Performers", text=col_name)
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            display_cols = ['Section_Rank']
            if 'Student_Name' in df.columns:
                display_cols.append('Student_Name')
            display_cols.extend([col_name, 'Percentage', 'Filtered_Rank'])
            
            st.dataframe(section_top[[c for c in display_cols if c in section_top.columns]], use_container_width=True)

# ============================================
# COURSE BRANCH ANALYTICS
# ============================================
elif data_mode == "course":
    st.title("🏛️ Branch & Cohort Analytics")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    if 'Branch Name' not in df.columns:
        st.error("Branch Name column not found in data.")
        st.stop()
    
    @st.cache_data
    def get_branch_year_stats(_df):
        stats = _df.groupby(['Branch Name', 'Year of Passing']).agg(
            Avg_Overall_Completion=('Overall Completion %', 'mean'),
            Avg_Courses_Started=('Courses Started', 'mean'),
            Avg_Courses_Completed=('Courses Completed', 'mean')
        ).reset_index()
        return stats
    
    @st.cache_data
    def get_top_courses_by_branch(_df, _course_columns):
        branches = _df['Branch Name'].unique()
        all_top_courses = []
        
        for branch in branches:
            branch_df = _df[_df['Branch Name'] == branch]
            branch_enrollment = (branch_df[_course_columns] > 0).sum().sort_values(ascending=False)
            
            top_10 = branch_enrollment.head(10).reset_index()
            top_10.columns = ['Course Name', 'Student Count']
            top_10['Branch Name'] = branch
            all_top_courses.append(top_10)
        
        return pd.concat(all_top_courses)
    
    tab1, tab2, tab3 = st.tabs(["**Branch Comparison**", "**Top Courses by Branch**", "**Progress Distribution**"])
    
    with tab1:
        st.header("Branch Comparison Dashboard")
        
        st.subheader("Filters")
        
        all_branches = list(df['Branch Name'].dropna().unique())
        selected_branches = st.multiselect("Select Branches:", options=all_branches, default=all_branches)
        
        if 'Year of Passing' in df.columns:
            all_years = sorted(list(df['Year of Passing'].dropna().unique()))
            selected_years = st.multiselect("Select Years:", options=all_years, default=all_years)
        else:
            selected_years = []
        
        if not selected_branches:
            st.info("Please select at least one Branch.")
            st.stop()
        
        filtered_df = df[df['Branch Name'].isin(selected_branches)]
        if selected_years and 'Year of Passing' in df.columns:
            filtered_df = filtered_df[filtered_df['Year of Passing'].isin(selected_years)]
        
        if 'Year of Passing' in filtered_df.columns and len(selected_years) > 0:
            branch_year_stats = get_branch_year_stats(filtered_df)
            
            st.subheader("Average Overall Completion %")
            
            chart = alt.Chart(branch_year_stats).mark_bar().encode(
                x=alt.X('Branch Name', sort=None),
                y=alt.Y('Avg_Overall_Completion', title='Avg. Overall Completion %'),
                color='Year of Passing:N',
                column=alt.Column('Year of Passing:N'),
                tooltip=['Branch Name', 'Year of Passing', 'Avg_Overall_Completion']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            branch_stats = filtered_df.groupby('Branch Name').agg({
                'Overall Completion %': 'mean',
                'Courses Started': 'mean'
            }).reset_index()
            
            fig = px.bar(branch_stats, x='Branch Name', y='Overall Completion %',
                        title="Average Completion by Branch")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Top 10 Popular Courses by Branch")
        
        if course_columns:
            top_courses_df = get_top_courses_by_branch(df, course_columns)
            top_courses_filtered = top_courses_df[top_courses_df['Branch Name'].isin(selected_branches)]
            
            for branch in selected_branches[:3]:
                st.subheader(f"📚 {branch}")
                branch_data = top_courses_filtered[top_courses_filtered['Branch Name'] == branch]
                
                chart = alt.Chart(branch_data).mark_bar().encode(
                    x=alt.X('Course Name', sort='-y'),
                    y='Student Count',
                    tooltip=['Course Name', 'Student Count']
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
    
    with tab3:
        st.header("Student Progress Distribution")
        
        if not selected_branches:
            st.info("Please select filters on the 'Branch Comparison' tab.")
            st.stop()
        
        filtered_df = df[df['Branch Name'].isin(selected_branches)]
        if selected_years and 'Year of Passing' in df.columns:
            filtered_df = filtered_df[filtered_df['Year of Passing'].isin(selected_years)]
        
        st.write(f"Showing distribution for {len(filtered_df)} selected students.")
        
        if 'Overall Completion %' in filtered_df.columns:
            histogram = alt.Chart(filtered_df).mark_bar().encode(
                alt.X("Overall Completion %", bin=alt.Bin(maxbins=20)),
                alt.Y('count()', title="Number of Students"),
                tooltip=[alt.X("Overall Completion %", bin=alt.Bin(maxbins=20)), 'count()']
            ).properties(
                title="Distribution of Student Overall Completion"
            ).interactive()
            
            st.altair_chart(histogram, use_container_width=True)
