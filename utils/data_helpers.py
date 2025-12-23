"""
Shared data helper functions for the Student Analytics Dashboard.
"""
import pandas as pd
import numpy as np
import re
import streamlit as st


def detect_score_columns(df):
    """
    Auto-detect score columns and their max values from the dataframe.
    Returns dict: {column_name: max_score}
    """
    score_columns = {}
    
    for col in df.columns:
        col_lower = col.lower()
        # Look for patterns like "Quants (160)" or score-related columns
        if any(keyword in col_lower for keyword in ['quants', 'logical', 'verbal', 'english', 'technical', 'coding', 'mcq']):
            # Try to extract max score from column name (e.g., "Quants (160)")
            match = re.search(r'\((\d+)\)', col)
            if match:
                max_score = int(match.group(1))
            else:
                # Estimate from data
                max_val = df[col].max()
                if max_val <= 100:
                    max_score = 100
                elif max_val <= 160:
                    max_score = 160
                else:
                    max_score = int(np.ceil(max_val / 10) * 10)
            score_columns[col] = max_score
    
    return score_columns


def get_score_column_info(df):
    """
    Get score columns with their display names and max values.
    Returns list of dicts with 'column', 'display_name', 'max_score'
    """
    score_cols = detect_score_columns(df)
    result = []
    
    for col, max_val in score_cols.items():
        display_name = col.split('(')[0].strip()
        result.append({
            'column': col,
            'display_name': display_name,
            'max_score': max_val
        })
    
    return result


def calculate_percentages(df, score_columns):
    """
    Calculate percentage columns for each score column.
    """
    for col, max_val in score_columns.items():
        pct_col = col.split('(')[0].strip().replace(' ', '_') + '_Percentage'
        df[pct_col] = (df[col] / max_val * 100).round(2)
    
    return df


def get_percentage_column(col_name):
    """Get the percentage column name for a score column."""
    return col_name.split('(')[0].strip().replace(' ', '_') + '_Percentage'


def categorize_performance(percentage):
    """Categorize performance based on percentage."""
    if percentage >= 80:
        return "Excellent (≥80%)"
    elif percentage >= 65:
        return "Good (65-79%)"
    elif percentage >= 50:
        return "Average (50-64%)"
    else:
        return "Below Average (<50%)"


def get_performance_color(percentage):
    """Get color for performance level."""
    if percentage >= 80:
        return "green"
    elif percentage >= 65:
        return "blue"
    elif percentage >= 50:
        return "orange"
    else:
        return "red"


def safe_get_column(df, possible_names, default=None):
    """
    Safely get a column from dataframe trying multiple possible names.
    """
    for name in possible_names:
        if name in df.columns:
            return name
    return default


def format_score(score, max_score):
    """Format score display."""
    return f"{int(score)}/{max_score}"


def format_percentage(value):
    """Format percentage display."""
    return f"{value:.1f}%"
