import pandas as pd
import streamlit as st

# Assuming biolume_df is your dataframe
# Replace this with how you load the actual data
# biolume_df = pd.read_csv('your_data.csv')

# Function to generate the sales report
def generate_sales_report(employee_name):
    # Filter data by Employee Name
    filtered_df = biolume_df[biolume_df['Employee Name'] == employee_name]

    if filtered_df.empty:
        st.write(f"No data found for employee: {employee_name}")
        return

    # Ensure 'Order Date' is in datetime format
    filtered_df['Order Date'] = pd.to_datetime(filtered_df['Order Date'], errors='coerce')

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
    
    # Ensure that the repeated orders are from months *after* the shop's first order month
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

    # Display the report
    st.write(f"Sales Report for Employee: {employee_name}")
    st.dataframe(final_report)

# Streamlit app interface
def choose_employee_and_generate_report():
    # List all unique employee names
    employee_names = biolume_df['Employee Name'].unique()

    # Create a dropdown for employee selection
    employee_name = st.selectbox("Select an employee", employee_names)

    if st.button("Generate Report"):
        generate_sales_report(employee_name)

# Streamlit app main function
def main():
    st.title("Sales Report Generator")

    # Load your dataframe (replace with actual data loading logic)
    global biolume_df
    # For example, load data from a CSV file
    biolume_df = pd.read_csv('All - All.csv')


    choose_employee_and_generate_report()

# Run the Streamlit app
if __name__ == "__main__":
    main()
