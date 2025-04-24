import streamlit as st
import google.generativeai as genai
import json

class AIService:
    """Interface for AI services like Gemini."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.model = None
        self.api_key = "AIzaSyA0gqQS8UEF1CtDC1SRlAH9CI8kLrlLA64"  
    
    def setup(self):
        """Set up the AI service."""
        try:
            # Configure API key
            genai.configure(api_key=self.api_key)
            
            # Try different model names in case one fails
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception:
                try:
                    self.model = genai.GenerativeModel('models/gemini-pro')
                except Exception:
                    self.model = genai.GenerativeModel('gemini-pro')
            
            return True
        except Exception as e:
            st.error(f"Error setting up AI service: {str(e)}")
            return False
    
    def is_setup(self):
        """Check if the AI service is set up."""
        return self.model is not None
    
    def generate_content(self, prompt, temperature=0.2, max_tokens=1024):
        """Generate content using the AI service."""
        if not self.is_setup():
            if not self.setup():
                return {"error": "Could not set up AI service."}
        
        try:
            # Generate content
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
            }
            
            # Set safety settings to allow insurance policy content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            return {"text": response.text}
        
        except Exception as e:
            return {"error": f"Error generating content: {str(e)}"}
    
    def extract_policy_info(self, document_text):
        """Extract structured information from a policy document."""
        if not self.is_setup():
            if not self.setup():
                return None, {"error": "Could not set up AI service."}
        
        try:
            # Extraction prompt
            prompt = """
            Please extract ALL available information from this life insurance policy document and return it in a valid JSON format. Don't limit yourself to just the predefined fields - extract everything you can find.
            
            1. Policy Identification:
               - Policy Number (also look for: Policy No., Policy #, Certificate No., Proposal Number)
               - Insurer Name (company names like: LIC of India, HDFC Life, SBI Life, etc.)
               - Plan Name (also look for: Scheme, Product Name)
               - UIN (also look for: Unique Identification Number)
               - Date of Commencement (also look for: Start Date, Inception Date)
               - Date of Issuance (also look for: Date of Issue, Policy Issue Date)
               - Risk Commencement Date (also look for: Risk Start Date)
               - Policy Term (also look for: Term, Duration, Policy Period)
               - Premium Payment Term (also look for: Premium Term, Paying Term, PPT)
               - Plan Type (e.g., Traditional, ULIP, Term, etc.)
               - Premium Payment Frequency (also look for: Payment Mode, Premium Interval)
               - Deferment Period
               - Date of Vesting
               - Maturity Date (also look for: End Date, Date of Maturity)
               - Any other policy identification details found in the document
            
            2. Policyholder & Annuitant Information:
               - Policyholder Name (also look for: Proposer, Name of Proposer)
               - Annuitant/Primary Annuitant Name (also look for: Life Assured, Insured Person)
               - Secondary Annuitant Name (if joint life)
               - Date of Birth of Annuitant(s) (also look for: DOB)
               - Secondary Date of Birth
               - Age at Entry (also look for: Age on Risk Commencement, Entry Age)
               - Nominee Names (also look for: Beneficiary)
               - Nominee Relationships (also look for: Relation with Life Assured)
               - Nominee Percentage Shares (also look for: Share, Allocation)
               - Appointee (if nominee is minor)
               - Any other policyholder/annuitant details found in the document
            
            3. Financial Details:
               - Purchase Price
               - Premium Amount
               - Sum Assured (also look for: Basic Sum Assured, Coverage Amount)
               - Death Benefit (also look for: Sum Assured on Death, Death Cover)
               - Maturity Amount (also look for: Sum Assured on Maturity, Maturity Benefit)
               - Annuity Amount (also look for: Annuity Payout, Monthly/Yearly Income, Pension Amount)
               - Additional Death Benefit (Monthly)
               - Mode of Annuity Payment
               - Date of First Annuity Payment
               - Any additional riders and their costs
               - Any other financial details found in the document
            
            4. Annuity Option and Benefits:
               - Annuity Option Chosen (e.g., Deferred annuity for Single Life, Deferred annuity for Joint life)
               - Survival Benefits Description (extract all details of survival benefits)
               - Death Benefits Description (extract all details of death benefits)
               - Maturity Benefits Description (extract all details of maturity benefits)
               - GSV Factor Table
               - Bonus rates or details if mentioned
               - Any other benefits mentioned in the document
            
            5. Surrender and Loan Details:
               - Surrender Value Formula (also look for: Guaranteed Surrender Value, Special Surrender Value)
               - Guaranteed Surrender Value Factors
               - Policy Loan Availability (also look for: Loan Available)
               - Maximum Loan Amount
               - Loan Interest Rate
               - Loan During Deferment Period
               - Loan After Deferment Period
               - Any other surrender or loan-related provisions
            
            6. Special Provisions:
               - Free Look Period (also look for: Look-in Period, Cancellation Window)
               - QROPS Provisions
               - Divyangjan (Disability) Provisions
               - Options for Payment of Death Benefit (Lumpsum/Annuitisation/Installment)
               - Grace Period details
               - Revival/Reinstatement provisions
               - Auto-cover provisions
               - Any other special provisions found in the document
            
            7. Exclusions and Clauses:
               - IMPORTANT: Extract ALL exclusion clauses present in the document, not just accidental death ones
               - This includes suicide clause, waiting periods, disease-specific exclusions, etc.
               - Each exclusion should have a clear title and complete description
               - Extract exclusion details including conditions, waiting periods, and any exceptions
               - Extract claim procedures and requirements
               - Non-disclosure Clause
               - Assignment Provisions
               - Nomination Provisions
               - Any other exclusions or clauses found in the document
            
            8. Support Details:
               - Branch Office
               - Grievance Redressal Officer (also look for: Customer Care, Support Details)
               - Ombudsman Contact
               - All customer service contact numbers
               - Email addresses for support
               - Website information
               - Any other support details found in the document
            
            Return ONLY the JSON with no additional explanations. If you can't find a piece of information, set it to null.
            Do not include guesses or interpretations - if information is not clearly stated, use null.
            
            The JSON should look like this structure, but include any additional fields you find:
            
            {
                "policy_identification": {
                    "policy_number": "",
                    "insurer_name": "",
                    "plan_name": "",
                    "uin": "",
                    "date_of_commencement": "",
                    "date_of_issuance": "",
                    "risk_commencement_date": "",
                    "policy_term": "",
                    "premium_payment_term": "",
                    "plan_type": "",
                    "premium_payment_frequency": "",
                    "deferment_period": "",
                    "date_of_vesting": "",
                    "maturity_date": "",
                    "additional_identification_details": {}
                },
                "policyholder_annuitant_info": {
                    "policyholder_name": "",
                    "annuitant_name": "",
                    "secondary_annuitant_name": "",
                    "date_of_birth": "",
                    "secondary_date_of_birth": "",
                    "age_at_entry": "",
                    "nominees": [
                        {
                            "name": "",
                            "relationship": "",
                            "percentage": ""
                        }
                    ],
                    "appointee": "",
                    "additional_policyholder_details": {}
                },
                "financial_details": {
                    "purchase_price": "",
                    "premium_amount": "",
                    "sum_assured": "",
                    "death_benefit": "",
                    "maturity_amount": "",
                    "annuity_amount": "",
                    "additional_death_benefit_monthly": "",
                    "annuity_payment_mode": "",
                    "first_annuity_payment_date": "",
                    "riders": [
                        {
                            "name": "",
                            "sum_assured": "",
                            "premium": ""
                        }
                    ],
                    "additional_financial_details": {}
                },
                "annuity_benefits": {
                    "annuity_option": "",
                    "survival_benefits": "",
                    "death_benefits": "",
                    "maturity_benefits": "",
                    "additional_benefits": []
                },
                "surrender_loan_details": {
                    "surrender_value_formula": "",
                    "gsv_factors": {},
                    "loan_availability": "",
                    "max_loan_amount": "",
                    "loan_interest_rate": "",
                    "loan_during_deferment": "",
                    "loan_after_deferment": "",
                    "additional_surrender_loan_details": {}
                },
                "special_provisions": {
                    "free_look_period": "",
                    "qrops_provisions": "",
                    "divyangjan_provisions": "",
                    "death_benefit_payment_options": "",
                    "grace_period": "",
                    "revival_provisions": "",
                    "additional_provisions": []
                },
                "exclusions_clauses": {
                    "suicide_clause": "",
                    "non_disclosure_clause": "",
                    "assignment_provisions": "",
                    "nomination_provisions": "",
                    "all_exclusions": [
                        {
                            "title": "",
                            "description": ""
                        }
                    ],
                    "policy_termination_conditions": [],
                    "claim_procedure": ""
                },
                "support_details": {
                    "branch_office": "",
                    "grievance_officer": "",
                    "ombudsman_contact": "",
                    "customer_care_numbers": [],
                    "email_addresses": [],
                    "website": "",
                    "additional_support_details": {}
                }
            }
            
            Focus especially on the provided document. Pay close attention to structured sections, tables, and data fields.
            It's important that you extract ALL text for each field - do not truncate or summarize the content.
            For any list fields like exclusions, extract the complete text of each item without abbreviating.
            """
            
            # Combine prompt and document text
            full_prompt = prompt + "\n\nDocument text:\n" + document_text
            
            # Generate content with low temperature for factual extraction
            generation_config = {
                "temperature": 0.1,  # Low temperature for factual extraction
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,  # Increased to capture more complete information
            }
            
            # Set safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Extract and parse the JSON response
            response_text = response.text
            
            # Find JSON content
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extracted_info = json.loads(json_str)
            else:
                # If no JSON detected, attempt to parse the entire response
                extracted_info = json.loads(response_text)
            
            # Calculate extraction stats
            stats = self._calculate_extraction_stats(extracted_info)
            
            return extracted_info, stats
        
        except Exception as e:
            st.error(f"Error extracting information: {str(e)}")
            # Return empty structure and error stats
            empty_structure = {
                "policy_identification": {
                    "policy_number": None,
                    "insurer_name": None,
                    "plan_name": None,
                    # Other fields as needed
                },
                # Other sections as needed
            }
            error_stats = {"total_fields": 0, "filled_fields": 0, "percentage": 0, "error": str(e)}
            return empty_structure, error_stats
    
    def explain_annuity_option(self, annuity_option):
        """Provide an explanation of the annuity option."""
        if not annuity_option:
            return "No annuity option information available."
            
        prompt = f"""
        Please provide a simple, clear explanation of the following annuity option in a life insurance policy: 
        "{annuity_option}"
        
        Include details on:
        1. How the annuity works
        2. Who receives the payments
        3. What happens when the primary annuitant dies
        4. The key benefits and limitations
        
        Explain it in simple language that someone without insurance background can understand. 
        Keep it concise (200-300 words) and use bullet points where appropriate.
        """
        
        try:
            result = self.generate_content(prompt, temperature=0.2, max_tokens=500)
            return result.get("text", "Could not generate explanation.")
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"
    
    def _calculate_extraction_stats(self, doc_info):
        """Calculate extraction statistics."""
        
        def count_filled_fields(data):
            if isinstance(data, dict):
                filled = 0
                total = 0
                for k, v in data.items():
                    if isinstance(v, (dict, list)):
                        f, t = count_filled_fields(v)
                        filled += f
                        total += t
                    else:
                        total += 1
                        if v is not None and v != "":
                            filled += 1
                return filled, total
            elif isinstance(data, list):
                if not data:
                    return 0, 1
                filled = 0
                total = 0
                for item in data:
                    if isinstance(item, (dict, list)):
                        f, t = count_filled_fields(item)
                        filled += f
                        total += t
                    else:
                        total += 1
                        if item is not None and item != "":
                            filled += 1
                return filled, total
            else:
                return 0, 0
        
        filled, total = count_filled_fields(doc_info)
        if total == 0:
            percentage = 0
        else:
            percentage = (filled / total) * 100
        
        return {
            "total_fields": total,
            "filled_fields": filled,
            "percentage": percentage
        }