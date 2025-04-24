import re
from datetime import datetime, timedelta
import streamlit as st

def format_date(date_str):
    """Format date strings for consistent display."""
    if date_str is None or date_str == "" or date_str == "Not Available":
        return None
    
    try:
        # Try to standardize date format if it's a valid date
        date_patterns = [
            # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
            # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})',
            # Month name formats
            r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',
            r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                if pattern == date_patterns[0]:  # DD/MM/YYYY
                    day, month, year = match.groups()
                    parsed_date = datetime(int(year), int(month), int(day))
                elif pattern == date_patterns[1]:  # YYYY/MM/DD
                    year, month, day = match.groups()
                    parsed_date = datetime(int(year), int(month), int(day))
                elif pattern == date_patterns[2]:  # DD Month YYYY
                    day, month_name, year = match.groups()
                    month = datetime.strptime(month_name[:3], '%b').month
                    parsed_date = datetime(int(year), month, int(day))
                elif pattern == date_patterns[3]:  # Month DD, YYYY
                    month_name, day, year = match.groups()
                    month = datetime.strptime(month_name[:3], '%b').month
                    parsed_date = datetime(int(year), month, int(day))
                
                # Return formatted date
                return parsed_date.strftime("%d %b %Y")
        
        # If no pattern matched but the string is not empty, return it as is
        return date_str
    
    except Exception:
        # If parsing fails, return the original string
        return date_str

def create_timeline(dates_dict):
    """Create HTML for a visual timeline of key policy dates."""
    # Filter out None values and empty strings
    valid_dates = {k: v for k, v in dates_dict.items() if v}
    
    if not valid_dates:
        return "<p>No timeline data available</p>"
    
    # Convert dates to datetime objects for sorting if possible
    try:
        date_objects = {}
        for label, date_str in valid_dates.items():
            try:
                # Try to parse the date using the formatter
                formatted_date = format_date(date_str)
                if formatted_date:
                    date_obj = datetime.strptime(formatted_date, "%d %b %Y")
                    date_objects[label] = (date_obj, formatted_date)
            except:
                # If parsing fails, keep the original string
                date_objects[label] = (None, date_str)
        
        # Sort by date if possible, keeping labels with unparseable dates at the end
        sorted_dates = sorted(
            date_objects.items(), 
            key=lambda x: (x[1][0] is None, x[1][0] or datetime.max)
        )
        
        # Create the timeline HTML
        timeline_html = ""
        for label, (_, display_date) in sorted_dates:
            timeline_html += f"""
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <div class="timeline-date">{display_date}</div>
                    <div class="timeline-description">{label}</div>
                </div>
            </div>
            """
        
        return timeline_html
    
    except Exception as e:
        st.warning(f"Error creating timeline: {str(e)}")
        # Fallback to simple format
        timeline_html = ""
        for label, date in valid_dates.items():
            timeline_html += f"""
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <div class="timeline-date">{date}</div>
                    <div class="timeline-description">{label}</div>
                </div>
            </div>
            """
        
        return timeline_html

def calculate_policy_duration(start_date, end_date=None):
    """Calculate the duration of a policy in years and months."""
    if not start_date:
        return None
    
    try:
        # Parse start date
        if isinstance(start_date, str):
            start_date = format_date(start_date)
            if not start_date:
                return None
            start_date = datetime.strptime(start_date, "%d %b %Y")
        
        # Use current date if end_date not provided
        if not end_date:
            end_date = datetime.now()
        else:
            # Parse end date if it's a string
            if isinstance(end_date, str):
                end_date = format_date(end_date)
                if not end_date:
                    return None
                end_date = datetime.strptime(end_date, "%d %b %Y")
                # Calculate the difference
        delta = end_date - start_date
        
        # Convert to years and months
        years = delta.days // 365
        months = (delta.days % 365) // 30
        
        if years > 0 and months > 0:
            return f"{years} years, {months} months"
        elif years > 0:
            return f"{years} years"
        elif months > 0:
            return f"{months} months"
        else:
            return f"{delta.days} days"
            
    except Exception:
        return None

def create_policy_timeline_chart(policy_type, policy_identification):
    """Create a mermaid chart for the policy timeline."""
    
    # Extract key dates for the timeline
    start_date = policy_identification.get('date_of_commencement', 'Policy Start')
    maturity_date = policy_identification.get('maturity_date', 'Maturity Date')
    policy_term = policy_identification.get('policy_term', '')
    premium_term = policy_identification.get('premium_payment_term', '')
    
    # Format the term for display
    term_text = f"({policy_term})" if policy_term else ""
    premium_text = f"({premium_term})" if premium_term else ""
    
    if "Annuity" in policy_type or "Pension" in policy_type:
        # For annuity policies
        vesting_date = policy_identification.get('date_of_vesting', 'Vesting Date')
        chart = """
        ```mermaid
        flowchart LR
            A["{start_date}\\nPolicy Start"] --> |Deferment Period| B["{vesting_date}\\nVesting Date"]
            B --> |Annuity Payments Begin| C["Regular Annuity\\nPayments"]
            style A fill:#bbdefb,stroke:#1976d2
            style B fill:#c8e6c9,stroke:#388e3c
            style C fill:#fff9c4,stroke:#fbc02d
        ```
        """.replace("{start_date}", start_date).replace("{vesting_date}", vesting_date)
    else:
        # For regular insurance policies
        chart = """
        ```mermaid
        flowchart LR
            A["{start_date}\\nPolicy Start"] --> |Premium Payment Term {premium_text}| B["Premium\\nPayment Ends"]
            B --> |Remaining Policy Term| C["{maturity_date}\\nMaturity Date"]
            style A fill:#bbdefb,stroke:#1976d2
            style B fill:#c8e6c9,stroke:#388e3c
            style C fill:#fff9c4,stroke:#fbc02d
        ```
        """.replace("{start_date}", start_date).replace("{maturity_date}", maturity_date).replace("{premium_text}", premium_text)
    
    return chart