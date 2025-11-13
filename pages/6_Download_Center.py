import streamlit as st
import pandas as pd
import altair as alt
import io
import os


# ------------------------------------------------------------
# Optimized, Fast, Warning-Free Altair → PNG Exporter
# ------------------------------------------------------------
def save_chart_to_png(chart):
    """
    Save Altair chart as PNG using vl-convert (correct functions for your version).
    """
    import json
    from vl_convert import vegalite_to_png

    try:
        spec = json.loads(chart.to_json())

        # Convert Vega-Lite spec to PNG bytes
        png_bytes = vegalite_to_png(spec)

        return png_bytes

    except Exception as e:
        st.error(f"PNG export failed: {e}")
        return None


# ------------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------------
st.set_page_config(
    page_title="Download Center",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Download Center & Reports")

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

@st.cache_data
def get_top_k_courses(_df, course_columns, k):
    """Finds the top k most enrolled courses."""
    enrollment_counts = (_df[course_columns] > 0).sum()
    top_k_courses = enrollment_counts.nlargest(k).index.tolist()
    return top_k_courses

@st.cache_data
def create_master_report(_df, top_k_courses):
    """Creates the 'Master Student Report' DataFrame."""
    df_report = _df.copy()

    df_report['First Name'] = df_report['First Name'].fillna('')
    df_report['Last Name'] = df_report['Last Name'].fillna('')

    df_report['Full Name'] = df_report['First Name'] + ' ' + df_report['Last Name']
    df_report['S No.'] = range(1, len(df_report) + 1)

    base_columns = [
        'S No.', 'Full Name', 'Email', 'Branch Name', 'Registration Number',
        'Courses Started', 'Courses Completed'
    ]

    valid_top_k = [col for col in top_k_courses if col in df_report.columns]
    final_columns = base_columns + valid_top_k

    df_report = df_report[final_columns]
    return df_report

@st.cache_data
def create_summary_tables(_df, top_k_courses):
    """
    Creates the three summary tables.
    """

    df_summary = _df.copy()

    # --- Table 1: Course Started Summary ---
    df_summary['Started Status'] = df_summary['Courses Started'].apply(
        lambda x: 'Course Started' if x > 0 else 'Course Not Started'
    )
    all_started_categories = ['Course Not Started', 'Course Started']
    df_summary['Started Status'] = pd.Categorical(
        df_summary['Started Status'], categories=all_started_categories
    )

    started_summary = pd.pivot_table(
        df_summary, index='Branch Name', columns='Started Status',
        aggfunc='size', fill_value=0, dropna=False
    )
    started_summary['Grand Total'] = started_summary.sum(axis=1)
    started_summary.loc['Grand Total'] = started_summary.sum(axis=0)
    started_summary = started_summary.reindex(columns=all_started_categories + ['Grand Total'])

    # --- Table 2: Course Completed Summary ---
    df_summary['Completed Status'] = df_summary['Overall Completion %'].apply(
        lambda x: 'Course Completed' if x == 100 else 'Course Not Completed'
    )
    all_completed_categories = ['Course Completed', 'Course Not Completed']
    df_summary['Completed Status'] = pd.Categorical(
        df_summary['Completed Status'], categories=all_completed_categories
    )

    completed_summary = pd.pivot_table(
        df_summary, index='Branch Name', columns='Completed Status',
        aggfunc='size', fill_value=0, dropna=False
    )
    completed_summary['Grand Total'] = completed_summary.sum(axis=1)
    completed_summary.loc['Grand Total'] = completed_summary.sum(axis=0)
    completed_summary = completed_summary.reindex(columns=all_completed_categories + ['Grand Total'])

    # --- Table 3: Top K Courses Breakdown ---
    def categorize_course_buckets(val):
        val = pd.to_numeric(val, errors='coerce')
        if val == 100:
            return 'Completed'
        elif 80 <= val < 100:
            return '80% Completed'
        elif 70 <= val < 80:
            return '70% Completed'
        elif 60 <= val < 70:
            return '60% Completed'
        elif 30 <= val < 60:
            return '30% Completed'
        elif 20 <= val < 30:
            return '20% Completed'
        elif 0 < val < 20:
            return '10% Completed'
        elif val == 0:
            return 'Not Started'
        return 'Not Started'

    all_buckets = [
        'Not Started', '10% Completed', '20% Completed', '30% Completed',
        '60% Completed', '70% Completed', '80% Completed', 'Completed'
    ]

    top_k_tables = {}

    for course in top_k_courses:
        status_col_name = f"{course}_Status"
        df_summary[status_col_name] = df_summary[course].apply(categorize_course_buckets)
        df_summary[status_col_name] = pd.Categorical(
            df_summary[status_col_name], categories=all_buckets
        )

        table = pd.pivot_table(
            df_summary,
            index='Branch Name',
            columns=status_col_name,
            aggfunc='size',
            fill_value=0,
            dropna=False
        )

        cols_to_keep = []
        for col in all_buckets:
            if col in table.columns and table[col].sum() > 0:
                cols_to_keep.append(col)

        final_table = table[cols_to_keep].copy()

        final_table['Grand Total'] = final_table.sum(axis=1)
        final_table.loc['Grand Total'] = final_table.sum(axis=0)

        top_k_tables[course] = final_table

    return started_summary, completed_summary, top_k_tables

# ------------------------------------------------------------
# Excel Writer
# ------------------------------------------------------------
def to_excel(dfs_dict):
    """Writes multiple DataFrames to an Excel file in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)
    return output.getvalue()

# ------------------------------------------------------------
# Main Streamlit App Logic
# ------------------------------------------------------------
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page (using the sidebar) to begin.")
else:
    df = st.session_state["df"]
    course_columns = st.session_state["course_columns"]

    # --- 1. User Input: Select 'k' ---
    st.subheader("1. Select Top 'k' Courses")
    k = st.number_input("Select 'k' to define the top courses for your reports:", min_value=1, max_value=50, value=5, step=1)
    top_k_courses = get_top_k_courses(df, course_columns, k)
    st.info(f"The Top {k} Courses are: **{', '.join(top_k_courses)}**")
    st.write("---")

    # --- 2. Master Student Report ---
    st.subheader("2. Master Student Report")
    master_report_df = create_master_report(df, top_k_courses)
    st.dataframe(master_report_df.head())
    excel_master_report = to_excel({"Master Report": master_report_df})

    st.download_button(
        label="📥 Download Master Student Report (.xlsx)",
        data=excel_master_report,
        file_name=f"Master_Student_Report_Top_{k}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.write("---")

    # --- 3. Summary Reports & Graphs ---
    st.subheader("3. Summary Reports & Graphs")
    started_summary, completed_summary, top_k_tables = create_summary_tables(df, top_k_courses)

    tab1, tab2, tab3 = st.tabs(["**Course Started**", "**Course Completed**", f"**Top {k} Courses Breakdown**"])

    # ---------------------------------------------
    # TAB 1 — COURSE STARTED SUMMARY
    # ---------------------------------------------
    with tab1:
        st.header("Course Started Status")
        started_graph_df = started_summary.drop('Grand Total', axis=0).drop('Grand Total', axis=1)

        chart_data_started = started_graph_df.reset_index().melt(
            'Branch Name', var_name='Started Status', value_name='Student Count'
        )

        chart_started = alt.Chart(chart_data_started).mark_bar().encode(
            x=alt.X('Branch Name', sort=None),
            y='Student Count',
            color='Started Status',
            tooltip=['Branch Name', 'Started Status', 'Student Count']
        ).interactive()

        st.altair_chart(chart_started, use_container_width=True)

        png_data = save_chart_to_png(chart_started)
        if png_data:
            st.download_button(
                label="Download Chart as PNG",
                data=png_data,
                file_name="course_started_summary.png",
                mime="image/png"
            )

        st.write("#### Data Table:")
        st.dataframe(started_summary)

    # ---------------------------------------------
    # TAB 2 — COURSE COMPLETED SUMMARY
    # ---------------------------------------------
    with tab2:
        st.header("Overall Course Completed Status")
        completed_graph_df = completed_summary.drop('Grand Total', axis=0).drop('Grand Total', axis=1)

        chart_data_completed = completed_graph_df.reset_index().melt(
            'Branch Name', var_name='Completed Status', value_name='Student Count'
        )

        chart_completed = alt.Chart(chart_data_completed).mark_bar().encode(
            x=alt.X('Branch Name', sort=None),
            y='Student Count',
            color='Completed Status',
            tooltip=['Branch Name', 'Completed Status', 'Student Count']
        ).interactive()

        st.altair_chart(chart_completed, use_container_width=True)

        png_data = save_chart_to_png(chart_completed)
        if png_data:
            st.download_button(
                label="Download Chart as PNG",
                data=png_data,
                file_name="course_completed_summary.png",
                mime="image/png"
            )

        st.write("#### Data Table:")
        st.dataframe(completed_summary)

    # ---------------------------------------------
    # TAB 3 — TOP K COURSE BREAKDOWN
    # ---------------------------------------------
    with tab3:
        st.header(f"Top {k} Courses Breakdown")

        selected_course = st.selectbox("Select a course to view its breakdown:", options=top_k_courses)

        if selected_course:
            course_table = top_k_tables[selected_course]

            course_graph_df = course_table.drop('Grand Total', axis=0).drop('Grand Total', axis=1)
            chart_data = course_graph_df.reset_index().melt(
                'Branch Name', var_name='Status', value_name='Student Count'
            )

            chart_top_k = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Branch Name', sort=None),
                y='Student Count',
                color='Status',
                tooltip=['Branch Name', 'Status', 'Student Count']
            ).interactive()

            st.altair_chart(chart_top_k, use_container_width=True)

            png_data = save_chart_to_png(chart_top_k)
            if png_data:
                st.download_button(
                    label=f"Download '{selected_course}' Chart as PNG",
                    data=png_data,
                    file_name=f"top_k_{selected_course.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"png_{selected_course}"
                )

            st.write(f"#### Data Table: {selected_course}")
            st.dataframe(course_table)

    # ---------------------------------------------
    # DOWNLOAD ALL SUMMARY TABLES
    # ---------------------------------------------
    excel_sheets = {
        "Course Started Summary": started_summary,
        "Course Completed Summary": completed_summary
    }

    for course_name, table in top_k_tables.items():
        sheet_name = course_name.replace(' ', '_')[:31]
        excel_sheets[sheet_name] = table

    excel_summary_report = to_excel(excel_sheets)

    st.download_button(
        label="📥 Download All Summary Tables (.xlsx)",
        data=excel_summary_report,
        file_name=f"Summary_Report_Top_{k}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="summary_excel_download"
    )