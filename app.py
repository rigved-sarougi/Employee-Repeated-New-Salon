import streamlit as st
import pandas as pd

biolume_df = pd.read_csv('All - All.csv')

# Ensure 'Order Date' is in datetime format
biolume_df['Order Date'] = pd.to_datetime(biolume_df['Order Date'], format='%d-%m-%Y', errors='coerce')

# Function to generate the sales report
def generate_sales_report(employee_name):
    # Filter data by Employee Name
    filtered_df = biolume_df[biolume_df['Employee Name'] == employee_name]

    if filtered_df.empty:
        st.write(f"No data found for employee: {employee_name}")
        return

    # Extract the year-month for easier grouping
    filtered_df['Year-Month'] = filtered_df['Order Date'].dt.to_period('M')

    # Find the first order date (month) for each shop
    first_order_date = filtered_df.groupby('Shop Name')['Order Date'].min().reset_index()

    # Merge the first order date back with the original dataframe
    merged_df = pd.merge(filtered_df, first_order_date, on='Shop Name', suffixes=('', '_first'))

    # Identify new shops: where the order date matches their first order date
    new_shops = merged_df[merged_df['Order Date'] == merged_df['Order Date_first']]

    # Identify repeated shops: shops with more than one unique order
    unique_orders = filtered_df.drop_duplicates(subset=['Shop Name', 'Order Date'])
    unique_orders_after_first = unique_orders[unique_orders['Year-Month'] > unique_orders['Shop Name'].map(first_order_date.set_index('Shop Name')['Order Date'].dt.to_period('M'))]

    # Generate the report
    report = filtered_df.groupby('Year-Month').agg(
        total_shops=('Shop Name', 'nunique'),  # Total unique shops where sales happened
    ).reset_index()

    # Count the number of repeated shops per month (excluding the first month of each shop)
    repeated_shops_per_month = unique_orders_after_first.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='repeated_shops')

    # Count the number of new shops per month
    new_shops_per_month = new_shops.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='new_shops')

    # Merge all results into a single report
    final_report = pd.merge(report, repeated_shops_per_month, on='Year-Month', how='left')
    final_report = pd.merge(final_report, new_shops_per_month, on='Year-Month', how='left')

    # Fill NaN values with 0 (for months where no new or repeated shops exist)
    final_report.fillna(0, inplace=True)

    # Display the report in Streamlit
    st.write(f"Sales Report for Employee: {employee_name}")
    st.dataframe(final_report)

# Streamlit App UI
st.title("Employee Sales Report")

# Dropdown for employee selection
employee_names = biolume_df['Employee Name'].unique()
selected_employee = st.selectbox('Select an Employee:', employee_names)

# Button to generate the report
if st.button('Generate Report'):
    generate_sales_report(selected_employee)
