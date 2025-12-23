import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import io
from datetime import datetime

st.set_page_config(page_title="Downloads", page_icon="📥", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.stop()

# ============================================
# ASSESSMENT BULK DOWNLOADS
# ============================================
if data_mode == "assessment":
    st.title("📥 Bulk Downloads & Export Center")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    def create_excel_report(df, score_columns):
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student_Data', index=False)
            
            # Rankings
            rankings = df.sort_values('Score', ascending=False)
            cols = ['Rank', 'Student_Name', 'College_Reg', 'Score', 'Total_Percentage'] if 'Student_Name' in df.columns else ['Rank', 'Score', 'Total_Percentage']
            cols = [c for c in cols if c in rankings.columns]
            rankings[cols].to_excel(writer, sheet_name='Rankings', index=False)
            
            # Section toppers
            for col_name, max_val in score_columns.items():
                section = col_name.split('(')[0].strip()[:20]
                top_20 = df.nlargest(20, col_name)
                cols = ['Student_Name', col_name] if 'Student_Name' in df.columns else [col_name]
                cols = [c for c in cols if c in top_20.columns]
                top_20[cols].to_excel(writer, sheet_name=f'Top_{section}', index=False)
            
            # Statistics
            total_max = df['Total_Max'].iloc[0] if 'Total_Max' in df.columns else 480
            stats = pd.DataFrame({
                'Metric': ['Total Students', 'Average Score', 'Highest Score', 'Pass Rate (≥50%)'],
                'Value': [len(df), f"{df['Score'].mean():.2f}/{total_max}",
                         f"{df['Score'].max()}/{total_max}",
                         f"{len(df[df['Total_Percentage'] >= 50])/len(df)*100:.1f}%"]
            })
            stats.to_excel(writer, sheet_name='Statistics', index=False)
        
        return output.getvalue()
    
    def create_student_assessment_report(df, score_columns):
        """Generate Student Assessment Report with multiple sheets:
        Student_Data, Summary_Statistics, Rankings, Top_<Section> for each section"""
        output = io.BytesIO()
        
        # === Sheet 1: Student_Data ===
        student_data = pd.DataFrame()
        
        # Basic info columns
        for col in ['Student_Name', 'Email', 'College_Reg', 'Batch', 'Branch']:
            if col in df.columns:
                student_data[col] = df[col]
        
        # Score columns with max values
        for col_name, max_val in score_columns.items():
            student_data[col_name] = df[col_name]
        
        # Total Score
        if 'Score' in df.columns:
            student_data['Score'] = df['Score']
        
        # Additional columns if present
        for extra_col in ['English', 'Technical MCQ', 'Coding']:
            if extra_col in df.columns:
                student_data[extra_col] = df[extra_col]
        
        # Individual percentage columns for each score column
        for col_name, max_val in score_columns.items():
            section_name = col_name.split('(')[0].strip()
            pct_col = f"{section_name}_Percentage"
            if pct_col in df.columns:
                student_data[pct_col] = df[pct_col]
            elif max_val > 0:
                student_data[pct_col] = (df[col_name] / max_val * 100).round(2)
        
        # Total percentage and Rank
        if 'Total_Percentage' in df.columns:
            student_data['Total_Percentage'] = df['Total_Percentage']
        if 'Rank' in df.columns:
            student_data['Rank'] = df['Rank']
        
        # Sort by Rank
        if 'Rank' in student_data.columns:
            student_data = student_data.sort_values('Rank')
        
        # === Sheet 2: Summary_Statistics ===
        stats_data = []
        
        # General stats
        stats_data.append({'Metric': 'Total Students', 'Value': str(len(df)), 'Category': 'General'})
        if 'Score' in df.columns:
            stats_data.append({'Metric': 'Average Total Score', 'Value': f"{df['Score'].mean():.2f}", 'Category': 'General'})
        if 'Total_Percentage' in df.columns:
            stats_data.append({'Metric': 'Average Percentage', 'Value': f"{df['Total_Percentage'].mean():.2f}%", 'Category': 'General'})
        
        # Section-wise stats
        for col_name, max_val in score_columns.items():
            section_name = col_name.split('(')[0].strip()
            avg_score = df[col_name].mean()
            max_score = df[col_name].max()
            std_dev = df[col_name].std()
            
            stats_data.append({'Metric': f'{section_name} - Average Score', 'Value': f"{avg_score:.2f}/{max_val}", 'Category': section_name})
            stats_data.append({'Metric': f'{section_name} - Highest Score', 'Value': f"{int(max_score)}/{max_val}", 'Category': section_name})
            stats_data.append({'Metric': f'{section_name} - Standard Deviation', 'Value': f"{std_dev:.2f}", 'Category': section_name})
        
        summary_stats = pd.DataFrame(stats_data)
        
        # === Sheet 3: Rankings ===
        rankings = df.sort_values('Score', ascending=False).copy()
        ranking_cols = ['Rank', 'Student_Name', 'College_Reg', 'Score', 'Total_Percentage']
        ranking_cols = [c for c in ranking_cols if c in rankings.columns]
        rankings_sheet = rankings[ranking_cols].copy()
        
        # === Write all sheets ===
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            student_data.to_excel(writer, sheet_name='Student_Data', index=False)
            summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)
            rankings_sheet.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Top performers for each section
            for col_name, max_val in score_columns.items():
                section_name = col_name.split('(')[0].strip()
                pct_col = f"{section_name}_Percentage"
                
                # Get top 20 for this section
                top_section = df.nlargest(20, col_name).copy()
                
                # Build columns for this sheet
                top_cols = ['Student_Name', col_name]
                if pct_col in df.columns:
                    top_cols.append(pct_col)
                elif max_val > 0:
                    top_section[pct_col] = (top_section[col_name] / max_val * 100).round(2)
                    top_cols.append(pct_col)
                
                top_cols = [c for c in top_cols if c in top_section.columns]
                top_section[top_cols].to_excel(writer, sheet_name=f'Top_{section_name}'[:31], index=False)
        
        return output.getvalue()
    
    # Export Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Reports", "🏆 Rankings", "📧 Email Lists"])
    
    with tab1:
        st.subheader("📋 Complete Reports")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            batches = ["All"] + (sorted([str(b) for b in df['Batch'].dropna().unique().tolist()]) if 'Batch' in df.columns else [])
            batch_filter = st.selectbox("Batch:", batches)
        
        with col2:
            branches = ["All"] + (sorted(df['Branch'].dropna().unique().tolist()) if 'Branch' in df.columns else [])
            branch_filter = st.selectbox("Branch:", branches)
        
        with col3:
            perf_filter = st.selectbox("Performance:", ["All", "Top 25%", "Top 50%", "Bottom 25%"])
        
        # Apply filters
        filtered_df = df.copy()
        if batch_filter != "All" and 'Batch' in df.columns:
            filtered_df = filtered_df[filtered_df['Batch'].astype(str) == batch_filter]
        if branch_filter != "All" and 'Branch' in df.columns:
            filtered_df = filtered_df[filtered_df['Branch'] == branch_filter]
        if perf_filter == "Top 25%":
            threshold = filtered_df['Total_Percentage'].quantile(0.75)
            filtered_df = filtered_df[filtered_df['Total_Percentage'] >= threshold]
        elif perf_filter == "Top 50%":
            threshold = filtered_df['Total_Percentage'].quantile(0.50)
            filtered_df = filtered_df[filtered_df['Total_Percentage'] >= threshold]
        elif perf_filter == "Bottom 25%":
            threshold = filtered_df['Total_Percentage'].quantile(0.25)
            filtered_df = filtered_df[filtered_df['Total_Percentage'] <= threshold]
        
        st.info(f"📊 Filtered: {len(filtered_df)} students")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            excel_data = create_excel_report(filtered_df, score_columns)
            st.download_button("📥 Download Excel Report", data=excel_data,
                              file_name=f"Assessment_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True)
        
        with col2:
            # Student Assessment Report format (with individual percentages)
            assessment_report = create_student_assessment_report(filtered_df, score_columns)
            st.download_button("📥 Student Assessment Report", data=assessment_report,
                              file_name=f"Student_Assessment_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True)
        
        with col3:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button("📊 Download CSV", data=csv_data,
                              file_name=f"Student_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                              mime="text/csv", use_container_width=True)
    
    with tab2:
        st.subheader("🏆 Rankings Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ranking_type = st.selectbox("Type:", ["Overall", "Section-wise"])
            top_n = st.number_input("Top N:", min_value=10, max_value=len(df), value=50)
        
        rankings = df.nlargest(top_n, 'Score').copy()
        rankings['Export_Rank'] = range(1, len(rankings) + 1)
        
        st.dataframe(rankings.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            excel_out = io.BytesIO()
            with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
                rankings.to_excel(writer, index=False)
            st.download_button("📥 Excel", data=excel_out.getvalue(),
                              file_name=f"Rankings_{datetime.now().strftime('%Y%m%d')}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        with col2:
            st.download_button("📊 CSV", data=rankings.to_csv(index=False),
                              file_name=f"Rankings_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
        
        with col3:
            st.download_button("📋 JSON", data=rankings.to_json(orient='records', indent=2),
                              file_name=f"Rankings_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
    
    with tab3:
        st.subheader("📧 Email Lists")
        
        email_filter = st.selectbox("Filter:", ["All", "Top 25%", "Bottom 25%", "Above 50%", "Below 50%"])
        
        if email_filter == "Top 25%":
            threshold = df['Total_Percentage'].quantile(0.75)
            email_df = df[df['Total_Percentage'] >= threshold]
        elif email_filter == "Bottom 25%":
            threshold = df['Total_Percentage'].quantile(0.25)
            email_df = df[df['Total_Percentage'] <= threshold]
        elif email_filter == "Above 50%":
            email_df = df[df['Total_Percentage'] > 50]
        elif email_filter == "Below 50%":
            email_df = df[df['Total_Percentage'] <= 50]
        else:
            email_df = df
        
        st.metric("Contacts", len(email_df))
        
        if 'Email' in email_df.columns:
            cols = ['Student_Name', 'Email'] if 'Student_Name' in email_df.columns else ['Email']
            export_df = email_df[cols]
            
            st.dataframe(export_df.head(), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button("📧 Download CSV", data=export_df.to_csv(index=False),
                                  file_name=f"Email_List_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
            
            with col2:
                emails_only = "; ".join(export_df['Email'].dropna().tolist())
                st.download_button("📋 Emails Only (TXT)", data=emails_only,
                                  file_name=f"Emails_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")

# ============================================
# COURSE DOWNLOAD CENTER
# ============================================
elif data_mode == "course":
    st.title("📥 Download Center & Reports")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    @st.cache_data
    def get_top_k_courses(_df, _course_columns, k):
        enrollment = (_df[_course_columns] > 0).sum()
        return enrollment.nlargest(k).index.tolist()
    
    @st.cache_data
    def create_master_report(_df, top_k_courses):
        df_report = _df.copy()
        df_report['First Name'] = df_report['First Name'].fillna('')
        df_report['Last Name'] = df_report['Last Name'].fillna('')
        df_report['Full Name'] = df_report['First Name'] + ' ' + df_report['Last Name']
        df_report['S No.'] = range(1, len(df_report) + 1)
        
        base_cols = ['S No.', 'Full Name', 'Email', 'Branch Name', 'Registration Number',
                    'Courses Started', 'Courses Completed']
        valid_top_k = [col for col in top_k_courses if col in df_report.columns]
        
        return df_report[[c for c in base_cols + valid_top_k if c in df_report.columns]]
    
    @st.cache_data
    def create_summary_tables(_df, top_k_courses):
        _df = _df.copy()
        
        # Course Started Summary with proper column names
        _df['Started Status'] = _df['Courses Started'].apply(lambda x: 'Course Started' if x > 0 else 'Course Not Started')
        started_summary = pd.pivot_table(_df, index='Branch Name', columns='Started Status',
                                         aggfunc='size', fill_value=0).reset_index()
        # Add Grand Total row
        grand_total = started_summary.select_dtypes(include='number').sum()
        grand_total['Branch Name'] = 'Grand Total'
        started_summary = pd.concat([started_summary, pd.DataFrame([grand_total])], ignore_index=True)
        # Add Grand Total column
        numeric_cols = started_summary.select_dtypes(include='number').columns.tolist()
        started_summary['Grand Total'] = started_summary[numeric_cols].sum(axis=1)
        
        # Course Completed Summary with proper column names
        _df['Completed Status'] = _df['Overall Completion %'].apply(lambda x: 'Course Completed' if x == 100 else 'Course Not Completed')
        completed_summary = pd.pivot_table(_df, index='Branch Name', columns='Completed Status',
                                           aggfunc='size', fill_value=0).reset_index()
        # Add Grand Total row
        grand_total = completed_summary.select_dtypes(include='number').sum()
        grand_total['Branch Name'] = 'Grand Total'
        completed_summary = pd.concat([completed_summary, pd.DataFrame([grand_total])], ignore_index=True)
        # Add Grand Total column
        numeric_cols = completed_summary.select_dtypes(include='number').columns.tolist()
        completed_summary['Grand Total'] = completed_summary[numeric_cols].sum(axis=1)
        
        return started_summary, completed_summary
    
    @st.cache_data
    def create_course_breakdown(_df, course_col):
        """Create branch-wise breakdown by completion percentage buckets for a course"""
        _df = _df.copy()
        
        def get_completion_bucket(val):
            if pd.isna(val) or val == 0:
                return 'Not Started'
            elif val == 100:
                return 'Completed'
            elif val >= 80:
                return '80% Completed'
            elif val >= 70:
                return '70% Completed'
            elif val >= 60:
                return '60% Completed'
            elif val >= 50:
                return '50% Completed'
            elif val >= 40:
                return '40% Completed'
            elif val >= 30:
                return '30% Completed'
            elif val >= 20:
                return '20% Completed'
            elif val >= 10:
                return '10% Completed'
            else:
                return 'Not Started'
        
        _df['Completion Bucket'] = _df[course_col].apply(get_completion_bucket)
        
        # Create pivot table
        breakdown = pd.pivot_table(_df, index='Branch Name', columns='Completion Bucket',
                                   aggfunc='size', fill_value=0).reset_index()
        
        # Reorder columns logically
        bucket_order = ['Not Started', '10% Completed', '20% Completed', '30% Completed', 
                       '40% Completed', '50% Completed', '60% Completed', '70% Completed', 
                       '80% Completed', 'Completed']
        existing_buckets = [b for b in bucket_order if b in breakdown.columns]
        breakdown = breakdown[['Branch Name'] + existing_buckets]
        
        # Add Grand Total row
        grand_total = breakdown.select_dtypes(include='number').sum()
        grand_total['Branch Name'] = 'Grand Total'
        breakdown = pd.concat([breakdown, pd.DataFrame([grand_total])], ignore_index=True)
        
        # Add Grand Total column
        numeric_cols = breakdown.select_dtypes(include='number').columns.tolist()
        breakdown['Grand Total'] = breakdown[numeric_cols].sum(axis=1)
        
        return breakdown
    
    def create_full_student_report(_df, top_k_courses):
        """Generate Full Student Report with all sheets like the sample file"""
        output = io.BytesIO()
        
        # Master Student Report
        master_report = _df.copy()
        master_report['First Name'] = master_report['First Name'].fillna('')
        master_report['Last Name'] = master_report['Last Name'].fillna('')
        master_report['Full Name'] = master_report['First Name'] + ' ' + master_report['Last Name']
        master_report['S No.'] = range(1, len(master_report) + 1)
        
        base_cols = ['S No.', 'Full Name', 'Email', 'Branch Name', 'Registration Number',
                    'Courses Started', 'Courses Completed']
        valid_top_k = [col for col in top_k_courses if col in master_report.columns]
        master_report = master_report[[c for c in base_cols + valid_top_k if c in master_report.columns]]
        
        # Summary tables
        started_summary, completed_summary = create_summary_tables(_df, top_k_courses)
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Master Student Report
            master_report.to_excel(writer, sheet_name='Master Student Report', index=False)
            
            # Sheet 2: Course Started Summary
            started_summary.to_excel(writer, sheet_name='Course Started Summary', index=False)
            
            # Sheet 3: Course Completed Summary
            completed_summary.to_excel(writer, sheet_name='Course Completed Summary', index=False)
            
            # Individual course sheets with branch-wise completion breakdown
            for course_col in top_k_courses:
                # Create sheet name from course name (replace spaces with underscores, limit to 31 chars)
                sheet_name = course_col.replace(' ', '_')[:31]
                course_breakdown = create_course_breakdown(_df, course_col)
                course_breakdown.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return output.getvalue()
    
    def to_excel(dfs_dict):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df_sheet in dfs_dict.items():
                df_sheet.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        return output.getvalue()
    
    # User Input
    st.subheader("1. Select Top 'k' Courses")
    k = st.number_input("Select 'k':", min_value=1, max_value=50, value=5, step=1)
    top_k_courses = get_top_k_courses(df, course_columns, k)
    st.info(f"Top {k} Courses: **{', '.join(top_k_courses[:3])}**...")
    
    st.write("---")
    
    # Generate Reports
    st.subheader("2. Download Full Report")
    
    full_report = create_full_student_report(df, top_k_courses)
    
    st.download_button("📥 Download Full Report (.xlsx)", data=full_report,
                      file_name=f"Full_Student_Report_Top_{k}.xlsx",
                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                      use_container_width=True)
    
    st.write("---")
    
    # Interactive Tables
    st.subheader("3. Summary Tables")
    
    started_summary, completed_summary = create_summary_tables(df, top_k_courses)
    
    tab1, tab2 = st.tabs(["**Course Started**", "**Course Completed**"])
    
    with tab1:
        st.header("Course Started Status")
        
        # For chart, exclude Grand Total row
        chart_df = started_summary[started_summary['Branch Name'] != 'Grand Total'].copy()
        chart_cols = [c for c in chart_df.columns if c not in ['Branch Name', 'Grand Total']]
        chart_data = chart_df.melt(id_vars='Branch Name', value_vars=chart_cols, var_name='Status', value_name='Count')
        
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Branch Name', sort=None),
            y='Count',
            color='Status',
            tooltip=['Branch Name', 'Status', 'Count']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(started_summary, use_container_width=True)
    
    with tab2:
        st.header("Course Completed Status")
        
        # For chart, exclude Grand Total row
        chart_df = completed_summary[completed_summary['Branch Name'] != 'Grand Total'].copy()
        chart_cols = [c for c in chart_df.columns if c not in ['Branch Name', 'Grand Total']]
        chart_data = chart_df.melt(id_vars='Branch Name', value_vars=chart_cols, var_name='Status', value_name='Count')
        
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Branch Name', sort=None),
            y='Count',
            color='Status',
            tooltip=['Branch Name', 'Status', 'Count']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(completed_summary, use_container_width=True)
    
    st.write("---")
    
    st.subheader("4. Download Summary Tables Only")
    
    summary_sheets = {
        "Course Started Summary": started_summary,
        "Course Completed Summary": completed_summary
    }
    
    summary_excel = to_excel(summary_sheets)
    
    st.download_button("📥 Download Summary Tables (.xlsx)", data=summary_excel,
                      file_name=f"Summary_Report_Top_{k}.xlsx",
                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                      use_container_width=True)
