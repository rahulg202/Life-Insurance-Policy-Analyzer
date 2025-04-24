import streamlit as st
from utils.ui_components import safe_display

def terms_provisions_page():
    """Page for displaying terms and support details."""
    if st.session_state.document_info is None:
        st.warning("Please upload a policy document first!")
        return
    
    st.header("Terms & Support Details")
    doc_info = st.session_state.document_info
    
    # Get relevant information
    exclusions_clauses = doc_info.get("exclusions_clauses", {})
    support_details = doc_info.get("support_details", {})
    
    # Exclusions section
    st.subheader("📋 Policy Exclusions & Limitations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### Policy Exclusions & Clauses")
        
        # Display all exclusions dynamically
        all_exclusions = exclusions_clauses.get("all_exclusions", [])
        
        if all_exclusions:
            for i, exclusion in enumerate(all_exclusions):
                if isinstance(exclusion, dict):
                    title = exclusion.get('title', f'Exclusion {i+1}')
                    description = exclusion.get('description', 'Details not available')
                    
                    # Ensure full content is displayed, not reference
                    with st.expander(title):
                        st.markdown(f"<div class='full-content'>{description}</div>", unsafe_allow_html=True)
                else:
                    # Handle case where exclusion is a string
                    with st.expander(f"Exclusion {i+1}"):
                        st.markdown(f"<div class='full-content'>{str(exclusion)}</div>", unsafe_allow_html=True)
        
        # If no exclusions found in the new dynamic list, fall back to the predefined ones
        elif exclusions_clauses.get("suicide_clause") or exclusions_clauses.get("non_disclosure_clause"):
            if exclusions_clauses.get("suicide_clause"):
                with st.expander("Suicide Clause"):
                    suicide_clause = exclusions_clauses.get("suicide_clause")
                    st.markdown(f"<div class='full-content'>{suicide_clause}</div>", unsafe_allow_html=True)
            
            if exclusions_clauses.get("non_disclosure_clause"):
                with st.expander("Non-disclosure Clause"):
                    non_disclosure = exclusions_clauses.get("non_disclosure_clause")
                    st.markdown(f"<div class='full-content'>{non_disclosure}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='missing-info'>No policy exclusions could be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display Claim Procedure if available
        claim_procedure = exclusions_clauses.get("claim_procedure")
        if claim_procedure:
            with st.expander("Claim Procedure"):
                st.markdown(f"<div class='full-content'>{claim_procedure}</div>", unsafe_allow_html=True)
        
        # Policy termination conditions
        termination_conditions = exclusions_clauses.get("policy_termination_conditions", [])
        if termination_conditions:
            st.markdown("### Policy Termination Conditions")
            for i, condition in enumerate(termination_conditions):
                st.markdown(f"<div class='full-content'>**{i+1}.** {condition}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Assignment & Nomination section
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### Assignment & Nomination")
        
        # Display assignment provisions if available
        assignment_provisions = exclusions_clauses.get("assignment_provisions")
        if assignment_provisions:
            with st.expander("Assignment Provisions"):
                st.markdown(f"<div class='full-content'>{assignment_provisions}</div>", unsafe_allow_html=True)
        else:
            with st.expander("Assignment Provisions"):
                st.markdown("<div class='missing-info'>Assignment provisions could not be extracted from the document.</div>", unsafe_allow_html=True)
                st.markdown("""
                **Standard Assignment Provisions:**
                
                1. The holder of the Policy can assign the Policy to another person or entity in accordance with Section 38 of the Insurance Act, 1938 as amended from time to time.
                
                2. An assignment of the Policy may be made by an endorsement upon the Policy itself or by a separate instrument, signed in either case by the assignor specifically stating the fact of assignment and duly attested.
                
                3. The first assignment may be made only by the Policyholder. An assignment shall automatically cancel a nomination except an assignment in favor of the Company.
                """)
        
        # Display nomination provisions if available
        nomination_provisions = exclusions_clauses.get("nomination_provisions")
        if nomination_provisions:
            with st.expander("Nomination Provisions"):
                st.markdown(f"<div class='full-content'>{nomination_provisions}</div>", unsafe_allow_html=True)
        else:
            with st.expander("Nomination Provisions"):
                st.markdown("<div class='missing-info'>Nomination provisions could not be extracted from the document.</div>", unsafe_allow_html=True)
                st.markdown("""
                **Standard Nomination Provisions:**
                
                1. The policyholder of a life insurance policy on his/her own life may nominate a person or persons to whom money secured by the policy shall be paid in the event of his/her death in accordance with Section 39 of the Insurance Act, 1938 as amended from time to time.
                
                2. If the nominee is a minor, the policyholder may appoint any person to receive the money secured by the policy in the event of policyholder's death during the minority of the nominee.
                
                3. A nomination can be made at any time before the maturity of the policy.
                """)
        
        # Display any additional clauses found
        additional_clauses = exclusions_clauses.get("additional_clauses", [])
        if additional_clauses:
            st.markdown("### Additional Policy Clauses")
            for i, clause in enumerate(additional_clauses):
                if isinstance(clause, dict) and 'title' in clause and 'description' in clause:
                    with st.expander(clause['title']):
                        st.markdown(f"<div class='full-content'>{clause['description']}</div>", unsafe_allow_html=True)
                else:
                    with st.expander(f"Clause {i+1}"):
                        st.markdown(f"<div class='full-content'>{str(clause)}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Support details section
    st.markdown("---")
    st.subheader("📞 Support & Contact Information")
    
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Branch Office & Support")
        
        branch_office = support_details.get("branch_office")
        if branch_office:
            st.markdown(f"**Branch Office:** {branch_office}")
        else:
            st.markdown("<div class='missing-info'>Branch office information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display customer care numbers
        customer_care_numbers = support_details.get("customer_care_numbers", [])
        if customer_care_numbers:
            st.markdown("**Customer Care Numbers:**")
            for number in customer_care_numbers:
                st.markdown(f"- {number}")
        else:
            st.markdown("<div class='missing-info'>Customer care numbers could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display email addresses
        email_addresses = support_details.get("email_addresses", [])
        if email_addresses:
            st.markdown("**Email Addresses:**")
            for email in email_addresses:
                st.markdown(f"- {email}")
        else:
            st.markdown("<div class='missing-info'>Email addresses could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display website
        website = support_details.get("website")
        if website:
            st.markdown(f"**Website:** {website}")
    
    with col2:
        st.markdown("### Grievance Redressal")
        
        grievance_officer = support_details.get("grievance_officer")
        if grievance_officer:
            st.markdown(f"**Grievance Redressal Officer:** {grievance_officer}")
        else:
            st.markdown("<div class='missing-info'>Grievance officer information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        ombudsman_contact = support_details.get("ombudsman_contact")
        if ombudsman_contact:
            st.markdown(f"**Insurance Ombudsman:** {ombudsman_contact}")
        else:
            st.markdown("<div class='missing-info'>Ombudsman contact information could not be extracted from the document.</div>", unsafe_allow_html=True)
        
        # Display any additional support details
        additional_support = support_details.get("additional_support_details", {})
        if additional_support:
            st.markdown("**Additional Support Information:**")
            for key, value in additional_support.items():
                if value:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Legal clarifications section 
    st.markdown("---")
    st.subheader("⚖️ Legal Clarifications")
    
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.markdown("""
    ### Important Legal Notes

    The analysis provided by this application is for informational purposes only and should not be considered as legal or financial advice. The actual terms, conditions, benefits, and obligations of your insurance policy are governed by the policy document issued by your insurance company.

    **Disclaimer:**
    - In case of any discrepancy between the information displayed in this application and your policy document, the policy document shall prevail.
    - Tax benefits shown are as per current tax laws, which are subject to change.
    - The calculations shown are approximations and may not reflect the exact values applicable to your policy.
    
    We recommend confirming all critical information with your insurance provider before making any decisions regarding your policy.
    """)
    st.markdown("</div>", unsafe_allow_html=True)