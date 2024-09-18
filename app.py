import streamlit as st
import pandas as pd

# Use st.cache_data for caching data loading
@st.cache_data
def load_data():
    # Load your DataFrame here
    # For example: return pd.read_csv('path_to_your_file.csv')
    return pd.read_csv('All - All.csv')  # Replace with the actual file path or data loading method

biolume_df = load_data()

def generate_sales_report(employee_name):
    filtered_df = biolume_df[biolume_df['Employee Name'] == employee_name]

    if filtered_df.empty:
        st.write(f"No data found for employee: {employee_name}")
        return

    filtered_df['Year-Month'] = filtered_df['Order Date'].dt.to_period('M')
    first_order_date = filtered_df.groupby('Shop Name')['Order Date'].min().reset_index()
    merged_df = pd.merge(filtered_df, first_order_date, on='Shop Name', suffixes=('', '_first'))
    new_shops = merged_df[merged_df['Order Date'] == merged_df['Order Date_first']]
    unique_orders = filtered_df.drop_duplicates(subset=['Shop Name', 'Order Date'])
    unique_orders_after_first = unique_orders[unique_orders['Year-Month'] > unique_orders['Shop Name'].map(first_order_date.set_index('Shop Name')['Order Date'].dt.to_period('M'))]

    report = filtered_df.groupby('Year-Month').agg(
        total_shops=('Shop Name', 'nunique'),
    ).reset_index()

    repeated_shops_per_month = unique_orders_after_first.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='repeated_shops')
    new_shops_per_month = new_shops.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='new_shops')

    final_report = pd.merge(report, repeated_shops_per_month, on='Year-Month', how='left')
    final_report = pd.merge(final_report, new_shops_per_month, on='Year-Month', how='left')
    final_report.fillna(0, inplace=True)

    st.write(f"Sales Report for Employee: {employee_name}")
    st.write(final_report)

# Streamlit App Layout
st.title("Sales Report Generator")

employee_names = biolume_df['Employee Name'].unique()

# Employee selection
selected_employee = st.selectbox("Select an employee:", employee_names)

if st.button("Generate Report"):
    generate_sales_report(selected_employee)
