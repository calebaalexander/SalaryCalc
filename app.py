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

def calculate_detailed_budget(monthly_income):
    # Define category percentages
    needs_breakdown = {
        "Housing (Rent/Mortgage)": 0.15,
        "Utilities": 0.05,
        "Groceries": 0.08,
        "Transportation": 0.06,
        "Insurance": 0.05,
        "Healthcare": 0.04,
        "Minimum Debt Payments": 0.04,
        "Childcare/Education": 0.03
    }
    
    wants_breakdown = {
        "Dining Out": 0.06,
        "Entertainment": 0.06,
        "Travel": 0.06,
        "Hobbies": 0.04,
        "Shopping": 0.05,
        "Luxury Upgrades": 0.03
    }
    
    savings_breakdown = {
        "Emergency Fund": 0.06,
        "Retirement": 0.06,
        "Investments": 0.03,
        "Debt Repayment": 0.03,
        "Future Goals": 0.02
    }
    
    # Calculate amounts for each category
    budget_data = {
        'Category': [],
        'Main Category': [],
        'Amount': [],
        'Percentage': []
    }
    
    # Add needs
    for category, percentage in needs_breakdown.items():
        budget_data['Category'].append(category)
        budget_data['Main Category'].append('Needs')
        budget_data['Amount'].append(monthly_income * percentage)
        budget_data['Percentage'].append(percentage * 100)
    
    # Add wants
    for category, percentage in wants_breakdown.items():
        budget_data['Category'].append(category)
        budget_data['Main Category'].append('Wants')
        budget_data['Amount'].append(monthly_income * percentage)
        budget_data['Percentage'].append(percentage * 100)
    
    # Add savings
    for category, percentage in savings_breakdown.items():
        budget_data['Category'].append(category)
        budget_data['Main Category'].append('Savings')
        budget_data['Amount'].append(monthly_income * percentage)
        budget_data['Percentage'].append(percentage * 100)
    
    return pd.DataFrame(budget_data)

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
        fig = px.pie(breakdown_df, values='Amount', names='Category', 
                    title='Salary Breakdown')
        st.plotly_chart(fig)

    # Detailed Budget Planning
    st.header("Detailed Budget Planning")
    budget_df = calculate_detailed_budget(take_home_monthly)
    
    # Summary by main category
    summary_df = budget_df.groupby('Main Category').agg({
        'Amount': 'sum',
        'Percentage': 'sum'
    }).reset_index()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Budget Summary")
        st.dataframe(summary_df.style.format({
            'Amount': '${:,.2f}',
            'Percentage': '{:.1f}%'
        }))
    
    with col4:
        summary_fig = px.pie(summary_df, values='Amount', names='Main Category', 
                           title='Budget Distribution')
        st.plotly_chart(summary_fig)

    # Detailed Budget Breakdown
    st.subheader("Detailed Monthly Budget Breakdown")
    
    # Create tabs for each main category
    needs_tab, wants_tab, savings_tab = st.tabs(["Needs (50%)", "Wants (30%)", "Savings (20%)"])
    
    with needs_tab:
        needs_df = budget_df[budget_df['Main Category'] == 'Needs']
        st.dataframe(needs_df[['Category', 'Amount', 'Percentage']].style.format({
            'Amount': '${:,.2f}',
            'Percentage': '{:.1f}%'
        }))
        
        needs_fig = px.pie(needs_df, values='Amount', names='Category', 
                          title='Needs Breakdown')
        st.plotly_chart(needs_fig)
    
    with wants_tab:
        wants_df = budget_df[budget_df['Main Category'] == 'Wants']
        st.dataframe(wants_df[['Category', 'Amount', 'Percentage']].style.format({
            'Amount': '${:,.2f}',
            'Percentage': '{:.1f}%'
        }))
        
        wants_fig = px.pie(wants_df, values='Amount', names='Category', 
                          title='Wants Breakdown')
        st.plotly_chart(wants_fig)
    
    with savings_tab:
        savings_df = budget_df[budget_df['Main Category'] == 'Savings']
        st.dataframe(savings_df[['Category', 'Amount', 'Percentage']].style.format({
            'Amount': '${:,.2f}',
            'Percentage': '{:.1f}%'
        }))
        
        savings_fig = px.pie(savings_df, values='Amount', names='Category', 
                           title='Savings Breakdown')
        st.plotly_chart(savings_fig)

    # Budget Tips
    with st.expander("💡 Budgeting Tips"):
        st.markdown("""
        ### Tips for Managing Your Budget:
        
        #### Needs (50%):
        - Consider house-hacking or getting a roommate to reduce housing costs
        - Look for utility savings through energy-efficient upgrades
        - Use meal planning to optimize grocery spending
        - Consider public transportation or carpooling options
        
        #### Wants (30%):
        - Use cashback cards for dining and entertainment
        - Look for travel deals during off-peak seasons
        - Consider monthly memberships for frequent activities
        - Create a shopping list and stick to it
        
        #### Savings (20%):
        - Set up automatic transfers to your savings accounts
        - Take full advantage of employer 401(k) matching
        - Consider index funds for long-term investments
        - Build emergency fund before focusing on extra debt payments
        """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="SalaryCalc",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
