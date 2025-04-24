import streamlit as st
import pandas as pd

def setup_css():
    """Apply custom CSS styling to the application."""
    st.markdown("""
    <style>
        .policy-status-active {
            background-color: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .policy-status-inactive {
            background-color: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .info-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            height: 100%;
            overflow: auto; /* Added for better handling of long content */
        }
        .date-card {
            background-color: #e0f7fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .benefits-card {
            background-color: #fff8e1;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .warning-text {
            color: #ff6d00;
            font-weight: bold;
        }
        .header-style {
            font-size: 20px;
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 15px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 8px;
        }
        .subheader-style {
            font-size: 16px;
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 10px;
        }
        .policy-detail {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #f0f0f0;
            padding: 10px 0;
        }
        .policy-detail-label {
            font-weight: bold;
            color: #455a64;
            width: 45%;
        }
        .policy-detail-value {
            color: #37474f;
            width: 55%;
            text-align: right;
            word-break: break-word; /* Added to handle long values */
        }
        .highlight-box {
            background-color: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #2196f3;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        .timeline-item {
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }
        .timeline-marker {
            min-width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #2196f3;
            margin-right: 15px;
            margin-top: 3px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .timeline-content {
            flex-grow: 1;
        }
        .timeline-date {
            font-weight: bold;
            color: #0d47a1;
            margin-bottom: 3px;
        }
        .timeline-description {
            color: #455a64;
        }
        .nominee-card {
            background-color: #f3e5f5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .extraction-stats {
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            background-color: #1976d2;
            color: white;
            font-weight: bold;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .user-message {
            background-color: #e1f5fe;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: right;
            margin-left: 20%;
        }
        .ai-message {
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            margin-right: 20%;
        }
        .small-font {
            font-size: 14px;
        }
        .equal-height {
            display: flex;
            flex-direction: column;
        }
        .equal-height > div {
            flex: 1;
        }
        section[data-testid="stSidebar"] {
            background-color: #f5f5f5;
            border-right: 1px solid #e0e0e0;
        }
        .sidebar-nav {
            margin-bottom: 30px;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #1565c0;
            padding-bottom: 5px;
            border-bottom: 1px solid #e0e0e0;
        }
        .icon-text {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .icon {
            margin-right: 10px;
            color: #1976d2;
        }
        .exclusion-item {
            background-color: #fff3e0;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 3px solid #ff9800;
        }
        .exclusion-title {
            font-weight: bold;
            color: #e65100;
            margin-bottom: 5px;
        }
        .exclusion-description {
            color: #424242;
        }
        /* Added to ensure tables display properly */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
        /* Ensure full content is displayed in all text areas */
        .full-content {
            white-space: pre-wrap;
            word-break: break-word;
            overflow-wrap: break-word;
            max-width: 100%;
        }
        /* Improvements for GSV factors table */
        .gsv-table-container {
            max-height: 400px;
            overflow-y: auto;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        /* For missing information display */
        .missing-info {
            color: #9e9e9e;
            font-style: italic;
            margin: 5px 0;
        }
        /* RAG chat styling */
        .citation {
            background-color: #f0f7ff;
            border-left: 3px solid #2196f3;
            padding: 8px 12px;
            margin: 10px 0;
            font-size: 0.9em;
            border-radius: 4px;
        }
        .chat-query-info {
            font-size: 0.85em;
            color: #757575;
            margin-bottom: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

def display_missing_info_message(field_name="This information"):
    """Display a standardized message for missing information."""
    st.markdown(f'<div class="missing-info">{field_name} could not be extracted from the document.</div>', 
               unsafe_allow_html=True)

def safe_display(value, field_name=None, formatter=None, default_message=None):
    """Safely display a value with proper handling of missing information."""
    if value is None or value == "" or value == "Not Available":
        if default_message:
            display_missing_info_message(default_message)
        else:
            display_missing_info_message(field_name)
        return False
    
    # Format value if a formatter function is provided
    if formatter:
        formatted_value = formatter(value)
        st.markdown(formatted_value, unsafe_allow_html=True)
    else:
        st.markdown(f"{value}", unsafe_allow_html=True)
    
    return True

def format_gsv_factors_table(gsv_factors):
    """Format GSV factors as a properly sized and scrollable table."""
    if not gsv_factors or not isinstance(gsv_factors, dict) or len(gsv_factors) == 0:
        return None
    
    # Check if the GSV factors are in array format
    array_format = False
    for year, factor in gsv_factors.items():
        if isinstance(factor, list) or (isinstance(factor, str) and ('[' in factor and ']' in factor)):
            array_format = True
            break
    
    try:
        if array_format:
            # Handle array format
            df_rows = []
            
            for year, factors in gsv_factors.items():
                # Convert string representation of arrays to actual lists if needed
                if isinstance(factors, str) and '[' in factors:
                    try:
                        factors = factors.replace("'", "").replace("[", "").replace("]", "").split(', ')
                    except:
                        factors = [factors]
                
                # If it's already a list, use it directly
                if isinstance(factors, list):
                    row = {"Policy Year": year}
                    
                    # Add each factor as a separate column
                    for i, factor in enumerate(factors):
                        row[f"Factor {i+1}"] = factor
                    
                    df_rows.append(row)
                else:
                    # Handle simple value case
                    df_rows.append({"Policy Year": year, "GSV Factor": factors})
            
            # Convert to DataFrame
            if df_rows:
                df = pd.DataFrame(df_rows)
                
                # Sort by policy year if possible
                try:
                    df["Policy Year"] = df["Policy Year"].astype(int)
                    df = df.sort_values("Policy Year")
                except:
                    pass  # If conversion fails, keep original order
                
                # Return the HTML with container div for scrolling
                html_table = df.to_html(index=False, classes="table table-striped table-bordered")
                return f'<div class="gsv-table-container">{html_table}</div>'
        else:
            # Handle standard key-value format
            years = []
            factors = []
            
            # Sort the factors by policy year
            for year in sorted(gsv_factors.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                factor = gsv_factors[year]
                years.append(year)
                
                # Format the factor as percentage if it's a number
                if isinstance(factor, (int, float)):
                    if factor <= 1:
                        factors.append(f"{factor:.2%}")
                    else:
                        factors.append(f"{factor}%")
                else:
                    factors.append(str(factor))
            
            # Create a DataFrame
            df = pd.DataFrame({
                "Policy Year": years,
                "GSV Factor": factors
            })
            
            # Return the HTML table with container div for scrolling
            html_table = df.to_html(index=False, classes="table table-striped table-bordered")
            return f'<div class="gsv-table-container">{html_table}</div>'
    
    except Exception as e:
        st.warning(f"Could not format GSV factors table: {str(e)}")
        return None