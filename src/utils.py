import re

def get_address_from_url(url:str) -> str:
    match = re.search(r'/homedetails/([^/]+)/', url)
    if match:
        parts = match.group(1)
        address = parts.split('-Chicago-IL')[0]
        address = address.replace('-', ' ')
        return(address)  # 1519-N-Milwaukee-Ave-APT-2F-Chicago-IL-60622
    else:
        return('Could not find address from url. Update manually.')

def calc_monthly_payment_est(
    loan_amount:float,
    annual_interest_rate:float,
    annual_property_tax:float,
    annual_insurance:float,
    annual_pmi:float,
    monthly_hoa:float) -> dict:

    monthly_interest_rate = annual_interest_rate / 100 / 12
    num_payments = 360

    # Principal & Interest (P&I) using mortgage formula
    if monthly_interest_rate > 0:
        monthly_principal_interest = (
            loan_amount *
            (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) /
            ((1 + monthly_interest_rate) ** num_payments - 1)
        )
    else:
        monthly_principal_interest = loan_amount / num_payments  # No interest case

    # Monthly extras
    monthly_property_tax = annual_property_tax / 12
    monthly_insurance = annual_insurance / 12
    monthly_pmi = annual_pmi / 12

    total_monthly_payment = int(
        monthly_principal_interest +
        monthly_property_tax +
        monthly_insurance +
        monthly_pmi +
        monthly_hoa
    )

    return {
        "principal_interest": monthly_principal_interest,
        "property_tax": monthly_property_tax,
        "insurance": monthly_insurance,
        "pmi": monthly_pmi,
        "hoa": monthly_hoa,
        "total": total_monthly_payment
    }