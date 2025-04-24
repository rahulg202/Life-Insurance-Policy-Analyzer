import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def format_currency(value):
    """Format currency values with error handling."""
    if value is None or value == "":
        return None
    
    try:
        # If it's already a number, format it
        if isinstance(value, (int, float)):
            return f"₹{value:,.2f}"
        
        # If it's a string, try to convert to float
        if isinstance(value, str):
            # Remove any non-numeric characters except for decimal point
            cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
            if cleaned:
                return f"₹{float(cleaned):,.2f}"
            else:
                return value
        
        # For other types, return as is
        return value
    except Exception:
        # If any error occurs, return the original value
        return str(value)

def extract_numeric_value(value_str):
    """Extract numeric value from a string that might contain currency symbols, etc."""
    if value_str is None:
        return 0
        
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    if isinstance(value_str, str):
        # Remove currency symbols, commas, etc. and keep only digits and decimal points
        cleaned = ''.join(c for c in value_str if c.isdigit() or c == '.')
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return 0
    
    return 0

def calculate_loan_details(doc_info, max_loan_amount, loan_amount, interest_rate_val):
    """Calculate loan details with proper error handling."""
    results = {}
    
    try:
        # Calculate annual interest with safe type conversion
        annual_interest = float(loan_amount) * (float(interest_rate_val) / 100)
        
        results["loan_amount"] = format_currency(loan_amount)
        results["interest_rate"] = f"{interest_rate_val:.2f}%"
        results["annual_interest"] = format_currency(annual_interest)
        results["monthly_interest"] = format_currency(annual_interest/12)
        
        # Check if loan interest is high compared to annuity or premium
        policy_type = detect_policy_type(doc_info)
        warning_message = None
        
        if "Annuity" in policy_type or "Pension" in policy_type:
            # Compare with annuity
            financial_details = doc_info.get("financial_details", {})
            annuity_amount_value = extract_numeric_value(financial_details.get("annuity_amount"))
            
            if annuity_amount_value > 0:
                # Annualized annuity amount
                payment_mode = financial_details.get("annuity_payment_mode", "").lower()
                annual_payment = annuity_amount_value
                
                if "month" in str(payment_mode).lower():
                    annual_payment = annuity_amount_value * 12
                elif "quart" in str(payment_mode).lower():
                    annual_payment = annuity_amount_value * 4
                elif "half" in str(payment_mode).lower() or "semi" in str(payment_mode).lower():
                    annual_payment = annuity_amount_value * 2
                
                # Warning if interest exceeds 50% of annuity
                if annual_interest > (annual_payment * 0.5) and annual_payment > 0:
                    warning_message = "⚠️ The annual interest payment exceeds 50% of your annual annuity amount. This may affect your future income."
        else:
            # Compare with premium
            premium_amount_value = extract_numeric_value(doc_info.get("financial_details", {}).get("premium_amount"))
            
            if premium_amount_value > 0:
                # Warning if interest exceeds premium
                if annual_interest > premium_amount_value:
                    warning_message = "⚠️ The annual interest payment exceeds your premium amount. Consider the financial implications carefully."
        
        results["warning"] = warning_message
        
    except Exception as e:
        results["error"] = f"Unable to calculate loan details: {str(e)}"
    
    return results

def calculate_surrender_value(doc_info, policy_year):
    """Calculate approximate surrender value based on policy information."""
    financial_details = doc_info.get("financial_details", {})
    surrender_loan_details = doc_info.get("surrender_loan_details", {})
    
    # Determine base value (purchase price or premium sum)
    policy_type = detect_policy_type(doc_info)
    
    # Extract GSV factor
    gsv_factor = 0.0
    gsv_factors = surrender_loan_details.get("gsv_factors", {})
    
    # Check if GSV factors are available in document
    if gsv_factors and isinstance(gsv_factors, dict) and str(policy_year) in gsv_factors:
        factor_str = gsv_factors[str(policy_year)]
        if isinstance(factor_str, str) and "%" in factor_str:
            gsv_factor = float(factor_str.replace("%", "")) / 100
        else:
            try:
                gsv_factor = float(factor_str)
                if gsv_factor > 1:  # If factor is given as percentage (e.g., 75 instead of 0.75)
                    gsv_factor = gsv_factor / 100
            except (ValueError, TypeError):
                # Use default values if conversion fails
                gsv_factor = default_gsv_factor(policy_year)
    else:
        # Default GSV factor if not specified
        gsv_factor = default_gsv_factor(policy_year)
    
    # Get base value
    if "Annuity" in policy_type or "Pension" in policy_type:
        base_value = extract_numeric_value(financial_details.get("purchase_price"))
    else:
        # For regular policies, use premium × years (simplified)
        premium = extract_numeric_value(financial_details.get("premium_amount"))
        # Approximate paid premiums based on policy year
        payment_frequency = doc_info.get("policy_identification", {}).get("premium_payment_frequency", "").lower()
        
        payments_per_year = 1  # Default annual
        if "month" in payment_frequency:
            payments_per_year = 12
        elif "quart" in payment_frequency:
            payments_per_year = 4
        elif "half" in payment_frequency or "semi" in payment_frequency:
            payments_per_year = 2
            
        # Estimate total premiums paid
        # Cap policy_year to premium payment term if available
        ppt_str = doc_info.get("policy_identification", {}).get("premium_payment_term", "")
        premium_payment_term = 0
        if ppt_str:
            # Extract numeric value from PPT (e.g., "10 years" -> 10)
            ppt_digits = ''.join(filter(str.isdigit, str(ppt_str)))
            if ppt_digits:
                premium_payment_term = int(ppt_digits)
        
        years_paid = min(policy_year, premium_payment_term) if premium_payment_term > 0 else policy_year
        base_value = premium * payments_per_year * years_paid
    
    # Calculate surrender value
    surrender_value = base_value * gsv_factor
    
    return {
        "base_value": base_value,
        "gsv_factor": gsv_factor,
        "surrender_value": surrender_value
    }

def default_gsv_factor(policy_year):
    """Provide default GSV factors based on standard industry values."""
    if policy_year <= 3:
        return 0.70  # Default for years <= 3
    elif policy_year <= 5:
        return 0.75  # Default for years 4-5
    elif policy_year <= 7:
        return 0.80  # Default for years 6-7
    else:
        return 0.90  # Default for years > 7

def create_payment_projection_chart(doc_info, payment_type="premium"):
    """Create payment projection chart and dataframe."""
    financial_details = doc_info.get("financial_details", {})
    policy_identification = doc_info.get("policy_identification", {})
    
    try:
        if payment_type == "annuity":
            payment_value = extract_numeric_value(financial_details.get("annuity_amount"))
            payment_mode = financial_details.get("annuity_payment_mode", "").lower()
            payment_label = "Annuity"
        else:
            payment_value = extract_numeric_value(financial_details.get("premium_amount"))
            payment_mode = policy_identification.get("premium_payment_frequency", "").lower()
            payment_label = "Premium"
        
        # Get payment frequency
        payments_per_year = 1  # Default to yearly
        
        if "month" in str(payment_mode).lower():
            payments_per_year = 12
        elif "quart" in str(payment_mode).lower():
            payments_per_year = 4
        elif "half" in str(payment_mode).lower() or "semi" in str(payment_mode).lower():
            payments_per_year = 2
        
        # Calculate projections for 5 years
        years = list(range(1, 6))
        annual_amounts = [payment_value * payments_per_year * year for year in years]
        
        # Create dataframe for display
        df_projection = pd.DataFrame({
            "Year": years,
            f"Total {payment_label} {('Received' if payment_type == 'annuity' else 'Paid')}": [format_currency(amount) for amount in annual_amounts]
        })
        
        # Create bar chart figure
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df_projection["Year"], annual_amounts, color='#1976d2')
        ax.set_xlabel("Year")
        ax.set_ylabel(f"Total Amount (₹)")
        ax.set_title(f"Projected {payment_label} {'Income' if payment_type == 'annuity' else 'Costs'} Over 5 Years")
        
        # Format y-axis with commas
        import matplotlib.ticker as mtick
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
        
        return df_projection, fig
    
    except Exception as e:
        st.warning(f"Could not create payment projection: {str(e)}")
        return None, None