import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Branch Analytics",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Branch & Cohort Analytics")

@st.cache_data
def get_branch_year_stats(df):
    """Calculates average completion stats grouped by Branch and Year."""
    stats = df.groupby(['Branch Name', 'Year of Passing']).agg(
        Avg_Overall_Completion=('Overall Completion %', 'mean'),
        Avg_Courses_Started=('Courses Started', 'mean'),
        Avg_Courses_Completed=('Courses Completed', 'mean')
    ).reset_index()
    return stats

@st.cache_data
def get_top_courses_by_branch(df, course_columns):
    """Finds the top 10 most popular courses for each branch."""
    branches = df['Branch Name'].unique()
    all_top_courses = []
    
    for branch in branches:
        branch_df = df[df['Branch Name'] == branch]
        branch_enrollment = (branch_df[course_columns] > 0).sum().sort_values(ascending=False)
        
        top_10 = branch_enrollment.head(10).reset_index()
        top_10.columns = ['Course Name', 'Student Count']
        top_10['Branch Name'] = branch
        all_top_courses.append(top_10)
        
    return pd.concat(all_top_courses)


if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page to begin.")
else:
    df = st.session_state["df"]
    course_columns = st.session_state["course_columns"]

    tab1, tab2, tab3 = st.tabs([
        "**Branch Comparison**", 
        "**Top Courses by Branch**", 
        "**Progress Distribution**"
    ])

    with tab1:
        st.header("Branch Comparison Dashboard")
        
        st.subheader("Filters")
        
        all_branches = list(df['Branch Name'].dropna().unique())
        selected_branches = st.multiselect(
            "Select Branches to Compare (Default: All):",
            options=all_branches,
            default=all_branches
        )
        
        all_years = sorted(list(df['Year of Passing'].dropna().unique()))
        selected_years = st.multiselect(
            "Select Years to Compare (Default: All):",
            options=all_years,
            default=all_years
        )
        
        if not selected_branches or not selected_years:
            st.info("Please select at least one Branch and one Year to see results.")
        else:
            filtered_df = df[
                (df['Branch Name'].isin(selected_branches)) &
                (df['Year of Passing'].isin(selected_years))
            ]
            
            branch_year_stats = get_branch_year_stats(filtered_df)
            
            st.subheader("Average Overall Completion %")
            
            chart = alt.Chart(branch_year_stats).mark_bar().encode(
                x=alt.X('Branch Name', sort=None),
                y=alt.Y('Avg_Overall_Completion', title='Avg. Overall Completion %'),
                color='Year of Passing:N',  
                column=alt.Column('Year of Passing:N', header=alt.Header(titleOrient="bottom", labelOrient="bottom")), # Separate charts by year
                tooltip=['Branch Name', 'Year of Passing', 'Avg_Overall_Completion']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

    with tab2:
        st.header("Top 10 Popular Courses by Branch")
        
        top_courses_df = get_top_courses_by_branch(df, course_columns)
        
     
        top_courses_filtered = top_courses_df[top_courses_df['Branch Name'].isin(selected_branches)]

       
        chart = alt.Chart(top_courses_filtered).mark_bar().encode(
            x=alt.X('Course Name', sort='-y'),
            y=alt.Y('Student Count'),
            color='Branch Name',
            column=alt.Column('Branch Name', header=alt.Header(titleOrient="bottom", labelOrient="bottom")),
            tooltip=['Branch Name', 'Course Name', 'Student Count']
        ).interactive().resolve_scale(
            x='independent'  
        )
        
        st.altair_chart(chart)

    with tab3:
        st.header("Student Progress Distribution")
        
        if not selected_branches or not selected_years:
            st.info("Please select filters on the 'Branch Comparison' tab to see results.")
        else:
            filtered_df = df[
                (df['Branch Name'].isin(selected_branches)) &
                (df['Year of Passing'].isin(selected_years))
            ]
            
            st.write(f"Showing distribution for {len(filtered_df)} selected students.")
            
            histogram = alt.Chart(filtered_df).mark_bar().encode(
                alt.X("Overall Completion %", bin=alt.Bin(maxbins=20), title="Overall Completion %"),
                alt.Y('count()', title="Number of Students"),
                tooltip=[alt.X("Overall Completion %", bin=alt.Bin(maxbins=20)), 'count()']
            ).properties(
                title="Distribution of Student Overall Completion"
            ).interactive()
            
            st.altair_chart(histogram, use_container_width=True)