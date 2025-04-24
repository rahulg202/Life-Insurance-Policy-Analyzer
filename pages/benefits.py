import streamlit as st
from utils.policy_type import detect_policy_type
from utils.date_utils import format_date, create_policy_timeline_chart
from utils.ui_components import safe_display

def policy_benefits_page():
    """Page for displaying policy benefits and provisions."""
    if st.session_state.document_info is None:
        st.warning("Please upload a policy document first!")
        return
    
    st.header("Policy Benefits & Provisions")
    doc_info = st.session_state.document_info  # Get the document info from session state
    
    # Get annuity benefits information
    annuity_benefits = doc_info.get("annuity_benefits", {})
    
    # Main benefits section
    st.subheader("📊 Benefits Structure")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Annuity option details
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        policy_type = detect_policy_type(doc_info)
        
        if "Annuity" in policy_type or "Pension" in policy_type:
            annuity_option = annuity_benefits.get('annuity_option')
            if annuity_option:
                st.markdown(f"### Your Annuity Option: {annuity_option}")
            else:
                st.markdown("### Your Annuity Option")
                st.markdown("<div class='missing-info'>Annuity option could not be extracted from the document.</div>", unsafe_allow_html=True)
            
            # Display explanation if available
            if st.session_state.annuity_option_explanation:
                st.markdown(st.session_state.annuity_option_explanation)
        else:
            st.markdown(f"### Your {policy_type} Benefits")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Benefit details in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Survival Benefits", "Death Benefits", "Maturity Benefits", "Additional Benefits"])
        
        with tab1:
            survival_benefits = annuity_benefits.get("survival_benefits")
            st.markdown(f"**Survival Benefits:**")
            if survival_benefits:
                st.markdown(f"<div class='full-content'>{survival_benefits}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='missing-info'>Survival benefits information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        with tab2:
            death_benefits = annuity_benefits.get("death_benefits")
            st.markdown(f"**Death Benefits:**")
            if death_benefits:
                st.markdown(f"<div class='full-content'>{death_benefits}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='missing-info'>Death benefits information could not be extracted from the document.</div>", unsafe_allow_html=True)
            
            # Death benefit payment options
            death_benefit_options = doc_info.get("special_provisions", {}).get("death_benefit_payment_options")
            if death_benefit_options:
                st.markdown("#### Death Benefit Payment Options:")
                st.markdown(f"<div class='full-content'>{death_benefit_options}</div>", unsafe_allow_html=True)
        
        with tab3:
            maturity_benefits = annuity_benefits.get("maturity_benefits")
            st.markdown(f"**Maturity Benefits:**")
            if maturity_benefits:
                st.markdown(f"<div class='full-content'>{maturity_benefits}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='missing-info'>Maturity benefits information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        with tab4:
            # Display any additional benefits found
            additional_benefits = annuity_benefits.get("additional_benefits", [])
            if additional_benefits:
                for i, benefit in enumerate(additional_benefits):
                    if isinstance(benefit, dict) and 'title' in benefit and 'description' in benefit:
                        with st.expander(benefit['title']):
                            st.markdown(f"<div class='full-content'>{benefit['description']}</div>", unsafe_allow_html=True)
                    else:
                        with st.expander(f"Additional Benefit {i+1}"):
                            st.markdown(f"<div class='full-content'>{str(benefit)}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='missing-info'>No additional benefits information found in the document.</div>", unsafe_allow_html=True)
    
    with col2:
        # Create a visual representation of policy timeline
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        
        policy_type = detect_policy_type(doc_info)
        if "Annuity" in policy_type or "Pension" in policy_type:
            st.markdown("### Annuity Flow")
        else:
            st.markdown("### Policy Timeline")
        
        policy_identification = doc_info.get("policy_identification", {})
        financial_details = doc_info.get("financial_details", {})
        
        # Key phases visualization with mermaid chart
        st.markdown("#### Key Phases:")
        policy_chart = create_policy_timeline_chart(policy_type, policy_identification)
        if policy_chart:
            st.markdown(policy_chart)
        else:
            st.markdown("<div class='missing-info'>Could not create policy timeline due to missing date information.</div>", unsafe_allow_html=True)
        
        # Key dates
        st.markdown("#### Key Dates:")
        date_of_commencement = format_date(policy_identification.get('date_of_commencement', ''))
        if date_of_commencement:
            st.markdown(f"**Policy Start:** {date_of_commencement}")
        else:
            st.markdown("<div class='missing-info'>Policy start date could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        risk_commencement_date = format_date(policy_identification.get('risk_commencement_date', ''))
        if risk_commencement_date:
            st.markdown(f"**Risk Start:** {risk_commencement_date}")
            
        if "Annuity" in policy_type or "Pension" in policy_type:
            date_of_vesting = format_date(policy_identification.get('date_of_vesting', ''))
            if date_of_vesting:
                st.markdown(f"**Vesting Date:** {date_of_vesting}")
            
            first_annuity_payment = format_date(financial_details.get('first_annuity_payment_date', ''))
            if first_annuity_payment:
                st.markdown(f"**First Payment:** {first_annuity_payment}")
        
        maturity_date = format_date(policy_identification.get('maturity_date', ''))
        if maturity_date:
            st.markdown(f"**Maturity Date:** {maturity_date}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Detailed Special Provisions section
    st.markdown("---")
    st.subheader("📋 Special Provisions")
    
    special_provisions = doc_info.get("special_provisions", {})
    
    # Create expanded special provisions section with more details
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # First column of provisions
        # Free Look Period with detailed explanation
        free_look = special_provisions.get("free_look_period")
        if free_look:
            with st.expander("Free Look Period"):
                st.markdown(f"<div class='full-content'>{free_look}</div>", unsafe_allow_html=True)
                # Add explanatory text for better understanding
                st.markdown("""
                **What is Free Look Period?**  
                The free look period is a time frame during which you can review your newly purchased policy and decide if you want to keep it. If you're not satisfied, you can return the policy and get a refund of the premium paid, subject to certain deductions.
                """)
        
        # QROPS provisions if available
        qrops = special_provisions.get("qrops_provisions")
        if qrops:
            with st.expander("QROPS Provisions"):
                st.markdown(f"<div class='full-content'>{qrops}</div>", unsafe_allow_html=True)
        
        # Grace Period details
        grace_period = special_provisions.get("grace_period")
        if grace_period:
            with st.expander("Grace Period"):
                st.markdown(f"<div class='full-content'>{grace_period}</div>", unsafe_allow_html=True)
        
        # Revival provisions
        revival_provisions = special_provisions.get("revival_provisions")
        if revival_provisions:
            with st.expander("Revival/Reinstatement Provisions"):
                st.markdown(f"<div class='full-content'>{revival_provisions}</div>", unsafe_allow_html=True)
    
    with col2:
        # Second column of provisions
        # Divyangjan provisions if available
        divyangjan = special_provisions.get("divyangjan_provisions")
        if divyangjan:
            with st.expander("Provisions for Persons with Disability (Divyangjan)"):
                st.markdown(f"<div class='full-content'>{divyangjan}</div>", unsafe_allow_html=True)
        
        # Death benefit payment options
        death_benefit_options = special_provisions.get("death_benefit_payment_options")
        if death_benefit_options:
            with st.expander("Death Benefit Payment Options"):
                st.markdown(f"<div class='full-content'>{death_benefit_options}</div>", unsafe_allow_html=True)
        
        # Auto-cover provisions
        auto_cover = special_provisions.get("auto_cover_provisions")
        if auto_cover:
            with st.expander("Auto-Cover Provisions"):
                st.markdown(f"<div class='full-content'>{auto_cover}</div>", unsafe_allow_html=True)
        
        # Display ALL additional provisions
        additional_provisions = special_provisions.get("additional_provisions", [])
        if additional_provisions:
            st.markdown("### Other Special Provisions")
            for i, provision in enumerate(additional_provisions):
                if isinstance(provision, dict) and 'title' in provision and 'description' in provision:
                    with st.expander(provision['title']):
                        st.markdown(f"<div class='full-content'>{provision['description']}</div>", unsafe_allow_html=True)
                else:
                    with st.expander(f"Additional Provision {i+1}"):
                        st.markdown(f"<div class='full-content'>{str(provision)}</div>", unsafe_allow_html=True)
    
    # Show if no special provisions were found
    if not any([free_look, qrops, grace_period, revival_provisions, divyangjan, death_benefit_options, auto_cover, additional_provisions]):
        st.markdown("<div class='missing-info'>No special provisions could be extracted from the document.</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)