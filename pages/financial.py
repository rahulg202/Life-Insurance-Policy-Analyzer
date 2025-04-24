import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.policy_type import detect_policy_type
from utils.financial_utils import format_currency, extract_numeric_value, calculate_surrender_value, create_payment_projection_chart, calculate_loan_details
from utils.ui_components import format_gsv_factors_table, safe_display

def financial_details_page():
    """Page for displaying financial details and calculations."""
    if st.session_state.document_info is None:
        st.warning("Please upload a policy document first!")
        return
    
    st.header("Financial Details & Calculations")
    doc_info = st.session_state.document_info
    
    financial_details = doc_info.get("financial_details", {})
    surrender_loan_details = doc_info.get("surrender_loan_details", {})
    
    # Top row with financial summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 💰 Financial Summary")
        
        # Format currency values
        purchase_price = format_currency(financial_details.get("purchase_price"))
        premium_amount = format_currency(financial_details.get("premium_amount"))
        sum_assured = format_currency(financial_details.get("sum_assured"))
        maturity_amount = format_currency(financial_details.get("maturity_amount"))
        annuity_amount = format_currency(financial_details.get("annuity_amount"))
        death_benefit = format_currency(financial_details.get("death_benefit"))
        additional_benefit = format_currency(financial_details.get("additional_death_benefit_monthly"))
        
        # Create a table for financial details - only include fields that are available
        financial_items = []
        financial_values = []
        
        if purchase_price:
            financial_items.append("Purchase Price")
            financial_values.append(purchase_price)
        
        if premium_amount:
            financial_items.append("Premium Amount")
            financial_values.append(premium_amount)
        
        if sum_assured:
            financial_items.append("Sum Assured")
            financial_values.append(sum_assured)
        
        if maturity_amount:
            financial_items.append("Maturity Amount")
            financial_values.append(maturity_amount)
        
        if annuity_amount:
            financial_items.append("Annuity Amount")
            financial_values.append(annuity_amount)
        
        if death_benefit:
            financial_items.append("Death Benefit")
            financial_values.append(death_benefit)
        
        if additional_benefit:
            financial_items.append("Additional Death Benefit (Monthly)")
            financial_values.append(additional_benefit)
        
        # Add all additional financial details found
        additional_financials = financial_details.get("additional_financial_details", {})
        for key, value in additional_financials.items():
            if value and value != "":
                financial_items.append(key.replace('_', ' ').title())
                try:
                    # Try to format as currency if it looks like a number
                    formatted_value = format_currency(value)
                    if formatted_value:
                        financial_values.append(formatted_value)
                    else:
                        financial_values.append(str(value))
                except:
                    financial_values.append(str(value))
        
        # Create DataFrame if there are any items to display
        if financial_items:
            df = pd.DataFrame({
                "Item": financial_items,
                "Value": financial_values
            })
            st.table(df)
        else:
            st.markdown("<div class='missing-info'>No financial details could be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Payment frequency
        annuity_payment_mode = financial_details.get('annuity_payment_mode')
        if annuity_payment_mode:
            st.markdown(f"**Annuity Payment Mode:** {annuity_payment_mode}")
            
            first_annuity_payment = financial_details.get('first_annuity_payment_date')
            if first_annuity_payment:
                st.markdown(f"**First Annuity Payment:** {first_annuity_payment}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display policy riders in a separate card if available
        riders = financial_details.get('riders', [])
        if riders:
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ Policy Riders")
            
            rider_names = []
            rider_sums = []
            rider_premiums = []
            
            for rider in riders:
                rider_names.append(rider.get('name', 'Unknown Rider'))
                
                rider_sum = format_currency(rider.get('sum_assured'))
                rider_sums.append(rider_sum if rider_sum else "Not specified")
                
                rider_premium = format_currency(rider.get('premium'))
                rider_premiums.append(rider_premium if rider_premium else "Not specified")
            
            df_riders = pd.DataFrame({
                "Rider": rider_names,
                "Sum Assured": rider_sums,
                "Premium": rider_premiums
            })
            
            st.table(df_riders)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        
        policy_type = detect_policy_type(doc_info)
        if "Annuity" in policy_type or "Pension" in policy_type:
            st.markdown("### 📈 Annuity Payment Projection")
            payment_type = "annuity"
        else:
            st.markdown("### 📈 Premium Payment Projection")
            payment_type = "premium"
        
        # Create payment projection
        df_projection, fig = create_payment_projection_chart(doc_info, payment_type)
        
        if df_projection is not None and fig is not None:
            st.table(df_projection)
            st.pyplot(fig)
        else:
            st.markdown("<div class='missing-info'>Could not create payment projection due to missing financial information.</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row for surrender and loan details
    st.markdown("---")
    st.subheader("Surrender & Loan Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 💹 Surrender Value")
        
        # Surrender formula - show full content if available
        surrender_formula = surrender_loan_details.get("surrender_value_formula")
        if surrender_formula:
            st.markdown(f"**Surrender Value Formula:**")
            st.markdown(f"<div class='full-content'>{surrender_formula}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='missing-info'>Surrender value formula could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display GSV factors table if available
        gsv_factors = surrender_loan_details.get("gsv_factors", {})
        if gsv_factors:
            st.markdown("**Guaranteed Surrender Value Factors:**")
            gsv_table_html = format_gsv_factors_table(gsv_factors)
            if gsv_table_html:
                st.markdown(gsv_table_html, unsafe_allow_html=True)
            else:
                st.markdown("<div class='missing-info'>Could not format GSV factors table.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='missing-info'>GSV factors could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Additional surrender details
        additional_surrender = surrender_loan_details.get("additional_surrender_loan_details", {})
        if additional_surrender:
            st.markdown("**Additional Surrender Details:**")
            for key, value in additional_surrender.items():
                if value and "surrender" in key.lower():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Surrender calculator
        st.markdown("#### Surrender Value Calculator")
        st.markdown("*This is an approximate calculation. Please consult your policy document for exact terms.*")
        
        try:
            # Policy year selection
            max_policy_term = 15  # Default max
            policy_term_str = doc_info.get("policy_identification", {}).get("policy_term", "")
            if policy_term_str:
                # Try to extract just the number from the policy term
                import re
                term_digits = re.findall(r'\d+', str(policy_term_str))
                if term_digits:
                    max_policy_term = int(term_digits[0])
            
            policy_year = st.slider("Select Policy Year", 
                                  min_value=1, 
                                  max_value=max_policy_term, 
                                  value=3)
            
            # Calculate surrender value
            surrender_result = calculate_surrender_value(doc_info, policy_year)
            
            # Display calculation details
            if surrender_result["base_value"] > 0:
                st.markdown(f"**Base Value:** {format_currency(surrender_result['base_value'])}")
                st.markdown(f"**GSV Factor for Year {policy_year}:** {surrender_result['gsv_factor']:.2%}")
                st.markdown(f"**Estimated Surrender Value:** {format_currency(surrender_result['surrender_value'])}")
                st.markdown("*Note: Actual surrender value may be higher of GSV or Special Surrender Value*")
            else:
                st.markdown("<div class='missing-info'>Could not calculate surrender value due to missing financial information.</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"Unable to calculate surrender value. Please check with your insurance provider. Error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 💳 Policy Loan")
        
        # Loan availability - show full content
        loan_availability = surrender_loan_details.get("loan_availability")
        if loan_availability:
            st.markdown(f"**Loan Availability:** {loan_availability}")
        else:
            st.markdown("<div class='missing-info'>Loan availability information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Max loan amount
        max_loan = surrender_loan_details.get("max_loan_amount")
        if max_loan:
            st.markdown(f"**Maximum Loan Amount:** {max_loan}")
        
        # Loan interest rate
        interest_rate = surrender_loan_details.get("loan_interest_rate")
        if interest_rate:
            st.markdown(f"**Loan Interest Rate:** {interest_rate}")
        
        # Additional loan details if available
        if surrender_loan_details.get("loan_during_deferment"):
            st.markdown("**Loan During Deferment Period:**")
            st.markdown(f"<div class='full-content'>{surrender_loan_details.get('loan_during_deferment')}</div>", unsafe_allow_html=True)
        
        if surrender_loan_details.get("loan_after_deferment"):
            st.markdown("**Loan After Deferment Period:**")
            st.markdown(f"<div class='full-content'>{surrender_loan_details.get('loan_after_deferment')}</div>", unsafe_allow_html=True)
        
        # Additional loan details from additional_surrender_loan_details
        additional_loan = surrender_loan_details.get("additional_surrender_loan_details", {})
        if additional_loan:
            for key, value in additional_loan.items():
                if value and "loan" in key.lower():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Loan calculator
        st.markdown("#### Policy Loan Calculator")
        st.markdown("*This is an approximate calculation. Please consult with your insurer for actual eligibility.*")
        
        try:
            # Get surrender value from left column calculation if available
            surrender_value = None
            try:
                surrender_result = locals().get('surrender_result')
                if surrender_result and 'surrender_value' in surrender_result:
                    surrender_value = surrender_result['surrender_value']
            except:
                pass
            
            # Get max loan amount
            max_loan_amount = 0
            
            # If surrender value was calculated in the left column, use it
            if surrender_value is not None:
                max_loan_amount = surrender_value * 0.9  # Typically 90% of surrender value
            else:
                # Fallback - estimate from document info
                policy_type = detect_policy_type(doc_info)
                financial_details = doc_info.get("financial_details", {})
                
                if "Annuity" in policy_type or "Pension" in policy_type:
                    purchase_price_val = extract_numeric_value(financial_details.get("purchase_price"))
                    
                    # Extract loan limit from document if available
                    loan_limit_percentage = 60  # default
                    max_loan_amount_info = surrender_loan_details.get("max_loan_amount", "")
                    
                    if isinstance(max_loan_amount_info, str) and "%" in max_loan_amount_info:
                        # Try to extract percentage
                        import re
                        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', max_loan_amount_info)
                        if percentage_match:
                            loan_limit_percentage = float(percentage_match.group(1))
                    
                    max_loan_amount = purchase_price_val * (loan_limit_percentage / 100)
                else:
                    sum_assured_val = extract_numeric_value(financial_details.get("sum_assured"))
                    
                    # Extract loan limit from document if available
                    loan_limit_percentage = 40  # default
                    max_loan_amount_info = surrender_loan_details.get("max_loan_amount", "")
                    
                    if isinstance(max_loan_amount_info, str) and "%" in max_loan_amount_info:
                        # Try to extract percentage
                        import re
                        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', max_loan_amount_info)
                        if percentage_match:
                            loan_limit_percentage = float(percentage_match.group(1))
                    
                    max_loan_amount = sum_assured_val * (loan_limit_percentage / 100)
            
            # Ensure minimum loan amount for calculation
            max_loan_amount = max(max_loan_amount, 1000)  # Minimum 1000 for calculation purposes
            
            if max_loan_amount > 1000:  # Only show calculator if we have a meaningful amount
                # Loan amount selection
                loan_amount = st.slider("Select Loan Amount", 
                                      min_value=0.0, 
                                      max_value=float(max_loan_amount), 
                                      value=float(max_loan_amount/2),
                                      format="₹%.2f")
                
                # Extract interest rate from the document
                interest_rate_val = 9.5  # Default based on typical rates
                
                # Try to extract interest rate from policy info
                interest_rate_info = surrender_loan_details.get("loan_interest_rate", "")
                if isinstance(interest_rate_info, str):
                    # Extract the interest rate
                    import re
                    interest_patterns = [
                        r'(\d+\.?\d*)%',  # Match patterns like 9.5%
                        r'(\d+\.?\d*) percent',  # Match patterns like 9.5 percent
                        r'(\d+\.?\d*)',  # Just match a number
                    ]
                    
                    for pattern in interest_patterns:
                        matches = re.findall(pattern, interest_rate_info)
                        if matches:
                            try:
                                interest_rate_val = float(matches[0])
                                break
                            except (ValueError, TypeError):
                                pass
                elif isinstance(interest_rate_info, (int, float)):
                    interest_rate_val = float(interest_rate_info)
                
                # Calculate loan details
                loan_results = calculate_loan_details(doc_info, max_loan_amount, loan_amount, interest_rate_val)
                
                # Display results
                if "error" in loan_results:
                    st.warning(loan_results["error"])
                else:
                    st.markdown(f"**Loan Amount:** {loan_results['loan_amount']}")
                    st.markdown(f"**Interest Rate:** {loan_results['interest_rate']}")
                    st.markdown(f"**Annual Interest Payment:** {loan_results['annual_interest']}")
                    st.markdown(f"**Monthly Interest Payment:** {loan_results['monthly_interest']}")
                    
                    if loan_results.get("warning"):
                        st.warning(loan_results["warning"])
            else:
                st.markdown("<div class='missing-info'>Could not calculate loan details due to missing financial information.</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"Unable to calculate loan details. Please check with your insurance provider. Error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)