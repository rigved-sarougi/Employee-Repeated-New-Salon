import streamlit as st
import pandas as pd

# Load data
@st.cache
def load_data():
    # Load your data here
    return pd.read_csv('All - All.csv', parse_dates=['Order Date'])

biolume_df = load_data()

def generate_sales_report(employee_name):
    filtered_df = biolume_df[biolume_df['Employee Name'] == employee_name]

    if filtered_df.empty:
        return pd.DataFrame(), "No data found for employee: " + employee_name

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
    return final_report, ""

def main():
    st.title("Sales Report Generator")

    employee_names = biolume_df['Employee Name'].unique()
    employee_name = st.selectbox("Select an Employee", employee_names)

    if st.button("Generate Report"):
        report, error_message = generate_sales_report(employee_name)
        if error_message:
            st.error(error_message)
        else:
            st.write(f"Sales Report for Employee: {employee_name}")
            st.dataframe(report)

if __name__ == "__main__":
    main()
