import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(page_title="Customer Order Analytics Dashboard", layout="wide")

st.title("Customer Order Analytics Dashboard")

# ------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------

st.sidebar.header("Upload Excel File")

uploaded_file = st.sidebar.file_uploader(
    "Upload customer order Excel file",
    type=["xlsx", "xls"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to start the dashboard.")
    st.stop()

df = pd.read_excel(uploaded_file)

# ------------------------------------------------
# CLEAN COLUMN NAMES
# ------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[^\w]+", "_", regex=True)
)

# ------------------------------------------------
# DATA TYPE CONVERSION
# ------------------------------------------------

if "phone_no_" in df.columns:
    df = df.rename(columns={"phone_no_": "phone_no"})

df["doa"] = pd.to_datetime(df["doa"], errors="coerce")
df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# ------------------------------------------------
# PRODUCT COLUMNS
# ------------------------------------------------

product_columns = [
    "blueberries",
    "raspberries",
    "strawberry",
    "cherry",
    "frozen_blueberry",
    "frozen_strawberries",
    "darima_chilli_bomb",
    "darima_zarai",
    "darima_mild_cheddar",
    "darima_farmhouse_cheddar",
    "darima_gouda_cheese",
    "darima_alpine_gruyere_cheese"
]

for col in product_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------

st.sidebar.header("Filters")

search_customer = st.sidebar.text_input("Search Customer Name")
search_phone = st.sidebar.text_input("Search Phone Number")

min_date = df["doa"].min()
max_date = df["doa"].max()

date_range = st.sidebar.date_input(
    "Order Date Range",
    [min_date, max_date]
)

filtered_df = df.copy()

# Filter by customer name
if search_customer:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search_customer, case=False, na=False)
    ]

# Filter by phone number
if search_phone:
    filtered_df = filtered_df[
        filtered_df["phone_no"].astype(str).str.contains(search_phone, na=False)
    ]

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["doa"] >= pd.to_datetime(start_date)) &
        (filtered_df["doa"] <= pd.to_datetime(end_date))
    ]

# ------------------------------------------------
# KPI METRICS
# ------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", filtered_df["phone_no"].nunique())
col2.metric("Total Orders", len(filtered_df))
col3.metric("Total Revenue", f"₹{filtered_df['amount'].sum():,.0f}")

# ------------------------------------------------
# CUSTOMER SUMMARY
# ------------------------------------------------

today = pd.Timestamp(datetime.today().date())

summary = (
    filtered_df.groupby(["name", "phone_no", "location"])
    .agg(
        first_order_date=("doa", "min"),
        last_order_date=("delivery_date", "max"),
        total_sales=("amount", "sum")
    )
    .reset_index()
)
summary["days_since_last_order"] = (
    today - summary["last_order_date"]
).dt.days

st.subheader("Customer Summary")

st.dataframe(
    summary.rename(columns={
        "name": "Customer Name",
        "phone_no": "Phone Number",
        "location": "Location",
        "first_order_date": "First Order Date",
        "last_order_date": "Last Order Date",
        "total_sales": "Total Sales",
        "days_since_last_order": "Days Since Last Order"
    }),
    use_container_width=True
)


# ------------------------------------------------
# DOWNLOAD FILTERED DATA
# ------------------------------------------------

st.subheader("Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_customer_orders.csv",
    mime="text/csv"
)


# ------------------------------------------------
# TOP SELLING PRODUCTS
# ------------------------------------------------

available_products = [col for col in product_columns if col in filtered_df.columns]

product_sales = filtered_df[available_products].sum().sort_values(ascending=False)

st.subheader("Top Selling Products")

product_df = product_sales.reset_index()
product_df.columns = ["Product", "Units Sold"]

fig = px.bar(
    product_df,
    x="Product",
    y="Units Sold",
    color="Units Sold",
    color_continuous_scale="viridis",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# REVENUE BY PRODUCT
# ------------------------------------------------

st.subheader("Revenue by Product")

total_units = product_sales.sum()
total_revenue = filtered_df["amount"].sum()

product_revenue = (product_sales / total_units) * total_revenue

rev_df = product_revenue.reset_index()
rev_df.columns = ["Product", "Revenue"]

fig = px.bar(
    rev_df,
    x="Product",
    y="Revenue",
    color="Revenue",
    color_continuous_scale="plasma",
    height=400
)

st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------------
# MONTHLY SALES TREND
# ------------------------------------------------

st.subheader("Monthly Sales Trend")

filtered_df["month"] = filtered_df["doa"].dt.to_period("M").astype(str)

monthly_sales = (
    filtered_df.groupby("month")["amount"]
    .sum()
    .reset_index()
)

fig = px.line(
    monthly_sales,
    x="month",
    y="amount",
    markers=True
)

fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# REPEAT VS NEW CUSTOMERS
# ------------------------------------------------

st.subheader("Repeat vs New Customers")

customer_orders = filtered_df.groupby("phone_no").size()

repeat_customers = (customer_orders > 1).sum()
new_customers = (customer_orders == 1).sum()

freq_df = pd.DataFrame({
    "Customer Type": ["New Customers", "Repeat Customers"],
    "Count": [new_customers, repeat_customers]
})

fig = px.pie(freq_df, names="Customer Type", values="Count", hole=0.4)

st.plotly_chart(fig, use_container_width=True)

