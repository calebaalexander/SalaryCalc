import streamlit as st
import pandas as pd
import plotly.express as px

def calculate_taxes(salary, marital_status, allowances):
    # Simplified tax calculation (you may want to add more detailed tax brackets)
    federal_tax_rate = 0.22  # Example rate
    state_tax_rate = 0.05    # Example rate
    local_tax_rate = 0.01    # Example rate
    
    federal_tax = salary * federal_tax_rate * (1 - 0.1 * allowances['federal'])
    state_tax = salary * state_tax_rate * (1 - 0.1 * allowances['state'])
    local_tax = salary * local_tax_rate * (1 - 0.1 * allowances['local'])
    
    return federal_tax + state_tax + local_tax

def calculate_fica(salary):
    social_security_rate = 0.062
    medicare_rate = 0.0145
    
    social_security = min(salary * social_security_rate, 9932.40)  # 2024 cap
    medicare = salary * medicare_rate
    
    return social_security + medicare

def calculate_budget(take_home_pay):
    monthly_income = take_home_pay / 12
    
    # 50/30/20 Rule
    necessities = monthly_income * 0.5
    wants = monthly_income * 0.3
    savings = monthly_income * 0.2
    
    budget_breakdown = {
        'Category': ['Necessities', 'Wants', 'Savings'],
        'Amount': [necessities, wants, savings],
        'Percentage': [50, 30, 20]
    }
    
    return pd.DataFrame(budget_breakdown)

def main():
    st.title("SalaryCalc - Salary & Budget Calculator")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("WORK INFO")
        
        # Marital Status
        st.subheader("Marital Status")
        marital_status = st.radio("", ("Single", "Married"), horizontal=True)
        
        # Job Section
        st.subheader("JOB")
        
        # Location
        location = st.text_input("Location (ZIP Code)", "12051")
        
        # Pay Type and Frequency
        pay_type = st.radio("Type", ("Hourly", "Salary"), horizontal=True)
        pay_frequency = st.selectbox("Pay Frequency", ["Monthly", "Bi-weekly", "Weekly"])
        
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
        
        # Tax Exempt Status
        is_tax_exempt = st.radio("Are you exempt from any taxes?", ("No", "Yes"), horizontal=True) == "Yes"

    # Main content
    if pay_type == "Salary":
        salary = st.number_input("Salary (per year)", min_value=0, value=131000)
    else:
        hourly_rate = st.number_input("Hourly Rate", min_value=0.0, value=15.0)
        hours_per_week = st.number_input("Hours per Week", min_value=0.0, value=40.0)
        salary = hourly_rate * hours_per_week * 52

    # Calculate deductions
    if not is_tax_exempt:
        taxes = calculate_taxes(salary, marital_status, allowances)
        fica = calculate_fica(salary)
    else:
        taxes = 0
        fica = 0

    # Calculate take-home pay
    gross_monthly = salary / 12
    total_deductions = taxes + fica
    take_home = salary - total_deductions
    take_home_monthly = take_home / 12

    # Display results
    st.header("Your estimated monthly take home pay:")
    st.subheader(f"${take_home_monthly:,.2f}")

    # Where is your money going?
    st.header("Where is your money going?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        breakdown_data = {
            'Category': ['Taxes', 'FICA and State Insurance Taxes', 'Take Home Salary'],
            'Percentage': [
                (taxes/salary)*100,
                (fica/salary)*100,
                (take_home/salary)*100
            ],
            'Amount': [taxes, fica, take_home]
        }
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df.style.format({
            'Percentage': '{:.2f}%',
            'Amount': '${:,.2f}'
        }))

    with col2:
        fig = px.pie(breakdown_df, values='Amount', names='Category', title='Salary Breakdown')
        st.plotly_chart(fig)

    # Budget Planning (50/30/20 Rule)
    st.header("Budget Planning (50/30/20 Rule)")
    budget_df = calculate_budget(take_home)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.dataframe(budget_df.style.format({
            'Amount': '${:,.2f}',
            'Percentage': '{:.0f}%'
        }))
    
    with col4:
        budget_fig = px.pie(budget_df, values='Amount', names='Category', 
                          title='Recommended Budget Allocation')
        st.plotly_chart(budget_fig)

    # Budget Details
    st.subheader("Suggested Monthly Budget Breakdown")
    
    with st.expander("Necessities (50%)"):
        st.write("""
        - 🏠 Housing (30%): ${:,.2f}
        - 🥘 Groceries (10%): ${:,.2f}
        - 🚗 Transportation (5%): ${:,.2f}
        - 💊 Healthcare (5%): ${:,.2f}
        """.format(
            take_home_monthly * 0.3,
            take_home_monthly * 0.1,
            take_home_monthly * 0.05,
            take_home_monthly * 0.05
        ))
    
    with st.expander("Wants (30%)"):
        st.write("""
        - 🎭 Entertainment (10%): ${:,.2f}
        - 🛍️ Shopping (10%): ${:,.2f}
        - 🍽️ Dining Out (5%): ${:,.2f}
        - 🏋️ Health & Fitness (5%): ${:,.2f}
        """.format(
            take_home_monthly * 0.1,
            take_home_monthly * 0.1,
            take_home_monthly * 0.05,
            take_home_monthly * 0.05
        ))
    
    with st.expander("Savings (20%)"):
        st.write("""
        - 💰 Emergency Fund (10%): ${:,.2f}
        - 📈 Investments (5%): ${:,.2f}
        - 🎯 Financial Goals (5%): ${:,.2f}
        """.format(
            take_home_monthly * 0.1,
            take_home_monthly * 0.05,
            take_home_monthly * 0.05
        ))

if __name__ == "__main__":
    st.set_page_config(page_title="SalaryCalc", page_icon="💰", layout="wide")
    main()
