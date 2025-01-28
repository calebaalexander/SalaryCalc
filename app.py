import streamlit as st
import pandas as pd
import plotly.express as px
import math

def round_to_nearest(number):
    return int(round(number))

def calculate_taxes(salary, marital_status, allowances):
    # 2024 Federal Tax Brackets
    single_brackets = [
        (11600, 0.10),    # Standard deduction for single
        (44725, 0.12),
        (95375, 0.22),
        (182100, 0.24),
        (231250, 0.32),
        (578125, 0.35),
        (float('inf'), 0.37)
    ]
    
    married_brackets = [
        (23200, 0.10),    # Standard deduction for married
        (89450, 0.12),
        (190750, 0.22),
        (364200, 0.24),
        (462500, 0.32),
        (693750, 0.35),
        (float('inf'), 0.37)
    ]
    
    brackets = married_brackets if marital_status == "Married" else single_brackets
    standard_deduction = 23200 if marital_status == "Married" else 11600
    
    # Calculate federal tax using progressive brackets
    federal_tax = 0
    prev_bracket = 0
    taxable_income = max(salary - standard_deduction, 0)  # Apply standard deduction
    
    for bracket, rate in brackets:
        if taxable_income > prev_bracket:
            taxable_amount = min(taxable_income - prev_bracket, bracket - prev_bracket)
            federal_tax += taxable_amount * rate
        prev_bracket = bracket
    
    # Adjust for allowances
    federal_tax = round_to_nearest(federal_tax * (1 - 0.1 * allowances['federal']))
    
    # State and local taxes (simplified - could be enhanced with state-specific brackets)
    state_tax_rate = 0.05
    local_tax_rate = 0.01
    
    state_tax = round_to_nearest(salary * state_tax_rate * (1 - 0.1 * allowances['state']))
    local_tax = round_to_nearest(salary * local_tax_rate * (1 - 0.1 * allowances['local']))
    
    # Return total taxes
    return federal_tax + state_tax + local_tax
    
    return federal_tax + state_tax + local_tax

def calculate_fica(salary):
    social_security_rate = 0.062
    medicare_rate = 0.0145
    
    social_security = round_to_nearest(min(salary * social_security_rate, 9932.40))
    medicare = round_to_nearest(salary * medicare_rate)
    
    return social_security + medicare

def main():
    st.markdown("# **Salary & Budget Calculator**")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("WORK INFO")
        
        # Marital Status
        st.subheader("Marital Status")
        marital_status = st.radio("", ("Single", "Married"), horizontal=True)
        
        # Job Section
        st.subheader("JOB")
        location = st.text_input("Location (ZIP Code)", "12051")
        pay_type = st.radio("Type", ("Salary", "Hourly"), horizontal=True)
        pay_frequency = st.selectbox("Pay Frequency", ["Monthly", "Semi-Monthly", "Bi-weekly", "Weekly"], index=0)
        
        # Allowances
        st.subheader("Allowances")
        fed_allowances = st.number_input("Federal", min_value=0, value=1)
        state_allowances = st.number_input("State", min_value=0, value=1)
        local_allowances = st.number_input("Local", min_value=0, value=0)
        
        allowances = {
            'federal': fed_allowances,
            'state': state_allowances,
            'local': local_allowances
        }
        
        is_tax_exempt = st.radio("Are you exempt from any taxes?", ("No", "Yes"), horizontal=True) == "Yes"

    # Main content
    if pay_type == "Salary":
        salary = st.number_input("Salary (per year)", min_value=0, value=131000)
    else:
        hourly_rate = st.number_input("Hourly Rate", min_value=0.0, value=15.0)
        hours_per_week = st.number_input("Hours per Week", min_value=0.0, value=40.0)
        salary = round_to_nearest(hourly_rate * hours_per_week * 52)

    # Calculate deductions
    if not is_tax_exempt:
        taxes = calculate_taxes(salary, marital_status, allowances)
        fica = calculate_fica(salary)
    else:
        taxes = 0
        fica = 0

    # Calculate monthly take-home
    total_deductions = taxes + fica
    take_home = salary - total_deductions
    monthly_take_home = round_to_nearest(take_home / 12)

    # Display results
    st.header("Your estimated monthly take home pay:")
    st.subheader(f"${monthly_take_home:,}")

    # Detailed Monthly Budget Breakdown
    st.header("Detailed Monthly Budget Breakdown")

    # Define category percentages and amounts
    budget_categories = {
        "Needs": {
            "Housing (Rent/Mortgage)": 15,
            "Utilities": 5,
            "Groceries": 8,
            "Transportation": 6,
            "Insurance": 5,
            "Healthcare": 4,
            "Minimum Debt Payments": 4,
            "Childcare/Education": 3
        },
        "Wants": {
            "Dining Out": 6,
            "Entertainment": 6,
            "Travel": 6,
            "Hobbies": 4,
            "Shopping": 5,
            "Luxury Upgrades": 3
        },
        "Savings": {
            "Emergency Fund": 6,
            "Retirement": 6,
            "Investments": 3,
            "Debt Repayment": 3,
            "Future Goals": 2
        }
    }

    tabs = st.tabs(["Needs (50%)", "Wants (30%)", "Savings (20%)"])
    
    for idx, (category, subcategories) in enumerate(budget_categories.items()):
        with tabs[idx]:
            data = {
                'Category': [],
                'Amount': [],
                'Percentage': []
            }
            
            for subcategory, percentage in subcategories.items():
                amount = round_to_nearest(monthly_take_home * percentage / 100)
                data['Category'].append(subcategory)
                data['Amount'].append(amount)
                data['Percentage'].append(percentage)
            
            df = pd.DataFrame(data)
            
            # Display data table
            st.dataframe(
                df.style.format({
                    'Amount': '${:,}',
                    'Percentage': '{}%'
                }),
                hide_index=True
            )
            
            # Display pie chart
            fig = px.pie(
                df,
                values='Amount',
                names='Category',
                title=f'{category} Breakdown'
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    st.set_page_config(
        page_title="SalaryCalc",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
