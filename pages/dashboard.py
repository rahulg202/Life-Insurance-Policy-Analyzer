import streamlit as st
from utils.policy_type import detect_policy_type, get_policy_type_description
from utils.date_utils import format_date, create_timeline
from utils.ui_components import safe_display
from utils.financial_utils import format_currency

def policy_dashboard_page():
    """Dashboard page showing policy overview."""
    if st.session_state.document_info is None:
        st.warning("Please upload a policy document first!")
        return
    
    st.header("Policy Dashboard")
    doc_info = st.session_state.document_info
    
    # Top row with key policy information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        policy_identification = doc_info.get("policy_identification", {})
        plan_type = policy_identification.get("plan_type", "")
        
        # Policy status - assuming it's active if we have the document
        st.markdown("<div class='policy-status-active'>POLICY STATUS: ACTIVE</div>", unsafe_allow_html=True)
        
        # Policy type detection
        policy_type = detect_policy_type(doc_info)
        st.markdown(f"### Policy Type: {policy_type}")
        
        # Policy image/logo based on insurer
        insurer = policy_identification.get("insurer_name", "").upper()
        if insurer:
            if "LIC" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/en/thumb/9/93/Life_Insurance_Corporation_of_India_%28logo%29.svg/1200px-Life_Insurance_Corporation_of_India_%28logo%29.svg.png", width=150)
            elif "SBI" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/58/SBI_Life_logo.svg/1200px-SBI_Life_logo.svg.png", width=150)
            elif "HDFC" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/HDFC_Life.png", width=150)
            elif "ICICI" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/ICICI_Pru_Life_logo.svg/1200px-ICICI_Pru_Life_logo.svg.png", width=150)
            elif "MAX" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/commons/7/7b/Max_Life_Insurance_logo.png", width=150)
            elif "BAJAJ" in insurer:
                st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Bajaj_Allianz_logo.svg/1200px-Bajaj_Allianz_logo.svg.png", width=150)
        
        # Display extraction stats if available
        if st.session_state.extraction_stats:
            stats = st.session_state.extraction_stats
            st.markdown("### Document Completeness")
            st.progress(min(stats["percentage"]/100, 1.0))  # Ensure value doesn't exceed 1.0
            
            # Status text based on completeness
            if stats["percentage"] >= 75:
                st.success(f"{int(stats['percentage'])}% - Most details extracted successfully")
            elif stats["percentage"] >= 50:
                st.warning(f"{int(stats['percentage'])}% - Some details might be missing")
            else:
                st.error(f"{int(stats['percentage'])}% - Many details could not be extracted")
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("<p class='header-style'>Policy Details</p>", unsafe_allow_html=True)
        
        policy_identification = doc_info.get("policy_identification", {})
        
        # Create two columns for policy details
        c1, c2 = st.columns(2)
        
        with c1:
            # Policy number
            if policy_identification.get("policy_number"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Policy Number:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("policy_number")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Policy Number:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Plan name
            if policy_identification.get("plan_name"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Plan Name:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("plan_name")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Plan Name:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # UIN
            if policy_identification.get("uin"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>UIN:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("uin")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>UIN:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Plan type
            if policy_identification.get("plan_type"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Plan Type:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("plan_type")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Plan Type:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_type), unsafe_allow_html=True)
                
            # Policy term
            if policy_identification.get("policy_term"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Policy Term:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("policy_term")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Policy Term:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
        
        with c2:
            # Date of commencement
            date_of_commencement = format_date(policy_identification.get("date_of_commencement", ""))
            if date_of_commencement:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Date of Commencement:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    date_of_commencement), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Date of Commencement:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Date of issuance
            date_of_issuance = format_date(policy_identification.get("date_of_issuance", ""))
            if date_of_issuance:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Date of Issuance:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    date_of_issuance), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Date of Issuance:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Risk commencement date
            risk_commencement = format_date(policy_identification.get("risk_commencement_date", ""))
            if risk_commencement:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Risk Commencement:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    risk_commencement), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Risk Commencement:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Premium payment frequency
            if policy_identification.get("premium_payment_frequency"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Premium Payment:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("premium_payment_frequency")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Premium Payment:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
            
            # Premium payment term
            if policy_identification.get("premium_payment_term"):
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Premium Payment Term:</span> <span class='policy-detail-value'>{}</span></div>".format(
                    policy_identification.get("premium_payment_term")), unsafe_allow_html=True)
            else:
                st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Premium Payment Term:</span> <span class='policy-detail-value missing-info'>Not found in document</span></div>", unsafe_allow_html=True)
        
        # Display any additional identification details found
        additional_identification = policy_identification.get("additional_identification_details", {})
        if additional_identification:
            st.markdown("<p class='subheader-style'>Additional Policy Details</p>", unsafe_allow_html=True)
            for key, value in additional_identification.items():
                if value:
                    st.markdown(f"<div class='policy-detail'><span class='policy-detail-label'>{key.replace('_', ' ').title()}:</span> <span class='policy-detail-value'>{value}</span></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Annuity type explanation if available
        annuity_option = doc_info.get("annuity_benefits", {}).get("annuity_option", "")
        if annuity_option and st.session_state.annuity_option_explanation:
            st.markdown("<div class='highlight-box'>", unsafe_allow_html=True)
            st.markdown(f"**Your Annuity Type: {annuity_option}**")
            st.markdown(f"<div class='full-content'>{st.session_state.annuity_option_explanation}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Middle section with key information in cards
    st.markdown("---")
    st.markdown("### Key Policy Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='date-card'>", unsafe_allow_html=True)
        st.markdown("<p class='subheader-style'>📅 Important Dates</p>", unsafe_allow_html=True)
        
        policy_identification = doc_info.get("policy_identification", {})
        
        # Extract dates and format them
        date_of_commencement = format_date(policy_identification.get("date_of_commencement", ""))
        risk_commencement_date = format_date(policy_identification.get("risk_commencement_date", ""))
        date_of_vesting = format_date(policy_identification.get("date_of_vesting", ""))
        maturity_date = format_date(policy_identification.get("maturity_date", ""))
        first_annuity_payment = format_date(doc_info.get("financial_details", {}).get("first_annuity_payment_date", ""))
        
        dates_dict = {
            "Policy Commencement": date_of_commencement,
            "Risk Commencement": risk_commencement_date,
            "Date of Vesting": date_of_vesting,
            "Maturity Date": maturity_date,
            "First Annuity Payment": first_annuity_payment
        }
        
        # Filter out None/empty values
        dates_dict = {k: v for k, v in dates_dict.items() if v}
        
        if dates_dict:
            st.markdown(create_timeline(dates_dict), unsafe_allow_html=True)
        else:
            st.markdown("<div class='missing-info'>No dates could be extracted from the document.</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='benefits-card'>", unsafe_allow_html=True)
        st.markdown("<p class='subheader-style'>💰 Financial Summary</p>", unsafe_allow_html=True)
        
        financial_details = doc_info.get("financial_details", {})
        
        # Purchase price
        purchase_price = format_currency(financial_details.get("purchase_price", ""))
        if purchase_price:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Purchase Price:</span> <span class='policy-detail-value'>{}</span></div>".format(
                purchase_price), unsafe_allow_html=True)
        
        # Premium amount
        premium_amount = format_currency(financial_details.get("premium_amount", ""))
        if premium_amount:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Premium Amount:</span> <span class='policy-detail-value'>{}</span></div>".format(
                premium_amount), unsafe_allow_html=True)
        
        # Sum assured
        sum_assured = format_currency(financial_details.get("sum_assured", ""))
        if sum_assured:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Sum Assured:</span> <span class='policy-detail-value'>{}</span></div>".format(
                sum_assured), unsafe_allow_html=True)
        
        # Maturity amount
        maturity_amount = format_currency(financial_details.get("maturity_amount", ""))
        if maturity_amount:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Maturity Amount:</span> <span class='policy-detail-value'>{}</span></div>".format(
                maturity_amount), unsafe_allow_html=True)
        
        # Annuity amount
        annuity_amount = format_currency(financial_details.get("annuity_amount", ""))
        if annuity_amount:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Annuity Amount:</span> <span class='policy-detail-value'>{}</span></div>".format(
                annuity_amount), unsafe_allow_html=True)
        
        # Death benefit
        death_benefit = format_currency(financial_details.get("death_benefit", ""))
        if death_benefit:
            st.markdown("<div class='policy-detail'><span class='policy-detail-label'>Death Benefit:</span> <span class='policy-detail-value'>{}</span></div>".format(
                death_benefit), unsafe_allow_html=True)
        
        # If no financial details found
        if not any([purchase_price, premium_amount, sum_assured, maturity_amount, annuity_amount, death_benefit]):
            st.markdown("<div class='missing-info'>No financial details could be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display any riders information
        riders = financial_details.get("riders", [])
        if riders:
            st.markdown("<p class='subheader-style'>Policy Riders</p>", unsafe_allow_html=True)
            for rider in riders[:2]:  # Show only first 2 riders
                rider_name = rider.get('name', 'Rider')
                rider_sum = format_currency(rider.get('sum_assured', ''))
                if rider_name and rider_sum:
                    st.markdown(f"**{rider_name}:** {rider_sum}")
            if len(riders) > 2:
                st.markdown(f"*... and {len(riders) - 2} more riders*")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='nominee-card'>", unsafe_allow_html=True)
        st.markdown("<p class='subheader-style'>👥 Policyholder & Nominee Details</p>", unsafe_allow_html=True)
        
        policyholder_info = doc_info.get("policyholder_annuitant_info", {})
        
        # Policyholder & Annuitant
        policyholder_name = policyholder_info.get('policyholder_name')
        if policyholder_name:
            st.markdown(f"**Policyholder:** {policyholder_name}")
        else:
            st.markdown("<div class='missing-info'>Policyholder name could not be extracted from the document.</div>", unsafe_allow_html=True)
            
        annuitant_name = policyholder_info.get('annuitant_name')
        if annuitant_name:
            st.markdown(f"**Life Assured:** {annuitant_name}")
        else:
            st.markdown("<div class='missing-info'>Life assured name could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Secondary annuitant (for joint life policies)
        secondary_annuitant = policyholder_info.get('secondary_annuitant_name')
        if secondary_annuitant:
            st.markdown(f"**Secondary Life Assured:** {secondary_annuitant}")
        
        if policyholder_info.get('age_at_entry'):
            st.markdown(f"**Age at Entry:** {policyholder_info.get('age_at_entry')}")
        
        dob = format_date(policyholder_info.get('date_of_birth'))
        if dob:
            st.markdown(f"**Date of Birth:** {dob}")
        
        st.markdown("#### Nominees:")
        nominees = policyholder_info.get("nominees", [])
        
        if nominees:
            for nominee in nominees:
                nominee_name = nominee.get('name')
                nominee_relationship = nominee.get('relationship')
                nominee_percentage = nominee.get('percentage')
                
                if nominee_name:
                    st.markdown(f"**Name:** {nominee_name}")
                    if nominee_relationship:
                        st.markdown(f"**Relationship:** {nominee_relationship}")
                    if nominee_percentage:
                        st.markdown(f"**Share:** {nominee_percentage}")
                    st.markdown("---")
            
            # Appointee details if available
            appointee = policyholder_info.get("appointee")
            if appointee:
                st.markdown(f"**Appointee:** {appointee}")
        else:
            st.markdown("<div class='missing-info'>No nominee details could be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display any additional policyholder details
        additional_policyholder = policyholder_info.get("additional_policyholder_details", {})
        if additional_policyholder:
            st.markdown("#### Additional Details:")
            for key, value in additional_policyholder.items():
                if value:
                    st.markdown(f"<div class='full-content'>**{key.replace('_', ' ').title()}:** {value}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Bottom section with policy type description
    st.markdown("---")
    
    with st.expander("About this policy type", expanded=True):
        st.markdown(get_policy_type_description(policy_type))