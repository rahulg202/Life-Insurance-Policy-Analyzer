def detect_policy_type(doc_info):
    """Detect the type of insurance policy from extracted information."""
    
    # Check for specific keywords in plan name, annuity option, etc.
    plan_name = doc_info.get("policy_identification", {}).get("plan_name", "") or ""
    plan_name = str(plan_name).lower()
    
    annuity_option = doc_info.get("annuity_benefits", {}).get("annuity_option", "") or ""
    annuity_option = str(annuity_option).lower()
    
    plan_type = doc_info.get("policy_identification", {}).get("plan_type", "") or ""
    plan_type = str(plan_type).lower()
    
    uin = doc_info.get("policy_identification", {}).get("uin", "") or ""
    uin = str(uin).lower()
    
    # Check for specific phrases in death benefits or maturity benefits
    death_benefits = doc_info.get("annuity_benefits", {}).get("death_benefits", "") or ""
    death_benefits = str(death_benefits).lower()
    
    maturity_benefits = doc_info.get("annuity_benefits", {}).get("maturity_benefits", "") or ""
    maturity_benefits = str(maturity_benefits).lower()
    
    # Insurer name can also provide clues
    insurer_name = doc_info.get("policy_identification", {}).get("insurer_name", "") or ""
    insurer_name = str(insurer_name).lower()
    
    # Using a weighted approach to determine policy type
    policy_type_score = {
        "Term Insurance": 0,
        "Endowment Policy": 0,
        "Unit Linked Insurance Plan (ULIP)": 0,
        "Pension/Annuity Plan": 0,
        "Whole Life Policy": 0,
        "Money Back Policy": 0,
        "Guaranteed Savings Plan": 0
    }
    
    # Check for Term Insurance indicators
    if any(term in plan_name for term in ["term", "protection", "shield", "secure"]) or "term" in plan_type:
        policy_type_score["Term Insurance"] += 3
    if "term" in plan_type:
        policy_type_score["Term Insurance"] += 2
    if "pure risk cover" in death_benefits or "only death benefit" in death_benefits:
        policy_type_score["Term Insurance"] += 2
    
    # Check for HDFC Life Guaranteed Savings Plan
    if "guaranteed savings" in plan_name or "101n131" in uin:
        policy_type_score["Guaranteed Savings Plan"] += 4
    
    # Check for Endowment
    if any(term in plan_name for term in ["endowment", "jeevan anand", "jeevan labh", "assured income"]):
        policy_type_score["Endowment Policy"] += 3
    if "endowment" in plan_type:
        policy_type_score["Endowment Policy"] += 2
    if "sum assured plus bonus" in maturity_benefits:
        policy_type_score["Endowment Policy"] += 1
    
    # Check for ULIP
    if any(term in plan_name for term in ["ulip", "unit linked", "invest"]):
        policy_type_score["Unit Linked Insurance Plan (ULIP)"] += 3
    if "ulip" in plan_type:
        policy_type_score["Unit Linked Insurance Plan (ULIP)"] += 3
    if "nav" in maturity_benefits or "fund value" in maturity_benefits or "fund value" in death_benefits:
        policy_type_score["Unit Linked Insurance Plan (ULIP)"] += 2
    
    # Check for Pension/Annuity
    if any(term in plan_name for term in ["pension", "annuity", "retirement", "vaya vandhan"]):
        policy_type_score["Pension/Annuity Plan"] += 3
    if "annuity" in annuity_option or "pension" in annuity_option:
        policy_type_score["Pension/Annuity Plan"] += 3
    if "vesting" in maturity_benefits or "purchase price" in doc_info.get("financial_details", {}):
        policy_type_score["Pension/Annuity Plan"] += 2
    if doc_info.get("financial_details", {}).get("annuity_amount"):
        policy_type_score["Pension/Annuity Plan"] += 2
    
    # Check for Whole Life
    if any(term in plan_name for term in ["whole life", "lifetime", "jeevan umang"]):
        policy_type_score["Whole Life Policy"] += 3
    if "whole life" in plan_type:
        policy_type_score["Whole Life Policy"] += 2
    if "100 years" in maturity_benefits or "100 years" in death_benefits:
        policy_type_score["Whole Life Policy"] += 2
    
    # Check for Money Back
    if any(term in plan_name for term in ["money back", "cash back", "jeevan tarang"]):
        policy_type_score["Money Back Policy"] += 3
    if "survival benefit" in maturity_benefits or "periodic payment" in maturity_benefits:
        policy_type_score["Money Back Policy"] += 2
    
    # Determine the highest scoring policy type
    max_score = 0
    detected_type = "Traditional Life Insurance"  # Default
    
    for policy_type, score in policy_type_score.items():
        if score > max_score:
            max_score = score
            detected_type = policy_type
    
    return detected_type

def get_policy_type_description(policy_type):
    """Get a detailed description of the detected policy type."""
    descriptions = {
        "Term Insurance": """
        **Term Insurance** provides pure life insurance coverage for a specified term. If the insured dies during the policy term, the death benefit is paid to the nominees. If the insured survives the term, no benefit is payable. This is the most affordable type of life insurance as it offers protection without savings or investment components.
        
        **Key Features:**
        - Pure risk coverage
        - No maturity benefit if the insured survives the policy term
        - Lower premiums compared to other life insurance products
        - Options for additional riders like critical illness, accidental death, etc.
        """,
        
        "Endowment Policy": """
        **Endowment Policy** provides both insurance protection and savings. If the insured dies during the policy term, the death benefit is paid to the nominees. If the insured survives the policy term, the sum assured along with bonuses (if applicable) is paid as maturity benefit.
        
        **Key Features:**
        - Life insurance coverage with savings component
        - Guaranteed maturity benefit
        - Bonus additions based on insurer's performance (in participating policies)
        - Higher premiums compared to term insurance
        - Option for paid-up value and surrender value
        """,
        
        "Unit Linked Insurance Plan (ULIP)": """
        **Unit Linked Insurance Plan (ULIP)** combines insurance protection with investment. Part of the premium is used for insurance coverage, and the rest is invested in various funds as chosen by the policyholder. The investment risk is borne by the policyholder.
        
        **Key Features:**
        - Life insurance coverage with market-linked investment
        - Option to choose from various fund options (equity, debt, balanced, etc.)
        - Flexibility to switch between funds
        - Transparent charge structure
        - Lock-in period of 5 years
        - Tax benefits on premium paid and maturity amount
        """,
        
        "Pension/Annuity Plan": """
        **Pension/Annuity Plan** is designed to provide regular income during retirement. These plans typically have two phases: accumulation (where you build a corpus) and vesting (where you start receiving pension). After vesting, the purchase price is used to buy an annuity that provides regular income.
        
        **Key Features:**
        - Regular income post-retirement
        - Option for joint life annuity
        - Various annuity options (immediate, deferred, etc.)
        - Tax benefits on investment
        - Limited liquidity before vesting
        - Option for return of purchase price to nominees upon death
        """,
        
        "Whole Life Policy": """
        **Whole Life Policy** provides life insurance coverage for the entire lifetime of the insured, not just for a specific term. It typically offers a savings component in addition to death benefit. Premiums are usually payable for a specific period or until a certain age.
        
        **Key Features:**
        - Lifelong insurance coverage
        - Savings or cash value component that grows over time
        - Bonuses or dividends in participating policies
        - Option for paid-up value and surrender value
        - Higher premiums compared to term insurance
        - Estate planning and wealth transfer benefits
        """,
        
        "Money Back Policy": """
        **Money Back Policy** is a variant of endowment plan that provides periodic survival benefits as a percentage of sum assured during the policy term. The remaining sum assured along with bonuses is paid at maturity.
        
        **Key Features:**
        - Regular payouts at specified intervals during the policy term
        - Death benefit equal to full sum assured irrespective of survival benefits already paid
        - Bonuses added to maturity benefit
        - Better liquidity compared to traditional endowment plans
        - Higher premiums compared to term insurance
        """,
        
        "Guaranteed Savings Plan": """
        **Guaranteed Savings Plan** offers guaranteed returns along with life insurance coverage. These plans typically promise a fixed return at maturity, irrespective of market performance.
        
        **Key Features:**
        - Guaranteed maturity benefit
        - Life insurance coverage
        - Fixed returns irrespective of market performance
        - No participation in insurer's profits (usually non-participating)
        - Better suited for conservative investors
        - Option for paid-up value and surrender value
        """,
        
        "Traditional Life Insurance": """
        **Traditional Life Insurance** offers both protection and savings benefits. The policy pays a death benefit if the insured dies during the policy term, and a maturity benefit if the insured survives the term.
        
        **Key Features:**
        - Life insurance coverage with savings component
        - Bonuses in participating policies
        - Lower risk compared to market-linked products
        - Option for paid-up value and surrender value
        - Relatively stable returns
        """,
    }
    
    return descriptions.get(policy_type, descriptions["Traditional Life Insurance"])