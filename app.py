import streamlit as st
import pandas as pd
biolume_df = pd.read_csv('All - All.csv')
biolume_df['Order Date'] = pd.to_datetime(biolume_df['Order Date'], format='%d-%m-%Y', errors='coerce')

# Function to generate sales report with metrics and category breakdown
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
        total_sales=('Order Value', 'sum'),    # Total sales per month
        average_sales=('Order Value', 'mean')  # Average sales per month
    ).reset_index()

    # Count the number of repeated shops per month (excluding the first month of each shop)
    repeated_shops_per_month = unique_orders_after_first.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='repeated_shops')

    # Count the number of new shops per month
    new_shops_per_month = new_shops.groupby('Year-Month')['Shop Name'].nunique().reset_index(name='new_shops')

    # Merge all results into a single report
    final_report = pd.merge(report, repeated_shops_per_month, on='Year-Month', how='left')
    final_report = pd.merge(final_report, new_shops_per_month, on='Year-Month', how='left')
    final_report.fillna(0, inplace=True)

    # Sales Metrics Calculation
    total_sales = filtered_df['Order Value'].sum()
    average_sales = filtered_df['Order Value'].mean()

    # Repeat Order Sales
    repeat_orders = merged_df[merged_df['Order Date'] > merged_df['Order Date_first']]
    repeat_order_total_sales = repeat_orders['Order Value'].sum()
    average_repeat_order_sales = repeat_orders['Order Value'].mean() if not repeat_orders.empty else 0

    # New Shop Sales
    new_sales = new_shops['Order Value'].sum()
    average_new_sales = new_shops['Order Value'].mean() if not new_shops.empty else 0

    # Calculate monthly total and average monthly sales
    monthly_sales = filtered_df.groupby(filtered_df['Year-Month'])['Order Value'].sum().reset_index(name='monthly_sales')
    avg_monthly_sales = monthly_sales['monthly_sales'].mean()

    # Metrics Table
    sales_metrics = {
        'Total Sales': [total_sales],
        'Average Sales': [average_sales],
        'Repeat Order Total Sales': [repeat_order_total_sales],
        'Average Repeat Order Sales': [average_repeat_order_sales],
        'New Sales': [new_sales],
        'Average New Sales': [average_new_sales],
        'Average Monthly Sales': [avg_monthly_sales]
    }

    sales_metrics_df = pd.DataFrame(sales_metrics)

    # Shop Category Breakdown
    repeated_shop_names = repeat_orders['Shop Name'].unique()
    new_shop_names = new_shops['Shop Name'].unique()

    shop_categories = pd.DataFrame({
        'Shop Name': pd.concat([pd.Series(repeated_shop_names), pd.Series(new_shop_names)], ignore_index=True).drop_duplicates(),
        'Category': pd.concat([pd.Series(['Repeat'] * len(repeated_shop_names)), pd.Series(['New'] * len(new_shop_names))], ignore_index=True)
    })

    # Display the report in Streamlit
    st.write(f"Sales Report for Employee: {employee_name}")
    st.dataframe(final_report)

    # Display Sales Metrics
    st.write("Sales Metrics")
    st.dataframe(sales_metrics_df)

    # Display Monthly Sales Data
    st.write("Monthly Sales")
    st.dataframe(monthly_sales)

    # Display Shop Category Breakdown
    st.write("Shop Category Breakdown")
    st.dataframe(shop_categories)

# Streamlit App UI
st.title("Employee Sales Report")

# Dropdown for employee selection
employee_names = biolume_df['Employee Name'].unique()
selected_employee = st.selectbox('Select an Employee:', employee_names)

# Button to generate the report
if st.button('Generate Report'):
    generate_sales_report(selected_employee)
