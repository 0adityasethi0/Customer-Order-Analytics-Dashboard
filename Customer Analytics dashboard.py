import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(page_title="Customer Analytics Dashboard", layout="wide")

st.title("Customer Order Analytics Dashboard")

# ------------------------------------------------
# GOOGLE SHEET LINK
# ------------------------------------------------

file_url = "https://docs.google.com/spreadsheets/d/1J2yMFmakUqnF4LCZZtWoXQ-rBRk-JGvuFGxBd5-0iVs/export?format=csv&gid=0"

df = pd.read_csv(file_url)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(file_url)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "phone_no." in df.columns:
        df = df.rename(columns={"phone_no.": "phone_no"})

    # Convert dates
    df["doa"] = pd.to_datetime(df["doa"], errors="coerce")
    df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")

    # Convert numeric columns
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Product columns
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

    # Convert product columns to numeric
    for col in product_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------

st.sidebar.header("Filters")

search_customer = st.sidebar.text_input("Search Customer Name")

min_date = df["doa"].min()
max_date = df["doa"].max()

date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date])

filtered_df = df.copy()

if search_customer:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search_customer, case=False, na=False)
    ]

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

col1.metric("Total Customers", filtered_df["name"].nunique())
col2.metric("Total Orders", len(filtered_df))
col3.metric("Total Revenue", f"₹{filtered_df['amount'].sum():,.0f}")

# ------------------------------------------------
# CUSTOMER SUMMARY
# ------------------------------------------------

today = pd.Timestamp(datetime.today().date())

summary = (
    filtered_df.groupby(["name", "phone_no"])
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
        "first_order_date": "First Order Date",
        "last_order_date": "Last Order Date",
        "total_sales": "Total Sales",
        "days_since_last_order": "Days Since Last Order"
    }),
    use_container_width=True
)

# ------------------------------------------------
# PRODUCT SALES ANALYSIS
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

available_products = [col for col in product_columns if col in filtered_df.columns]

product_sales = filtered_df[available_products].sum().sort_values(ascending=False)



# ------------------------------------------------
# DOWNLOAD FILTERED DATA
# ------------------------------------------------

st.subheader("Download Data")

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

st.subheader("Top Selling Products")

product_df = product_sales.reset_index()
product_df.columns = ["Product", "Units Sold"]

fig = px.bar(
    product_df,
    x="Product",
    y="Units Sold",
    color="Units Sold",
    color_continuous_scale="viridis",
    height=350
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
    height=350
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

fig.update_layout(height=350)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# TOP 10 CUSTOMER LEADERBOARD
# ------------------------------------------------

st.subheader("Top 10 Customers")

top_customers = (
    filtered_df.groupby("name")["amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    top_customers,
    x="name",
    y="amount",
    color="amount",
    color_continuous_scale="sunset",
    height=350
)

st.plotly_chart(fig, use_container_width=True)




# ------------------------------------------------
# REVENUE BY LOCATION
# ------------------------------------------------



st.subheader("Revenue by Location")

location_sales = (
    filtered_df.groupby("location")["amount"]
    .sum()
    .reset_index()
)

fig = px.bar(
    location_sales,
    x="location",
    y="amount",
    color="amount",
    height=350
)

st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------------
# REPEAT VS NEW CUSTOMERS
# ------------------------------------------------

st.subheader("Customer Purchase Frequency")

# Count orders per phone number
customer_orders = filtered_df.groupby("phone_no").size()

# Identify repeat vs new customers
repeat_customers = (customer_orders > 1).sum()
new_customers = (customer_orders == 1).sum()

freq_df = pd.DataFrame({
    "Customer Type": ["New Customers", "Repeat Customers"],
    "Count": [new_customers, repeat_customers]
})

fig = px.pie(
    freq_df,
    names="Customer Type",
    values="Count",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)
