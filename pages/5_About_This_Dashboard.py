import streamlit as st

st.set_page_config(
    page_title="About This Dashboard",
    page_icon="❓",
    layout="wide"
)

st.title("❓ About This Dashboard")
st.write("This page documents all features and the logic behind them.")

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("Please upload a CSV file on the 'Home' page (using the sidebar) to see the features.")
else:
    st.info("Here is a breakdown of each page and its features.")

    st.subheader("🧑‍🎓 Student Analytics")
    with st.expander("**Student Portfolio**"):
        st.markdown("""
        * **Feature:** A search box to find any student by their 'Registration Number'.
        * **Logic:** It displays their academic details, overall progress metrics, and a table of all courses they have started (value > 0).
        """)
    with st.expander("**Recommended Courses (in Portfolio)**"):
        st.markdown("""
        * **Feature:** A list of courses suggested for the selected student.
        * **Logic:**
        1.  Finds the student's branch (e.g., "B.Tech CSE").
        2.  Finds the Top 10 most popular (highest enrollment) courses for that *entire* branch.
        3.  Compares the "Top 10" list to the student's "already started" list.
        4.  Recommends courses that are in the Top 10 but not yet started by the student.
        """)
    with st.expander("**Top Performers Leaderboard**"):
        st.markdown("""
        * **Feature:** A filterable table of the top 'N' students.
        * **Logic:**
        1.  Filters all students by the selected 'Branch Name' and 'Year of Passing' (or 'All').
        2.  Sorts the filtered list by 'Overall Completion %' from highest to lowest.
        3.  Displays the top 'N' students from this list.
        """)

    st.subheader("📊 Course Analytics")
    with st.expander("**⭐ Top Enrolled Courses**"):
        st.markdown("""
        * **Feature:** A bar chart and table of the most popular courses.
        * **Logic:** Counts the number of students who have a completion value **> 0** for each course and shows the top 'N'.
        """)
    with st.expander("**Course Deep Dive**"):
        st.markdown("""
        * **Feature:** A detailed look at a single course selected from a dropdown.
        * **Logic:** For the selected course, it calculates:
            * **Total Enrollment:** `Count of students > 0%`
            * **Completion Rate:** `(Count of students == 100%) / (Count of students > 0%)`
            * **Avg. Completion (of enrolled):** The mean percentage of all students `> 0%`
            * **Enrollment by Branch:** A bar chart showing how many enrolled students come from each branch.
        """)
    with st.expander("**Course Performance**"):
        st.markdown("""
        * **Feature:** Two tables showing the best and worst performing courses.
        * **Logic:** It uses the same **"Completion Rate"** logic from the Deep Dive.
            * Uses a slider to filter out courses with low enrollment (e.g., fewer than 10 students).
            * **Top 5:** Sorts the filtered courses by Completion Rate (highest to lowest).
            * **Bottom 5:** Sorts the filtered courses by Completion Rate (lowest to highest).
        """)
    with st.expander("**Course Co-Enrollment**"):
        st.markdown("""
        * **Feature:** A heatmap showing which courses are frequently taken together.
        * **Logic:**
        1.  Filters for popular courses (e.g., > 10 students).
        2.  Counts how many students are enrolled in every possible *pair* of courses (e.g., 50 students took *both* 'Python' and 'SQL').
        3.  Displays these counts in a heatmap, where darker squares mean a stronger connection.
        """)

    st.subheader("🏛️ Branch & Cohort Analytics")
    with st.expander("**Branch Comparison**"):
        st.markdown("""
        * **Feature:** A bar chart comparing average performance across branches and years.
        * **Logic:** Calculates the `Average Overall Completion %` for all students, grouped by 'Branch Name' and 'Year of Passing'.
        """)
    with st.expander("**Top Courses by Branch**"):
        st.markdown("""
        * **Feature:** A set of bar charts showing the Top 10 most popular courses for each branch, side-by-side.
        * **Logic:**
        1.  Groups all students by their 'Branch Name'.
        2.  For each branch, it counts enrollment for all courses and finds its unique Top 10 list.
        3.  Displays each branch's Top 10 list on its own independent chart, sorted from highest to lowest.
        """)
    with st.expander("**Student Progress Distribution**"):
        st.markdown("""
        * **Feature:** A histogram showing the "shape" of student performance.
        * **Logic:**
        1.  Takes the filtered list of students (from the first tab).
        2.  Looks at their 'Overall Completion %'.
        3.  Groups them into "bins" (e.g., 0-10%, 10-20%, etc.).
        4.  Plots how many students fall into each bin.
        """)

    st.subheader("🔮 Predictive Features")
    with st.expander("**At-Risk Student Identifier**"):
        st.markdown("""
        * **Feature:** A filterable report to find students who need help.
        * **Logic:** You use sliders to define "at-risk". The app finds all students who match both conditions:
        ```python
        (Courses Started >= N) AND (Overall Completion % <= Y)
        ```
        """)
    with st.expander("**Course Recommendation Engine**"):
        st.markdown("""
        * **Feature:** A tool to find "next steps" for a specific student.
        * **Logic:** This uses the *exact same logic* as the "Recommended Courses" feature in the Student Portfolio tab.
        """)